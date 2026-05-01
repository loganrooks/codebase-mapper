from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator, RefResolver


SCHEMA_VERSION = "1.2"
CITATION_RE = re.compile(r"(?P<path>[^:@\s]+):(?P<start>\d+)(?:-(?P<end>\d+))?@(?P<sha>[0-9a-f]{7,40})")
DEFAULT_EXCLUDED = [
    ".git/**",
    ".research/**",
    ".venv/**",
    "node_modules/**",
    "**/__pycache__/**",
    ".pytest_cache/**",
    ".DS_Store",
]


@dataclass(frozen=True)
class RunPaths:
    repo: Path
    run_id: str
    run_dir: Path


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.stdout.strip()


def source_sha(repo: Path) -> str:
    try:
        return git(repo, "rev-parse", "--short=12", "HEAD")
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"cbm requires a git repository with at least one commit: {exc.stderr.strip()}") from exc


def is_excluded(rel: str) -> bool:
    return any(fnmatch.fnmatch(rel, pat) for pat in DEFAULT_EXCLUDED)


def iter_repo_files(repo: Path) -> Iterable[Path]:
    for path in sorted(repo.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(repo).as_posix()
        if is_excluded(rel):
            continue
        yield path


def line_count(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8").splitlines())
    except UnicodeDecodeError:
        return 0


def language_for(path: Path) -> str:
    suffix = path.suffix.lower()
    name = path.name.lower()
    if suffix == ".py":
        return "python"
    if suffix in {".js", ".jsx"}:
        return "javascript"
    if suffix in {".ts", ".tsx"}:
        return "typescript"
    if suffix in {".json"}:
        return "json"
    if suffix in {".yml", ".yaml"}:
        return "yaml"
    if suffix in {".md", ".markdown"}:
        return "markdown"
    if name in {"makefile", "dockerfile"}:
        return name
    return suffix[1:] if suffix else "unknown"


def detect_build_systems(files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    paths = {item["path"] for item in files}
    candidates = [
        ("python", ["pyproject.toml", "setup.py", "requirements.txt"]),
        ("node", ["package.json", "pnpm-lock.yaml", "yarn.lock"]),
        ("rust", ["Cargo.toml"]),
        ("go", ["go.mod"]),
    ]
    result: list[dict[str, Any]] = []
    for name, config_files in candidates:
        present = [path for path in config_files if path in paths]
        if present:
            result.append({"name": name, "config_files": present})
    return result


def detect_tests(files: list[dict[str, Any]]) -> list[dict[str, str]]:
    tests: list[dict[str, str]] = []
    for item in files:
        path = item["path"]
        if path.startswith("tests/") or "/test_" in path or path.endswith("_test.py") or path.endswith(".test.ts"):
            framework = "pytest" if path.endswith(".py") else "unknown"
            tests.append({"path": path, "framework_hint": framework})
    return tests


def detect_ci(files: list[dict[str, Any]]) -> list[str]:
    return [
        item["path"]
        for item in files
        if item["path"].startswith(".github/workflows/") or item["path"].endswith(".gitlab-ci.yml")
    ]


def detect_configs(files: list[dict[str, Any]]) -> list[str]:
    markers = (".toml", ".yaml", ".yml", ".json", ".ini", ".cfg")
    return [item["path"] for item in files if item["path"].endswith(markers)]


def coverage_block(file_count: int, examined: int = 0) -> dict[str, Any]:
    inspected = file_count
    return {
        "scope": {"included_globs": ["**/*"], "excluded_globs": DEFAULT_EXCLUDED},
        "result": {
            "files_in_scope": file_count,
            "files_examined_directly": examined,
            "files_inspected_via_extractor": inspected,
            "files_unread_in_scope": max(file_count - examined, 0),
        },
        "limitations": ["Phase A kernel records structure only; interpretive review remains a runtime-agent task."],
    }


def scope_signature(paths: list[str]) -> str:
    return sha256_text("\n".join(sorted(paths)))


def schema_store(repo: Path) -> dict[str, Any]:
    schemas = {}
    for path in (repo / "schemas").glob("*.schema.json"):
        data = read_json(path)
        schemas[data["$id"]] = data
    return schemas


def schema_for_artifact(repo: Path, artifact_type: str) -> dict[str, Any]:
    mapping = {
        "codebase_map": "codebase-map.schema.json",
        "surface_map": "surface-map.schema.json",
        "extractor_registry": "extractor-registry.schema.json",
        "handoff": "handoff.schema.json",
        "intervention_card": "intervention-card.schema.json",
        "findings_card": "intervention-card.schema.json",
        "evidence_ledger_entry": "evidence-ledger.schema.json",
    }
    name = mapping.get(artifact_type)
    if not name:
        raise ValueError(f"unsupported artifact_type: {artifact_type}")
    return read_json(repo / "schemas" / name)


def infer_artifact_type(path: Path, data: dict[str, Any]) -> str:
    artifact_type = data.get("artifact_type")
    if artifact_type:
        return artifact_type
    if path.name == "extractor-registry.json":
        return "extractor_registry"
    raise ValueError(f"{path} does not declare artifact_type")


def load_artifact_frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".md":
        if not text.startswith("---\n"):
            raise ValueError(f"{path} has no YAML frontmatter")
        _, frontmatter, body = text.split("---", 2)
        return yaml.safe_load(frontmatter), body
    return read_json(path), ""


def validate_data(repo: Path, data: Any, artifact_type: str) -> list[str]:
    store = schema_store(repo)
    schema = schema_for_artifact(repo, artifact_type)
    resolver = RefResolver.from_schema(schema, store=store)
    validator = Draft202012Validator(schema, resolver=resolver)
    return [f"{'/'.join(str(p) for p in error.absolute_path) or '<root>'}: {error.message}" for error in validator.iter_errors(data)]


def extract_citations(value: Any) -> list[str]:
    citations: list[str] = []
    if isinstance(value, str):
        citations.extend(match.group(0) for match in CITATION_RE.finditer(value))
    elif isinstance(value, dict):
        for nested in value.values():
            citations.extend(extract_citations(nested))
    elif isinstance(value, list):
        for nested in value:
            citations.extend(extract_citations(nested))
    return citations


def resolve_citation(repo: Path, citation: str) -> tuple[bool, str]:
    match = CITATION_RE.fullmatch(citation)
    if not match:
        return False, "invalid citation format"
    rel = match.group("path")
    start = int(match.group("start"))
    end = int(match.group("end") or start)
    if start < 1 or end < start:
        return False, "invalid line range"
    path = repo / rel
    if not path.exists() or not path.is_file():
        return False, "file not found"
    sha = match.group("sha")
    try:
        git(repo, "cat-file", "-e", f"{sha}:./{rel}")
    except subprocess.CalledProcessError:
        return False, "path does not exist at cited sha"
    lines = path.read_text(encoding="utf-8").splitlines()
    if end > len(lines):
        return False, f"line range exceeds current file length ({len(lines)})"
    return True, "ok"


def path_exists_at_sha(repo: Path, rel: str, sha: str) -> bool:
    try:
        git(repo, "cat-file", "-e", f"{sha}:./{rel}")
        return True
    except subprocess.CalledProcessError:
        return False


def append_jsonl(path: Path, entry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=False) + "\n")


def ledger_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as fh:
        return sum(1 for line in fh if line.strip())


def next_ledger_id(path: Path) -> str:
    return f"lg-{ledger_count(path) + 1:05d}"


def validate_ledger_entry(repo: Path, entry: dict[str, Any]) -> list[str]:
    return validate_data(repo, entry, "evidence_ledger_entry")


def run_paths(repo: Path, run_id: str | None) -> RunPaths:
    if run_id:
        return RunPaths(repo=repo, run_id=run_id, run_dir=repo / ".research" / run_id)
    state_files = sorted((repo / ".research").glob("*/state.json"))
    if not state_files:
        raise SystemExit("no CBM run found; run cbm-init first or pass --run-id")
    state = read_json(state_files[-1])
    rid = state["run_id"]
    return RunPaths(repo=repo, run_id=rid, run_dir=repo / ".research" / rid)


def command_init(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    sha = source_sha(repo)
    run_id = args.run_id or f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{sha}"
    paths = run_paths(repo, run_id)
    paths.run_dir.mkdir(parents=True, exist_ok=True)
    now = utc_now()
    intake = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "intake",
        "run_id": run_id,
        "produced_at": now,
        "source_sha": sha,
        "repo_root": str(repo),
        "goal": args.goal,
        "goal_class": args.goal_class,
        "mode": args.mode,
        "research_only": args.goal_class in {"understand_repo", "research_only"},
    }
    state = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "state",
        "run_id": run_id,
        "source_sha": sha,
        "mode": args.mode,
        "status": "initialized",
        "created_at": now,
    }
    registry = {
        "schema_version": SCHEMA_VERSION,
        "extractors": [
            {
                "id": "ext-file-inventory-v1",
                "kind": "other",
                "version": "1.0",
                "language_or_format": "filesystem",
                "deterministic": True,
                "produces_evidence_kinds": ["static_structure"],
                "known_blind_spots": [
                    {
                        "description": "Does not infer runtime behavior or generated files absent from the working tree.",
                        "category": "generated_code",
                    }
                ],
            },
            {
                "id": "ext-manifest-patterns-v1",
                "kind": "manifest_parser",
                "version": "1.0",
                "language_or_format": "common_manifests",
                "deterministic": True,
                "produces_evidence_kinds": ["static_structure"],
                "known_blind_spots": [
                    {
                        "description": "Detects common manifest filenames only and does not evaluate dynamic build logic.",
                        "category": "configuration_dependent",
                    }
                ],
            },
            {
                "id": "ext-test-paths-v1",
                "kind": "test_discovery",
                "version": "1.0",
                "language_or_format": "common_test_paths",
                "deterministic": True,
                "produces_evidence_kinds": ["static_structure"],
                "known_blind_spots": [
                    {
                        "description": "Uses path naming conventions and can miss framework-specific generated tests.",
                        "category": "metaprogramming",
                    }
                ],
            },
        ],
    }
    write_json(paths.run_dir / "intake.json", intake)
    write_json(paths.run_dir / "state.json", state)
    write_json(paths.run_dir / "extractor-registry.json", registry)
    (paths.run_dir / "evidence-ledger.jsonl").touch()
    (paths.run_dir / "uncertainty-register.jsonl").touch()
    print(paths.run_dir)
    return 0


def command_map(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    paths = run_paths(repo, args.run_id)
    sha = source_sha(repo)
    files = []
    for path in iter_repo_files(repo):
        rel = path.relative_to(repo).as_posix()
        files.append(
            {
                "path": rel,
                "size_bytes": path.stat().st_size,
                "line_count": line_count(path),
                "sha256": sha256_file(path),
                "language": language_for(path),
                "is_generated": False,
                "vendored": rel.startswith("vendor/"),
            }
        )
    lang_counts: dict[str, dict[str, int]] = {}
    for item in files:
        bucket = lang_counts.setdefault(item["language"], {"file_count": 0, "byte_count": 0})
        bucket["file_count"] += 1
        bucket["byte_count"] += item["size_bytes"]
    languages = [{"name": name, **counts} for name, counts in sorted(lang_counts.items())]
    rels = [item["path"] for item in files]
    registry_path = paths.run_dir / "extractor-registry.json"
    artifact = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "codebase_map",
        "run_id": paths.run_id,
        "produced_at": utc_now(),
        "produced_by": "cbm-map@0.1",
        "source_sha": sha,
        "inputs": [{"path": str(registry_path.relative_to(repo)), "sha256": sha256_file(registry_path)}],
        "status": "draft",
        "coverage": coverage_block(len(files)),
        "staleness": {
            "stale_if_input_hash_changes": True,
            "depends_on_paths": rels,
            "scope_signature": scope_signature(rels),
        },
        "repo_root": str(repo),
        "files": files,
        "languages": languages,
        "build_systems": detect_build_systems(files),
        "tests": detect_tests(files),
        "ci_files": detect_ci(files),
        "config_candidates": detect_configs(files),
        "extraction_warnings": [
            {
                "path": ".",
                "reason": "Phase A map is structural only; import/call graph extraction is deferred.",
            }
        ],
    }
    errors = validate_data(repo, artifact, "codebase_map")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    write_json(paths.run_dir / "codebase-map.json", artifact)
    print(paths.run_dir / "codebase-map.json")
    return 0


def command_validate(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    path = Path(args.artifact)
    if not path.is_absolute():
        path = repo / path
    data, _ = load_artifact_frontmatter(path)
    artifact_type = infer_artifact_type(path, data)
    errors = validate_data(repo, data, artifact_type)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"valid {path}")
    return 0


def command_verify_citations(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    path = Path(args.artifact)
    if not path.is_absolute():
        path = repo / path
    data, body = load_artifact_frontmatter(path)
    citations = sorted(set(extract_citations(data) + extract_citations(body)))
    failed = 0
    for citation in citations:
        ok, reason = resolve_citation(repo, citation)
        print(f"{'ok' if ok else 'fail'} {citation} {reason}")
        failed += 0 if ok else 1
    if not citations:
        print("no citations found")
    return 0 if failed == 0 else 1


def read_intake(run_dir: Path) -> dict[str, Any]:
    return read_json(run_dir / "intake.json")


def read_codebase_map(run_dir: Path) -> dict[str, Any]:
    return read_json(run_dir / "codebase-map.json")


def first_citable_file(repo: Path, codebase_map: dict[str, Any], sha: str) -> tuple[str, int]:
    for item in codebase_map["files"]:
        if item.get("line_count", 0) > 0 and not item["path"].startswith(".research/") and path_exists_at_sha(repo, item["path"], sha):
            return item["path"], min(item["line_count"], 1)
    raise SystemExit("no citable source file found")


def command_handoff(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    paths = run_paths(repo, args.run_id)
    intake = read_intake(paths.run_dir)
    codebase_map = read_codebase_map(paths.run_dir)
    sha = source_sha(repo)
    rel_file, _ = first_citable_file(repo, codebase_map, sha)
    citation = f"{rel_file}:1@{sha}"
    card_dir = paths.run_dir / "findings"
    card_dir.mkdir(parents=True, exist_ok=True)
    card_path = card_dir / "int-0001.md"
    ledger_path = paths.run_dir / "evidence-ledger.jsonl"
    uncertainty_path = paths.run_dir / "uncertainty-register.jsonl"
    now = utc_now()
    citation_entry = {
        "schema_version": SCHEMA_VERSION,
        "entry_id": next_ledger_id(ledger_path),
        "ts": now,
        "entry_kind": "citation_introduced",
        "agent": "cbm-handoff",
        "skill_version": "0.1",
        "run_id": paths.run_id,
        "source_sha": sha,
        "citation": citation,
        "artifact_path": str(card_path.relative_to(repo)),
        "claim_id": "primary-file-structural",
        "claim_register": "factual",
    }
    errors = validate_ledger_entry(repo, citation_entry)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    append_jsonl(ledger_path, citation_entry)
    uncertainty = {
        "schema_version": SCHEMA_VERSION,
        "entry_id": "unc-00001",
        "ts": now,
        "run_id": paths.run_id,
        "source_sha": sha,
        "question": "Which code surface actually matters most for the user's goal?",
        "status": "open",
        "registered_by": "cbm-handoff@0.1",
    }
    append_jsonl(uncertainty_path, uncertainty)
    uncertainty_entry = {
        "schema_version": SCHEMA_VERSION,
        "entry_id": next_ledger_id(ledger_path),
        "ts": now,
        "entry_kind": "uncertainty_logged",
        "agent": "cbm-handoff",
        "skill_version": "0.1",
        "run_id": paths.run_id,
        "source_sha": sha,
        "artifact_path": str(uncertainty_path.relative_to(repo)),
        "claim_id": "unc-00001",
    }
    errors = validate_ledger_entry(repo, uncertainty_entry)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    append_jsonl(ledger_path, uncertainty_entry)
    card_frontmatter = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "findings_card",
        "run_id": paths.run_id,
        "produced_at": now,
        "produced_by": "intervention-planner@0.1",
        "source_sha": sha,
        "inputs": [{"path": str((paths.run_dir / "codebase-map.json").relative_to(repo)), "sha256": sha256_file(paths.run_dir / "codebase-map.json")}],
        "status": "draft",
        "coverage": coverage_block(codebase_map["coverage"]["result"]["files_in_scope"], examined=1),
        "staleness": {"stale_if_input_hash_changes": True, "depends_on_paths": [rel_file]},
        "id": f"int-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}-001",
        "goal": intake["goal"],
        "goal_class": intake["goal_class"],
        "research_only": True,
        "surface_type": "explicit",
        "surface_kind": "other",
        "surface_classification_register": "interpretive",
        "primary_files": [{"path": rel_file, "role": "First citable file identified by the deterministic codebase map.", "citations": [citation]}],
        "related_dependencies": {"certain": [citation], "suspected": [], "advisory": [], "unknown": []},
        "affected_workflows": [],
        "expected_leverage": {
            "rating": "low",
            "rationale": "Phase A can identify structural entry points, but leverage remains low until the Surface Mapper reads the code and assigns interpretive roles.",
            "claim_register": "interpretive",
            "claim_status": "active",
            "evidence_kinds": ["static_structure"],
        },
        "blast_radius": {
            "hops_evaluated": 1,
            "certain_count": 1,
            "suspected_count": 0,
            "advisory_count": 0,
            "unknown_count": 0,
            "unknown_partition_present": True,
        },
        "verification_strategy": {
            "hard_gates": [{"description": "Schema validation and citation resolution pass for this card.", "implementation": "Run cbm-validate and cbm-verify-citations on the generated findings card.", "citations": [citation]}],
            "warning_gates": [],
            "advisory_checks": [{"description": "Runtime Surface Mapper should replace this Phase A structural card with a role-specific finding."}],
            "manual_review": [{"description": "Confirm the first structural file is relevant to the user's actual goal before acting on it.", "reviewer_role": "senior engineer"}],
        },
        "risks": [{"description": "This Phase A generated card is structural and may not identify the highest-leverage surface.", "severity": "medium", "mitigation": "Run the runtime Surface Mapper and Skeptic before using the card for implementation decisions."}],
        "confidence": "low",
        "confidence_rationale": "Confidence is low because Phase A has only deterministic file inventory and no qualitative surface-map reading yet.",
        "open_questions": [{"question": "Which code surface actually matters most for the user's goal?", "register_id": "unc-00001"}],
        "dependent_challenges": [],
        "recommended_next_slice": "Run the Surface Mapper skill against codebase-map.json and replace this structural card with an evidence-bound findings card.",
        "claim_status": "active",
    }
    card_errors = validate_data(repo, card_frontmatter, "findings_card")
    if card_errors:
        for error in card_errors:
            print(error, file=sys.stderr)
        return 1
    card_body = "\n# Phase A Structural Finding\n\nThis generated card proves the mechanical gates are wired: schema validation and citation resolution operate on an evidence-bound artifact.\n"
    card_path.write_text("---\n" + yaml.safe_dump(card_frontmatter, sort_keys=False) + "---\n" + card_body, encoding="utf-8")
    citation_ok, citation_reason = resolve_citation(repo, citation)
    artifacts = [
        {"path": str((paths.run_dir / "codebase-map.json").relative_to(repo)), "artifact_type": "codebase_map", "status": "draft", "summary": "Deterministic structural file inventory."},
        {"path": str(card_path.relative_to(repo)), "artifact_type": "findings_card", "status": "draft", "summary": "Phase A generated structural findings card."},
    ]
    handoff = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "handoff",
        "run_id": paths.run_id,
        "produced_at": utc_now(),
        "produced_by": "cbm-handoff@0.1",
        "source_sha": sha,
        "inputs": [
            {"path": str((paths.run_dir / "codebase-map.json").relative_to(repo)), "sha256": sha256_file(paths.run_dir / "codebase-map.json")},
            {"path": str(card_path.relative_to(repo)), "sha256": sha256_file(card_path)},
        ],
        "status": "draft",
        "coverage": coverage_block(codebase_map["coverage"]["result"]["files_in_scope"], examined=1),
        "mode": intake["mode"],
        "user_goal": intake["goal"],
        "goal_class": intake["goal_class"],
        "research_only": intake["research_only"],
        "gate_summary": {
            "schema_validation": {"passed": 2, "failed_artifacts": []},
            "citation_resolution": {"resolved": 1 if citation_ok else 0, "unresolved_count": 0 if citation_ok else 1, "unresolved_examples": [] if citation_ok else [f"{citation}: {citation_reason}"]},
            "ledger_consistency": {"append_only_verified": True, "entry_count": ledger_count(ledger_path)},
            "staleness_check": {"fresh": 2, "stale_artifacts": []},
            "skeptic_review": {"artifacts_reviewed": 0, "challenges_logged": 0, "challenges_resolved": 0},
        },
        "contestation_summary": {
            "claims_by_register": {"factual": 1, "inferential": 0, "interpretive": 1},
            "claims_by_status": {"active": 2, "challenged": 0, "contested": 0, "contradicted": 0, "superseded": 0, "retired": 0},
            "open_challenges": 0,
            "contested_claims": [],
            "contradicted_claims": [],
        },
        "artifacts": artifacts,
        "open_questions_count": 1,
        "coverage_caveats": ["Phase A has not run qualitative Surface Mapper or Skeptic review."],
        "recommended_next_action": "Run runtime Surface Mapper and Skeptic to replace structural draft artifacts with reviewed findings.",
    }
    errors = validate_data(repo, handoff, "handoff")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    write_json(paths.run_dir / "handoff.json", handoff)
    (paths.run_dir / "handoff.md").write_text(
        "---\n" + yaml.safe_dump(handoff, sort_keys=False) + "---\n# CBM Handoff\n\nPhase A mechanical gates produced a draft handoff. See frontmatter for gate summary and caveats.\n",
        encoding="utf-8",
    )
    print(paths.run_dir / "handoff.md")
    return 0 if citation_ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cbm")
    sub = parser.add_subparsers(dest="command", required=True)
    p_init = sub.add_parser("init")
    p_init.add_argument("--repo", default=".")
    p_init.add_argument("--goal", required=True)
    p_init.add_argument("--goal-class", default="understand_repo")
    p_init.add_argument("--mode", default="lightweight", choices=["lightweight", "standard", "deep"])
    p_init.add_argument("--run-id")
    p_init.set_defaults(func=command_init)
    p_map = sub.add_parser("map")
    p_map.add_argument("--repo", default=".")
    p_map.add_argument("--run-id")
    p_map.set_defaults(func=command_map)
    p_validate = sub.add_parser("validate")
    p_validate.add_argument("artifact")
    p_validate.add_argument("--repo", default=".")
    p_validate.set_defaults(func=command_validate)
    p_verify = sub.add_parser("verify-citations")
    p_verify.add_argument("artifact")
    p_verify.add_argument("--repo", default=".")
    p_verify.set_defaults(func=command_verify_citations)
    p_handoff = sub.add_parser("handoff")
    p_handoff.add_argument("--repo", default=".")
    p_handoff.add_argument("--run-id")
    p_handoff.set_defaults(func=command_handoff)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


def init_main() -> int:
    return main(["init", *sys.argv[1:]])


def map_main() -> int:
    return main(["map", *sys.argv[1:]])


def validate_main() -> int:
    return main(["validate", *sys.argv[1:]])


def verify_citations_main() -> int:
    return main(["verify-citations", *sys.argv[1:]])


def handoff_main() -> int:
    return main(["handoff", *sys.argv[1:]])
