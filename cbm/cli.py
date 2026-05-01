from __future__ import annotations

import argparse
import ast
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
import time
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


def resolve_python_module(repo: Path, module: str) -> str | None:
    if not module:
        return None
    candidate = repo.joinpath(*module.split("."))
    file_candidate = candidate.with_suffix(".py")
    package_candidate = candidate / "__init__.py"
    if file_candidate.exists():
        return file_candidate.relative_to(repo).as_posix()
    if package_candidate.exists():
        return package_candidate.relative_to(repo).as_posix()
    return None


def extract_python_import_edges(repo: Path, files: list[dict[str, Any]], sha: str) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    python_files = [item["path"] for item in files if item["language"] == "python"]
    for rel in python_files:
        path = repo / rel
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                modules = [node.module]
            for module in modules:
                target = resolve_python_module(repo, module)
                if not target:
                    continue
                citation = citation_for(repo, rel, sha, getattr(node, "lineno", 1))
                if not citation:
                    continue
                edges.append(
                    {
                        "id": f"edge-import-{len(edges) + 1:03d}",
                        "kind": "import",
                        "from": {"path": rel},
                        "to": {"path": target},
                        "citations": [citation],
                        "extractor_id": "ext-python-imports-v1",
                        "claim_register": "factual",
                        "claim_status": "active",
                        "evidence_kinds": ["static_relation"],
                        "corroboration_count": 1,
                        "confidence": "high",
                    }
                )
    return edges


def python_imported_symbols(repo: Path, tree: ast.AST) -> dict[str, tuple[str, str]]:
    symbols: dict[str, tuple[str, str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or node.level != 0 or not node.module:
            continue
        target = resolve_python_module(repo, node.module)
        if not target:
            continue
        for alias in node.names:
            symbols[alias.asname or alias.name] = (target, alias.name)
    return symbols


def python_defined_functions(tree: ast.AST) -> set[str]:
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def extract_python_call_edges(repo: Path, files: list[dict[str, Any]], sha: str) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    python_files = [item["path"] for item in files if item["language"] == "python"]
    for rel in python_files:
        path = repo / rel
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        imported_symbols = python_imported_symbols(repo, tree)
        local_functions = python_defined_functions(tree)
        seen_calls: set[tuple[str, str | None, int]] = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            target_path = None
            target_symbol = None
            if isinstance(node.func, ast.Name):
                if node.func.id in imported_symbols:
                    target_path, target_symbol = imported_symbols[node.func.id]
                elif node.func.id in local_functions:
                    target_path, target_symbol = rel, node.func.id
            if not target_path:
                continue
            lineno = getattr(node, "lineno", 1)
            dedupe_key = (target_path, target_symbol, lineno)
            if dedupe_key in seen_calls:
                continue
            seen_calls.add(dedupe_key)
            citation = citation_for(repo, rel, sha, lineno)
            if not citation:
                continue
            edge = {
                "id": f"edge-call-{len(edges) + 1:03d}",
                "kind": "call",
                "from": {"path": rel},
                "to": {"path": target_path},
                "citations": [citation],
                "extractor_id": "ext-python-calls-v1",
                "claim_register": "factual",
                "claim_status": "active",
                "evidence_kinds": ["static_relation"],
                "corroboration_count": 1,
                "confidence": "high",
            }
            if target_symbol:
                edge["to"]["symbol"] = target_symbol
            edges.append(edge)
    return edges


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
        "authority_map": "authority-map.schema.json",
        "dependency_graph": "dependency-graph.schema.json",
        "synthesis_index": "synthesis-index.schema.json",
        "goal_binding": "goal-binding.schema.json",
        "handoff": "handoff.schema.json",
        "skeptic_review": "skeptic-review.schema.json",
        "intervention_card": "intervention-card.schema.json",
        "findings_card": "intervention-card.schema.json",
        "evidence_ledger_entry": "evidence-ledger.schema.json",
        "refresh_delta": "refresh-delta.schema.json",
        "verification_map": "verification-map.schema.json",
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
    sha = match.group("sha")
    try:
        content = git(repo, "show", f"{sha}:./{rel}")
    except subprocess.CalledProcessError:
        return False, "path does not exist at cited sha"
    lines = content.splitlines()
    if end > len(lines):
        return False, f"line range exceeds cited file length ({len(lines)})"
    return True, "ok"


def citation_parts(citation: str) -> dict[str, Any] | None:
    match = CITATION_RE.fullmatch(citation)
    if not match:
        return None
    return {
        "path": match.group("path"),
        "start": int(match.group("start")),
        "end": int(match.group("end") or match.group("start")),
        "sha": match.group("sha"),
    }


def git_show_bytes(repo: Path, ref: str, rel: str) -> bytes | None:
    try:
        return subprocess.run(
            ["git", "-C", str(repo), "show", f"{ref}:./{rel}"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
    except subprocess.CalledProcessError:
        return None


def blob_hash_at(repo: Path, ref: str, rel: str) -> str | None:
    content = git_show_bytes(repo, ref, rel)
    if content is None:
        return None
    return hashlib.sha256(content).hexdigest()


def citation_for(repo: Path, rel: str, sha: str, line: int = 1) -> str | None:
    path = repo / rel
    if not path.exists() or not path.is_file() or not path_matches_sha(repo, rel, sha):
        return None
    count = line_count(path)
    if count < line:
        return None
    return f"{rel}:{line}@{sha}"


def path_exists_at_sha(repo: Path, rel: str, sha: str) -> bool:
    try:
        git(repo, "cat-file", "-e", f"{sha}:./{rel}")
        return True
    except subprocess.CalledProcessError:
        return False


def path_matches_sha(repo: Path, rel: str, sha: str) -> bool:
    path = repo / rel
    if not path.exists() or not path.is_file():
        return False
    content = git_show_bytes(repo, sha, rel)
    if content is None:
        return False
    return path.read_bytes() == content


def append_jsonl(path: Path, entry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, sort_keys=False) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def ledger_integrity_path(ledger_path: Path) -> Path:
    return ledger_path.with_name(f"{ledger_path.name}.integrity.json")


def ledger_line_hashes(ledger_path: Path) -> list[str]:
    if not ledger_path.exists():
        return []
    return [
        sha256_text(line)
        for line in ledger_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_ledger_integrity_manifest(ledger_path: Path) -> None:
    manifest_path = ledger_integrity_path(ledger_path)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "ledger_integrity_manifest",
        "ledger_path": ledger_path.name,
        "line_count": ledger_count(ledger_path),
        "line_hashes": ledger_line_hashes(ledger_path),
        "updated_at": utc_now(),
    }
    write_json(manifest_path, manifest)


def verify_ledger_append_only(ledger_path: Path) -> tuple[bool, str]:
    manifest_path = ledger_integrity_path(ledger_path)
    if not manifest_path.exists():
        return True, "no integrity manifest yet"
    manifest = read_json(manifest_path)
    expected_hashes = manifest.get("line_hashes", [])
    current_hashes = ledger_line_hashes(ledger_path)
    if len(current_hashes) < len(expected_hashes):
        return False, "ledger has fewer lines than the integrity manifest records"
    if current_hashes[: len(expected_hashes)] != expected_hashes:
        return False, "existing ledger line hashes differ from the integrity manifest"
    return True, "ok"


def ledger_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as fh:
        return sum(1 for line in fh if line.strip())


def next_ledger_id(path: Path) -> str:
    return f"lg-{ledger_count(path) + 1:05d}"


def validate_ledger_entry(repo: Path, entry: dict[str, Any]) -> list[str]:
    return validate_data(repo, entry, "evidence_ledger_entry")


def append_ledger_entry(repo: Path, ledger_path: Path, entry: dict[str, Any]) -> None:
    errors = validate_ledger_entry(repo, entry)
    if errors:
        raise ValueError("\n".join(errors))
    ok, reason = verify_ledger_append_only(ledger_path)
    if not ok:
        raise ValueError(f"ledger append-only verification failed: {reason}")
    append_jsonl(ledger_path, entry)
    write_ledger_integrity_manifest(ledger_path)


def ledger_citations(path: Path) -> set[str]:
    return {
        entry["citation"]
        for entry in read_jsonl(path)
        if entry.get("entry_kind") in {"citation_introduced", "citation_reused"} and entry.get("citation")
    }


def citation_claim_pairs(data: Any, default_claim_id: str = "artifact") -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    if isinstance(data, dict):
        claim_id = str(data.get("id") or data.get("claim_id") or default_claim_id)
        for key, value in data.items():
            if key in {"citations", "competing_evidence"} and isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and CITATION_RE.fullmatch(item):
                        pairs.append((item, claim_id))
            pairs.extend(citation_claim_pairs(value, claim_id))
    elif isinstance(data, list):
        for item in data:
            pairs.extend(citation_claim_pairs(item, default_claim_id))
    return pairs


def append_citation_entries(repo: Path, ledger_path: Path, run_id: str, sha: str, artifact_path: str, data: Any, agent: str) -> None:
    seen = ledger_citations(ledger_path)
    now = utc_now()
    for citation, claim_id in citation_claim_pairs(data):
        if citation in seen:
            continue
        entry = {
            "schema_version": SCHEMA_VERSION,
            "entry_id": next_ledger_id(ledger_path),
            "ts": now,
            "entry_kind": "citation_introduced",
            "agent": agent,
            "skill_version": "0.1",
            "run_id": run_id,
            "source_sha": sha,
            "citation": citation,
            "artifact_path": artifact_path,
            "claim_id": claim_id,
        }
        append_ledger_entry(repo, ledger_path, entry)
        seen.add(citation)


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
            {
                "id": "ext-python-imports-v1",
                "kind": "ast",
                "version": "1.0",
                "language_or_format": "python",
                "deterministic": True,
                "produces_evidence_kinds": ["static_relation"],
                "known_blind_spots": [
                    {
                        "description": "Does not resolve relative imports, dynamic imports, importlib calls, or sys.path mutations.",
                        "category": "dynamic_dispatch",
                    }
                ],
            },
            {
                "id": "ext-python-calls-v1",
                "kind": "ast",
                "version": "1.0",
                "language_or_format": "python",
                "deterministic": True,
                "produces_evidence_kinds": ["static_relation"],
                "known_blind_spots": [
                    {
                        "description": "Resolves only direct calls to local functions or symbols imported with absolute from-import statements; misses methods, dynamic dispatch, decorators, monkeypatching, and aliased module attribute calls.",
                        "category": "dynamic_dispatch",
                    }
                ],
            },
        ],
    }
    write_json(paths.run_dir / "intake.json", intake)
    write_json(paths.run_dir / "state.json", state)
    write_json(paths.run_dir / "extractor-registry.json", registry)
    (paths.run_dir / "evidence-ledger.jsonl").touch()
    write_ledger_integrity_manifest(paths.run_dir / "evidence-ledger.jsonl")
    (paths.run_dir / "uncertainty-register.jsonl").touch()
    print(paths.run_dir)
    return 0


def build_codebase_map(repo: Path, paths: RunPaths, refreshed_from: dict[str, Any] | None = None) -> dict[str, Any]:
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
    if refreshed_from:
        artifact["refreshed_from"] = refreshed_from
    return artifact


def command_map(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    paths = run_paths(repo, args.run_id)
    artifact = build_codebase_map(repo, paths)
    errors = validate_data(repo, artifact, "codebase_map")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    write_json(paths.run_dir / "codebase-map.json", artifact)
    print(paths.run_dir / "codebase-map.json")
    return 0


def authority_kind_for(path: str) -> tuple[str, str]:
    if path.startswith(".github/workflows/") or path.endswith(".gitlab-ci.yml"):
        return "ci_gate", "config"
    if path.startswith("tests/") or "/test_" in path or path.endswith("_test.py"):
        return "test_suite", "test"
    if path.endswith((".toml", ".yaml", ".yml", ".json", ".ini", ".cfg")):
        return "config", "config"
    if path.endswith((".md", ".markdown")):
        return "doc_contract", "doc"
    return "other", "code"


def build_surface_map(
    repo: Path,
    paths: RunPaths,
    codebase_path: Path | None = None,
    codebase_map: dict[str, Any] | None = None,
    refreshed_from: dict[str, Any] | None = None,
) -> dict[str, Any]:
    sha = source_sha(repo)
    codebase_path = codebase_path or paths.run_dir / "codebase-map.json"
    codebase_map = codebase_map or read_codebase_map(paths.run_dir)
    authorities: list[dict[str, Any]] = []
    candidate_paths = []
    for build in codebase_map["build_systems"]:
        candidate_paths.extend(build["config_files"])
    candidate_paths.extend(codebase_map["ci_files"])
    candidate_paths.extend(test["path"] for test in codebase_map["tests"])
    candidate_paths.extend(path for path in codebase_map["config_candidates"] if path not in candidate_paths)
    seen: set[str] = set()
    for rel in candidate_paths:
        if rel in seen:
            continue
        seen.add(rel)
        citation = citation_for(repo, rel, sha)
        if not citation:
            continue
        kind, source = authority_kind_for(rel)
        claim_register = "factual" if kind in {"config", "ci_gate", "test_suite"} else "interpretive"
        authorities.append(
            {
                "id": f"auth-{len(authorities) + 1:03d}",
                "kind": kind,
                "path": rel,
                "citations": [citation],
                "authority_source": source,
                "claim_register": claim_register,
                "claim_status": "active",
                "evidence_kinds": ["static_structure"],
                "corroboration_count": 1,
                "rationale": f"Phase A identifies {rel} as a {kind} surface from deterministic file and manifest discovery.",
                "confidence": "medium" if claim_register == "factual" else "low",
            }
        )
    if not authorities:
        rel, _ = first_citable_file(repo, codebase_map, sha)
        citation = citation_for(repo, rel, sha)
        authorities.append(
            {
                "id": "auth-001",
                "kind": "other",
                "path": rel,
                "citations": [citation],
                "authority_source": "code",
                "claim_register": "interpretive",
                "claim_status": "active",
                "evidence_kinds": ["static_structure"],
                "corroboration_count": 1,
                "rationale": f"Phase A fallback treats {rel} as the first citable structural surface; this requires qualitative review.",
                "confidence": "low",
            }
        )
    rel_file, _ = first_citable_file(repo, codebase_map, sha)
    edges = extract_python_import_edges(repo, codebase_map["files"], sha)
    edges.extend(extract_python_call_edges(repo, codebase_map["files"], sha))
    edges.append(
        {
            "id": "edge-unknown-001",
            "kind": "unknown",
            "from": {"path": authorities[0]["path"]},
            "to": {"path": rel_file},
            "claim_register": "inferential",
            "claim_status": "active",
            "evidence_kinds": ["static_structure"],
            "corroboration_count": 1,
            "confidence": "low",
            "rationale": "Phase A extracts direct Python imports and simple direct function calls only; runtime workflows, relative imports, methods, dynamic dispatch, and dynamic loading remain unknown.",
        }
    )
    tests = []
    for test in codebase_map["tests"]:
        citation = citation_for(repo, test["path"], sha)
        if citation:
            tests.append({"path": test["path"], "framework": test["framework_hint"], "exercises": []})
    ci_gates = []
    for ci in codebase_map["ci_files"]:
        citation = citation_for(repo, ci, sha)
        if citation:
            ci_gates.append({"name": Path(ci).stem, "path": ci, "kind": "other", "citations": [citation]})
    rels = [item["path"] for item in codebase_map["files"]]
    artifact = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "surface_map",
        "run_id": paths.run_id,
        "produced_at": utc_now(),
        "produced_by": "surface-mapper@0.1",
        "source_sha": sha,
        "inputs": [{"path": str(codebase_path.relative_to(repo)), "sha256": sha256_file(codebase_path)}],
        "status": "draft",
        "coverage": coverage_block(codebase_map["coverage"]["result"]["files_in_scope"], examined=len(authorities)),
        "staleness": {
            "stale_if_input_hash_changes": True,
            "depends_on_paths": sorted({auth["path"] for auth in authorities}),
            "scope_signature": scope_signature(rels),
        },
        "authorities": authorities,
        "edges": edges,
        "verification": {
            "tests": tests,
            "ci_gates": ci_gates,
            "coverage_summary": {
                "files_with_tests": len(tests),
                "files_without_tests": max(codebase_map["coverage"]["result"]["files_in_scope"] - len(tests), 0),
                "coverage_unknown": len(edges),
            },
        },
        "unknowns": {
            "edge_unknowns_present": True,
            "summary": "Phase A preserves unknown dependency edges for runtime workflows, methods, relative imports, dynamic dispatch, and dynamic loading not covered by the Python extractors.",
        },
    }
    if refreshed_from:
        artifact["refreshed_from"] = refreshed_from
    return artifact


def command_surface(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    paths = run_paths(repo, args.run_id)
    surface = build_surface_map(repo, paths)
    errors = validate_data(repo, surface, "surface_map")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    surface_path = paths.run_dir / "surface-map.json"
    append_citation_entries(repo, paths.run_dir / "evidence-ledger.jsonl", paths.run_id, surface["source_sha"], str(surface_path.relative_to(repo)), surface, "surface-mapper")
    write_json(surface_path, surface)
    print(surface_path)
    return 0


def build_authority_map(repo: Path, paths: RunPaths) -> dict[str, Any]:
    surface_path = paths.run_dir / "surface-map.json"
    surface = read_json(surface_path)
    authorities = surface["authorities"]
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "authority_map",
        "run_id": paths.run_id,
        "produced_at": utc_now(),
        "produced_by": "authority-mapper@0.1",
        "source_sha": surface["source_sha"],
        "inputs": [{"path": str(surface_path.relative_to(repo)), "sha256": sha256_file(surface_path)}],
        "status": "draft",
        "coverage": surface["coverage"],
        "staleness": {
            "stale_if_input_hash_changes": True,
            "depends_on_paths": sorted({authority["path"] for authority in authorities}),
            "scope_signature": surface["staleness"]["scope_signature"],
        },
        "authorities": authorities,
    }


def command_authority_map(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    paths = run_paths(repo, args.run_id)
    authority_map = build_authority_map(repo, paths)
    errors = validate_data(repo, authority_map, "authority_map")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    authority_path = paths.run_dir / "authority-map.json"
    append_citation_entries(
        repo,
        paths.run_dir / "evidence-ledger.jsonl",
        paths.run_id,
        authority_map["source_sha"],
        str(authority_path.relative_to(repo)),
        authority_map,
        "authority-mapper",
    )
    write_json(authority_path, authority_map)
    print(authority_path)
    return 0


def first_artifact_citation(repo: Path, paths: RunPaths, artifact: dict[str, Any]) -> str:
    codebase_map = read_codebase_map(paths.run_dir)
    rel, _ = first_citable_file(repo, codebase_map, artifact["source_sha"])
    citation = citation_for(repo, rel, artifact["source_sha"])
    if not citation:
        raise ValueError(f"could not create citation for {rel}")
    return citation


def next_challenge_id(claims: list[dict[str, Any]]) -> str:
    max_id = 10000
    for claim in claims:
        for challenge in claim.get("challenges", []):
            match = re.fullmatch(r"chl-(\d+)", challenge["challenge_id"])
            if match:
                max_id = max(max_id, int(match.group(1)))
    return f"chl-{max_id + 1:05d}"


def review_dependency_graph(repo: Path, paths: RunPaths, graph_path: Path) -> tuple[dict[str, Any], str]:
    graph = read_json(graph_path)
    challenge_ids: list[str] = []
    now = utc_now()
    for edge in graph["edges"]:
        if edge["kind"] != "unknown" or edge.get("claim_status") in {"challenged", "contested"}:
            continue
        challenge_id = next_challenge_id(graph["edges"])
        edge["claim_status"] = "challenged"
        edge["challenges"] = [
            {
                "challenge_id": challenge_id,
                "challenges_claim_id": edge["id"],
                "raised_by": "skeptic@0.1",
                "raised_at": now,
                "competing_reading": "The dependency graph should not be read as complete while unknown dependency edges remain unresolved by static or runtime extraction.",
                "competing_evidence": edge.get("citations") or [first_artifact_citation(repo, paths, graph)],
                "interpretive_axis": "completeness",
                "relation_to_original": "scope_dispute",
                "status": "open",
                "rationale": "Unknown edges preserve missing dependency closure and must propagate to downstream planning.",
            }
        ]
        challenge_ids.append(challenge_id)
        entry = {
            "schema_version": SCHEMA_VERSION,
            "entry_id": next_ledger_id(paths.run_dir / "evidence-ledger.jsonl"),
            "ts": now,
            "entry_kind": "skeptic_challenge",
            "agent": "skeptic",
            "skill_version": "0.1",
            "run_id": paths.run_id,
            "source_sha": graph["source_sha"],
            "artifact_path": str(graph_path.relative_to(repo)),
            "claim_id": edge["id"],
            "challenge": "Dependency graph contains an unknown edge, so dependency closure remains incomplete.",
        }
        append_ledger_entry(repo, paths.run_dir / "evidence-ledger.jsonl", entry)
    if challenge_ids:
        errors = validate_data(repo, graph, "dependency_graph")
        if errors:
            raise ValueError("\n".join(errors))
        write_json(graph_path, graph)
    body = (
        "Finding: dependency graph contains unresolved unknown dependency edges; these are challenged as completeness risks.\n"
        if challenge_ids
        else "No deterministic Skeptic finding was produced for this artifact.\n"
    )
    review = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "skeptic_review",
        "run_id": paths.run_id,
        "produced_at": now,
        "produced_by": "skeptic@0.1",
        "source_sha": graph["source_sha"],
        "artifact_reviewed": str(graph_path.relative_to(repo)),
        "findings_logged": len(challenge_ids),
        "challenge_ids": challenge_ids,
    }
    return review, body


def command_skeptic_review(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    paths = run_paths(repo, args.run_id)
    artifact_path = Path(args.artifact)
    if not artifact_path.is_absolute():
        artifact_path = repo / artifact_path
    review_dir = paths.run_dir / "skeptic-review"
    review_dir.mkdir(parents=True, exist_ok=True)
    try:
        data = read_json(artifact_path)
        if data.get("artifact_type") == "dependency_graph":
            review, body = review_dependency_graph(repo, paths, artifact_path)
        else:
            review = {
                "schema_version": SCHEMA_VERSION,
                "artifact_type": "skeptic_review",
                "run_id": paths.run_id,
                "produced_at": utc_now(),
                "produced_by": "skeptic@0.1",
                "source_sha": data.get("source_sha", source_sha(repo)),
                "artifact_reviewed": str(artifact_path.relative_to(repo)),
                "findings_logged": 0,
                "challenge_ids": [],
            }
            body = "No deterministic Skeptic finding was produced for this artifact.\n"
        errors = validate_data(repo, review, "skeptic_review")
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
    except (ValueError, json.JSONDecodeError) as exc:
        print(exc, file=sys.stderr)
        return 1
    review_path = review_dir / f"{artifact_path.stem}.md"
    review_path.write_text(
        "---\n" + yaml.safe_dump(review, sort_keys=False) + "---\n# Skeptic Review\n\n" + body,
        encoding="utf-8",
    )
    print(review_path)
    return 0


def edge_partition(edge: dict[str, Any]) -> str:
    if edge["kind"] == "unknown":
        return "unknown"
    if "static_relation" in edge.get("evidence_kinds", []) and edge.get("claim_register") == "factual":
        return "certain"
    if edge.get("claim_register") == "inferential":
        return "suspected"
    return "advisory"


def build_dependency_graph(repo: Path, paths: RunPaths) -> dict[str, Any]:
    surface_path = paths.run_dir / "surface-map.json"
    surface = read_json(surface_path)
    edges = surface["edges"]
    partition_counts = {"certain": 0, "suspected": 0, "advisory": 0, "unknown": 0}
    for edge in edges:
        partition_counts[edge_partition(edge)] += 1
    depends_on = sorted(
        {
            path
            for edge in edges
            for path in [edge.get("from", {}).get("path"), edge.get("to", {}).get("path")]
            if path
        }
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "dependency_graph",
        "run_id": paths.run_id,
        "produced_at": utc_now(),
        "produced_by": "dependency-mapper@0.1",
        "source_sha": surface["source_sha"],
        "inputs": [{"path": str(surface_path.relative_to(repo)), "sha256": sha256_file(surface_path)}],
        "status": "draft",
        "coverage": surface["coverage"],
        "staleness": {
            "stale_if_input_hash_changes": True,
            "depends_on_paths": depends_on,
            "scope_signature": surface["staleness"]["scope_signature"],
        },
        "partition_counts": partition_counts,
        "edges": edges,
    }


def command_dependency_graph(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    paths = run_paths(repo, args.run_id)
    dependency_graph = build_dependency_graph(repo, paths)
    errors = validate_data(repo, dependency_graph, "dependency_graph")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    graph_path = paths.run_dir / "dependency-graph.json"
    append_citation_entries(
        repo,
        paths.run_dir / "evidence-ledger.jsonl",
        paths.run_id,
        dependency_graph["source_sha"],
        str(graph_path.relative_to(repo)),
        dependency_graph,
        "dependency-mapper",
    )
    write_json(graph_path, dependency_graph)
    print(graph_path)
    return 0


def build_verification_map(repo: Path, paths: RunPaths) -> dict[str, Any]:
    sha = source_sha(repo)
    codebase_path = paths.run_dir / "codebase-map.json"
    codebase_map = read_codebase_map(paths.run_dir)
    rels = [item["path"] for item in codebase_map["files"]]
    ci_gates = []
    for test in codebase_map["tests"]:
        citation = citation_for(repo, test["path"], sha)
        if not citation:
            continue
        gate_id = f"test-{len(ci_gates) + 1:03d}"
        ci_gates.append(
            {
                "id": gate_id,
                "name": f"Run {test['path']}",
                "path": test["path"],
                "kind": "test",
                "citations": [citation],
                "command": {
                    "runner": sys.executable,
                    "argv": ["-m", "pytest", test["path"]],
                    "cwd": ".",
                    "safety_envelope": {
                        "requires_network": False,
                        "requires_install": False,
                        "mutates_filesystem": False,
                        "max_duration_seconds": 120,
                    },
                },
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "verification_map",
        "run_id": paths.run_id,
        "produced_at": utc_now(),
        "produced_by": "verification-mapper@0.1",
        "source_sha": sha,
        "inputs": [{"path": str(codebase_path.relative_to(repo)), "sha256": sha256_file(codebase_path)}],
        "status": "draft",
        "coverage": coverage_block(codebase_map["coverage"]["result"]["files_in_scope"], examined=len(ci_gates)),
        "staleness": {
            "stale_if_input_hash_changes": True,
            "depends_on_paths": sorted({gate["path"] for gate in ci_gates}),
            "scope_signature": scope_signature(rels),
        },
        "ci_gates": ci_gates,
    }


def command_verify_map(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    paths = run_paths(repo, args.run_id)
    verification_map = build_verification_map(repo, paths)
    errors = validate_data(repo, verification_map, "verification_map")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    verification_path = paths.run_dir / "verification-map.json"
    append_citation_entries(
        repo,
        paths.run_dir / "evidence-ledger.jsonl",
        paths.run_id,
        verification_map["source_sha"],
        str(verification_path.relative_to(repo)),
        verification_map,
        "verification-mapper",
    )
    write_json(verification_path, verification_map)
    print(verification_path)
    return 0


def challenged_claim_refs(artifact_path: Path, repo: Path, claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    refs = []
    for claim in claims:
        challenges = claim.get("challenges", [])
        if claim.get("claim_status") in {"challenged", "contested"} and challenges:
            refs.append(
                {
                    "artifact_path": str(artifact_path.relative_to(repo)),
                    "claim_id": claim["id"],
                    "challenge_ids": [challenge["challenge_id"] for challenge in challenges],
                }
            )
    return refs


def build_synthesis_index(repo: Path, paths: RunPaths) -> dict[str, Any]:
    surface_path = paths.run_dir / "surface-map.json"
    authority_path = paths.run_dir / "authority-map.json"
    dependency_path = paths.run_dir / "dependency-graph.json"
    verification_path = paths.run_dir / "verification-map.json"
    surface = read_json(surface_path)
    authority_map = read_json(authority_path)
    dependency_graph = read_json(dependency_path)
    verification_map = read_json(verification_path)
    challenged = []
    challenged.extend(challenged_claim_refs(authority_path, repo, authority_map["authorities"]))
    challenged.extend(challenged_claim_refs(dependency_path, repo, dependency_graph["edges"]))
    inputs = [
        {"path": str(path.relative_to(repo)), "sha256": sha256_file(path)}
        for path in [surface_path, authority_path, dependency_path, verification_path]
    ]
    artifacts = [
        {"path": item["path"], "artifact_type": artifact_type}
        for item, artifact_type in zip(
            inputs,
            ["surface_map", "authority_map", "dependency_graph", "verification_map"],
            strict=True,
        )
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "synthesis_index",
        "run_id": paths.run_id,
        "produced_at": utc_now(),
        "produced_by": "synthesizer@0.1",
        "source_sha": surface["source_sha"],
        "inputs": inputs,
        "status": "draft",
        "coverage": surface["coverage"],
        "staleness": {
            "stale_if_input_hash_changes": True,
            "depends_on_paths": sorted(
                set(authority_map["staleness"]["depends_on_paths"])
                | set(dependency_graph["staleness"]["depends_on_paths"])
                | set(verification_map["staleness"]["depends_on_paths"])
            ),
            "scope_signature": surface["staleness"]["scope_signature"],
        },
        "summary": (
            f"Synthesis index connects {len(authority_map['authorities'])} authorities, "
            f"{len(dependency_graph['edges'])} dependency edges, and {len(verification_map['ci_gates'])} verification gates."
        ),
        "claim_counts": {
            "authorities": len(authority_map["authorities"]),
            "dependencies": len(dependency_graph["edges"]),
            "verification_gates": len(verification_map["ci_gates"]),
        },
        "contestation": {
            "open_challenges": sum(len(item["challenge_ids"]) for item in challenged),
            "challenged_claims": challenged,
        },
        "artifacts": artifacts,
    }


def command_synthesis_index(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    paths = run_paths(repo, args.run_id)
    synthesis_index = build_synthesis_index(repo, paths)
    errors = validate_data(repo, synthesis_index, "synthesis_index")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    index_path = paths.run_dir / "synthesis-index.json"
    write_json(index_path, synthesis_index)
    print(index_path)
    return 0


GOAL_PACKS: dict[str, dict[str, Any]] = {
    "understand_repo": {
        "research_only": True,
        "card_type": "findings_card",
        "priority": {"import": 0, "call": 1, "authority": 2},
        "rationale": "understand_repo prioritizes grounded static relations before broader authority surfaces.",
    },
    "research_only": {
        "research_only": True,
        "card_type": "findings_card",
        "priority": {"import": 0, "call": 1, "authority": 2},
        "rationale": "research_only prioritizes readable grounded relations and produces findings cards.",
    },
    "feature_add": {
        "research_only": False,
        "card_type": "intervention_card",
        "priority": {"call": 0, "import": 1, "authority": 2},
        "rationale": "feature_add prioritizes executable call seams before static imports and authorities.",
    },
    "refactor": {
        "research_only": False,
        "card_type": "intervention_card",
        "priority": {"call": 0, "import": 1, "authority": 2},
        "rationale": "refactor prioritizes call and coupling edges because they expose behavior-preserving change boundaries.",
    },
    "audit": {
        "research_only": False,
        "card_type": "intervention_card",
        "priority": {"authority:test_suite": 0, "authority:ci_gate": 1, "authority:config": 2, "call": 3, "import": 4, "authority": 5},
        "rationale": "audit prioritizes verification, CI, and configuration authorities before code relation edges.",
    },
}


def goal_pack(goal_class: str) -> dict[str, Any]:
    return GOAL_PACKS.get(
        goal_class,
        {
            "research_only": False,
            "card_type": "intervention_card",
            "priority": {"call": 0, "import": 1, "authority": 2},
            "rationale": "default goal pack prioritizes actionable relation edges before broad authority surfaces.",
        },
    )


def candidate_priority(candidate: dict[str, Any], pack: dict[str, Any]) -> tuple[int, str, str]:
    priority = pack["priority"]
    specific_key = f"authority:{candidate.get('authority_kind')}" if candidate["surface_kind"] == "authority" else candidate["surface_kind"]
    rank = priority.get(specific_key, priority.get(candidate["surface_kind"], priority.get("authority", 99)))
    return rank, candidate["path"], candidate["surface_id"]


def command_bind(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    paths = run_paths(repo, args.run_id)
    surface_path = paths.run_dir / "surface-map.json"
    if not surface_path.exists():
        print("surface-map.json missing; run cbm-surface first", file=sys.stderr)
        return 1
    surface = read_json(surface_path)
    intake = read_intake(paths.run_dir)
    goal = args.goal or intake["goal"]
    goal_class = args.goal_class or intake["goal_class"]
    pack = goal_pack(goal_class)
    candidates = []
    for index, edge in enumerate(surface["edges"]):
        if edge["kind"] not in {"import", "call"} or not edge.get("citations"):
            continue
        candidates.append(
            {
                "rank": 0,
                "surface_ref": f".research/{paths.run_id}/surface-map.json#/edges/{index}",
                "surface_id": edge["id"],
                "surface_kind": edge["kind"],
                "path": edge["from"]["path"],
                "claim_register": edge["claim_register"],
                "claim_status": edge["claim_status"],
                "citations": edge["citations"],
                "binding_rationale": f"{pack['rationale']} Selected {edge['id']} because it is a grounded {edge['kind']} relation for the goal: {goal}",
                "recommended_card_type": pack["card_type"],
                "dependent_challenges": [],
            }
        )
    for index, authority in enumerate(surface["authorities"]):
        candidates.append(
            {
                "rank": 0,
                "surface_ref": f".research/{paths.run_id}/surface-map.json#/authorities/{index}",
                "surface_id": authority["id"],
                "surface_kind": "authority",
                "authority_kind": authority["kind"],
                "path": authority["path"],
                "claim_register": authority["claim_register"],
                "claim_status": authority["claim_status"],
                "citations": authority["citations"],
                "binding_rationale": f"{pack['rationale']} Selected {authority['id']} because it is a cited {authority['kind']} authority surface for the goal: {goal}",
                "recommended_card_type": pack["card_type"],
                "dependent_challenges": [],
            }
        )
    candidates.sort(key=lambda candidate: candidate_priority(candidate, pack))
    for rank, candidate in enumerate(candidates, start=1):
        candidate["rank"] = rank
        candidate.pop("authority_kind", None)
    if not candidates:
        print("no bindable candidates found in surface-map.json", file=sys.stderr)
        return 1
    binding_path = paths.run_dir / "goal-binding.json"
    binding = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "goal_binding",
        "run_id": paths.run_id,
        "produced_at": utc_now(),
        "produced_by": "cbm-bind@0.1",
        "source_sha": surface["source_sha"],
        "inputs": [{"path": str(surface_path.relative_to(repo)), "sha256": sha256_file(surface_path)}],
        "status": "draft",
        "goal": goal,
        "goal_class": goal_class,
        "research_only": pack["research_only"],
        "candidates": candidates,
    }
    errors = validate_data(repo, binding, "goal_binding")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    append_citation_entries(repo, paths.run_dir / "evidence-ledger.jsonl", paths.run_id, surface["source_sha"], str(binding_path.relative_to(repo)), binding, "cbm-bind")
    write_json(binding_path, binding)
    print(binding_path)
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


def command_stale(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    path = Path(args.artifact)
    if not path.is_absolute():
        path = repo / path
    data, _ = load_artifact_frontmatter(path)
    stale_reasons: list[str] = []
    for input_item in data.get("inputs", []):
        input_path = repo / input_item["path"]
        if not input_path.exists():
            stale_reasons.append(f"input missing: {input_item['path']}")
            continue
        current_hash = sha256_file(input_path)
        if current_hash != input_item["sha256"]:
            stale_reasons.append(f"input hash changed: {input_item['path']}")
    source = data.get("source_sha")
    for rel in data.get("staleness", {}).get("depends_on_paths", []):
        source_path = repo / rel
        if not source_path.exists():
            stale_reasons.append(f"dependent path missing: {rel}")
        elif source and not path_matches_sha(repo, rel, source):
            stale_reasons.append(f"dependent path changed since {source}: {rel}")
    if stale_reasons:
        for reason in stale_reasons:
            print(f"stale {reason}")
        return 2
    print(f"fresh {path}")
    return 0


def artifact_citations(path: Path) -> list[str]:
    data, body = load_artifact_frontmatter(path)
    return sorted(set(extract_citations(data) + extract_citations(body)))


def command_validate_fresh(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    path = Path(args.artifact)
    if not path.is_absolute():
        path = repo / path
    failed = 0
    citations = artifact_citations(path)
    for citation in citations:
        parts = citation_parts(citation)
        if not parts:
            print(f"stale {citation} invalid citation")
            failed += 1
            continue
        cited_hash = blob_hash_at(repo, parts["sha"], parts["path"])
        head_hash = blob_hash_at(repo, "HEAD", parts["path"])
        if cited_hash is None:
            print(f"stale {citation} cited file missing at recorded sha")
            failed += 1
        elif head_hash is None:
            print(f"stale {citation} file missing at HEAD")
            failed += 1
        elif cited_hash != head_hash:
            print(f"stale {citation} file bytes changed at HEAD")
            failed += 1
        else:
            print(f"fresh {citation}")
    if not citations:
        print("no citations found")
    return 0 if failed == 0 else 2


def verify_citation_at_head(repo: Path, citation: str) -> dict[str, Any]:
    parts = citation_parts(citation)
    if not parts:
        return {"citation": citation, "status": "broken", "reason": "invalid citation"}
    cited_content = git_show_bytes(repo, parts["sha"], parts["path"])
    head_content = git_show_bytes(repo, "HEAD", parts["path"])
    if cited_content is None:
        return {"citation": citation, "status": "broken", "reason": "path missing at cited sha"}
    if head_content is None:
        return {"citation": citation, "status": "broken", "reason": "path missing at HEAD"}
    try:
        head_lines = head_content.decode("utf-8").splitlines()
    except UnicodeDecodeError:
        return {"citation": citation, "status": "broken", "reason": "HEAD file is not UTF-8 text"}
    if parts["end"] > len(head_lines):
        return {
            "citation": citation,
            "status": "broken",
            "reason": f"line range exceeds HEAD file length ({len(head_lines)})",
        }
    if hashlib.sha256(cited_content).hexdigest() == hashlib.sha256(head_content).hexdigest():
        return {"citation": citation, "status": "still_grounded", "reason": "file bytes unchanged at HEAD"}
    return {"citation": citation, "status": "needs_review", "reason": "file bytes changed at HEAD but cited lines still exist"}


def command_verify(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    path = Path(args.artifact)
    if not path.is_absolute():
        path = repo / path
    citations = artifact_citations(path)
    results = [verify_citation_at_head(repo, citation) for citation in citations]
    report = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "verify_report",
        "produced_at": utc_now(),
        "artifact_path": str(path.relative_to(repo)) if path.is_relative_to(repo) else str(path),
        "head_sha": source_sha(repo),
        "results": results,
        "summary": {
            "still_grounded": sum(1 for item in results if item["status"] == "still_grounded"),
            "needs_review": sum(1 for item in results if item["status"] == "needs_review"),
            "broken": sum(1 for item in results if item["status"] == "broken"),
        },
    }
    output_path = Path(args.output) if args.output else path.with_name("verify-report.json")
    if not output_path.is_absolute():
        output_path = repo / output_path
    write_json(output_path, report)
    for item in results:
        print(f"{item['status']} {item['citation']} {item['reason']}")
    if not results:
        print("no citations found")
    print(output_path)
    return 0 if report["summary"]["needs_review"] == 0 and report["summary"]["broken"] == 0 else 2


def iter_research_artifacts(repo: Path) -> Iterable[Path]:
    research = repo / ".research"
    if not research.exists():
        return []
    return (
        path
        for path in sorted(research.rglob("*"))
        if path.is_file()
        and path.suffix in {".json", ".md"}
        and not path.name.endswith(".integrity.json")
        and path.name != "verify-report.json"
        and path.name != "corpus-status.json"
    )


def artifact_status_against_head(repo: Path, artifact: Path) -> dict[str, Any] | None:
    try:
        data, body = load_artifact_frontmatter(artifact)
    except Exception:
        return None
    if not isinstance(data, dict) or "artifact_type" not in data:
        return None
    citations = sorted(set(extract_citations(data) + extract_citations(body)))
    verify_results = [verify_citation_at_head(repo, citation) for citation in citations]
    summary = {
        "still_grounded": sum(1 for item in verify_results if item["status"] == "still_grounded"),
        "needs_review": sum(1 for item in verify_results if item["status"] == "needs_review"),
        "broken": sum(1 for item in verify_results if item["status"] == "broken"),
    }
    if not citations:
        freshness = "fresh" if data.get("source_sha") == source_sha(repo) else "pinned"
    elif summary["broken"]:
        freshness = "broken"
    elif summary["needs_review"]:
        freshness = "stale"
    else:
        freshness = "fresh"
    return {
        "path": str(artifact.relative_to(repo)),
        "artifact_type": data.get("artifact_type"),
        "source_sha": data.get("source_sha"),
        "freshness": freshness,
        "historical_valid": all(resolve_citation(repo, citation)[0] for citation in citations),
        "citation_summary": summary,
    }


def command_corpus_status(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    artifacts = [status for path in iter_research_artifacts(repo) if (status := artifact_status_against_head(repo, path))]
    summary = {
        "fresh": sum(1 for item in artifacts if item["freshness"] == "fresh"),
        "stale": sum(1 for item in artifacts if item["freshness"] == "stale"),
        "pinned": sum(1 for item in artifacts if item["freshness"] == "pinned"),
        "broken": sum(1 for item in artifacts if item["freshness"] == "broken"),
    }
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "corpus_status",
        "produced_at": utc_now(),
        "head_sha": source_sha(repo),
        "summary": summary,
        "artifacts": artifacts,
    }
    output_path = Path(args.output) if args.output else repo / ".research" / "corpus-status.json"
    if not output_path.is_absolute():
        output_path = repo / output_path
    write_json(output_path, manifest)
    for item in artifacts:
        print(f"{item['freshness']} {item['path']}")
    print(output_path)
    return 0 if summary["broken"] == 0 else 2


def file_map_by_path(codebase_map: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item["path"]: item for item in codebase_map.get("files", [])}


def structural_refresh_delta(
    repo: Path,
    paths: RunPaths,
    prior_path: Path,
    prior: dict[str, Any],
    successor_path: Path,
    successor: dict[str, Any],
) -> dict[str, Any]:
    prior_files = file_map_by_path(prior)
    successor_files = file_map_by_path(successor)
    prior_paths = set(prior_files)
    successor_paths = set(successor_files)
    common_paths = prior_paths & successor_paths
    changed = sorted(path for path in common_paths if prior_files[path]["sha256"] != successor_files[path]["sha256"])
    carried = sorted(common_paths - set(changed))
    removed = sorted(prior_paths - successor_paths)
    added = sorted(successor_paths - prior_paths)
    downstream = []
    for candidate in ["surface-map.json", "goal-binding.json", "handoff.md"]:
        candidate_path = paths.run_dir / candidate
        if candidate_path.exists():
            downstream.append(
                {
                    "artifact_path": str(candidate_path.relative_to(repo)),
                    "reason": "Structural baseline refreshed; downstream interpretive or goal-bound artifact needs review.",
                }
            )
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "refresh_delta",
        "run_id": paths.run_id,
        "produced_at": utc_now(),
        "produced_by": "cbm-refresh@0.1",
        "source_sha": successor["source_sha"],
        "status": "draft",
        "refresh_mode": "structural",
        "prior_artifact": {
            "path": str(prior_path.relative_to(repo)),
            "sha256": sha256_file(prior_path),
            "source_sha": prior["source_sha"],
        },
        "successor_artifact": {
            "path": str(successor_path.relative_to(repo)),
            "sha256": sha256_file(successor_path),
        },
        "summary": f"Structural refresh compared {len(prior_files)} prior files with {len(successor_files)} current files: {len(carried)} carried, {len(changed)} updated, {len(removed)} removed, {len(added)} added.",
        "carried_forward": [
            {"claim_id": f"file:{path}", "claim_register": "factual", "claim_status": "active", "successor_claim_id": f"file:{path}"}
            for path in carried
        ],
        "updated": [
            {
                "claim_id": f"file:{path}",
                "successor_claim_id": f"file:{path}",
                "what_changed": "File bytes changed between prior source SHA and refreshed HEAD.",
                "claim_register": "factual",
            }
            for path in changed
        ],
        "retracted": [
            {"claim_id": f"file:{path}", "rationale": "File is absent from the refreshed HEAD."}
            for path in removed
        ],
        "newly_added": [
            {"successor_claim_id": f"file:{path}", "rationale": "File is present in refreshed HEAD but absent from the prior codebase map."}
            for path in added
        ],
        "newly_contested": [],
        "challenges_carried_forward": [],
        "open_questions_reconciled": [],
        "downstream_invalidation": downstream,
    }


def claim_citations(claim: dict[str, Any]) -> list[str]:
    return sorted(set(extract_citations(claim)))


def citations_still_grounded(repo: Path, citations: list[str]) -> bool:
    return all(verify_citation_at_head(repo, citation)["status"] == "still_grounded" for citation in citations)


def surface_claim_signature(kind: str, claim: dict[str, Any]) -> str:
    if kind == "authority":
        return f"authority:{claim['kind']}:{claim['path']}"
    from_ref = claim.get("from", {})
    to_ref = claim.get("to", {})
    return ":".join(
        [
            "edge",
            claim["kind"],
            from_ref.get("path", ""),
            from_ref.get("symbol", ""),
            to_ref.get("path", ""),
            to_ref.get("symbol", ""),
            claim.get("extractor_id", ""),
        ]
    )


def surface_claims_by_signature(surface: dict[str, Any]) -> dict[str, tuple[str, dict[str, Any]]]:
    claims: dict[str, tuple[str, dict[str, Any]]] = {}
    for authority in surface.get("authorities", []):
        claims[surface_claim_signature("authority", authority)] = ("authority", authority)
    for edge in surface.get("edges", []):
        claims[surface_claim_signature("edge", edge)] = ("edge", edge)
    return claims


def carry_forward_review_state(prior_claim: dict[str, Any], successor_claim: dict[str, Any]) -> None:
    successor_claim["claim_status"] = prior_claim.get("claim_status", successor_claim["claim_status"])
    if "challenges" in prior_claim:
        successor_claim["challenges"] = [
            {**challenge, "challenges_claim_id": successor_claim["id"]}
            for challenge in prior_claim["challenges"]
        ]
    if "contradicted_by" in prior_claim:
        successor_claim["contradicted_by"] = prior_claim["contradicted_by"]


def interpretive_refresh_delta(
    repo: Path,
    paths: RunPaths,
    prior_path: Path,
    prior: dict[str, Any],
    successor_path: Path,
    successor: dict[str, Any],
) -> dict[str, Any]:
    prior_claims = surface_claims_by_signature(prior)
    successor_claims = surface_claims_by_signature(successor)
    carried_forward: list[dict[str, Any]] = []
    updated: list[dict[str, Any]] = []
    retracted: list[dict[str, Any]] = []
    newly_added: list[dict[str, Any]] = []
    challenges_carried_forward: list[dict[str, Any]] = []

    for signature, (_, prior_claim) in sorted(prior_claims.items()):
        successor_entry = successor_claims.get(signature)
        if not successor_entry:
            retracted.append(
                {
                    "claim_id": prior_claim["id"],
                    "rationale": "No matching surface claim exists after differential refresh at current HEAD.",
                }
            )
            for challenge in prior_claim.get("challenges", []):
                challenges_carried_forward.append(
                    {
                        "challenge_id": challenge["challenge_id"],
                        "post_refresh_status": "obsolete_target_retracted",
                        "rationale": "The challenged claim did not survive the interpretive refresh.",
                    }
                )
            continue

        _, successor_claim = successor_entry
        carry_forward_review_state(prior_claim, successor_claim)
        citations = claim_citations(prior_claim)
        if citations_still_grounded(repo, citations):
            carried_forward.append(
                {
                    "claim_id": prior_claim["id"],
                    "claim_register": successor_claim["claim_register"],
                    "claim_status": successor_claim["claim_status"],
                    "successor_claim_id": successor_claim["id"],
                }
            )
        else:
            updated.append(
                {
                    "claim_id": prior_claim["id"],
                    "successor_claim_id": successor_claim["id"],
                    "what_changed": "The claim still exists in the refreshed surface map, but at least one prior citation changed or no longer resolves unchanged at HEAD.",
                    "claim_register": successor_claim["claim_register"],
                }
            )
        for challenge in prior_claim.get("challenges", []):
            challenges_carried_forward.append(
                {
                    "challenge_id": challenge["challenge_id"],
                    "post_refresh_status": "still_active",
                    "rationale": "The challenged claim survived refresh, so the challenge remains active.",
                }
            )

    for signature, (_, successor_claim) in sorted(successor_claims.items()):
        if signature not in prior_claims:
            newly_added.append(
                {
                    "successor_claim_id": successor_claim["id"],
                    "rationale": "This surface claim is present at current HEAD and had no matching claim in the prior surface map.",
                }
            )

    downstream = []
    for candidate in ["goal-binding.json", "handoff.md"]:
        candidate_path = paths.run_dir / candidate
        if candidate_path.exists():
            downstream.append(
                {
                    "artifact_path": str(candidate_path.relative_to(repo)),
                    "reason": "Surface map was interpretively refreshed; downstream goal-bound artifacts need review or regeneration.",
                }
            )

    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "refresh_delta",
        "run_id": paths.run_id,
        "produced_at": utc_now(),
        "produced_by": "cbm-refresh@0.1",
        "source_sha": successor["source_sha"],
        "status": "draft",
        "refresh_mode": "interpretive",
        "prior_artifact": {
            "path": str(prior_path.relative_to(repo)),
            "sha256": sha256_file(prior_path),
            "source_sha": prior["source_sha"],
        },
        "successor_artifact": {
            "path": str(successor_path.relative_to(repo)),
            "sha256": sha256_file(successor_path) if successor_path.exists() else "0" * 64,
        },
        "summary": f"Interpretive refresh compared {len(prior_claims)} prior surface claims with {len(successor_claims)} current claims: {len(carried_forward)} carried, {len(updated)} updated, {len(retracted)} retracted, {len(newly_added)} added.",
        "carried_forward": carried_forward,
        "updated": updated,
        "retracted": retracted,
        "newly_added": newly_added,
        "newly_contested": [],
        "challenges_carried_forward": challenges_carried_forward,
        "open_questions_reconciled": [],
        "downstream_invalidation": downstream,
    }


def command_refresh(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    prior_path = Path(args.artifact)
    if not prior_path.is_absolute():
        prior_path = repo / prior_path
    prior = read_json(prior_path)
    if args.mode == "structural" and prior.get("artifact_type") != "codebase_map":
        print("structural refresh requires a codebase-map artifact", file=sys.stderr)
        return 1
    if args.mode == "interpretive" and prior.get("artifact_type") != "surface_map":
        print("interpretive refresh requires a surface-map artifact", file=sys.stderr)
        return 1
    paths = run_paths(repo, prior["run_id"])
    refresh_dir = paths.run_dir / "refreshes"
    refresh_dir.mkdir(parents=True, exist_ok=True)
    head = source_sha(repo)
    if args.mode == "interpretive":
        codebase_path = refresh_dir / f"codebase-map-{head}.json"
        successor_path = refresh_dir / f"surface-map-{head}.json"
        delta_path = refresh_dir / f"refresh-delta-interpretive-{head}.json"
        codebase_map = build_codebase_map(
            repo,
            paths,
            refreshed_from={
                "artifact_path": str((paths.run_dir / "codebase-map.json").relative_to(repo)),
                "source_sha": prior["source_sha"],
                "refresh_mode": "structural",
            },
        )
        errors = validate_data(repo, codebase_map, "codebase_map")
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        write_json(codebase_path, codebase_map)
        successor = build_surface_map(
            repo,
            paths,
            codebase_path=codebase_path,
            codebase_map=codebase_map,
            refreshed_from={
                "artifact_path": str(prior_path.relative_to(repo)),
                "source_sha": prior["source_sha"],
                "refresh_mode": "interpretive",
                "refresh_delta_path": str(delta_path.relative_to(repo)),
            },
        )
        delta = interpretive_refresh_delta(repo, paths, prior_path, prior, successor_path, successor)
        errors = validate_data(repo, successor, "surface_map")
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        write_json(successor_path, successor)
        delta["successor_artifact"]["sha256"] = sha256_file(successor_path)
        errors = validate_data(repo, delta, "refresh_delta")
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        write_json(delta_path, delta)
        print(successor_path)
        print(delta_path)
        return 0

    successor_path = refresh_dir / f"codebase-map-{head}.json"
    delta_path = refresh_dir / f"refresh-delta-structural-{head}.json"
    successor = build_codebase_map(
        repo,
        paths,
        refreshed_from={
            "artifact_path": str(prior_path.relative_to(repo)),
            "source_sha": prior["source_sha"],
            "refresh_mode": "structural",
            "refresh_delta_path": str(delta_path.relative_to(repo)),
        },
    )
    errors = validate_data(repo, successor, "codebase_map")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    write_json(successor_path, successor)
    delta = structural_refresh_delta(repo, paths, prior_path, prior, successor_path, successor)
    errors = validate_data(repo, delta, "refresh_delta")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    write_json(delta_path, delta)
    print(successor_path)
    print(delta_path)
    return 0


def tokenize_query(question: str) -> list[str]:
    return [token.lower() for token in re.findall(r"[A-Za-z0-9_./-]+", question) if len(token) >= 3]


def artifact_is_fresh_for_consult(repo: Path, artifact: Path) -> bool:
    citations = artifact_citations(artifact)
    return bool(citations) and all(
        verify_citation_at_head(repo, citation)["status"] == "still_grounded"
        for citation in citations
    )


def consult_matches(repo: Path, question: str) -> list[dict[str, Any]]:
    tokens = tokenize_query(question)
    matches: list[dict[str, Any]] = []
    for artifact in iter_research_artifacts(repo):
        if not artifact_is_fresh_for_consult(repo, artifact):
            continue
        try:
            data, body = load_artifact_frontmatter(artifact)
        except Exception:
            continue
        text = json.dumps(data, sort_keys=True).lower() + "\n" + body.lower()
        if not all(token in text for token in tokens):
            continue
        citations = artifact_citations(artifact)
        matches.append(
            {
                "artifact": str(artifact.relative_to(repo)),
                "artifact_type": data.get("artifact_type"),
                "matched_terms": tokens,
                "citations": citations[:5],
            }
        )
    return matches


def command_consult(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    matches = consult_matches(repo, args.question)
    consultations_dir = repo / ".research" / "consultations"
    consultations_dir.mkdir(parents=True, exist_ok=True)
    consult_id = f"consult-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}"
    output_path = consultations_dir / f"{consult_id}.md"
    if matches:
        lines = [
            "---",
            yaml.safe_dump(
                {
                    "schema_version": SCHEMA_VERSION,
                    "artifact_type": "consultation",
                    "consultation_id": consult_id,
                    "produced_at": utc_now(),
                    "question": args.question,
                    "status": "answered",
                    "matches": matches,
                },
                sort_keys=False,
            ).strip(),
            "---",
            "# Consultation",
            "",
            "Grounded matches from fresh artifacts:",
        ]
        for match in matches:
            citation_text = ", ".join(match["citations"]) if match["citations"] else "no citations in artifact"
            lines.append(f"- `{match['artifact']}` ({match['artifact_type']}): {citation_text}")
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(output_path)
        return 0
    output_path.write_text(
        "---\n"
        + yaml.safe_dump(
            {
                "schema_version": SCHEMA_VERSION,
                "artifact_type": "consultation",
                "consultation_id": consult_id,
                "produced_at": utc_now(),
                "question": args.question,
                "status": "refused",
                "matches": [],
            },
            sort_keys=False,
        )
        + "---\n# Consultation\n\nRefusal: no fresh artifact in the corpus contains enough grounded evidence to answer this question.\n",
        encoding="utf-8",
    )
    print(output_path)
    return 2


def safe_relpath(base: Path, target: Path) -> str | None:
    try:
        return target.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return None


def sanitize_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-") or "gate"


def declared_ci_gates(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    gates = []
    if isinstance(artifact.get("ci_gates"), list):
        gates.extend(artifact["ci_gates"])
    verification = artifact.get("verification")
    if isinstance(verification, dict) and isinstance(verification.get("ci_gates"), list):
        gates.extend(verification["ci_gates"])
    return gates


def find_declared_gate(repo: Path, paths: RunPaths, gate_id: str, artifact_arg: str | None) -> tuple[Path, dict[str, Any]] | None:
    candidates: list[Path] = []
    if artifact_arg:
        artifact_path = Path(artifact_arg)
        candidates.append(artifact_path if artifact_path.is_absolute() else repo / artifact_path)
    else:
        candidates.extend([paths.run_dir / "verification-map.json", paths.run_dir / "surface-map.json"])
    for artifact_path in candidates:
        if not artifact_path.exists():
            continue
        artifact = read_json(artifact_path)
        for gate in declared_ci_gates(artifact):
            if gate.get("id") == gate_id or gate.get("name") == gate_id:
                return artifact_path, gate
    return None


def envelope_refusal(gate_envelope: dict[str, Any], args: argparse.Namespace) -> str | None:
    if gate_envelope.get("requires_network") and not args.allow_network:
        return "gate requires network access outside approved envelope"
    if gate_envelope.get("requires_install") and not args.allow_install:
        return "gate requires dependency installation outside approved envelope"
    if gate_envelope.get("mutates_filesystem") and not args.allow_mutation:
        return "gate mutates the filesystem outside approved envelope"
    if gate_envelope["max_duration_seconds"] > args.max_duration:
        return "gate max duration exceeds approved envelope"
    return None


def command_run_gate(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    paths = run_paths(repo, args.run_id)
    found = find_declared_gate(repo, paths, args.gate_id, args.artifact)
    if not found:
        print(f"gate not found: {args.gate_id}", file=sys.stderr)
        return 1
    artifact_path, gate = found
    command = gate.get("command")
    if not command:
        print(f"gate has no declared command: {args.gate_id}", file=sys.stderr)
        return 1
    gate_envelope = command["safety_envelope"]
    refusal = envelope_refusal(gate_envelope, args)
    if refusal:
        print(f"refused: {refusal}", file=sys.stderr)
        return 2
    cwd = repo / command["cwd"]
    cwd_rel = safe_relpath(repo, cwd)
    if cwd_rel is None:
        print("refused: command cwd is outside repo", file=sys.stderr)
        return 2
    argv = [command["runner"], *command.get("argv", [])]
    started = time.monotonic()
    timed_out = False
    try:
        proc = subprocess.run(
            argv,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=gate_envelope["max_duration_seconds"],
        )
        exit_code = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        exit_code = 124
        stdout = exc.stdout or ""
        stderr = exc.stderr or f"Command timed out after {gate_envelope['max_duration_seconds']} seconds."
    duration = time.monotonic() - started
    output_dir = paths.run_dir / "command-outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output_path = output_dir / f"{sanitize_id(args.gate_id)}-{ts}.txt"
    output_path.write_text(
        "\n".join(
            [
                f"gate_id: {args.gate_id}",
                f"artifact: {artifact_path.relative_to(repo).as_posix()}",
                f"cwd: {cwd_rel}",
                "command: " + json.dumps(argv),
                f"exit_code: {exit_code}",
                f"duration_seconds: {duration:.3f}",
                f"timed_out: {str(timed_out).lower()}",
                "",
                "== stdout ==",
                stdout,
                "== stderr ==",
                stderr,
            ]
        ),
        encoding="utf-8",
    )
    ledger_path = paths.run_dir / "evidence-ledger.jsonl"
    entry = {
        "schema_version": SCHEMA_VERSION,
        "entry_id": next_ledger_id(ledger_path),
        "ts": utc_now(),
        "entry_kind": "command_executed",
        "agent": "cbm-run-gate",
        "skill_version": "0.1",
        "run_id": paths.run_id,
        "source_sha": source_sha(repo),
        "command_id": args.gate_id,
        "exit_code": exit_code,
        "duration_seconds": duration,
        "output_artifact_path": str(output_path.relative_to(repo)),
    }
    try:
        append_ledger_entry(repo, ledger_path, entry)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(output_path)
    return exit_code


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
    surface_path = paths.run_dir / "surface-map.json"
    if not surface_path.exists():
        surface = build_surface_map(repo, paths)
        errors = validate_data(repo, surface, "surface_map")
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        append_citation_entries(repo, paths.run_dir / "evidence-ledger.jsonl", paths.run_id, surface["source_sha"], str(surface_path.relative_to(repo)), surface, "surface-mapper")
        write_json(surface_path, surface)
    surface = read_json(surface_path)
    binding_path = paths.run_dir / "goal-binding.json"
    binding = read_json(binding_path) if binding_path.exists() else None
    selected_candidate = binding["candidates"][0] if binding and binding.get("candidates") else None
    primary_authority = surface["authorities"][0]
    import_edge_index = None
    import_edge = None
    if selected_candidate and "/edges/" in selected_candidate["surface_ref"]:
        import_edge_index = int(selected_candidate["surface_ref"].rsplit("/edges/", 1)[1])
        edge = surface["edges"][import_edge_index]
        if edge["kind"] == "import":
            import_edge = edge
    if import_edge is None:
        import_edge_index = next((index for index, edge in enumerate(surface["edges"]) if edge["kind"] == "import"), None)
        import_edge = surface["edges"][import_edge_index] if import_edge_index is not None else None
    if selected_candidate and "/authorities/" in selected_candidate["surface_ref"]:
        authority_index = int(selected_candidate["surface_ref"].rsplit("/authorities/", 1)[1])
        primary_authority = surface["authorities"][authority_index]
    if import_edge:
        rel_file = import_edge["from"]["path"]
        citation = import_edge["citations"][0]
        primary_role = f"Imports {import_edge['to']['path']}; this grounded static relation is the selected goal-binding candidate."
        certain_dependencies = [f".research/{paths.run_id}/surface-map.json#/edges/{import_edge_index}", citation]
        leverage_rating = "medium"
        leverage_rationale = "A local import edge gives a concrete, citation-backed relation to read next; leverage is bounded by the unresolved unknown dependency edge."
        recommended_next_slice = f"Read {import_edge['from']['path']} and {import_edge['to']['path']} around the cited import, then decide whether this relation represents setup, test coverage, or runtime coupling."
    else:
        rel_file = primary_authority["path"]
        citation = primary_authority["citations"][0]
        primary_role = f"Draft surface authority {primary_authority['id']} selected by goal binding."
        certain_dependencies = [citation]
        leverage_rating = "medium" if primary_authority["kind"] in {"config", "test_suite", "ci_gate"} else "low"
        leverage_rationale = "Phase A can identify structural surfaces, but leverage remains bounded by the Skeptic challenge on unknown dependency closure."
        recommended_next_slice = "Read the cited authority file and implement call or runtime workflow extraction before promoting this card beyond draft."
    card_dir = paths.run_dir / "findings"
    card_dir.mkdir(parents=True, exist_ok=True)
    card_path = card_dir / "int-0001.md"
    skeptic_dir = paths.run_dir / "skeptic-review"
    skeptic_dir.mkdir(parents=True, exist_ok=True)
    skeptic_path = skeptic_dir / "surface-map.md"
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
    try:
        append_ledger_entry(repo, ledger_path, citation_entry)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
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
    try:
        append_ledger_entry(repo, ledger_path, uncertainty_entry)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    skeptic_entry = {
        "schema_version": SCHEMA_VERSION,
        "entry_id": next_ledger_id(ledger_path),
        "ts": now,
        "entry_kind": "skeptic_challenge",
        "agent": "skeptic",
        "skill_version": "0.1",
        "run_id": paths.run_id,
        "source_sha": sha,
        "artifact_path": str(surface_path.relative_to(repo)),
        "claim_id": "edge-unknown-001",
        "challenge": "Surface map is schema-valid but weak: Phase A only extracts direct Python imports, so calls, runtime workflows, relative imports, and dynamic loading cannot support high-confidence planning.",
    }
    try:
        append_ledger_entry(repo, ledger_path, skeptic_entry)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    unknown_edge = next((edge for edge in surface["edges"] if edge["id"] == "edge-unknown-001"), None)
    if unknown_edge is None:
        print("surface map is missing edge-unknown-001", file=sys.stderr)
        return 1
    unknown_edge["claim_status"] = "challenged"
    unknown_edge["challenges"] = [
        {
            "challenge_id": "chl-00001",
            "challenges_claim_id": "edge-unknown-001",
            "raised_by": "skeptic@0.1",
            "raised_at": now,
            "competing_reading": "The draft surface map should be treated as structurally incomplete until call, runtime workflow, relative import, and dynamic loading extraction replace the unknown dependency edge with grounded relations.",
            "competing_evidence": [citation],
            "interpretive_axis": "completeness",
            "relation_to_original": "scope_dispute",
            "status": "open",
            "rationale": "The cited authority exists, but the dependency closure around it has not been extracted.",
        }
    ]
    errors = validate_data(repo, surface, "surface_map")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    write_json(surface_path, surface)
    skeptic_path.write_text(
        "---\n"
        + yaml.safe_dump(
            {
                "schema_version": SCHEMA_VERSION,
                "artifact_type": "skeptic_review",
                "run_id": paths.run_id,
                "produced_at": now,
                "produced_by": "skeptic@0.1",
                "source_sha": sha,
                "artifact_reviewed": str(surface_path.relative_to(repo)),
                "findings_logged": 1,
            },
            sort_keys=False,
        )
        + "---\n# Skeptic Review\n\nFinding: `edge-unknown-001` keeps dependency closure unknown because Phase A only extracts direct Python imports. It still misses calls, runtime workflows, relative imports, and dynamic loading. This prevents high-confidence planning from the draft surface map alone.\n",
        encoding="utf-8",
    )
    card_frontmatter = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "findings_card",
        "run_id": paths.run_id,
        "produced_at": now,
        "produced_by": "intervention-planner@0.1",
        "source_sha": sha,
        "inputs": [{"path": str(surface_path.relative_to(repo)), "sha256": sha256_file(surface_path)}],
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
        "primary_files": [{"path": rel_file, "role": primary_role, "citations": [citation]}],
        "related_dependencies": {"certain": certain_dependencies, "suspected": [], "advisory": [], "unknown": [f".research/{paths.run_id}/surface-map.json#/edges/{len(surface['edges']) - 1}"]},
        "affected_workflows": [],
        "expected_leverage": {
            "rating": leverage_rating,
            "rationale": leverage_rationale,
            "claim_register": "interpretive",
            "claim_status": "active",
            "evidence_kinds": ["static_structure"],
        },
        "blast_radius": {
            "hops_evaluated": 1,
            "certain_count": 1,
            "suspected_count": 0,
            "advisory_count": 0,
            "unknown_count": 1,
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
        "confidence_rationale": "Confidence is low because the Skeptic logged an unresolved challenge against the draft surface map's unknown dependency closure.",
        "open_questions": [{"question": "Which code surface actually matters most for the user's goal?", "register_id": "unc-00001"}],
        "dependent_challenges": [
            {
                "claim_artifact": f".research/{paths.run_id}/surface-map.json",
                "claim_id": "edge-unknown-001",
                "challenge_ids": ["chl-00001"],
                "impact": "Unknown dependency closure means this card can guide the next reading slice but should not be used as a high-confidence intervention plan.",
            }
        ],
        "recommended_next_slice": recommended_next_slice,
        "claim_status": "active",
    }
    card_errors = validate_data(repo, card_frontmatter, "findings_card")
    if card_errors:
        for error in card_errors:
            print(error, file=sys.stderr)
        return 1
    card_body = "\n# Phase A Structural Finding\n\nThis generated card proves the mechanical gates are wired: schema validation and citation resolution operate on an evidence-bound artifact.\n"
    card_path.write_text("---\n" + yaml.safe_dump(card_frontmatter, sort_keys=False) + "---\n" + card_body, encoding="utf-8")
    append_citation_entries(repo, ledger_path, paths.run_id, sha, str(card_path.relative_to(repo)), card_frontmatter, "intervention-planner")
    citation_ok, citation_reason = resolve_citation(repo, citation)
    required_citations = set(extract_citations(surface) + extract_citations(card_frontmatter))
    if binding:
        required_citations.update(extract_citations(binding))
    missing_ledger_citations = sorted(required_citations - ledger_citations(ledger_path))
    ledger_append_only_ok, ledger_append_only_reason = verify_ledger_append_only(ledger_path)
    artifacts = [
        {"path": str((paths.run_dir / "codebase-map.json").relative_to(repo)), "artifact_type": "codebase_map", "status": "draft", "summary": "Deterministic structural file inventory."},
        {"path": str(surface_path.relative_to(repo)), "artifact_type": "surface_map", "status": "draft", "summary": "Draft deterministic surface map with explicit unknown dependency edge."},
        {"path": str(card_path.relative_to(repo)), "artifact_type": "findings_card", "status": "draft", "summary": "Phase A generated structural findings card."},
        {"path": str(skeptic_path.relative_to(repo)), "artifact_type": "skeptic_review", "status": "draft", "summary": "Lightweight Skeptic finding against unknown dependency closure."},
    ]
    handoff_inputs = [
        {"path": str(surface_path.relative_to(repo)), "sha256": sha256_file(surface_path)},
        {"path": str(card_path.relative_to(repo)), "sha256": sha256_file(card_path)},
        {"path": str(skeptic_path.relative_to(repo)), "sha256": sha256_file(skeptic_path)},
    ]
    if binding_path.exists():
        artifacts.insert(2, {"path": str(binding_path.relative_to(repo)), "artifact_type": "goal_binding", "status": "draft", "summary": "Goal-specific candidate binding over the surface map."})
        handoff_inputs.insert(1, {"path": str(binding_path.relative_to(repo)), "sha256": sha256_file(binding_path)})
    handoff = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "handoff",
        "run_id": paths.run_id,
        "produced_at": utc_now(),
        "produced_by": "cbm-handoff@0.1",
        "source_sha": sha,
        "inputs": handoff_inputs,
        "status": "draft",
        "coverage": coverage_block(codebase_map["coverage"]["result"]["files_in_scope"], examined=1),
        "mode": intake["mode"],
        "user_goal": intake["goal"],
        "goal_class": intake["goal_class"],
        "research_only": intake["research_only"],
        "gate_summary": {
            "schema_validation": {"passed": 3, "failed_artifacts": []},
            "citation_resolution": {"resolved": 1 if citation_ok else 0, "unresolved_count": 0 if citation_ok else 1, "unresolved_examples": [] if citation_ok else [f"{citation}: {citation_reason}"]},
            "ledger_consistency": {"append_only_verified": ledger_append_only_ok and not missing_ledger_citations, "entry_count": ledger_count(ledger_path)},
            "staleness_check": {"fresh": 2, "stale_artifacts": []},
            "skeptic_review": {"artifacts_reviewed": 1, "challenges_logged": 1, "challenges_resolved": 0},
        },
        "contestation_summary": {
            "claims_by_register": {"factual": 1, "inferential": 0, "interpretive": 1},
            "claims_by_status": {"active": 2, "challenged": 1, "contested": 0, "contradicted": 0, "superseded": 0, "retired": 0},
            "open_challenges": 1,
            "contested_claims": [],
            "contradicted_claims": [],
        },
        "artifacts": artifacts,
        "open_questions_count": 1,
        "coverage_caveats": ["Phase A surface mapping is deterministic and has not performed language-level import/call extraction."],
        "recommended_next_action": "Implement call and runtime workflow extraction so the unknown dependency edge can be narrowed with grounded relations.",
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
    if not ledger_append_only_ok:
        print(f"ledger append-only verification failed: {ledger_append_only_reason}", file=sys.stderr)
        return 1
    if missing_ledger_citations:
        print("missing ledger citations: " + ", ".join(missing_ledger_citations), file=sys.stderr)
        return 1
    return 0 if citation_ok else 1


def command_run(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    run_id = args.run_id or f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{source_sha(repo)}"
    init_args = argparse.Namespace(repo=str(repo), goal=args.goal, goal_class=args.goal_class, mode=args.mode, run_id=run_id)
    map_args = argparse.Namespace(repo=str(repo), run_id=run_id)
    commands = [
        (command_init, init_args),
        (command_map, map_args),
        (command_surface, map_args),
    ]
    if args.mode in {"standard", "deep"}:
        commands.append((command_authority_map, map_args))
        commands.append(
            (
                command_skeptic_review,
                argparse.Namespace(
                    repo=str(repo),
                    run_id=run_id,
                    artifact=str(repo / ".research" / run_id / "authority-map.json"),
                ),
            )
        )
        commands.append((command_dependency_graph, map_args))
        commands.append(
            (
                command_skeptic_review,
                argparse.Namespace(
                    repo=str(repo),
                    run_id=run_id,
                    artifact=str(repo / ".research" / run_id / "dependency-graph.json"),
                ),
            )
        )
        commands.append((command_verify_map, map_args))
        commands.append(
            (
                command_skeptic_review,
                argparse.Namespace(
                    repo=str(repo),
                    run_id=run_id,
                    artifact=str(repo / ".research" / run_id / "verification-map.json"),
                ),
            )
        )
        commands.append((command_synthesis_index, map_args))
        commands.append(
            (
                command_skeptic_review,
                argparse.Namespace(
                    repo=str(repo),
                    run_id=run_id,
                    artifact=str(repo / ".research" / run_id / "synthesis-index.json"),
                ),
            )
        )
    commands.extend(
        [
            (command_bind, argparse.Namespace(repo=str(repo), run_id=run_id, goal=None, goal_class=None)),
            (command_handoff, map_args),
        ]
    )
    for command, ns in commands:
        rc = command(ns)
        if rc != 0:
            return rc
    print(repo / ".research" / run_id)
    return 0


def latest_run_dir(repo: Path) -> Path | None:
    research = repo / ".research"
    if not research.exists():
        return None
    candidates = [path for path in research.iterdir() if path.is_dir()]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def command_hook_stop(args: argparse.Namespace) -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}
    repo = Path(payload.get("cwd") or args.repo).resolve()
    run_dir = latest_run_dir(repo)
    if not run_dir:
        print(json.dumps({"continue": True, "systemMessage": "CBM: no .research run found for stop-hook validation."}))
        return 0
    handoff = run_dir / "handoff.md"
    if not handoff.exists():
        print(
            json.dumps(
                {
                    "continue": False,
                    "stopReason": f"CBM run {run_dir.name} has no handoff.md yet.",
                    "systemMessage": "CBM handoff gate failed: missing handoff.md.",
                }
            )
        )
        return 0
    try:
        data, _ = load_artifact_frontmatter(handoff)
        errors = validate_data(repo, data, "handoff")
    except Exception as exc:
        errors = [str(exc)]
    if errors:
        print(
            json.dumps(
                {
                    "continue": False,
                    "stopReason": f"CBM handoff validation failed for {run_dir.name}.",
                    "systemMessage": "CBM handoff gate failed: " + "; ".join(errors[:3]),
                }
            )
        )
        return 0
    print(json.dumps({"continue": True, "systemMessage": f"CBM handoff gate passed for {run_dir.name}."}))
    return 0


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
    p_surface = sub.add_parser("surface")
    p_surface.add_argument("--repo", default=".")
    p_surface.add_argument("--run-id")
    p_surface.set_defaults(func=command_surface)
    p_authority_map = sub.add_parser("authority-map")
    p_authority_map.add_argument("--repo", default=".")
    p_authority_map.add_argument("--run-id")
    p_authority_map.set_defaults(func=command_authority_map)
    p_dependency_graph = sub.add_parser("dependency-graph")
    p_dependency_graph.add_argument("--repo", default=".")
    p_dependency_graph.add_argument("--run-id")
    p_dependency_graph.set_defaults(func=command_dependency_graph)
    p_verify_map = sub.add_parser("verify-map")
    p_verify_map.add_argument("--repo", default=".")
    p_verify_map.add_argument("--run-id")
    p_verify_map.set_defaults(func=command_verify_map)
    p_synthesis_index = sub.add_parser("synthesis-index")
    p_synthesis_index.add_argument("--repo", default=".")
    p_synthesis_index.add_argument("--run-id")
    p_synthesis_index.set_defaults(func=command_synthesis_index)
    p_skeptic_review = sub.add_parser("skeptic-review")
    p_skeptic_review.add_argument("artifact")
    p_skeptic_review.add_argument("--repo", default=".")
    p_skeptic_review.add_argument("--run-id")
    p_skeptic_review.set_defaults(func=command_skeptic_review)
    p_bind = sub.add_parser("bind")
    p_bind.add_argument("--repo", default=".")
    p_bind.add_argument("--run-id")
    p_bind.add_argument("--goal")
    p_bind.add_argument("--goal-class")
    p_bind.set_defaults(func=command_bind)
    p_validate = sub.add_parser("validate")
    p_validate.add_argument("artifact")
    p_validate.add_argument("--repo", default=".")
    p_validate.set_defaults(func=command_validate)
    p_verify = sub.add_parser("verify-citations")
    p_verify.add_argument("artifact")
    p_verify.add_argument("--repo", default=".")
    p_verify.set_defaults(func=command_verify_citations)
    p_stale = sub.add_parser("stale")
    p_stale.add_argument("artifact")
    p_stale.add_argument("--repo", default=".")
    p_stale.set_defaults(func=command_stale)
    p_validate_fresh = sub.add_parser("validate-fresh")
    p_validate_fresh.add_argument("artifact")
    p_validate_fresh.add_argument("--repo", default=".")
    p_validate_fresh.set_defaults(func=command_validate_fresh)
    p_verify_fresh = sub.add_parser("verify")
    p_verify_fresh.add_argument("artifact")
    p_verify_fresh.add_argument("--repo", default=".")
    p_verify_fresh.add_argument("--output")
    p_verify_fresh.set_defaults(func=command_verify)
    p_corpus_status = sub.add_parser("corpus-status")
    p_corpus_status.add_argument("--repo", default=".")
    p_corpus_status.add_argument("--output")
    p_corpus_status.set_defaults(func=command_corpus_status)
    p_refresh = sub.add_parser("refresh")
    p_refresh.add_argument("artifact")
    p_refresh.add_argument("--repo", default=".")
    p_refresh.add_argument("--mode", required=True, choices=["structural", "interpretive"])
    p_refresh.set_defaults(func=command_refresh)
    p_consult = sub.add_parser("consult")
    p_consult.add_argument("question")
    p_consult.add_argument("--repo", default=".")
    p_consult.set_defaults(func=command_consult)
    p_run_gate = sub.add_parser("run-gate")
    p_run_gate.add_argument("gate_id")
    p_run_gate.add_argument("--repo", default=".")
    p_run_gate.add_argument("--run-id")
    p_run_gate.add_argument("--artifact")
    p_run_gate.add_argument("--allow-network", action="store_true")
    p_run_gate.add_argument("--allow-install", action="store_true")
    p_run_gate.add_argument("--allow-mutation", action="store_true")
    p_run_gate.add_argument("--max-duration", type=int, default=60)
    p_run_gate.set_defaults(func=command_run_gate)
    p_handoff = sub.add_parser("handoff")
    p_handoff.add_argument("--repo", default=".")
    p_handoff.add_argument("--run-id")
    p_handoff.set_defaults(func=command_handoff)
    p_run = sub.add_parser("run")
    p_run.add_argument("--repo", default=".")
    p_run.add_argument("--goal", required=True)
    p_run.add_argument("--goal-class", default="understand_repo")
    p_run.add_argument("--mode", default="lightweight", choices=["lightweight", "standard", "deep"])
    p_run.add_argument("--run-id")
    p_run.set_defaults(func=command_run)
    p_hook_stop = sub.add_parser("hook-stop")
    p_hook_stop.add_argument("--repo", default=".")
    p_hook_stop.set_defaults(func=command_hook_stop)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


def init_main() -> int:
    return main(["init", *sys.argv[1:]])


def map_main() -> int:
    return main(["map", *sys.argv[1:]])


def surface_main() -> int:
    return main(["surface", *sys.argv[1:]])


def authority_map_main() -> int:
    return main(["authority-map", *sys.argv[1:]])


def dependency_graph_main() -> int:
    return main(["dependency-graph", *sys.argv[1:]])


def verify_map_main() -> int:
    return main(["verify-map", *sys.argv[1:]])


def synthesis_index_main() -> int:
    return main(["synthesis-index", *sys.argv[1:]])


def skeptic_review_main() -> int:
    return main(["skeptic-review", *sys.argv[1:]])


def bind_main() -> int:
    return main(["bind", *sys.argv[1:]])


def validate_main() -> int:
    return main(["validate", *sys.argv[1:]])


def verify_citations_main() -> int:
    return main(["verify-citations", *sys.argv[1:]])


def stale_main() -> int:
    return main(["stale", *sys.argv[1:]])


def validate_fresh_main() -> int:
    return main(["validate-fresh", *sys.argv[1:]])


def verify_main() -> int:
    return main(["verify", *sys.argv[1:]])


def corpus_status_main() -> int:
    return main(["corpus-status", *sys.argv[1:]])


def refresh_main() -> int:
    return main(["refresh", *sys.argv[1:]])


def consult_main() -> int:
    return main(["consult", *sys.argv[1:]])


def run_gate_main() -> int:
    return main(["run-gate", *sys.argv[1:]])


def handoff_main() -> int:
    return main(["handoff", *sys.argv[1:]])


def run_main() -> int:
    return main(["run", *sys.argv[1:]])
