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
from importlib import resources
from pathlib import Path
from typing import Any, Iterable

import yaml
from cbm.skill_loader import LoadedSkill, load_skill
from jsonschema import Draft202012Validator, RefResolver


SCHEMA_VERSION = "1.2"
CITATION_RE = re.compile(r"(?P<path>[^`:',#@\s]+):(?P<start>\d+)(?:-(?P<end>\d+))?@(?P<sha>[0-9a-f]{7,40})")
DEFAULT_EXCLUDED = [
    ".git/**",
    ".research/**",
    ".venv/**",
    "node_modules/**",
    "**/__pycache__/**",
    ".pytest_cache/**",
    ".DS_Store",
]
OPEN_CHALLENGE_STATUSES = {"open"}
LIVE_CHALLENGE_STATUSES = {"open", "accepted_as_alternative", "accepted_as_replacement"}
AUTHORITY_DOC_PATHS = [
    "AGENTS.md",
    "VISION.md",
    "RUNTIME-CONSTITUTION.md",
    ".planning/STATE.md",
    ".planning/HORIZONS.md",
    ".planning/CURRENT-PLAN.md",
]
RECOVERY_ALLOWED_WORK_CATEGORIES = {
    "false-provenance",
    "coverage-honesty",
    "producer-registry",
    "run-manifest",
    "benchmark",
    "codex-isolation",
    "loop-status",
    "recovery-governance",
    "runtime-producer",
}
DETERMINISTIC_PRODUCERS = {
    "project_type_report": "cbm-baseline-project-type@0.1",
    "codebase_map": "cbm-baseline-map@0.1",
    "surface_map": "cbm-baseline-surface@0.1",
    "authority_map": "cbm-baseline-authority@0.1",
    "dependency_graph": "cbm-baseline-dependency@0.1",
    "verification_map": "cbm-baseline-verification@0.1",
    "synthesis_index": "cbm-baseline-synthesis@0.1",
    "goal_binding": "cbm-baseline-bind@0.1",
    "workflow_trace": "dev-fixture-tracer@0.1",
    "refinement_report": "dev-fixture-refinement@0.1",
    "approval_plan": "dev-fixture-approval@0.1",
    "skeptic_review": "dev-fixture-skeptic@0.1",
    "findings_card": "dev-fixture-planner@0.1",
    "intervention_card": "dev-fixture-planner@0.1",
    "handoff": "cbm-baseline-handoff@0.1",
}
BASELINE_BANNER_TEXT = (
    "This run includes deterministic baseline output. Cards and artifacts labeled cbm-baseline-* or dev-fixture-* are NOT runtime-agent readings; "
    "they inherit baseline guarantees only (schema-valid, citation-resolved, evidence-table-checked). Do not act on them as if they had Skeptic review."
)
CODEX_CLI_SMOKE_PRODUCER = "codex-cli-smoke@0.1"
CODEX_CLI_SKILL_SURFACE_PRODUCER = "surface-mapper@1.2"
CODEX_CLI_SKILL_SKEPTIC_PRODUCER = "skeptic@1.2"
BACKEND_CHOICES = ["deterministic", "external", "codex-cli"]
DEFAULT_CODEX_CLI_MODEL = "gpt-5.4-mini"
DEFAULT_CODEX_CLI_REASONING_EFFORT = "medium"
DEFAULT_CODEX_CLI_TIMEOUT_SECONDS = 600
INTERRUPTED_EXIT_CODE = 124
RUN_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


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


def validate_run_id(run_id: str) -> str:
    if not RUN_ID_RE.fullmatch(run_id) or run_id in {".", ".."}:
        raise SystemExit("invalid run_id: use 1-64 letters, numbers, dot, underscore, or hyphen")
    return run_id


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def subprocess_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_text_if_nonempty(path: Path, text: str) -> None:
    if not text:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sha256_if_nonempty(path: Path) -> str:
    if not path.exists() or path.stat().st_size == 0:
        return ""
    return sha256_file(path)


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


def coverage_caveats(coverage: dict[str, Any]) -> list[str]:
    result = coverage["result"]
    examined = result["files_examined_directly"]
    in_scope = result["files_in_scope"]
    unread = result["files_unread_in_scope"]
    extractor_only = max(result["files_inspected_via_extractor"] - examined, 0)
    return [
        f"{examined} of {in_scope} in-scope file(s) were directly examined for role claims; {unread} file(s) remain unread by an agent or human.",
        f"{extractor_only} file(s) were inspected via deterministic extractors only; those observations support structural claims, not settled interpretive role claims.",
    ]


def input_staleness(repo: Path, inputs: list[dict[str, str]]) -> dict[str, Any]:
    stale_artifacts = []
    for input_item in inputs:
        input_path = repo / input_item["path"]
        if not input_path.exists():
            stale_artifacts.append(f"missing: {input_item['path']}")
        elif sha256_file(input_path) != input_item["sha256"]:
            stale_artifacts.append(f"input hash changed: {input_item['path']}")
    return {"fresh": len(inputs) - len(stale_artifacts), "stale_artifacts": stale_artifacts}


def artifact_bundle_citation_resolution(repo: Path, artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    citations: set[str] = set()
    unresolved = []
    for artifact in artifacts:
        artifact_path = repo / artifact["path"]
        try:
            data, body = load_artifact_frontmatter(artifact_path)
            citations.update(extract_citations(data))
            citations.update(extract_citations(body))
        except Exception as exc:
            unresolved.append(f"{artifact['path']}: {exc}")
    resolved = 0
    for citation in sorted(citations):
        ok, reason = resolve_citation(repo, citation)
        if not ok:
            unresolved.append(f"{citation}: {reason}")
        else:
            resolved += 1
    return {
        "resolved": resolved,
        "unresolved_count": len(unresolved),
        "unresolved_examples": unresolved[:5],
        "citations": citations,
    }


def scope_signature(paths: list[str]) -> str:
    return sha256_text("\n".join(sorted(paths)))


def resource_exists(path: Any) -> bool:
    if isinstance(path, Path):
        return path.exists()
    return path.is_file() or path.is_dir()


def read_schema_json(path: Any) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def schema_source_key(path: Any) -> str:
    if isinstance(path, Path):
        return str(path.resolve())
    return str(path)


def schema_source_roots(repo: Path) -> list[Any]:
    roots: list[Any] = []
    env_root = os.environ.get("CBM_SCHEMA_DIR")
    if env_root:
        roots.append(Path(env_root).expanduser().resolve())
    package_root = resources.files("cbm").joinpath("schemas")
    if resource_exists(package_root):
        roots.append(package_root)
    source_root = Path(__file__).resolve().parents[1] / "schemas"
    if source_root.exists():
        roots.append(source_root)
    repo_root = repo / "schemas"
    if repo_root.exists():
        roots.append(repo_root)
    unique_roots: list[Any] = []
    seen: set[str] = set()
    for root in roots:
        key = schema_source_key(root)
        if key not in seen:
            unique_roots.append(root)
            seen.add(key)
    return unique_roots


def schema_store(repo: Path) -> dict[str, Any]:
    schemas = {}
    for root in schema_source_roots(repo):
        for path in root.iterdir():
            if not path.name.endswith(".schema.json"):
                continue
            data = read_schema_json(path)
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
        "workflow_trace": "workflow-trace.schema.json",
        "refinement_report": "refinement-report.schema.json",
        "approval_plan": "approval-plan.schema.json",
        "project_type_report": "project-type.schema.json",
        "producer_registry": "producer-registry.schema.json",
        "run_manifest": "run-manifest.schema.json",
    }
    name = mapping.get(artifact_type)
    if not name:
        raise ValueError(f"unsupported artifact_type: {artifact_type}")
    for root in schema_source_roots(repo):
        candidate = root.joinpath(name)
        if resource_exists(candidate):
            return read_schema_json(candidate)
    roots = ", ".join(str(root) for root in schema_source_roots(repo)) or "<none>"
    raise FileNotFoundError(f"schema {name} not found for {artifact_type}; searched {roots}")


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


def has_any_evidence(claim: dict[str, Any], allowed: set[str]) -> bool:
    return bool(set(claim.get("evidence_kinds", [])) & allowed)


def extractors_for_artifact(repo: Path, data: dict[str, Any]) -> dict[str, dict[str, Any]] | None:
    run_id = data.get("run_id")
    if not run_id:
        return None
    registry_path = repo / ".research" / run_id / "extractor-registry.json"
    if not registry_path.exists():
        return None
    registry = read_json(registry_path)
    return {extractor["id"]: extractor for extractor in registry.get("extractors", [])}


def extractor_registry_validation_errors(repo: Path, data: dict[str, Any]) -> list[str]:
    errors = validate_data(repo, data, "extractor_registry")
    seen_extractor_ids: dict[str, int] = {}
    for index, extractor in enumerate(data.get("extractors", [])):
        extractor_id = extractor.get("id", "<unknown>")
        if extractor_id in seen_extractor_ids:
            errors.append(f"extractors/{index}/{extractor_id}: duplicate id first declared at extractors/{seen_extractor_ids[extractor_id]}")
        else:
            seen_extractor_ids[extractor_id] = index
        if not extractor.get("known_blind_spots"):
            errors.append(f"extractors/{index}/{extractor_id}: known_blind_spots must be non-empty")
    seen_annotation_keys: dict[tuple[str, str], int] = {}
    for index, annotation in enumerate(data.get("project_pack_annotations", [])):
        project_type = annotation.get("project_type", "<unknown>")
        pack_id = annotation.get("pack_id", "<unknown>")
        annotation_key = (project_type, pack_id)
        if annotation_key in seen_annotation_keys:
            errors.append(
                f"project_pack_annotations/{index}/{project_type}/{pack_id}: "
                f"duplicate annotation first declared at project_pack_annotations/{seen_annotation_keys[annotation_key]}"
            )
        else:
            seen_annotation_keys[annotation_key] = index
        if not annotation.get("extractor_annotations"):
            errors.append(f"project_pack_annotations/{index}/{project_type}: extractor_annotations must be non-empty")
        if not annotation.get("known_blind_spots"):
            errors.append(f"project_pack_annotations/{index}/{project_type}: known_blind_spots must be non-empty")
    return errors


def extractor_registry_errors_for_artifact(repo: Path, data: dict[str, Any]) -> list[str]:
    run_id = data.get("run_id")
    if not run_id:
        return []
    registry_path = repo / ".research" / run_id / "extractor-registry.json"
    if not registry_path.exists():
        return []
    try:
        registry = read_json(registry_path)
    except Exception as exc:
        return [f"{registry_path.relative_to(repo)}: {exc}"]
    return [f"{registry_path.relative_to(repo)}: {error}" for error in extractor_registry_validation_errors(repo, registry)]


def check_claim_evidence(data: dict[str, Any], extractors: dict[str, dict[str, Any]] | None = None) -> list[str]:
    errors: list[str] = []

    def check_interpretive(claim: dict[str, Any], ref: str) -> None:
        if claim.get("claim_register") == "interpretive":
            if not claim.get("rationale"):
                errors.append(f"{ref}: interpretive claim requires rationale")
            if not claim.get("evidence_kinds"):
                errors.append(f"{ref}: interpretive claim requires at least one evidence_kind")

    def check_authority(authority: dict[str, Any], ref: str) -> None:
        check_interpretive(authority, ref)
        kind = authority.get("kind")
        if kind == "config":
            if not has_any_evidence(authority, {"static_relation"}):
                errors.append(f"{ref}: authority.config requires static_relation evidence")
            if authority.get("corroboration_count", 0) < 2:
                errors.append(f"{ref}: authority.config requires corroboration_count >= 2")
        elif kind == "routing":
            if not has_any_evidence(authority, {"static_relation", "runtime_trace"}):
                errors.append(f"{ref}: authority.routing requires static_relation or runtime_trace evidence")
        elif kind == "policy":
            if not has_any_evidence(authority, {"static_relation", "maintainer_statement"}):
                errors.append(f"{ref}: authority.policy requires static_relation or maintainer_statement evidence")

    def check_edge(edge: dict[str, Any], ref: str) -> None:
        check_interpretive(edge, ref)
        extractor_id = edge.get("extractor_id")
        if extractors is not None and extractor_id:
            extractor = extractors.get(extractor_id)
            if extractor is None:
                errors.append(f"{ref}: extractor_id {extractor_id} is not registered")
            else:
                supported = set(extractor.get("produces_evidence_kinds", []))
                unsupported = sorted(set(edge.get("evidence_kinds", [])) - supported)
                if unsupported:
                    errors.append(
                        f"{ref}: extractor_id {extractor_id} does not support evidence_kinds {','.join(unsupported)}"
                    )
        kind = edge.get("kind")
        evidence = set(edge.get("evidence_kinds", []))
        if kind in {"import", "call"} and "static_relation" not in evidence:
            errors.append(f"{ref}: edge.{kind} requires static_relation evidence")
        elif kind == "runtime_workflow":
            if not evidence & {"runtime_trace", "command_output"}:
                errors.append(f"{ref}: edge.runtime_workflow requires runtime_trace or command_output evidence")
            if evidence == {"static_structure"}:
                errors.append(f"{ref}: edge.runtime_workflow cannot rely on static_structure alone")
        elif kind == "test_exercises" and not evidence & {"static_relation", "command_output"}:
            errors.append(f"{ref}: edge.test_exercises requires static_relation or command_output evidence")
        elif kind == "config_contract":
            if "static_relation" not in evidence:
                errors.append(f"{ref}: edge.config_contract requires static_relation evidence")
            if edge.get("corroboration_count", 0) < 2:
                errors.append(f"{ref}: edge.config_contract requires corroboration_count >= 2")

    for index, authority in enumerate(data.get("authorities", [])):
        check_authority(authority, f"authorities/{index}/{authority.get('id', '<unknown>')}")
    for index, edge in enumerate(data.get("edges", [])):
        check_edge(edge, f"edges/{index}/{edge.get('id', '<unknown>')}")
    return errors


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


def verify_ledger_append_only(ledger_path: Path, require_manifest: bool = False) -> tuple[bool, str]:
    manifest_path = ledger_integrity_path(ledger_path)
    if not manifest_path.exists():
        if require_manifest:
            return False, "integrity manifest is missing"
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
    ok, reason = verify_ledger_append_only(ledger_path, require_manifest=True)
    if not ok:
        raise ValueError(f"ledger append-only verification failed: {reason}")
    append_jsonl(ledger_path, entry)
    write_ledger_integrity_manifest(ledger_path)


def append_uncertainty_entry(uncertainty_path: Path, entry: dict[str, Any]) -> None:
    ok, reason = verify_ledger_append_only(uncertainty_path, require_manifest=True)
    if not ok:
        raise ValueError(f"uncertainty register append-only verification failed: {reason}")
    append_jsonl(uncertainty_path, entry)
    write_ledger_integrity_manifest(uncertainty_path)


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
    pairs = citation_claim_pairs(data)
    if not pairs:
        pairs = [(citation, "artifact") for citation in extract_citations(data)]
    for citation, claim_id in pairs:
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
        run_id = validate_run_id(run_id)
        return RunPaths(repo=repo, run_id=run_id, run_dir=repo / ".research" / run_id)
    state_files = sorted((repo / ".research").glob("*/state.json"))
    if not state_files:
        raise SystemExit("no CBM run found; run cbm-init first or pass --run-id")
    state = read_json(state_files[-1])
    rid = state["run_id"]
    rid = validate_run_id(rid)
    return RunPaths(repo=repo, run_id=rid, run_dir=repo / ".research" / rid)


def producer_execution_contract(producer_id: str) -> str:
    if producer_id.startswith("cbm-baseline-"):
        return "deterministic_baseline"
    if producer_id.startswith("dev-fixture-"):
        return "dev_fixture"
    return "external_agent"


def codex_cli_surface_producer_id(mode: str, existing_producer_id: str | None = None) -> str:
    if mode == "skill":
        return CODEX_CLI_SKILL_SURFACE_PRODUCER
    if mode == "existing":
        return existing_producer_id or CODEX_CLI_SKILL_SURFACE_PRODUCER
    return DETERMINISTIC_PRODUCERS["surface_map"]


def codex_cli_skeptic_producer_id(mode: str) -> str:
    if mode == "none":
        return DETERMINISTIC_PRODUCERS["skeptic_review"]
    return CODEX_CLI_SKILL_SKEPTIC_PRODUCER if mode == "skill" else CODEX_CLI_SMOKE_PRODUCER


def skill_manifest(skill: LoadedSkill) -> dict[str, str]:
    return {"name": skill.name, "path": skill.path, "sha256": skill.sha256}


def build_producer_registry(
    backend: str,
    codex_skeptic_mode: str = "smoke",
    codex_surface_mode: str = "baseline",
    existing_surface_producer_id: str | None = None,
) -> dict[str, Any]:
    producers = []
    if backend == "deterministic":
        for artifact_type, producer_id in DETERMINISTIC_PRODUCERS.items():
            producers.append(
                {
                    "artifact_type": artifact_type,
                    "producer_id": producer_id,
                    "backend": "deterministic",
                    "execution_contract": producer_execution_contract(producer_id),
                }
            )
    elif backend == "codex-cli":
        for artifact_type, producer_id in DETERMINISTIC_PRODUCERS.items():
            if artifact_type == "surface_map" and codex_surface_mode in {"skill", "existing"}:
                producer_id = codex_cli_surface_producer_id(codex_surface_mode, existing_surface_producer_id)
                producer_backend = "codex-cli"
                execution_contract = "external_agent"
            elif artifact_type == "skeptic_review" and codex_skeptic_mode != "none":
                producer_id = codex_cli_skeptic_producer_id(codex_skeptic_mode)
                producer_backend = "codex-cli"
                execution_contract = "external_agent"
            else:
                producer_backend = "deterministic"
                execution_contract = producer_execution_contract(producer_id)
            producers.append(
                {
                    "artifact_type": artifact_type,
                    "producer_id": producer_id,
                    "backend": producer_backend,
                    "execution_contract": execution_contract,
                }
            )
    else:
        for artifact_type in sorted(DETERMINISTIC_PRODUCERS):
            producers.append(
                {
                    "artifact_type": artifact_type,
                    "producer_id": f"external-{artifact_type.replace('_', '-')}@0.1",
                    "backend": "external",
                    "execution_contract": "external_agent",
                }
            )
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "producer_registry",
        "backend": backend,
        "producers": producers,
    }


def run_manifest_step(
    step_id: str,
    command: str,
    artifact_type: str,
    producer_id: str,
    backend: str = "deterministic",
    skill: dict[str, str] | None = None,
) -> dict[str, Any]:
    step = {
        "step_id": step_id,
        "command": command,
        "artifact_type": artifact_type,
        "producer_id": producer_id,
        "backend": backend,
        "status": "planned",
        "exit_code": None,
    }
    if skill:
        step["skill"] = skill
    return step


def surface_artifact_producer_id(surface_artifact: Path | None) -> str | None:
    if not surface_artifact:
        return None
    try:
        data = read_json(surface_artifact)
    except Exception:
        return None
    produced_by = str(data.get("produced_by", ""))
    return produced_by or None


def refusal_reason(args: argparse.Namespace) -> str:
    if args.backend == "codex-cli":
        return "codex-cli backend requires --allow-live-codex because it may invoke a live model subprocess"
    return "external backend is declared but no external producer runner is configured"


def build_run_manifest(args: argparse.Namespace, repo: Path, run_id: str, status: str, steps: list[dict[str, Any]]) -> dict[str, Any]:
    registry_path = repo / ".research" / run_id / "producer-registry.json"
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "run_manifest",
        "run_id": run_id,
        "produced_at": utc_now(),
        "backend": args.backend,
        "mode": args.mode,
        "goal": args.goal,
        "goal_class": args.goal_class,
        "status": status,
        "producer_registry": {
            "path": str(registry_path.relative_to(repo)),
            "sha256": sha256_file(registry_path) if registry_path.exists() else None,
        },
        "steps": steps,
    }
    if status == "refused":
        manifest["refusal_reason"] = refusal_reason(args)
    return manifest


def annotate_codex_step_outputs(repo: Path, run_id: str, step: dict[str, Any]) -> None:
    if step.get("backend") != "codex-cli":
        return
    run_dir = repo / ".research" / run_id
    step_id = str(step["step_id"])
    step["stdout_sha256"] = sha256_if_nonempty(run_dir / "logs" / f"{step_id}.stdout")
    step["stderr_sha256"] = sha256_if_nonempty(run_dir / "logs" / f"{step_id}.stderr")
    output_name = "codex-cli-surface-output.json" if step_id == "codex-cli-skill-surface-map" else "codex-cli-smoke-output.json"
    output_path = run_dir / output_name
    step["output_path"] = str(output_path.relative_to(repo))
    step["output_path_sha256"] = sha256_if_nonempty(run_dir / output_name)
    repair_output = run_dir / "codex_outputs" / f"{step_id}.repair-output-1.json"
    repair_prompt = run_dir / "codex_outputs" / f"{step_id}.repair-prompt-1.txt"
    repair_stdout = run_dir / "logs" / f"{step_id}.repair-1.stdout"
    repair_stderr = run_dir / "logs" / f"{step_id}.repair-1.stderr"
    if repair_output.exists() or repair_prompt.exists():
        step["repair_attempts"] = [
            {
                "attempt": 1,
                "status": "succeeded" if step.get("status") == "succeeded" else "failed",
                "prompt_sha256": sha256_if_nonempty(repair_prompt),
                "output_sha256": sha256_if_nonempty(repair_output),
                "stdout_sha256": sha256_if_nonempty(repair_stdout),
                "stderr_sha256": sha256_if_nonempty(repair_stderr),
            }
        ]


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
        "backend": getattr(args, "backend", "deterministic"),
        "research_only": args.goal_class in {"understand_repo", "research_only"},
    }
    state = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "state",
        "run_id": run_id,
        "source_sha": sha,
        "mode": args.mode,
        "backend": getattr(args, "backend", "deterministic"),
        "status": "initialized",
        "created_at": now,
    }
    project_type_report = build_project_type_report(repo, paths, sha)
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
        "project_pack_annotations": [
            {
                "project_type": detection["project_type"],
                "pack_id": detection["pack_id"],
                "extractor_annotations": detection["extractor_annotations"],
                "known_blind_spots": detection["known_blind_spots"],
            }
            for detection in project_type_report["detections"]
        ],
    }
    write_json(paths.run_dir / "intake.json", intake)
    write_json(paths.run_dir / "state.json", state)
    write_json(paths.run_dir / "extractor-registry.json", registry)
    write_json(
        paths.run_dir / "producer-registry.json",
        build_producer_registry(
            getattr(args, "backend", "deterministic"),
            getattr(args, "codex_skeptic_mode", "smoke"),
            getattr(args, "codex_surface_mode", "baseline"),
        ),
    )
    write_json(paths.run_dir / "project-type.json", project_type_report)
    (paths.run_dir / "evidence-ledger.jsonl").touch()
    write_ledger_integrity_manifest(paths.run_dir / "evidence-ledger.jsonl")
    append_citation_entries(
        repo,
        paths.run_dir / "evidence-ledger.jsonl",
        run_id,
        sha,
        str((paths.run_dir / "project-type.json").relative_to(repo)),
        project_type_report,
        "cbm-baseline-project-type",
    )
    (paths.run_dir / "uncertainty-register.jsonl").touch()
    write_ledger_integrity_manifest(paths.run_dir / "uncertainty-register.jsonl")
    print(paths.run_dir)
    return 0


def pack_file_matches(pattern: str, paths: set[str]) -> list[str]:
    if any(char in pattern for char in "*?["):
        return sorted(path for path in paths if fnmatch.fnmatch(path, pattern))
    return [pattern] if pattern in paths else []


def text_contains_marker(repo: Path, rel: str, marker: str) -> bool:
    try:
        return marker.lower() in (repo / rel).read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        return False


def build_project_type_report(repo: Path, paths: RunPaths, sha: str) -> dict[str, Any]:
    files = [path.relative_to(repo).as_posix() for path in iter_repo_files(repo)]
    file_set = set(files)
    detections = []
    for project_type, pack in load_project_packs().items():
        evidence_paths: list[tuple[str, str]] = []
        for pattern in pack["any_files"]:
            for match in pack_file_matches(pattern, file_set):
                evidence_paths.append((match, f"matched pack file pattern {pattern}"))
        all_matches: list[tuple[str, str]] = []
        all_files_present = True
        for pattern in pack["all_files"]:
            matches = pack_file_matches(pattern, file_set)
            if not matches:
                all_files_present = False
                break
            all_matches.extend((match, f"matched required pack file pattern {pattern}") for match in matches)
        if all_files_present:
            evidence_paths.extend(all_matches)
        for marker in pack["content_markers"]:
            marker_hit = next((rel for rel in files if line_count(repo / rel) > 0 and text_contains_marker(repo, rel, marker)), None)
            if marker_hit:
                evidence_paths.append((marker_hit, f"contains marker {marker}"))
        deduped: list[tuple[str, str]] = []
        seen_paths: set[str] = set()
        for rel, reason in evidence_paths:
            if rel in seen_paths:
                continue
            seen_paths.add(rel)
            deduped.append((rel, reason))
        if not deduped:
            continue
        confidence = "high" if len(deduped) >= 2 and all_files_present else "medium"
        evidence = []
        for rel, reason in deduped[:5]:
            citation = citation_for(repo, rel, sha)
            if citation:
                evidence.append({"path": rel, "reason": reason, "citation": citation})
        if not evidence:
            continue
        detections.append(
            {
                "project_type": project_type,
                "display_name": pack["display_name"],
                "confidence": confidence,
                "pack_id": pack["pack_id"],
                "evidence": evidence,
                "extractor_annotations": pack["extractor_annotations"],
                "authority_hints": pack["authority_hints"],
                "known_blind_spots": pack["known_blind_spots"],
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "project_type_report",
        "run_id": paths.run_id,
        "produced_at": utc_now(),
        "produced_by": "cbm-baseline-project-type@0.1",
        "source_sha": sha,
        "inputs": [],
        "status": "draft",
        "detections": sorted(detections, key=lambda item: item["project_type"]),
    }


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
        "produced_by": "cbm-baseline-map@0.1",
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
    if path in {"pyproject.toml", "setup.py", "requirements.txt", "package.json", "pnpm-lock.yaml", "yarn.lock", "Cargo.toml", "go.mod"}:
        return "build", "config"
    if path.endswith((".toml", ".yaml", ".yml", ".json", ".ini", ".cfg")):
        return "other", "config"
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
        "produced_by": "cbm-baseline-surface@0.1",
        "source_sha": sha,
        "inputs": [{"path": str(codebase_path.relative_to(repo)), "sha256": sha256_file(codebase_path)}],
        "status": "draft",
        "coverage": coverage_block(codebase_map["coverage"]["result"]["files_in_scope"]),
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
    append_citation_entries(repo, paths.run_dir / "evidence-ledger.jsonl", paths.run_id, surface["source_sha"], str(surface_path.relative_to(repo)), surface, "cbm-baseline-surface")
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
        "produced_by": "cbm-baseline-authority@0.1",
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
        "cbm-baseline-authority",
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
    now = utc_now()
    citation = first_artifact_citation(repo, paths, graph)
    body = (
        "No runtime Skeptic finding was produced for this artifact. "
        "Deterministic review leaves unknown edges active for a real isolated Skeptic.\n\n"
        f"Reviewed artifact evidence: {citation}\n"
    )
    review = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "skeptic_review",
        "run_id": paths.run_id,
        "produced_at": now,
        "produced_by": "dev-fixture-skeptic@0.1",
        "source_sha": graph["source_sha"],
        "artifact_reviewed": str(graph_path.relative_to(repo)),
        "findings_logged": 0,
        "challenge_ids": [],
    }
    return review, body


def command_skeptic_review(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    paths = run_paths(repo, args.run_id)
    artifact_path = Path(args.artifact)
    if not artifact_path.is_absolute():
        artifact_path = repo / artifact_path
    artifact_path = artifact_path.resolve()
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
                "produced_by": "dev-fixture-skeptic@0.1",
                "source_sha": data.get("source_sha", source_sha(repo)),
                "artifact_reviewed": str(artifact_path.relative_to(repo)),
                "findings_logged": 0,
                "challenge_ids": [],
            }
            citation = first_artifact_citation(repo, paths, data)
            body = f"No runtime Skeptic finding was produced for this artifact.\n\nReviewed artifact evidence: {citation}\n"
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
        "produced_by": "cbm-baseline-dependency@0.1",
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
        "cbm-baseline-dependency",
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
        "produced_by": "cbm-baseline-verification@0.1",
        "source_sha": sha,
        "inputs": [{"path": str(codebase_path.relative_to(repo)), "sha256": sha256_file(codebase_path)}],
        "status": "draft",
        "coverage": coverage_block(codebase_map["coverage"]["result"]["files_in_scope"]),
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
        "cbm-baseline-verification",
    )
    write_json(verification_path, verification_map)
    print(verification_path)
    return 0


def challenged_claim_refs(artifact_path: Path, repo: Path, claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    refs = []
    for claim in claims:
        challenges = live_challenges(claim)
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
    challenged.extend(challenged_claim_refs(surface_path, repo, all_artifact_claims(surface)))
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
        "produced_by": "cbm-baseline-synthesis@0.1",
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


DEFAULT_GOAL_PACK: dict[str, Any] = {
    "research_only": False,
    "card_type": "intervention_card",
    "priority": {"call": 0, "import": 1, "authority": 2},
    "rationale": "default goal pack prioritizes actionable relation edges before broad authority surfaces.",
}


_GOAL_PACK_CACHE: dict[str, dict[str, Any]] | None = None


def validate_goal_pack_definition(pack_name: str, data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError(f"goal pack {pack_name} must be a JSON object")
    required = {"goal_class", "research_only", "card_type", "priority", "rationale"}
    missing = sorted(required - data.keys())
    if missing:
        raise ValueError(f"goal pack {pack_name} missing required fields: {', '.join(missing)}")
    if not isinstance(data["goal_class"], str) or not data["goal_class"]:
        raise ValueError(f"goal pack {pack_name} goal_class must be a non-empty string")
    if not isinstance(data["research_only"], bool):
        raise ValueError(f"goal pack {pack_name} research_only must be boolean")
    if data["card_type"] not in {"findings_card", "intervention_card"}:
        raise ValueError(f"goal pack {pack_name} card_type must be findings_card or intervention_card")
    if not isinstance(data["priority"], dict) or not data["priority"]:
        raise ValueError(f"goal pack {pack_name} priority must be a non-empty object")
    for key, value in data["priority"].items():
        if not isinstance(key, str) or not isinstance(value, int):
            raise ValueError(f"goal pack {pack_name} priority entries must map strings to integers")
    if not isinstance(data["rationale"], str) or not data["rationale"]:
        raise ValueError(f"goal pack {pack_name} rationale must be a non-empty string")
    return {
        "research_only": data["research_only"],
        "card_type": data["card_type"],
        "priority": data["priority"],
        "rationale": data["rationale"],
    }


def load_goal_packs() -> dict[str, dict[str, Any]]:
    global _GOAL_PACK_CACHE
    if _GOAL_PACK_CACHE is not None:
        return _GOAL_PACK_CACHE
    packs: dict[str, dict[str, Any]] = {}
    pack_root = resources.files("cbm.goal_packs")
    for pack_file in sorted(pack_root.iterdir(), key=lambda path: path.name):
        if pack_file.name == "__init__.py" or not pack_file.name.endswith(".json"):
            continue
        raw_pack = json.loads(pack_file.read_text(encoding="utf-8"))
        goal_class = raw_pack.get("goal_class") if isinstance(raw_pack, dict) else pack_file.name.removesuffix(".json")
        packs[goal_class] = validate_goal_pack_definition(pack_file.name, raw_pack)
    _GOAL_PACK_CACHE = packs
    return packs


_PROJECT_PACK_CACHE: dict[str, dict[str, Any]] | None = None


def validate_project_pack_definition(pack_name: str, data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError(f"project pack {pack_name} must be a JSON object")
    required = {"pack_id", "project_type", "display_name", "any_files", "all_files", "content_markers", "extractor_annotations", "authority_hints", "known_blind_spots"}
    missing = sorted(required - data.keys())
    if missing:
        raise ValueError(f"project pack {pack_name} missing required fields: {', '.join(missing)}")
    for key in ["pack_id", "project_type", "display_name"]:
        if not isinstance(data[key], str) or not data[key]:
            raise ValueError(f"project pack {pack_name} {key} must be a non-empty string")
    for key in ["any_files", "all_files", "content_markers", "extractor_annotations", "authority_hints", "known_blind_spots"]:
        if not isinstance(data[key], list) or not all(isinstance(item, str) for item in data[key]):
            raise ValueError(f"project pack {pack_name} {key} must be a string array")
    return data


def load_project_packs() -> dict[str, dict[str, Any]]:
    global _PROJECT_PACK_CACHE
    if _PROJECT_PACK_CACHE is not None:
        return _PROJECT_PACK_CACHE
    packs: dict[str, dict[str, Any]] = {}
    pack_root = resources.files("cbm.project_packs")
    for pack_file in sorted(pack_root.iterdir(), key=lambda path: path.name):
        if pack_file.name == "__init__.py" or not pack_file.name.endswith(".json"):
            continue
        pack = validate_project_pack_definition(pack_file.name, json.loads(pack_file.read_text(encoding="utf-8")))
        packs[pack["project_type"]] = pack
    _PROJECT_PACK_CACHE = packs
    return packs


def goal_pack(goal_class: str) -> dict[str, Any]:
    return load_goal_packs().get(goal_class, DEFAULT_GOAL_PACK)


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
        "produced_by": "cbm-baseline-bind@0.1",
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
    append_citation_entries(repo, paths.run_dir / "evidence-ledger.jsonl", paths.run_id, surface["source_sha"], str(binding_path.relative_to(repo)), binding, "cbm-baseline-bind")
    write_json(binding_path, binding)
    print(binding_path)
    return 0


def command_trace_workflows(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    paths = run_paths(repo, args.run_id)
    dependency_path = paths.run_dir / "dependency-graph.json"
    if not dependency_path.exists():
        print("dependency-graph.json missing; run cbm-dependency-graph first", file=sys.stderr)
        return 1
    codebase_map = read_codebase_map(paths.run_dir)
    dependency_graph = read_json(dependency_path)
    intake = read_intake(paths.run_dir)
    binding_path = paths.run_dir / "goal-binding.json"
    binding = read_json(binding_path) if binding_path.exists() else None
    selected_candidate = binding["candidates"][0] if binding and binding.get("candidates") else None
    edges = [edge for edge in dependency_graph["edges"] if edge["kind"] in {"call", "import"} and edge.get("citations")]
    selected_edge = None
    if selected_candidate and "/edges/" in selected_candidate["surface_ref"]:
        selected_id = selected_candidate["surface_id"]
        selected_edge = next((edge for edge in edges if edge["id"] == selected_id), None)
    if selected_edge is None and edges:
        selected_edge = edges[0]
    if selected_edge is None:
        print("dependency-graph.json has no citable import or call edge to trace", file=sys.stderr)
        return 1
    sha = dependency_graph["source_sha"]
    citation = selected_edge["citations"][0]
    goal = binding["goal"] if binding else intake["goal"]
    goal_class = binding["goal_class"] if binding else intake["goal_class"]
    relation = selected_edge["kind"]
    target = selected_edge["to"]["path"]
    if selected_edge["to"].get("symbol"):
        target = f"{target}::{selected_edge['to']['symbol']}"
    trace_path = paths.run_dir / "workflow-traces" / "trace-0001.json"
    inputs = [{"path": str(dependency_path.relative_to(repo)), "sha256": sha256_file(dependency_path)}]
    if binding_path.exists():
        inputs.append({"path": str(binding_path.relative_to(repo)), "sha256": sha256_file(binding_path)})
    trace = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "workflow_trace",
        "run_id": paths.run_id,
        "produced_at": utc_now(),
        "produced_by": "dev-fixture-tracer@0.1",
        "source_sha": sha,
        "inputs": inputs,
        "status": "draft",
        "coverage": coverage_block(codebase_map["coverage"]["result"]["files_in_scope"]),
        "staleness": {"stale_if_input_hash_changes": True, "depends_on_paths": [selected_edge["from"]["path"], selected_edge["to"]["path"]]},
        "goal": goal,
        "goal_class": goal_class,
        "workflow_id": "wft-0001",
        "workflow_name": f"{goal_class} trace through {selected_edge['from']['path']}",
        "trigger": {
            "kind": "goal_binding" if binding else "unknown",
            "description": f"Trace selected from the {relation} relation bound to the goal: {goal}",
            "claim_register": "inferential",
            "evidence_kinds": ["static_relation"],
            "citations": [citation],
        },
        "steps": [
            {
                "step_id": "step-0001",
                "order": 1,
                "path": selected_edge["from"]["path"],
                "description": f"Observed source side of {relation} relation toward {target}.",
                "claim_register": selected_edge["claim_register"],
                "claim_status": selected_edge["claim_status"],
                "evidence_kinds": selected_edge["evidence_kinds"],
                "citations": [citation],
            },
            {
                "step_id": "step-0002",
                "order": 2,
                "path": selected_edge["to"]["path"],
                "symbol": selected_edge["to"].get("symbol", ""),
                "description": f"Observed target side of {relation} relation from {selected_edge['from']['path']}.",
                "claim_register": "inferential",
                "claim_status": "active",
                "evidence_kinds": ["static_relation"],
                "citations": [citation],
            },
        ],
        "unknowns": [
            {
                "description": "This first tracer artifact is derived from static dependency evidence only; it does not execute or observe runtime behavior.",
                "impact": "Treat ordering and workflow semantics as inferential until a runtime_trace or command_output step is added.",
            }
        ],
        "confidence": "low",
        "confidence_rationale": "Confidence is low because the trace is a deterministic projection from static relations, not an observed runtime workflow.",
    }
    if not trace["steps"][1]["symbol"]:
        trace["steps"][1].pop("symbol")
    errors = validate_data(repo, trace, "workflow_trace")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    append_citation_entries(repo, paths.run_dir / "evidence-ledger.jsonl", paths.run_id, sha, str(trace_path.relative_to(repo)), trace, "dev-fixture-tracer")
    write_json(trace_path, trace)
    print(trace_path)
    return 0


def command_refine(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    paths = run_paths(repo, args.run_id)
    dependency_path = paths.run_dir / "dependency-graph.json"
    if not dependency_path.exists():
        print("dependency-graph.json missing; run cbm-dependency-graph first", file=sys.stderr)
        return 1
    dependency_graph = read_json(dependency_path)
    inputs = [{"path": str(dependency_path.relative_to(repo)), "sha256": sha256_file(dependency_path)}]
    refinements: list[dict[str, Any]] = []
    for edge in dependency_graph["edges"]:
        for challenge in edge.get("challenges", []):
            citations = challenge.get("competing_evidence") or edge.get("citations") or [first_artifact_citation(repo, paths, dependency_graph)]
            refinements.append(
                {
                    "item_id": f"rfi-{len(refinements) + 1:04d}",
                    "source_artifact": str(dependency_path.relative_to(repo)),
                    "source_kind": "skeptic_challenge",
                    "claim_id": edge["id"],
                    "challenge_id": challenge["challenge_id"],
                    "disposition": "needs_runtime_trace" if edge["kind"] == "unknown" else "needs_mapper_rerun",
                    "reentry_targets": ["tracer", "dependency_mapper"],
                    "rationale": "The challenge remains live and must re-enter a later tracing or dependency-mapping round before downstream confidence can increase.",
                    "citations": citations,
                }
            )
    trace_dir = paths.run_dir / "workflow-traces"
    if trace_dir.exists():
        for trace_path in sorted(trace_dir.glob("*.json")):
            trace = read_json(trace_path)
            inputs.append({"path": str(trace_path.relative_to(repo)), "sha256": sha256_file(trace_path)})
            fallback_citations = trace["steps"][0]["citations"]
            for unknown in trace.get("unknowns", []):
                refinements.append(
                    {
                        "item_id": f"rfi-{len(refinements) + 1:04d}",
                        "source_artifact": str(trace_path.relative_to(repo)),
                        "source_kind": "trace_unknown",
                        "claim_id": trace["workflow_id"],
                        "disposition": "needs_runtime_trace",
                        "reentry_targets": ["tracer", "manual_review"],
                        "rationale": f"Trace unknown remains unresolved: {unknown['description']}",
                        "citations": fallback_citations,
                    }
                )
    if not refinements:
        rel, _ = first_citable_file(repo, read_codebase_map(paths.run_dir), dependency_graph["source_sha"])
        citation = citation_for(repo, rel, dependency_graph["source_sha"])
        if not citation:
            print(f"could not create citation for {rel}", file=sys.stderr)
            return 1
        refinements.append(
            {
                "item_id": "rfi-0001",
                "source_artifact": str(dependency_path.relative_to(repo)),
                "source_kind": "skeptic_challenge",
                "claim_id": "no-open-challenge",
                "disposition": "parked",
                "reentry_targets": ["skeptic"],
                "rationale": "No open deterministic challenges were present; refinement is parked until a later Skeptic round produces one.",
                "citations": [citation],
            }
        )
    report_path = paths.run_dir / "refinements" / "refinement-0001.json"
    report = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "refinement_report",
        "run_id": paths.run_id,
        "produced_at": utc_now(),
        "produced_by": "dev-fixture-refinement@0.1",
        "source_sha": dependency_graph["source_sha"],
        "inputs": inputs,
        "status": "draft",
        "round_id": "ref-0001",
        "round_number": 1,
        "refinements": refinements,
        "next_round_required": any(item["disposition"] in {"accepted_live_unknown", "needs_runtime_trace", "needs_mapper_rerun"} for item in refinements),
        "summary": "Deep-mode refinement records unresolved challenges and trace unknowns as explicit re-entry work rather than treating the run as complete.",
    }
    errors = validate_data(repo, report, "refinement_report")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    append_citation_entries(repo, paths.run_dir / "evidence-ledger.jsonl", paths.run_id, dependency_graph["source_sha"], str(report_path.relative_to(repo)), report, "dev-fixture-refinement")
    write_json(report_path, report)
    print(report_path)
    return 0


def risk_for_envelope(envelope: dict[str, Any]) -> str:
    if envelope.get("requires_network") or envelope.get("requires_install") or envelope.get("mutates_filesystem"):
        return "high"
    if envelope.get("max_duration_seconds", 0) > 120:
        return "medium"
    return "low"


def command_approval_plan(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    paths = run_paths(repo, args.run_id)
    verification_path = paths.run_dir / "verification-map.json"
    refinement_paths = sorted((paths.run_dir / "refinements").glob("*.json")) if (paths.run_dir / "refinements").exists() else []
    inputs: list[dict[str, str]] = []
    approval_items: list[dict[str, Any]] = []
    source = source_sha(repo)
    if verification_path.exists():
        verification_map = read_json(verification_path)
        source = verification_map["source_sha"]
        inputs.append({"path": str(verification_path.relative_to(repo)), "sha256": sha256_file(verification_path)})
        for gate in verification_map.get("ci_gates", []):
            command = gate.get("command")
            if not command:
                continue
            envelope = command["safety_envelope"]
            approval_items.append(
                {
                    "approval_id": f"apv-{len(approval_items) + 1:04d}",
                    "source_artifact": str(verification_path.relative_to(repo)),
                    "source_ref": gate["id"],
                    "approval_kind": "command_execution",
                    "action": f"Run gate {gate['id']}: {' '.join(command['argv'])}",
                    "risk_level": risk_for_envelope(envelope),
                    "approval_status": "pending",
                    "safety_envelope": envelope,
                    "rationale": "Deep mode requires explicit approval before command execution, even when the safety envelope is low risk.",
                }
            )
    for refinement_path in refinement_paths:
        refinement = read_json(refinement_path)
        source = refinement["source_sha"]
        inputs.append({"path": str(refinement_path.relative_to(repo)), "sha256": sha256_file(refinement_path)})
        for item in refinement["refinements"]:
            if "manual_review" not in item["reentry_targets"]:
                continue
            approval_items.append(
                {
                    "approval_id": f"apv-{len(approval_items) + 1:04d}",
                    "source_artifact": str(refinement_path.relative_to(repo)),
                    "source_ref": item["item_id"],
                    "approval_kind": "manual_review",
                    "action": f"Review refinement item {item['item_id']} before escalating {item['claim_id']}.",
                    "risk_level": "medium",
                    "approval_status": "pending",
                    "safety_envelope": {
                        "requires_network": False,
                        "requires_install": False,
                        "mutates_filesystem": False,
                        "max_duration_seconds": 1,
                        "declared_output_paths": [],
                    },
                    "rationale": "Manual review is required because this refinement item depends on human adjudication before confidence can increase.",
                }
            )
    if not inputs:
        print("no verification-map.json or refinement reports found for approval planning", file=sys.stderr)
        return 1
    if not approval_items:
        approval_items.append(
            {
                "approval_id": "apv-0001",
                "source_artifact": inputs[0]["path"],
                "approval_kind": "manual_review",
                "action": "Confirm no manual approval items are required for this run.",
                "risk_level": "low",
                "approval_status": "not_required",
                "safety_envelope": {
                    "requires_network": False,
                    "requires_install": False,
                    "mutates_filesystem": False,
                    "max_duration_seconds": 1,
                    "declared_output_paths": [],
                },
                "rationale": "No runnable gates or manual-review refinement items were present, so approval is recorded as not required.",
            }
        )
    plan_path = paths.run_dir / "approvals" / "approval-plan.json"
    plan = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "approval_plan",
        "run_id": paths.run_id,
        "produced_at": utc_now(),
        "produced_by": "dev-fixture-approval@0.1",
        "source_sha": source,
        "inputs": inputs,
        "status": "draft",
        "approval_items": approval_items,
        "summary": "Deep-mode approval plan lists command execution and manual review actions that require explicit approval before proceeding.",
    }
    errors = validate_data(repo, plan, "approval_plan")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    write_json(plan_path, plan)
    print(plan_path)
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


def command_extractor_registry(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    if args.registry:
        path = Path(args.registry)
        if not path.is_absolute():
            path = repo / path
    else:
        path = run_paths(repo, args.run_id).run_dir / "extractor-registry.json"
    data = read_json(path)
    errors = extractor_registry_validation_errors(repo, data)
    if errors:
        for error in errors:
            print(f"registry-fail {error}")
        return 2
    print(f"valid extractor registry {path}")
    return 0


def command_check_evidence(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    path = Path(args.artifact)
    if not path.is_absolute():
        path = repo / path
    data, _ = load_artifact_frontmatter(path)
    errors = extractor_registry_errors_for_artifact(repo, data)
    errors.extend(check_claim_evidence(data, extractors_for_artifact(repo, data)))
    if errors:
        for error in errors:
            print(f"evidence-fail {error}")
        return 2
    print(f"evidence-ok {path}")
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
        failed += 1
    return 0 if failed == 0 else 1


def artifact_gate_failures(repo: Path, path: Path) -> list[str]:
    failures: list[str] = []
    try:
        data, body = load_artifact_frontmatter(path)
        artifact_type = infer_artifact_type(path, data)
        failures.extend(f"schema: {error}" for error in validate_data(repo, data, artifact_type))
        citations = sorted(set(extract_citations(data) + extract_citations(body)))
        if not citations:
            failures.append("citation: no citations found")
        for citation in citations:
            ok, reason = resolve_citation(repo, citation)
            if not ok:
                failures.append(f"citation: {citation}: {reason}")
        failures.extend(f"extractor-registry: {error}" for error in extractor_registry_errors_for_artifact(repo, data))
        failures.extend(f"evidence: {error}" for error in check_claim_evidence(data, extractors_for_artifact(repo, data)))
        contestation = verify_contestation_propagation(repo, data)
        for item in contestation["missing"]:
            failures.append(
                "contestation: missing dependent challenge "
                f"{item['claim_artifact']} {item['claim_id']} {','.join(item['missing_challenge_ids'])}"
            )
        for item in contestation["stale"]:
            stale_ids = ",".join(item.get("stale_challenge_ids", []))
            suffix = f" {stale_ids}" if stale_ids else ""
            failures.append(f"contestation: stale dependent challenge {item['claim_artifact']} {item['claim_id']}{suffix}")
        confidence_check = verify_card_confidence(data)
        for item in confidence_check["violations"]:
            failures.append(f"confidence: {item['field']}: {item['reason']}")
        coverage_check = verify_card_coverage_honesty(data)
        for item in coverage_check["violations"]:
            failures.append(f"coverage: {item['field']}: {item['reason']}")
    except Exception as exc:
        failures.append(str(exc))
    return failures


def command_gate_artifact(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    path = Path(args.artifact)
    if not path.is_absolute():
        path = repo / path
    failures = artifact_gate_failures(repo, path)
    if failures:
        for failure in failures:
            print(f"gate-fail {failure}")
        return 2
    print(f"gate-ok {path}")
    return 0


def artifact_claim_collections(data: dict[str, Any]) -> list[tuple[str, list[dict[str, Any]]]]:
    collections: list[tuple[str, list[dict[str, Any]]]] = []
    if isinstance(data.get("authorities"), list):
        collections.append(("authorities", data["authorities"]))
    if isinstance(data.get("edges"), list):
        collections.append(("edges", data["edges"]))
    return collections


def find_claim(data: dict[str, Any], claim_id: str) -> dict[str, Any] | None:
    for _, claims in artifact_claim_collections(data):
        for claim in claims:
            if claim.get("id") == claim_id:
                return claim
    return None


def all_artifact_claims(data: dict[str, Any]) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    for _, collection in artifact_claim_collections(data):
        claims.extend(collection)
    return claims


def command_challenge(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    artifact_path = Path(args.artifact)
    if not artifact_path.is_absolute():
        artifact_path = repo / artifact_path
    artifact_path = artifact_path.resolve()
    data = read_json(artifact_path)
    artifact_type = infer_artifact_type(artifact_path, data)
    if artifact_type not in {"surface_map", "authority_map", "dependency_graph"}:
        print(f"{artifact_type} does not support claim challenges", file=sys.stderr)
        return 1
    claim = find_claim(data, args.claim_id)
    if claim is None:
        print(f"claim not found: {args.claim_id}", file=sys.stderr)
        return 1
    evidence = args.evidence
    for citation in evidence:
        ok, reason = resolve_citation(repo, citation)
        if not ok:
            print(f"evidence citation does not resolve: {citation}: {reason}", file=sys.stderr)
            return 1
    challenge_id = next_challenge_id(all_artifact_claims(data))
    challenge = {
        "challenge_id": challenge_id,
        "challenges_claim_id": args.claim_id,
        "raised_by": args.raised_by,
        "raised_at": utc_now(),
        "competing_reading": args.competing_reading,
        "competing_evidence": evidence,
        "interpretive_axis": args.axis,
        "relation_to_original": args.relation,
        "status": "open",
        "rationale": args.rationale,
    }
    claim.setdefault("challenges", []).append(challenge)
    claim["claim_status"] = "contested" if len(claim["challenges"]) > 1 else "challenged"
    errors = validate_data(repo, data, artifact_type)
    errors.extend(extractor_registry_errors_for_artifact(repo, data))
    errors.extend(check_claim_evidence(data, extractors_for_artifact(repo, data)))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    ledger_path = artifact_path.parent / "evidence-ledger.jsonl"
    if not ledger_path.exists():
        ledger_path = artifact_path.parents[1] / "evidence-ledger.jsonl"
    entry = {
        "schema_version": SCHEMA_VERSION,
        "entry_id": next_ledger_id(ledger_path),
        "ts": utc_now(),
        "entry_kind": "claim_challenged",
        "agent": args.raised_by,
        "skill_version": "0.1",
        "run_id": data["run_id"],
        "source_sha": data["source_sha"],
        "artifact_path": str(artifact_path.relative_to(repo)),
        "claim_id": args.claim_id,
        "challenge_id": challenge_id,
        "challenge": args.competing_reading,
        "competing_evidence": evidence,
    }
    try:
        append_ledger_entry(repo, ledger_path, entry)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    write_json(artifact_path, data)
    print(challenge_id)
    return 0


def apply_runtime_skeptic_challenges(repo: Path, artifact_path: Path, data: dict[str, Any], output: dict[str, Any], raised_by: str) -> list[str]:
    artifact_type = infer_artifact_type(artifact_path, data)
    if artifact_type not in {"surface_map", "authority_map", "dependency_graph"}:
        raise ValueError(f"{artifact_type} does not support runtime skeptic challenges")
    challenges = output.get("challenges", [])
    if not challenges:
        return []
    ledger_path = artifact_path.parent / "evidence-ledger.jsonl"
    if not ledger_path.exists():
        ledger_path = artifact_path.parents[1] / "evidence-ledger.jsonl"
    ingested_ids: list[str] = []
    # Buffer ledger entries; commit only after the mutated artifact
    # validates (F2 from Codex review). Otherwise a validation failure
    # leaves the append-only ledger with `claim_challenged` rows that
    # reference challenges not present in the persisted artifact.
    pending_entries: list[dict[str, Any]] = []
    for item in challenges:
        claim_id = item["claim_id"]
        claim = find_claim(data, claim_id)
        if claim is None:
            raise ValueError(f"runtime skeptic challenge references missing claim: {claim_id}")
        evidence = item["competing_evidence"]
        for citation in evidence:
            ok, reason = resolve_citation(repo, citation)
            if not ok:
                raise ValueError(f"runtime skeptic evidence citation does not resolve: {citation}: {reason}")
        challenge_id = next_challenge_id(all_artifact_claims(data))
        challenge = {
            "challenge_id": challenge_id,
            "challenges_claim_id": claim_id,
            "raised_by": raised_by,
            "raised_at": utc_now(),
            "competing_reading": item["competing_reading"],
            "competing_evidence": evidence,
            "interpretive_axis": item["interpretive_axis"],
            "relation_to_original": item["relation_to_original"],
            "status": "open",
            "rationale": item["rationale"],
        }
        claim.setdefault("challenges", []).append(challenge)
        claim["claim_status"] = "contested" if len(claim["challenges"]) > 1 else "challenged"
        pending_entries.append(
            {
                "schema_version": SCHEMA_VERSION,
                # entry_id assigned at commit time (after validation) so a
                # buffered batch does not collide on ids.
                "ts": utc_now(),
                "entry_kind": "claim_challenged",
                "agent": raised_by,
                "skill_version": "1.2",
                "run_id": data["run_id"],
                "source_sha": data["source_sha"],
                "artifact_path": str(artifact_path.relative_to(repo)),
                "claim_id": claim_id,
                "challenge_id": challenge_id,
                "challenge": item["competing_reading"],
                "competing_evidence": evidence,
            }
        )
        ingested_ids.append(challenge_id)
    errors = validate_data(repo, data, artifact_type)
    errors.extend(extractor_registry_errors_for_artifact(repo, data))
    errors.extend(check_claim_evidence(data, extractors_for_artifact(repo, data)))
    if errors:
        raise ValueError("\n".join(errors))
    for entry in pending_entries:
        entry["entry_id"] = next_ledger_id(ledger_path)
        append_ledger_entry(repo, ledger_path, entry)
    write_json(artifact_path, data)
    return ingested_ids


def render_runtime_skeptic_body(output: dict[str, Any], durable_challenge_ids: list[str], skill: LoadedSkill | None, citation: str) -> str:
    body = output["body"].strip()
    raw_ids = list(output.get("challenge_ids", []))
    if skill and raw_ids and durable_challenge_ids:
        for raw_id, durable_id in zip(raw_ids, durable_challenge_ids):
            body = re.sub(re.escape(raw_id), durable_id, body, flags=re.IGNORECASE)
    prefix = "# Codex CLI Skill-Loaded Skeptic Review\n\n" if skill else "# Codex CLI Smoke Review\n\n"
    review_body = prefix + body + "\n"
    if not skill:
        review_body += f"\nSmoke citation anchor: {citation}\n"
    return review_body


def find_challenge(data: dict[str, Any], challenge_id: str) -> tuple[dict[str, Any], dict[str, Any]] | None:
    for claim in all_artifact_claims(data):
        for challenge in claim.get("challenges", []):
            if challenge.get("challenge_id") == challenge_id:
                return claim, challenge
    return None


def update_claim_status_from_challenges(claim: dict[str, Any]) -> None:
    challenges = claim.get("challenges", [])
    openish = [challenge for challenge in challenges if challenge.get("status") in LIVE_CHALLENGE_STATUSES]
    if not openish:
        claim["claim_status"] = "active"
    elif any(challenge.get("status") == "accepted_as_replacement" for challenge in openish):
        claim["claim_status"] = "contested"
    elif len(openish) > 1 or any(challenge.get("status") == "accepted_as_alternative" for challenge in openish):
        claim["claim_status"] = "contested"
    else:
        claim["claim_status"] = "challenged"


def live_challenges(claim: dict[str, Any]) -> list[dict[str, Any]]:
    return [challenge for challenge in claim.get("challenges", []) if challenge.get("status") in LIVE_CHALLENGE_STATUSES]


def resolved_challenges(claim: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        challenge
        for challenge in claim.get("challenges", [])
        if challenge.get("status") not in OPEN_CHALLENGE_STATUSES
    ]


def contestation_summary_for_claim_refs(claim_refs: list[tuple[str, dict[str, Any]]]) -> dict[str, Any]:
    registers = {"factual": 0, "inferential": 0, "interpretive": 0}
    statuses = {"active": 0, "challenged": 0, "contested": 0, "contradicted": 0, "superseded": 0, "retired": 0}
    open_challenges = 0
    contested_claims = []
    contradicted_claims = []
    for artifact_path, claim in claim_refs:
        register = claim.get("claim_register")
        if register in registers:
            registers[register] += 1
        status = claim.get("claim_status", "active")
        if status in statuses:
            statuses[status] += 1
        challenges = live_challenges(claim)
        open_challenges += sum(1 for challenge in challenges if challenge.get("status") in OPEN_CHALLENGE_STATUSES)
        if status == "contested":
            accepted_alternatives = [
                challenge["challenge_id"]
                for challenge in challenges
                if challenge.get("status") == "accepted_as_alternative"
            ]
            summary = f"{claim['id']} has {len(challenges)} live challenge(s)."
            if accepted_alternatives:
                summary = (
                    f"{claim['id']} has accepted alternative reading "
                    f"{', '.join(accepted_alternatives)}."
                )
            contested_claims.append(
                {
                    "claim_artifact": artifact_path,
                    "claim_id": claim["id"],
                    "challenge_count": len(challenges),
                    "summary": summary,
                }
            )
        if status == "contradicted":
            contradicted_claims.append({"claim_artifact": artifact_path, "claim_id": claim["id"]})
    return {
        "claims_by_register": registers,
        "claims_by_status": statuses,
        "open_challenges": open_challenges,
        "contested_claims": contested_claims,
        "contradicted_claims": contradicted_claims,
    }


def contestation_summary_for_claims(claims: list[dict[str, Any]], artifact_path: str) -> dict[str, Any]:
    return contestation_summary_for_claim_refs([(artifact_path, claim) for claim in claims])


def command_resolve_challenge(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    artifact_path = Path(args.artifact)
    if not artifact_path.is_absolute():
        artifact_path = repo / artifact_path
    artifact_path = artifact_path.resolve()
    data = read_json(artifact_path)
    artifact_type = infer_artifact_type(artifact_path, data)
    if artifact_type not in {"surface_map", "authority_map", "dependency_graph"}:
        print(f"{artifact_type} does not support claim challenges", file=sys.stderr)
        return 1
    found = find_challenge(data, args.challenge_id)
    if found is None:
        print(f"challenge not found: {args.challenge_id}", file=sys.stderr)
        return 1
    claim, challenge = found
    challenge["status"] = args.status
    response_note = getattr(args, "response_note", None)
    if response_note:
        existing_rationale = claim.get("rationale", "")
        separator = " " if existing_rationale and not existing_rationale.endswith(" ") else ""
        claim["rationale"] = f"{existing_rationale}{separator}Mapper response: {response_note}"
    update_claim_status_from_challenges(claim)
    errors = validate_data(repo, data, artifact_type)
    errors.extend(extractor_registry_errors_for_artifact(repo, data))
    errors.extend(check_claim_evidence(data, extractors_for_artifact(repo, data)))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    ledger_path = artifact_path.parent / "evidence-ledger.jsonl"
    if not ledger_path.exists():
        ledger_path = artifact_path.parents[1] / "evidence-ledger.jsonl"
    entry = {
        "schema_version": SCHEMA_VERSION,
        "entry_id": next_ledger_id(ledger_path),
        "ts": utc_now(),
        "entry_kind": "challenge_resolved",
        "agent": args.resolved_by,
        "skill_version": "0.1",
        "run_id": data["run_id"],
        "source_sha": data["source_sha"],
        "challenge_id": args.challenge_id,
        "resolution": args.resolution,
        "artifact_path": str(artifact_path.relative_to(repo)),
        "claim_id": claim["id"],
    }
    try:
        append_ledger_entry(repo, ledger_path, entry)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    write_json(artifact_path, data)
    print(args.challenge_id)
    return 0


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
        failed += 1
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


def referenced_claim(repo: Path, ref: str) -> tuple[str, dict[str, Any]] | None:
    if "#/" not in ref:
        return None
    artifact_ref, pointer = ref.split("#/", 1)
    artifact_path = repo / artifact_ref
    if not artifact_path.exists():
        return None
    data = read_json(artifact_path)
    parts = pointer.split("/")
    if len(parts) != 2 or parts[0] not in {"authorities", "edges"}:
        return None
    try:
        claim = data[parts[0]][int(parts[1])]
    except (KeyError, IndexError, ValueError, TypeError):
        return None
    return artifact_ref, claim


def verify_contestation_propagation(repo: Path, data: dict[str, Any]) -> dict[str, Any]:
    if data.get("artifact_type") not in {"findings_card", "intervention_card"}:
        return {"checked": False, "missing": [], "stale": []}
    dependent_by_claim = {
        (item["claim_artifact"], item["claim_id"]): set(item["challenge_ids"])
        for item in data.get("dependent_challenges", [])
    }
    refs = []
    for values in data.get("related_dependencies", {}).values():
        if isinstance(values, list):
            refs.extend(value for value in values if isinstance(value, str))
    missing = []
    stale = []
    expected_keys = set()
    for ref in refs:
        referenced = referenced_claim(repo, ref)
        if referenced is None:
            continue
        artifact_ref, claim = referenced
        live_ids = {challenge["challenge_id"] for challenge in live_challenges(claim)}
        if claim.get("claim_status") in {"challenged", "contested"} and live_ids:
            key = (artifact_ref, claim["id"])
            expected_keys.add(key)
            actual_ids = dependent_by_claim.get(key, set())
            missing_ids = sorted(live_ids - actual_ids)
            if missing_ids:
                missing.append(
                    {
                        "claim_artifact": artifact_ref,
                        "claim_id": claim["id"],
                        "missing_challenge_ids": missing_ids,
                    }
                )
            stale_ids = sorted(actual_ids - live_ids)
            if stale_ids:
                stale.append(
                    {
                        "claim_artifact": artifact_ref,
                        "claim_id": claim["id"],
                        "stale_challenge_ids": stale_ids,
                    }
                )
    for claim_artifact, claim_id in dependent_by_claim:
        if (claim_artifact, claim_id) not in expected_keys:
            stale.append({"claim_artifact": claim_artifact, "claim_id": claim_id})
    return {"checked": True, "missing": missing, "stale": stale}


def verify_card_confidence(data: dict[str, Any]) -> dict[str, Any]:
    if data.get("artifact_type") not in {"findings_card", "intervention_card"}:
        return {"checked": False, "violations": []}
    violations = []
    if data.get("confidence") == "high" and data.get("dependent_challenges"):
        violations.append(
            {
                "field": "confidence",
                "reason": "high confidence requires zero dependent_challenges",
            }
        )
    coverage = data.get("coverage")
    coverage_result = coverage.get("result", {}) if isinstance(coverage, dict) else {}
    if data.get("confidence") == "high" and coverage_result.get("files_unread_in_scope", 0) != 0:
        violations.append(
            {
                "field": "confidence",
                "reason": "high confidence requires zero unread files in scope",
            }
        )
    return {"checked": True, "violations": violations}


def verify_card_coverage_honesty(data: dict[str, Any]) -> dict[str, Any]:
    coverage = data.get("coverage")
    if not isinstance(coverage, dict):
        return {"checked": False, "violations": []}
    result = coverage.get("result", {})
    violations = []
    files_in_scope = result.get("files_in_scope")
    examined = result.get("files_examined_directly", 0)
    unread = result.get("files_unread_in_scope")
    if isinstance(files_in_scope, int) and isinstance(examined, int) and isinstance(unread, int):
        expected_unread = max(files_in_scope - examined, 0)
        if unread != expected_unread:
            violations.append(
                {
                    "field": "coverage.result.files_unread_in_scope",
                    "reason": f"expected {expected_unread} from files_in_scope={files_in_scope} and files_examined_directly={examined}",
                }
            )
    if data.get("artifact_type") not in {"findings_card", "intervention_card"}:
        return {"checked": True, "violations": violations}
    primary_files = data.get("primary_files", [])
    if len(primary_files) > examined:
        violations.append(
            {
                "field": "coverage.result.files_examined_directly",
                "reason": f"{len(primary_files)} primary file role claim(s) require at least {len(primary_files)} directly examined file(s)",
            }
        )
    for index, primary_file in enumerate(primary_files):
        path = primary_file.get("path")
        citations = primary_file.get("citations", [])
        if path and not any((parts := citation_parts(citation)) and parts["path"] == path for citation in citations):
            violations.append(
                {
                    "field": f"primary_files/{index}/citations",
                    "reason": f"primary file role claim for {path} requires a citation to the same path",
                }
            )
    return {"checked": True, "violations": violations}


def command_verify(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    path = Path(args.artifact)
    if not path.is_absolute():
        path = repo / path
    citations = artifact_citations(path)
    results = [verify_citation_at_head(repo, citation) for citation in citations]
    data, _ = load_artifact_frontmatter(path)
    registry_errors = extractor_registry_errors_for_artifact(repo, data)
    evidence_errors = check_claim_evidence(data, extractors_for_artifact(repo, data))
    contestation = verify_contestation_propagation(repo, data)
    confidence_check = verify_card_confidence(data)
    coverage_check = verify_card_coverage_honesty(data)
    report = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "verify_report",
        "produced_at": utc_now(),
        "artifact_path": str(path.relative_to(repo)) if path.is_relative_to(repo) else str(path),
        "head_sha": source_sha(repo),
        "results": results,
        "extractor_registry": {"errors": registry_errors},
        "claim_evidence": {"errors": evidence_errors},
        "contestation_propagation": contestation,
        "card_confidence": confidence_check,
        "coverage_honesty": coverage_check,
        "summary": {
            "still_grounded": sum(1 for item in results if item["status"] == "still_grounded"),
            "needs_review": sum(1 for item in results if item["status"] == "needs_review"),
            "broken": sum(1 for item in results if item["status"] == "broken"),
            "missing_citations": 0 if results else 1,
            "extractor_registry_errors": len(registry_errors),
            "claim_evidence_errors": len(evidence_errors),
            "contestation_missing": len(contestation["missing"]),
            "contestation_stale": len(contestation["stale"]),
            "confidence_violations": len(confidence_check["violations"]),
            "coverage_violations": len(coverage_check["violations"]),
        },
    }
    output_path = Path(args.output) if args.output else path.with_name("verify-report.json")
    if not output_path.is_absolute():
        output_path = repo / output_path
    write_json(output_path, report)
    for item in results:
        print(f"{item['status']} {item['citation']} {item['reason']}")
    for error in registry_errors:
        print(f"extractor_registry_error {error}")
    for error in evidence_errors:
        print(f"claim_evidence_error {error}")
    for item in contestation["missing"]:
        print(f"contestation_missing {item['claim_artifact']} {item['claim_id']} {','.join(item['missing_challenge_ids'])}")
    for item in contestation["stale"]:
        stale_ids = ",".join(item.get("stale_challenge_ids", []))
        suffix = f" {stale_ids}" if stale_ids else ""
        print(f"contestation_stale {item['claim_artifact']} {item['claim_id']}{suffix}")
    for item in confidence_check["violations"]:
        print(f"confidence_violation {item['field']} {item['reason']}")
    for item in coverage_check["violations"]:
        print(f"coverage_violation {item['field']} {item['reason']}")
    if not results:
        print("no citations found")
    print(output_path)
    return (
        0
        if report["summary"]["needs_review"] == 0
        and report["summary"]["broken"] == 0
        and report["summary"]["missing_citations"] == 0
        and report["summary"]["extractor_registry_errors"] == 0
        and report["summary"]["claim_evidence_errors"] == 0
        and report["summary"]["contestation_missing"] == 0
        and report["summary"]["contestation_stale"] == 0
        and report["summary"]["confidence_violations"] == 0
        and report["summary"]["coverage_violations"] == 0
        else 2
    )


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


def artifact_requires_citations(data: dict[str, Any]) -> bool:
    artifact_type = data.get("artifact_type")
    if artifact_type in {
        "surface_map",
        "authority_map",
        "dependency_graph",
        "verification_map",
        "workflow_trace",
        "refinement_report",
        "goal_binding",
        "findings_card",
        "intervention_card",
        "skeptic_review",
        "refresh_delta",
        "project_type_report",
    }:
        return True
    if artifact_type == "consultation":
        return data.get("status") == "answered"
    return False


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
        "missing_citations": 1 if not citations and artifact_requires_citations(data) else 0,
    }
    if summary["missing_citations"]:
        freshness = "broken"
    elif not citations:
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
        "historical_valid": bool(citations) and all(resolve_citation(repo, citation)[0] for citation in citations),
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
        "missing_citations": sum(item["citation_summary"].get("missing_citations", 0) for item in artifacts),
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


def open_questions_reconciled(paths: RunPaths, rationale: str) -> list[dict[str, Any]]:
    register_path = paths.run_dir / "uncertainty-register.jsonl"
    reconciled = []
    for entry in read_jsonl(register_path):
        if entry.get("status") != "open":
            continue
        register_id = entry.get("entry_id")
        if not register_id:
            continue
        reconciled.append(
            {
                "register_id": register_id,
                "post_refresh_status": "still_open",
                "rationale": rationale,
            }
        )
    return reconciled


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
        "open_questions_reconciled": open_questions_reconciled(
            paths,
            "Structural refresh updates file inventory only; existing open questions remain open until an interpretive refresh or reviewer resolves them.",
        ),
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


def refresh_replacement_claim(prior_kind: str, prior_claim: dict[str, Any], successors: dict[str, tuple[str, dict[str, Any]]]) -> dict[str, Any] | None:
    if prior_kind == "authority":
        for successor_kind, successor_claim in successors.values():
            if (
                successor_kind == "authority"
                and successor_claim.get("kind") == prior_claim.get("kind")
                and successor_claim.get("path") == prior_claim.get("path")
            ):
                return successor_claim
        return None
    prior_from = prior_claim.get("from", {})
    for successor_kind, successor_claim in successors.values():
        successor_from = successor_claim.get("from", {})
        if (
            successor_kind == "edge"
            and successor_claim.get("kind") == prior_claim.get("kind")
            and successor_claim.get("extractor_id") == prior_claim.get("extractor_id")
            and successor_from.get("path") == prior_from.get("path")
            and successor_from.get("symbol") == prior_from.get("symbol")
        ):
            return successor_claim
    return None


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

    for signature, (prior_kind, prior_claim) in sorted(prior_claims.items()):
        successor_entry = successor_claims.get(signature)
        if not successor_entry:
            replacement = refresh_replacement_claim(prior_kind, prior_claim, successor_claims)
            retracted_claim = {
                "claim_id": prior_claim["id"],
                "rationale": "No matching surface claim exists after differential refresh at current HEAD.",
            }
            if replacement:
                retracted_claim["superseded_by"] = replacement["id"]
            retracted.append(
                retracted_claim
            )
            for challenge in prior_claim.get("challenges", []):
                if replacement:
                    challenges_carried_forward.append(
                        {
                            "challenge_id": challenge["challenge_id"],
                            "post_refresh_status": "resolved_by_refresh",
                            "rationale": f"The challenged claim was replaced by successor claim {replacement['id']}.",
                        }
                    )
                    continue
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
        "open_questions_reconciled": open_questions_reconciled(
            paths,
            "Interpretive refresh did not resolve this open question automatically; it remains available for later review.",
        ),
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


def artifact_consult_freshness(repo: Path, artifact: Path) -> tuple[bool, list[dict[str, Any]]]:
    citations = artifact_citations(artifact)
    results = [verify_citation_at_head(repo, citation) for citation in citations]
    return bool(citations) and all(item["status"] == "still_grounded" for item in results), results


def consult_scan(repo: Path, question: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    tokens = tokenize_query(question)
    matches: list[dict[str, Any]] = []
    stale_matches: list[dict[str, Any]] = []
    for artifact in iter_research_artifacts(repo):
        try:
            data, body = load_artifact_frontmatter(artifact)
        except Exception:
            continue
        text = json.dumps(data, sort_keys=True).lower() + "\n" + body.lower()
        if not all(token in text for token in tokens):
            continue
        fresh, freshness_results = artifact_consult_freshness(repo, artifact)
        citations = artifact_citations(artifact)
        match = {
            "artifact": str(artifact.relative_to(repo)),
            "artifact_type": data.get("artifact_type"),
            "matched_terms": tokens,
            "citations": citations[:5],
        }
        challenged = []
        for claim in all_artifact_claims(data):
            claim_text = json.dumps(claim, sort_keys=True).lower()
            if not all(token in claim_text for token in tokens):
                continue
            challenges = live_challenges(claim)
            if claim.get("claim_status") in {"challenged", "contested"} and challenges:
                challenged.append(
                    {
                        "claim_id": claim["id"],
                        "claim_status": claim["claim_status"],
                        "challenge_ids": [challenge["challenge_id"] for challenge in challenges],
                    }
                )
        if challenged:
            match["live_challenges"] = challenged
        if fresh:
            matches.append(match)
        else:
            match["freshness"] = {
                "still_grounded": sum(1 for item in freshness_results if item["status"] == "still_grounded"),
                "needs_review": sum(1 for item in freshness_results if item["status"] == "needs_review"),
                "broken": sum(1 for item in freshness_results if item["status"] == "broken"),
            }
            stale_matches.append(match)
    return matches, stale_matches


def consult_matches(repo: Path, question: str) -> list[dict[str, Any]]:
    matches, _ = consult_scan(repo, question)
    return matches


def append_consultation_reuse_entries(repo: Path, consult_id: str, matches: list[dict[str, Any]]) -> None:
    for match in matches:
        artifact_path = repo / match["artifact"]
        try:
            data, body = load_artifact_frontmatter(artifact_path)
        except Exception:
            continue
        citation_claims = {citation: claim_id for citation, claim_id in citation_claim_pairs(data)}
        for citation in extract_citations(body):
            citation_claims.setdefault(citation, "artifact")
        rel_parts = artifact_path.relative_to(repo).parts
        if len(rel_parts) < 3 or rel_parts[0] != ".research":
            continue
        run_id = rel_parts[1]
        ledger_path = repo / ".research" / run_id / "evidence-ledger.jsonl"
        if not ledger_path.exists():
            continue
        for citation in match["citations"]:
            entry = {
                "schema_version": SCHEMA_VERSION,
                "entry_id": next_ledger_id(ledger_path),
                "ts": utc_now(),
                "entry_kind": "citation_reused",
                "agent": "cbm-consult",
                "skill_version": "0.1",
                "run_id": run_id,
                "source_sha": data.get("source_sha", source_sha(repo)),
                "citation": citation,
                "artifact_path": match["artifact"],
                "claim_id": citation_claims.get(citation, f"consultation:{consult_id}"),
            }
            append_ledger_entry(repo, ledger_path, entry)


def next_uncertainty_id(path: Path) -> str:
    highest = 0
    for entry in read_jsonl(path):
        entry_id = entry.get("entry_id")
        if isinstance(entry_id, str) and entry_id.startswith("unc-"):
            try:
                highest = max(highest, int(entry_id.removeprefix("unc-")))
            except ValueError:
                continue
    return f"unc-{highest + 1:05d}"


def append_consultation_uncertainty(repo: Path, consult_id: str, question: str) -> None:
    try:
        paths = run_paths(repo, None)
    except SystemExit:
        return
    uncertainty_path = paths.run_dir / "uncertainty-register.jsonl"
    ledger_path = paths.run_dir / "evidence-ledger.jsonl"
    if not ledger_path.exists():
        return
    sha = source_sha(repo)
    now = utc_now()
    uncertainty_id = next_uncertainty_id(uncertainty_path)
    uncertainty = {
        "schema_version": SCHEMA_VERSION,
        "entry_id": uncertainty_id,
        "ts": now,
        "run_id": paths.run_id,
        "source_sha": sha,
        "question": f"Consultation question could not be answered from fresh corpus artifacts: {question}",
        "status": "open",
        "registered_by": "cbm-consult@0.1",
        "consultation_id": consult_id,
    }
    append_uncertainty_entry(uncertainty_path, uncertainty)
    entry = {
        "schema_version": SCHEMA_VERSION,
        "entry_id": next_ledger_id(ledger_path),
        "ts": now,
        "entry_kind": "uncertainty_logged",
        "agent": "cbm-consult",
        "skill_version": "0.1",
        "run_id": paths.run_id,
        "source_sha": sha,
        "artifact_path": str(uncertainty_path.relative_to(repo)),
        "claim_id": uncertainty_id,
    }
    append_ledger_entry(repo, ledger_path, entry)


def command_consult(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    matches, stale_matches = consult_scan(repo, args.question)
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
            line = f"- `{match['artifact']}` ({match['artifact_type']}): {citation_text}"
            if match.get("live_challenges"):
                challenge_ids = [
                    challenge_id
                    for challenged in match["live_challenges"]
                    for challenge_id in challenged["challenge_ids"]
                ]
                line += f" Live challenges: {', '.join(challenge_ids)}."
            lines.append(line)
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        append_consultation_reuse_entries(repo, consult_id, matches)
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
                "refusal_reason": "stale_corpus_match" if stale_matches else "no_grounded_match",
                "matches": [],
                "stale_matches": stale_matches,
            },
            sort_keys=False,
        )
        + (
            "---\n# Consultation\n\n"
            "Refusal: matching corpus artifacts exist, but their cited source bytes changed at HEAD. Run `cbm-refresh` or re-run before consulting this question.\n"
            if stale_matches
            else "---\n# Consultation\n\nRefusal: no fresh artifact in the corpus contains enough grounded evidence to answer this question.\n"
        ),
        encoding="utf-8",
    )
    try:
        append_consultation_uncertainty(repo, consult_id, args.question)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(output_path)
    return 2


def safe_relpath(base: Path, target: Path) -> str | None:
    try:
        return target.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return None


def sanitize_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-") or "gate"


def sanitize_slug(value: str, max_len: int = 48) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return (slug[:max_len].strip("-") or "checkpoint")


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


def codex_cli_surface_output_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": ["surface_map_json", "notes"],
        "properties": {
            "surface_map_json": {"type": "string", "minLength": 2},
            "notes": {"type": "string"},
        },
    }


def codex_cli_smoke_output_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": ["body", "findings_logged", "challenge_ids"],
        "properties": {
            "body": {"type": "string", "minLength": 1},
            "findings_logged": {"type": "integer", "minimum": 0},
            "challenge_ids": {
                "type": "array",
                "items": {"type": "string", "pattern": "^chl-[0-9]{5,}$"},
            },
        },
    }


def codex_cli_skill_skeptic_output_schema() -> dict[str, Any]:
    schema = codex_cli_smoke_output_schema()
    schema["required"] = [*schema["required"], "factual_spot_checks", "interpretive_challenges_attempted", "challenges"]
    schema["properties"] = {
        **schema["properties"],
        "factual_spot_checks": {"type": "integer", "minimum": 0},
        "interpretive_challenges_attempted": {"type": "integer", "minimum": 0},
        "challenges": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "claim_id",
                    "competing_reading",
                    "competing_evidence",
                    "interpretive_axis",
                    "relation_to_original",
                    "rationale",
                ],
                "properties": {
                    "claim_id": {"type": "string", "minLength": 1},
                    "competing_reading": {"type": "string", "minLength": 20},
                    "competing_evidence": {
                        "type": "array",
                        "minItems": 1,
                        "items": {"type": "string", "pattern": r"^[^`:',#@\s]+:\d+(?:-\d+)?@[0-9a-f]{7,40}$"},
                    },
                    "interpretive_axis": {"enum": ["centrality", "scope", "salience", "classification", "framing", "completeness", "other"]},
                    "relation_to_original": {"enum": ["complementary", "competing", "reframing", "scope_dispute"]},
                    "rationale": {"type": "string", "minLength": 1},
                },
            },
        },
    }
    return schema


def parse_json_object_output(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    data = json.loads(stripped)
    if not isinstance(data, dict):
        raise ValueError("Codex smoke output must be a JSON object")
    return data


def codex_cli_surface_output_path(repo: Path, run_id: str) -> Path:
    return repo / ".research" / run_id / "codex-cli-surface-output.json"


def codex_cli_surface_schema_path(repo: Path, run_id: str) -> Path:
    return repo / ".research" / run_id / "codex-cli-surface-output.schema.json"


def validate_json_with_schema(data: Any, schema: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema)
    return [f"{'/'.join(str(p) for p in error.absolute_path) or '<root>'}: {error.message}" for error in validator.iter_errors(data)]


def codex_cli_reasoning_config(reasoning_effort: str) -> str:
    return f'model_reasoning_effort="{reasoning_effort}"'


def codex_cli_approval_config() -> str:
    return 'approval_policy="never"'


def codex_cli_smoke_command_display(codex_command: str, repo: Path, run_id: str, model: str, reasoning_effort: str) -> str:
    run_dir = repo / ".research" / run_id
    output_path = run_dir / "codex-cli-smoke-output.json"
    output_schema_path = run_dir / "codex-cli-smoke-output.schema.json"
    return " ".join(
        [
            codex_command,
            "exec",
            "-m",
            model,
            "-c",
            codex_cli_reasoning_config(reasoning_effort),
            "-c",
            codex_cli_approval_config(),
            "--ephemeral",
            "--ignore-user-config",
            "--ignore-rules",
            "-C",
            str(repo),
            "-s",
            "read-only",
            "--json",
            "-o",
            str(output_path),
            "--output-schema",
            str(output_schema_path),
            "-",
        ]
    )


def codex_cli_surface_command_display(codex_command: str, repo: Path, run_id: str, model: str, reasoning_effort: str) -> str:
    output_path = codex_cli_surface_output_path(repo, run_id)
    output_schema_path = codex_cli_surface_schema_path(repo, run_id)
    return " ".join(
        [
            codex_command,
            "exec",
            "-m",
            model,
            "-c",
            codex_cli_reasoning_config(reasoning_effort),
            "-c",
            codex_cli_approval_config(),
            "--ephemeral",
            "--ignore-user-config",
            "--ignore-rules",
            "-C",
            str(repo),
            "-s",
            "read-only",
            "--json",
            "-o",
            str(output_path),
            "--output-schema",
            str(output_schema_path),
            "-",
        ]
    )


def codex_cli_surface_prompt(skill: LoadedSkill, repo: Path, paths: RunPaths, citation: str) -> str:
    codebase_path = paths.run_dir / "codebase-map.json"
    intake_path = paths.run_dir / "intake.json"
    state_path = paths.run_dir / "state.json"
    registry_path = paths.run_dir / "extractor-registry.json"
    return (
        "You are a CBM runtime Surface Mapper producer. Use the runtime skill below as your governing procedure. "
        "Read the CBM baseline artifacts and directly inspect the source files needed for any interpretive claim you make. "
        "Return JSON matching the supplied schema. The `surface_map_json` field must be a string containing one complete JSON object for the surface map. The parent process will parse that string and validate the object against `schemas/surface-map.schema.json`, "
        "verify every citation against source bytes at the recorded SHA, reject baseline/dev-fixture producer identities, and reject zero direct file examination for this producer. "
        "The surface map must use `produced_by: surface-mapper@1.2`, `artifact_type: surface_map`, the exact run id and source SHA below, and source citations only in `path:line@sha` or `path:start-end@sha` form. "
        "Do not cite `.research/` artifacts as claim evidence. In `inputs`, include the four CBM input artifacts and their sha256 values shown below. "
        "Keep coverage honest: `files_examined_directly` is the number of source files you opened and read; `files_inspected_via_extractor` is the baseline extractor count; `files_unread_in_scope` is the remaining in-scope count.\n\n"
        "Schema-critical checklist before you answer:\n"
        "- Top-level surface map requires `status: \"draft\"`, `staleness`, `coverage.result.files_in_scope`, `coverage.result.files_examined_directly`, `coverage.result.files_inspected_via_extractor`, and `coverage.result.files_unread_in_scope`.\n"
        "- Authority `kind` must be one of: routing, config, schema, policy, registry, build, ci_gate, test_suite, doc_contract, other. Use `test_suite`, not `test`; use `doc_contract`, not `doc`.\n"
        "- Every edge, including `kind: \"unknown\"`, must include `claim_register`, `claim_status`, `evidence_kinds`, `corroboration_count`, and `confidence`; low or medium confidence edges also need `rationale`.\n"
        "- Include at least one explicit unknown edge with `kind: \"unknown\"`; the id may be producer-specific and must not be used as an acceptance condition.\n"
        "- Do not set `claim_status` to challenged/contested/contradicted unless you also include the required `challenges` or `contradicted_by` fields. Prefer `claim_status: \"active\"` for this first map.\n"
        "- `verification` must contain exactly `tests`, `ci_gates`, and `coverage_summary`. Each test exercise must use `target_path`, optional `target_symbol`, `citations`, `claim_register`, and `evidence_kinds`; do not use `target` or `symbol` keys.\n\n"
        f"Runtime skill: {skill.name}\n"
        f"Runtime skill path: {skill.path}\n"
        f"Runtime skill sha256: {skill.sha256}\n\n"
        "<runtime_skill>\n"
        f"{skill.body}\n"
        "</runtime_skill>\n\n"
        f"Repository: {repo}\n"
        f"Run id: {paths.run_id}\n"
        f"Source sha: {source_sha(repo)}\n"
        f"Codebase map input: {codebase_path.relative_to(repo)} sha256={sha256_file(codebase_path)}\n"
        f"Intake input: {intake_path.relative_to(repo)} sha256={sha256_file(intake_path)}\n"
        f"State input: {state_path.relative_to(repo)} sha256={sha256_file(state_path)}\n"
        f"Extractor registry input: {registry_path.relative_to(repo)} sha256={sha256_file(registry_path)}\n"
        f"Required citation anchor available for format checking: {citation}\n"
    )


def codex_cli_surface_repair_prompt(original_prompt: str, rejected_output: str, errors: list[str]) -> str:
    return (
        original_prompt
        + "\n\n<parent_validation_errors>\n"
        + "\n".join(f"- {error}" for error in errors)
        + "\n</parent_validation_errors>\n\n"
        + "<rejected_output>\n"
        + rejected_output
        + "\n</rejected_output>\n\n"
        + "Return corrected JSON matching the same outer schema. Preserve source-grounded claims where possible, but fix every parent validation error. "
        "Do not explain outside the `notes` string. The `surface_map_json` value must parse as one complete schema-valid surface map object.\n"
    )


def codex_cli_skill_prompt(skill: LoadedSkill, repo: Path, paths: RunPaths, surface_path: Path, citation: str) -> str:
    return (
        "You are a CBM runtime Skeptic producer. Use the runtime skill below as your governing procedure. "
        "You may read the artifact under review, evidence ledger, uncertainty register, extractor registry, and source files needed to verify citations. "
        "Return JSON matching the supplied schema. The `body` field must be Markdown for the Skeptic review body and should include an Overall section plus any factual/inferential or interpretive challenges you can substantiate. "
        "For every challenge that should affect CBM contestation state, include a matching object in `challenges` with a claim_id from the reviewed artifact and resolving competing_evidence citations. "
        "`competing_evidence` must contain source citations only, formatted like `path/to/file.py:10-12@abcdef1`; do not put artifact JSON pointers or prose inside that array. "
        "Do not invent challenges. If no non-trivial challenge is defensible, explain why in the body and set challenge counts to 0 with an empty challenges array.\n\n"
        f"Runtime skill: {skill.name}\n"
        f"Runtime skill path: {skill.path}\n"
        f"Runtime skill sha256: {skill.sha256}\n\n"
        "<runtime_skill>\n"
        f"{skill.body}\n"
        "</runtime_skill>\n\n"
        f"Repository: {repo}\n"
        f"Run id: {paths.run_id}\n"
        f"Artifact under review: {surface_path.relative_to(repo)}\n"
        f"Required citation anchor available for spot-checking: {citation}\n"
    )


def surface_map_parent_validation_errors(repo: Path, paths: RunPaths, surface: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    sha = source_sha(repo)
    if surface.get("artifact_type") != "surface_map":
        errors.append("surface_map.artifact_type must be surface_map")
    if surface.get("run_id") != paths.run_id:
        errors.append(f"surface_map.run_id must be {paths.run_id}")
    surface_sha = str(surface.get("source_sha", ""))
    if not (surface_sha.startswith(sha) or sha.startswith(surface_sha)):
        errors.append(f"surface_map.source_sha must match current source sha {sha}")
    produced_by = str(surface.get("produced_by", ""))
    if produced_by != CODEX_CLI_SKILL_SURFACE_PRODUCER:
        errors.append(f"surface_map.produced_by must be {CODEX_CLI_SKILL_SURFACE_PRODUCER}")
    if is_baseline_like_producer(produced_by):
        errors.append("surface_map.produced_by must not be a baseline or dev-fixture producer")
    coverage_result = surface.get("coverage", {}).get("result", {})
    try:
        files_examined_directly = int(coverage_result.get("files_examined_directly", 0) or 0)
    except (TypeError, ValueError):
        files_examined_directly = 0
    if files_examined_directly < 1:
        errors.append("surface_map.coverage.result.files_examined_directly must be >= 1 for codex-cli Surface Mapper output")
    claim_registers = [
        claim.get("claim_register")
        for claim in [*surface.get("authorities", []), *surface.get("edges", [])]
        if isinstance(claim, dict)
    ]
    if not any(register in {"factual", "inferential", "interpretive"} for register in claim_registers):
        errors.append("surface_map must contain at least one factual, inferential, or interpretive claim")
    citations = sorted(set(extract_citations(surface)))
    if not citations:
        errors.append("surface_map must contain at least one source citation")
    if not any(isinstance(edge, dict) and edge.get("kind") == "unknown" for edge in surface.get("edges", [])):
        errors.append('surface_map.edges must include at least one edge where kind == unknown')
    for citation in citations:
        parts = citation_parts(citation)
        if not parts:
            errors.append(f"{citation}: invalid citation format")
            continue
        if parts["path"].startswith(".research/"):
            errors.append(f"{citation}: citations must point to source files, not .research artifacts")
        citation_sha = str(parts["sha"])
        if not (citation_sha.startswith(sha) or sha.startswith(citation_sha)):
            errors.append(f"{citation}: citation sha must match current source sha {sha}")
            continue
        ok, reason = resolve_citation(repo, citation)
        if not ok:
            errors.append(f"{citation}: {reason}")
    errors.extend(validate_data(repo, surface, "surface_map"))
    return errors


def command_codex_cli_surface_map(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    paths = run_paths(repo, args.run_id)
    codebase_path = paths.run_dir / "codebase-map.json"
    if not codebase_path.exists():
        print("codex-cli Surface Mapper requires codebase-map.json", file=sys.stderr)
        return 1
    sha = source_sha(repo)
    codebase_map = read_codebase_map(paths.run_dir)
    citation_path, citation_line = first_citable_file(repo, codebase_map, sha)
    citation = f"{citation_path}:{citation_line}@{sha}"
    output_schema_path = codex_cli_surface_schema_path(repo, paths.run_id)
    output_path = codex_cli_surface_output_path(repo, paths.run_id)
    output_schema = codex_cli_surface_output_schema()
    write_json(output_schema_path, output_schema)
    skill = load_skill("surface-mapping", repo)
    prompt = codex_cli_surface_prompt(skill, repo, paths, citation)
    command = [
        args.codex_command,
        "exec",
        "-m",
        args.codex_model,
        "-c",
        codex_cli_reasoning_config(args.codex_reasoning_effort),
        "-c",
        codex_cli_approval_config(),
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "-C",
        str(repo),
        "-s",
        "read-only",
        "--json",
        "-o",
        str(output_path),
        "--output-schema",
        str(output_schema_path),
        "-",
    ]
    step_id = "codex-cli-skill-surface-map"
    try:
        proc = subprocess.run(
            command,
            input=prompt,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=args.codex_timeout,
        )
    except subprocess.TimeoutExpired as exc:
        detail = f"codex-cli Surface Mapper timed out after {args.codex_timeout} seconds"
        output = subprocess_text(exc.output)
        stderr = subprocess_text(exc.stderr)
        partial_chunks = []
        if output:
            partial_chunks.append("[stdout]\n" + output.rstrip())
        if stderr:
            partial_chunks.append("[stderr]\n" + stderr.rstrip())
        if partial_chunks:
            partial_dir = paths.run_dir / "codex_outputs"
            partial_dir.mkdir(parents=True, exist_ok=True)
            partial_dir.joinpath(f"{step_id}.partial").write_text("\n\n".join(partial_chunks) + "\n", encoding="utf-8")
        if stderr:
            detail += f": {stderr.strip()}"
        elif output:
            detail += f": {output.strip()}"
        print(detail, file=sys.stderr)
        return INTERRUPTED_EXIT_CODE
    logs_dir = paths.run_dir / "logs"
    write_text_if_nonempty(logs_dir / f"{step_id}.stdout", proc.stdout)
    write_text_if_nonempty(logs_dir / f"{step_id}.stderr", proc.stderr)
    write_text_if_nonempty(logs_dir / f"{step_id}.attempt-1.stdout", proc.stdout)
    write_text_if_nonempty(logs_dir / f"{step_id}.attempt-1.stderr", proc.stderr)
    if proc.returncode != 0:
        detail = "codex-cli Surface Mapper failed"
        if proc.stderr:
            detail += f"; stderr logged at {(logs_dir / f'{step_id}.stderr').relative_to(repo)}"
        elif proc.stdout:
            detail += f"; stdout logged at {(logs_dir / f'{step_id}.stdout').relative_to(repo)}"
        print(detail, file=sys.stderr)
        return proc.returncode
    def parse_surface_output() -> tuple[dict[str, Any] | None, list[str]]:
        if not output_path.exists():
            return None, ["codex-cli Surface Mapper did not write output"]
        try:
            output = parse_json_object_output(output_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError) as exc:
            return None, [f"codex-cli Surface Mapper output invalid: {exc}"]
        output_errors = validate_json_with_schema(output, output_schema)
        if output_errors:
            return None, [f"codex-cli Surface Mapper output invalid {error}" for error in output_errors]
        try:
            surface_obj = json.loads(output["surface_map_json"])
        except (json.JSONDecodeError, TypeError) as exc:
            return None, [f"codex-cli Surface Mapper output invalid: surface_map_json must contain a JSON object: {exc}"]
        if not isinstance(surface_obj, dict):
            return None, ["codex-cli Surface Mapper output invalid: surface_map_json must contain a JSON object"]
        validation_errors = surface_map_parent_validation_errors(repo, paths, surface_obj)
        return surface_obj, validation_errors

    surface, errors = parse_surface_output()
    if errors and output_path.exists():
        rejected_text = output_path.read_text(encoding="utf-8")
        repair_dir = paths.run_dir / "codex_outputs"
        repair_dir.mkdir(parents=True, exist_ok=True)
        repair_dir.joinpath(f"{step_id}.rejected-1.json").write_text(rejected_text, encoding="utf-8")
        repair_prompt = codex_cli_surface_repair_prompt(prompt, rejected_text, errors)
        repair_dir.joinpath(f"{step_id}.repair-prompt-1.txt").write_text(repair_prompt, encoding="utf-8")
        try:
            repair_proc = subprocess.run(
                command,
                input=repair_prompt,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=args.codex_timeout,
            )
        except subprocess.TimeoutExpired as exc:
            detail = f"codex-cli Surface Mapper repair timed out after {args.codex_timeout} seconds"
            output = subprocess_text(exc.output)
            stderr = subprocess_text(exc.stderr)
            partial_chunks = []
            if output:
                partial_chunks.append("[stdout]\n" + output.rstrip())
            if stderr:
                partial_chunks.append("[stderr]\n" + stderr.rstrip())
            if partial_chunks:
                repair_dir.joinpath(f"{step_id}.repair.partial").write_text("\n\n".join(partial_chunks) + "\n", encoding="utf-8")
            print(detail, file=sys.stderr)
            return INTERRUPTED_EXIT_CODE
        if output_path.exists():
            repair_dir.joinpath(f"{step_id}.repair-output-1.json").write_text(output_path.read_text(encoding="utf-8"), encoding="utf-8")
        write_text_if_nonempty(logs_dir / f"{step_id}.repair-1.stdout", repair_proc.stdout)
        write_text_if_nonempty(logs_dir / f"{step_id}.repair-1.stderr", repair_proc.stderr)
        combined_stdout = "\n".join(part for part in [proc.stdout, "[repair attempt]\n" + repair_proc.stdout if repair_proc.stdout else ""] if part)
        combined_stderr = "\n".join(part for part in [proc.stderr, "[repair attempt]\n" + repair_proc.stderr if repair_proc.stderr else ""] if part)
        write_text_if_nonempty(logs_dir / f"{step_id}.stdout", combined_stdout)
        write_text_if_nonempty(logs_dir / f"{step_id}.stderr", combined_stderr)
        if repair_proc.returncode != 0:
            detail = "codex-cli Surface Mapper repair failed"
            if repair_proc.stderr:
                detail += f"; stderr logged at {(logs_dir / f'{step_id}.stderr').relative_to(repo)}"
            elif repair_proc.stdout:
                detail += f"; stdout logged at {(logs_dir / f'{step_id}.stdout').relative_to(repo)}"
            print(detail, file=sys.stderr)
            return repair_proc.returncode
        surface, errors = parse_surface_output()
    if errors:
        for error in errors:
            print(f"codex-cli Surface Mapper rejected output: {error}", file=sys.stderr)
        return 1
    assert surface is not None
    surface_path = paths.run_dir / "surface-map.json"
    try:
        append_citation_entries(
            repo,
            paths.run_dir / "evidence-ledger.jsonl",
            paths.run_id,
            sha,
            str(surface_path.relative_to(repo)),
            surface,
            CODEX_CLI_SKILL_SURFACE_PRODUCER,
        )
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    write_json(surface_path, surface)
    print(surface_path)
    return 0


def command_import_surface_artifact(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    paths = run_paths(repo, args.run_id)
    source_path = Path(args.surface_artifact).expanduser().resolve()
    if not source_path.exists():
        print(f"surface artifact not found: {source_path}", file=sys.stderr)
        return 1
    try:
        surface = read_json(source_path)
    except Exception as exc:
        print(f"surface artifact invalid JSON: {exc}", file=sys.stderr)
        return 1
    if surface.get("artifact_type") != "surface_map":
        print("surface artifact must have artifact_type surface_map", file=sys.stderr)
        return 1
    errors = validate_data(repo, surface, "surface_map")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    output_path = paths.run_dir / "surface-map.json"
    output_path.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")
    try:
        append_citation_entries(
            repo,
            paths.run_dir / "evidence-ledger.jsonl",
            paths.run_id,
            source_sha(repo),
            str(output_path.relative_to(repo)),
            surface,
            str(surface.get("produced_by", "surface-import")),
        )
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(output_path)
    return 0


def command_codex_cli_smoke_review(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    paths = run_paths(repo, args.run_id)
    surface_path = paths.run_dir / "surface-map.json"
    if not surface_path.exists():
        print("codex-cli smoke requires surface-map.json", file=sys.stderr)
        return 1
    sha = source_sha(repo)
    codebase_map = read_codebase_map(paths.run_dir)
    citation_path, citation_line = first_citable_file(repo, codebase_map, sha)
    citation = f"{citation_path}:{citation_line}@{sha}"
    output_schema_path = paths.run_dir / "codex-cli-smoke-output.schema.json"
    output_path = paths.run_dir / "codex-cli-smoke-output.json"
    skill = load_skill("skeptic", repo) if args.codex_skeptic_mode == "skill" else None
    output_schema = codex_cli_skill_skeptic_output_schema() if args.codex_skeptic_mode == "skill" else codex_cli_smoke_output_schema()
    write_json(output_schema_path, output_schema)
    if skill:
        prompt = codex_cli_skill_prompt(skill, repo, paths, surface_path, citation)
    else:
        prompt = (
            "You are a bounded CBM smoke reviewer. Read the existing surface-map.json only as an artifact under review. "
            "Return JSON matching the supplied schema. This smoke is not a full Skeptic pass; report findings_logged=0 "
            "unless the artifact is unreadable.\n\n"
            f"Repository: {repo}\n"
            f"Run id: {paths.run_id}\n"
            f"User goal/probe objective: {args.goal}\n"
            f"Artifact under review: {surface_path.relative_to(repo)}\n"
            f"Required citation anchor to include in your reasoning: {citation}\n"
        )
    command = [
        args.codex_command,
        "exec",
        "-m",
        args.codex_model,
        "-c",
        codex_cli_reasoning_config(args.codex_reasoning_effort),
        "-c",
        codex_cli_approval_config(),
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "-C",
        str(repo),
        "-s",
        "read-only",
        "--json",
        "-o",
        str(output_path),
        "--output-schema",
        str(output_schema_path),
        "-",
    ]
    try:
        proc = subprocess.run(
            command,
            input=prompt,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=args.codex_timeout,
        )
    except subprocess.TimeoutExpired as exc:
        detail = f"codex-cli smoke timed out after {args.codex_timeout} seconds"
        output = subprocess_text(exc.output)
        stderr = subprocess_text(exc.stderr)
        partial_chunks = []
        if output:
            partial_chunks.append("[stdout]\n" + output.rstrip())
        if stderr:
            partial_chunks.append("[stderr]\n" + stderr.rstrip())
        if partial_chunks:
            partial_dir = paths.run_dir / "codex_outputs"
            partial_dir.mkdir(parents=True, exist_ok=True)
            step_id = "codex-cli-skill-skeptic-review" if args.codex_skeptic_mode == "skill" else "codex-cli-smoke-skeptic-review"
            partial_dir.joinpath(f"{step_id}.partial").write_text("\n\n".join(partial_chunks) + "\n", encoding="utf-8")
        if stderr:
            detail += f": {stderr.strip()}"
        elif output:
            detail += f": {output.strip()}"
        print(detail, file=sys.stderr)
        return INTERRUPTED_EXIT_CODE
    step_id = "codex-cli-skill-skeptic-review" if args.codex_skeptic_mode == "skill" else "codex-cli-smoke-skeptic-review"
    logs_dir = paths.run_dir / "logs"
    write_text_if_nonempty(logs_dir / f"{step_id}.stdout", proc.stdout)
    write_text_if_nonempty(logs_dir / f"{step_id}.stderr", proc.stderr)
    if proc.returncode != 0:
        detail = "codex-cli smoke failed"
        if proc.stderr:
            detail += f"; stderr logged at {(logs_dir / f'{step_id}.stderr').relative_to(repo)}"
        elif proc.stdout:
            detail += f"; stdout logged at {(logs_dir / f'{step_id}.stdout').relative_to(repo)}"
        print(detail, file=sys.stderr)
        return proc.returncode
    if not output_path.exists():
        print("codex-cli smoke did not write output", file=sys.stderr)
        return 1
    try:
        output = parse_json_object_output(output_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"codex-cli smoke output invalid: {exc}", file=sys.stderr)
        return 1
    output_errors = validate_json_with_schema(output, output_schema)
    if output_errors:
        for error in output_errors:
            print(f"codex-cli smoke output invalid {error}", file=sys.stderr)
        return 1
    challenge_ids = list(output.get("challenge_ids", []))
    if skill:
        try:
            surface_data = read_json(surface_path)
            challenge_ids = apply_runtime_skeptic_challenges(
                repo,
                surface_path,
                surface_data,
                output,
                codex_cli_skeptic_producer_id(args.codex_skeptic_mode),
            )
        except ValueError as exc:
            print(exc, file=sys.stderr)
            return 1
    now = utc_now()
    frontmatter = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "skeptic_review",
        "run_id": paths.run_id,
        "produced_at": now,
        "produced_by": codex_cli_skeptic_producer_id(args.codex_skeptic_mode),
        "source_sha": sha,
        "artifact_reviewed": str(surface_path.relative_to(repo)),
        "findings_logged": int(output.get("findings_logged", 0)),
        "challenge_ids": challenge_ids,
    }
    errors = validate_data(repo, frontmatter, "skeptic_review")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    skeptic_path = paths.run_dir / "skeptic-review" / "surface-map.md"
    skeptic_path.parent.mkdir(parents=True, exist_ok=True)
    review_body = render_runtime_skeptic_body(output, challenge_ids, skill, citation)
    skeptic_path.write_text(
        "---\n"
        + yaml.safe_dump(frontmatter, sort_keys=False)
        + "---\n"
        + review_body,
        encoding="utf-8",
    )
    try:
        append_citation_entries(
            repo,
            paths.run_dir / "evidence-ledger.jsonl",
            paths.run_id,
            sha,
            str(skeptic_path.relative_to(repo)),
            {"frontmatter": frontmatter, "body": review_body},
            "codex-cli-skeptic" if skill else "codex-cli-smoke",
        )
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(skeptic_path)
    return 0


def validate_existing_skeptic_review(repo: Path, skeptic_path: Path) -> list[str]:
    try:
        frontmatter, _ = load_artifact_frontmatter(skeptic_path)
    except Exception as exc:
        return [str(exc)]
    return validate_data(repo, frontmatter, "skeptic_review")


def is_baseline_like_producer(produced_by: str | None) -> bool:
    return bool(produced_by and (produced_by.startswith("cbm-baseline-") or produced_by.startswith("dev-fixture-")))


def is_runtime_surface_map(surface: dict[str, Any]) -> bool:
    return surface.get("artifact_type") == "surface_map" and not is_baseline_like_producer(str(surface.get("produced_by", "")))


def is_real_skeptic_producer(produced_by: str | None) -> bool:
    return bool(produced_by and produced_by.startswith("skeptic@"))


def runtime_surface_summary(surface: dict[str, Any]) -> str:
    authorities = surface.get("authorities", [])
    edges = surface.get("edges", [])
    unknown_edges = [edge for edge in edges if isinstance(edge, dict) and edge.get("kind") == "unknown"]
    return (
        f"Runtime Surface Mapper output from {surface.get('produced_by')} with "
        f"{len(authorities)} authorities, {len(edges)} edges, and {len(unknown_edges)} unknown edge"
        f"{'' if len(unknown_edges) == 1 else 's'}."
    )


def render_card_title(card_type: str, produced_by: str) -> str:
    marker = "[BASELINE] " if is_baseline_like_producer(produced_by) else ""
    title = "Goal-Bound Intervention Card" if card_type == "intervention_card" else "Phase A Structural Finding"
    return f"# {marker}{title}"


def render_handoff_body(include_baseline_banner: bool, promoted_runtime_surface: bool = False) -> str:
    banner = f"> {BASELINE_BANNER_TEXT}\n\n" if include_baseline_banner else ""
    if promoted_runtime_surface:
        return (
            "# CBM Handoff\n\n"
            + banner
            + "CBM produced a draft handoff containing runtime Surface Mapper output; see frontmatter for producer identities, gate summary, coverage, and caveats.\n"
        )
    return "# CBM Handoff\n\n" + banner + "Phase A mechanical gates produced a draft handoff. See frontmatter for gate summary and caveats.\n"


def artifact_produced_by(repo: Path, artifact_path: Path) -> str:
    if artifact_path.suffix == ".json":
        try:
            return str(read_json(artifact_path).get("produced_by", ""))
        except Exception:
            return ""
    try:
        frontmatter, _ = load_artifact_frontmatter(artifact_path)
        return str(frontmatter.get("produced_by", ""))
    except Exception:
        return ""


def recommended_handoff_next_action(
    promoted_runtime_surface: bool,
    skeptic_artifacts_reviewed: int,
    contestation_summary: dict[str, Any],
    resolved_skeptic_challenges: int = 0,
) -> str:
    return render_recommended_handoff_next_action(
        recommended_handoff_next_action_kind(
            promoted_runtime_surface,
            skeptic_artifacts_reviewed,
            contestation_summary,
            resolved_skeptic_challenges,
        )
    )


def recommended_handoff_next_action_kind(
    promoted_runtime_surface: bool,
    skeptic_artifacts_reviewed: int,
    contestation_summary: dict[str, Any],
    resolved_skeptic_challenges: int = 0,
) -> str:
    if not promoted_runtime_surface:
        return "produce_runtime_surface_evidence"
    if skeptic_artifacts_reviewed == 0:
        return "run_skeptic_review"
    if contestation_summary.get("open_challenges", 0) > 0:
        return "respond_to_open_challenges"
    if contestation_summary.get("claims_by_status", {}).get("contested", 0) > 0:
        return "prepare_pass_claim_review"
    if resolved_skeptic_challenges > 0:
        return "prepare_pass_claim_review"
    if skeptic_artifacts_reviewed > 0:
        return "prepare_pass_claim_review"
    return "review_handoff"


def render_recommended_handoff_next_action(action_kind: str) -> str:
    if action_kind == "produce_runtime_surface_evidence":
        return "Produce or import a runtime Surface Mapper artifact before relying on this handoff for Skeptic review or pass-claim review."
    if action_kind == "run_skeptic_review":
        return "Run a real isolated Skeptic review before relying on this handoff for pass-claim review."
    if action_kind == "respond_to_open_challenges":
        return "Disposition the Skeptic challenge as accepted, revised, or unresolved contestation and carry the response into the handoff path."
    if action_kind == "prepare_pass_claim_review":
        return "Prepare a validated runtime handoff and non-current-model pass-claim review packet."
    return "Review the validated handoff and choose the next evidence step."


def handoff_includes_baseline_outputs(repo: Path, artifacts: list[dict[str, Any]]) -> bool:
    for artifact in artifacts:
        produced_by = artifact_produced_by(repo, repo / artifact["path"])
        if is_baseline_like_producer(produced_by):
            return True
    return False


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
        append_citation_entries(repo, paths.run_dir / "evidence-ledger.jsonl", paths.run_id, surface["source_sha"], str(surface_path.relative_to(repo)), surface, "cbm-baseline-surface")
        write_json(surface_path, surface)
    surface = read_json(surface_path)
    binding_path = paths.run_dir / "goal-binding.json"
    binding = read_json(binding_path) if binding_path.exists() else None
    selected_candidate = binding["candidates"][0] if binding and binding.get("candidates") else None
    handoff_goal = binding["goal"] if binding else intake["goal"]
    handoff_goal_class = binding["goal_class"] if binding else intake["goal_class"]
    handoff_research_only = binding["research_only"] if binding else intake["research_only"]
    card_type = selected_candidate.get("recommended_card_type", "findings_card") if selected_candidate else "findings_card"
    card_dir_name = "interventions" if card_type == "intervention_card" else "findings"
    card_summary = "Goal-bound intervention card." if card_type == "intervention_card" else "Goal-bound structural findings card."
    primary_authority = surface["authorities"][0]
    relation_edge_index = None
    relation_edge = None
    if selected_candidate and "/edges/" in selected_candidate["surface_ref"]:
        relation_edge_index = int(selected_candidate["surface_ref"].rsplit("/edges/", 1)[1])
        edge = surface["edges"][relation_edge_index]
        if edge["kind"] in {"import", "call"}:
            relation_edge = edge
    if relation_edge is None:
        relation_edge_index = next((index for index, edge in enumerate(surface["edges"]) if edge["kind"] in {"import", "call"}), None)
        relation_edge = surface["edges"][relation_edge_index] if relation_edge_index is not None else None
    if selected_candidate and "/authorities/" in selected_candidate["surface_ref"]:
        authority_index = int(selected_candidate["surface_ref"].rsplit("/authorities/", 1)[1])
        primary_authority = surface["authorities"][authority_index]
        if selected_candidate["surface_kind"] == "authority":
            relation_edge = None
            relation_edge_index = None
    if relation_edge:
        rel_file = relation_edge["from"]["path"]
        citation = relation_edge["citations"][0]
        relation_target = relation_edge["to"]["path"]
        if relation_edge["kind"] == "call":
            relation_target = f"{relation_target}::{relation_edge['to'].get('symbol', '<unknown>')}"
            primary_role = f"Calls {relation_target}; this grounded static relation is the selected goal-binding candidate."
        else:
            primary_role = f"Imports {relation_target}; this grounded static relation is the selected goal-binding candidate."
        certain_dependencies = [f".research/{paths.run_id}/surface-map.json#/edges/{relation_edge_index}", citation]
        leverage_rating = "medium"
        leverage_rationale = "A local relation edge gives a concrete, citation-backed relation to read next; leverage is bounded by the unresolved unknown dependency edge."
        recommended_next_slice = f"Read {relation_edge['from']['path']} and {relation_edge['to']['path']} around the cited {relation_edge['kind']}, then decide whether this relation represents setup, test coverage, or runtime coupling."
    else:
        rel_file = primary_authority["path"]
        citation = primary_authority["citations"][0]
        primary_role = f"Draft surface authority {primary_authority['id']} selected by goal binding."
        certain_dependencies = [citation]
        leverage_rating = "medium" if primary_authority["kind"] in {"config", "test_suite", "ci_gate"} else "low"
        leverage_rationale = "Phase A can identify structural surfaces, but leverage remains bounded by the Skeptic challenge on unknown dependency closure."
        recommended_next_slice = "Read the cited authority file and implement call or runtime workflow extraction before promoting this card beyond draft."
    card_dir = paths.run_dir / card_dir_name
    card_dir.mkdir(parents=True, exist_ok=True)
    card_path = card_dir / "int-0001.md"
    skeptic_dir = paths.run_dir / "skeptic-review"
    skeptic_dir.mkdir(parents=True, exist_ok=True)
    skeptic_path = skeptic_dir / "surface-map.md"
    ledger_path = paths.run_dir / "evidence-ledger.jsonl"
    uncertainty_path = paths.run_dir / "uncertainty-register.jsonl"
    uncertainty_append_only_ok, uncertainty_append_only_reason = verify_ledger_append_only(uncertainty_path, require_manifest=True)
    if not uncertainty_append_only_ok:
        print(f"uncertainty register append-only verification failed: {uncertainty_append_only_reason}", file=sys.stderr)
        return 1
    # Validate the surface BEFORE mutating any append-only ledger or
    # uncertainty register (F4 from Codex review): a validation failure
    # after the ledger writes leaves durable provenance pointing at a
    # finding card that was never written.
    unknown_edge = next((edge for edge in surface["edges"] if edge["kind"] == "unknown"), None)
    if unknown_edge is None:
        print("surface map is missing an edge with kind == unknown", file=sys.stderr)
        return 1
    errors = validate_data(repo, surface, "surface_map")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    evidence_errors = extractor_registry_errors_for_artifact(repo, surface)
    evidence_errors.extend(check_claim_evidence(surface, extractors_for_artifact(repo, surface)))
    if evidence_errors:
        for error in evidence_errors:
            print(f"evidence-fail {error}", file=sys.stderr)
        return 1
    # Validation passed; now commit ledger entries and write artifact.
    now = utc_now()
    citation_entry = {
        "schema_version": SCHEMA_VERSION,
        "entry_id": next_ledger_id(ledger_path),
        "ts": now,
        "entry_kind": "citation_introduced",
        "agent": "cbm-baseline-handoff",
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
        "registered_by": "cbm-baseline-handoff@0.1",
    }
    try:
        append_uncertainty_entry(uncertainty_path, uncertainty)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    uncertainty_entry = {
        "schema_version": SCHEMA_VERSION,
        "entry_id": next_ledger_id(ledger_path),
        "ts": now,
        "entry_kind": "uncertainty_logged",
        "agent": "cbm-baseline-handoff",
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
    write_json(surface_path, surface)
    if skeptic_path.exists():
        review_errors = validate_existing_skeptic_review(repo, skeptic_path)
        if review_errors:
            for error in review_errors:
                print(f"skeptic-review invalid {error}", file=sys.stderr)
            return 1
    else:
        skeptic_path.write_text(
            "---\n"
            + yaml.safe_dump(
                {
                    "schema_version": SCHEMA_VERSION,
                    "artifact_type": "skeptic_review",
                    "run_id": paths.run_id,
                    "produced_at": now,
                    "produced_by": "dev-fixture-skeptic@0.1",
                    "source_sha": sha,
                    "artifact_reviewed": str(surface_path.relative_to(repo)),
                    "findings_logged": 0,
                    "challenge_ids": [],
                },
                sort_keys=False,
            )
            + "---\n# Skeptic Review\n\nNo runtime Skeptic ran for this deterministic baseline handoff. The unknown dependency edge remains active for a real isolated Skeptic.\n\n"
            + f"Reviewed artifact evidence: {citation}\n",
            encoding="utf-8",
        )
    dependent_challenges = []
    selected_claim = relation_edge if relation_edge else primary_authority
    selected_challenges = live_challenges(selected_claim)
    if selected_claim.get("kind") != "unknown" and selected_challenges:
        dependent_challenges.append(
            {
                "claim_artifact": f".research/{paths.run_id}/surface-map.json",
                "claim_id": selected_claim["id"],
                "challenge_ids": [challenge["challenge_id"] for challenge in selected_challenges],
                "impact": "The selected goal-binding surface has live contestation, so downstream planning must preserve the competing reading.",
            }
        )
    card_confidence = "low"
    if selected_challenges:
        selected_ids = ", ".join(challenge["challenge_id"] for challenge in selected_challenges)
        confidence_rationale = (
            "Confidence is low because the selected goal-bound surface has live challenge(s) "
            f"{selected_ids}, and dependency closure remains unknown at {unknown_edge['id']}."
        )
    else:
        confidence_rationale = f"Confidence is low because dependency closure remains unknown at {unknown_edge['id']}."
    card_inputs = [{"path": str(surface_path.relative_to(repo)), "sha256": sha256_file(surface_path)}]
    if binding_path.exists():
        card_inputs.append({"path": str(binding_path.relative_to(repo)), "sha256": sha256_file(binding_path)})
    card_frontmatter = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": card_type,
        "run_id": paths.run_id,
        "produced_at": now,
        "produced_by": "dev-fixture-planner@0.1",
        "source_sha": sha,
        "inputs": card_inputs,
        "status": "draft",
        "coverage": coverage_block(codebase_map["coverage"]["result"]["files_in_scope"], examined=1),
        "staleness": {"stale_if_input_hash_changes": True, "depends_on_paths": [rel_file]},
        "id": f"int-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}-001",
        "goal": handoff_goal,
        "goal_class": handoff_goal_class,
        "research_only": handoff_research_only,
        "surface_type": "explicit",
        "surface_kind": "other",
        "surface_classification_register": "interpretive",
        "primary_files": [{"path": rel_file, "role": primary_role, "citations": [citation]}],
        "related_dependencies": {"certain": certain_dependencies, "suspected": [], "advisory": [], "unknown": [f".research/{paths.run_id}/surface-map.json#/edges/{surface['edges'].index(unknown_edge)}"]},
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
            "hard_gates": [{"description": "Schema validation, citation resolution, evidence requirements, and contestation propagation pass for this card.", "implementation": "Run cbm-gate-artifact on the generated findings card.", "citations": [citation]}],
            "warning_gates": [],
            "advisory_checks": [{"description": "Runtime Surface Mapper should replace this Phase A structural card with a role-specific finding."}],
            "manual_review": [{"description": "Confirm the first structural file is relevant to the user's actual goal before acting on it.", "reviewer_role": "senior engineer"}],
        },
        "risks": [{"description": "This Phase A generated card is structural and may not identify the highest-leverage surface.", "severity": "medium", "mitigation": "Run the runtime Surface Mapper and Skeptic before using the card for implementation decisions."}],
        "confidence": card_confidence,
        "confidence_rationale": confidence_rationale,
        "open_questions": [{"question": "Which code surface actually matters most for the user's goal?", "register_id": "unc-00001"}],
        "dependent_challenges": dependent_challenges,
        "recommended_next_slice": recommended_next_slice,
        "claim_status": "active",
    }
    card_errors = validate_data(repo, card_frontmatter, card_type)
    if card_errors:
        for error in card_errors:
            print(error, file=sys.stderr)
        return 1
    card_contestation = verify_contestation_propagation(repo, card_frontmatter)
    card_confidence_check = verify_card_confidence(card_frontmatter)
    card_coverage_check = verify_card_coverage_honesty(card_frontmatter)
    if card_contestation["missing"] or card_contestation["stale"]:
        for item in card_contestation["missing"]:
            print(
                "card-gate-fail missing dependent challenge "
                f"{item['claim_artifact']} {item['claim_id']} {','.join(item['missing_challenge_ids'])}",
                file=sys.stderr,
            )
        for item in card_contestation["stale"]:
            stale_ids = ",".join(item.get("stale_challenge_ids", []))
            suffix = f" {stale_ids}" if stale_ids else ""
            print(f"card-gate-fail stale dependent challenge {item['claim_artifact']} {item['claim_id']}{suffix}", file=sys.stderr)
        return 1
    if card_confidence_check["violations"]:
        for item in card_confidence_check["violations"]:
            print(f"card-gate-fail confidence {item['field']}: {item['reason']}", file=sys.stderr)
        return 1
    if card_coverage_check["violations"]:
        for item in card_coverage_check["violations"]:
            print(f"card-gate-fail coverage {item['field']}: {item['reason']}", file=sys.stderr)
        return 1
    card_title = render_card_title(card_type, card_frontmatter["produced_by"])
    if card_type == "intervention_card":
        card_body = f"\n{card_title}\n\nThis generated card carries the selected goal pack into a draft intervention artifact while preserving schema validation and citation resolution gates.\n"
    else:
        card_body = f"\n{card_title}\n\nThis generated card proves the mechanical gates are wired: schema validation and citation resolution operate on an evidence-bound artifact.\n"
    card_path.write_text("---\n" + yaml.safe_dump(card_frontmatter, sort_keys=False) + "---\n" + card_body, encoding="utf-8")
    append_citation_entries(repo, ledger_path, paths.run_id, sha, str(card_path.relative_to(repo)), card_frontmatter, "dev-fixture-planner")
    promoted_runtime_surface = is_runtime_surface_map(surface)
    surface_summary = (
        runtime_surface_summary(surface)
        if promoted_runtime_surface
        else "Draft deterministic surface map with explicit unknown dependency edge."
    )
    artifacts = [
        {"path": str((paths.run_dir / "codebase-map.json").relative_to(repo)), "artifact_type": "codebase_map", "status": "draft", "summary": "Deterministic structural file inventory."},
        {"path": str(surface_path.relative_to(repo)), "artifact_type": "surface_map", "status": "draft", "summary": surface_summary},
        {"path": str(card_path.relative_to(repo)), "artifact_type": card_type, "status": "draft", "summary": card_summary},
    ]
    handoff_inputs = [
        {"path": str(surface_path.relative_to(repo)), "sha256": sha256_file(surface_path)},
        {"path": str(card_path.relative_to(repo)), "sha256": sha256_file(card_path)},
    ]
    skeptic_produced_by = artifact_produced_by(repo, skeptic_path) if skeptic_path.exists() else ""
    if is_real_skeptic_producer(skeptic_produced_by):
        artifacts.append({"path": str(skeptic_path.relative_to(repo)), "artifact_type": "skeptic_review", "status": "draft", "summary": "Runtime Skeptic review output."})
        handoff_inputs.append({"path": str(skeptic_path.relative_to(repo)), "sha256": sha256_file(skeptic_path)})
    if binding_path.exists():
        artifacts.insert(2, {"path": str(binding_path.relative_to(repo)), "artifact_type": "goal_binding", "status": "draft", "summary": "Goal-specific candidate binding over the surface map."})
        handoff_inputs.insert(1, {"path": str(binding_path.relative_to(repo)), "sha256": sha256_file(binding_path)})
    project_type_path = paths.run_dir / "project-type.json"
    if project_type_path.exists():
        artifacts.insert(1, {"path": str(project_type_path.relative_to(repo)), "artifact_type": "project_type_report", "status": "draft", "summary": "Phase 0 project-type detection report."})
        handoff_inputs.insert(1, {"path": str(project_type_path.relative_to(repo)), "sha256": sha256_file(project_type_path)})
    trace_paths = sorted((paths.run_dir / "workflow-traces").glob("*.json")) if (paths.run_dir / "workflow-traces").exists() else []
    for trace_path in trace_paths:
        artifacts.insert(-1, {"path": str(trace_path.relative_to(repo)), "artifact_type": "workflow_trace", "status": "draft", "summary": "Deep-mode static workflow trace."})
        handoff_inputs.insert(-1, {"path": str(trace_path.relative_to(repo)), "sha256": sha256_file(trace_path)})
    refinement_paths = sorted((paths.run_dir / "refinements").glob("*.json")) if (paths.run_dir / "refinements").exists() else []
    for refinement_path in refinement_paths:
        artifacts.insert(-1, {"path": str(refinement_path.relative_to(repo)), "artifact_type": "refinement_report", "status": "draft", "summary": "Deep-mode refinement disposition report."})
        handoff_inputs.insert(-1, {"path": str(refinement_path.relative_to(repo)), "sha256": sha256_file(refinement_path)})
    approval_path = paths.run_dir / "approvals" / "approval-plan.json"
    if approval_path.exists():
        artifacts.insert(-1, {"path": str(approval_path.relative_to(repo)), "artifact_type": "approval_plan", "status": "draft", "summary": "Deep-mode manual approval plan."})
        handoff_inputs.insert(-1, {"path": str(approval_path.relative_to(repo)), "sha256": sha256_file(approval_path)})
    citation_resolution = artifact_bundle_citation_resolution(repo, artifacts)
    missing_ledger_citations = sorted(citation_resolution["citations"] - ledger_citations(ledger_path))
    ledger_append_only_ok, ledger_append_only_reason = verify_ledger_append_only(ledger_path, require_manifest=True)
    claim_refs = [(str(surface_path.relative_to(repo)), claim) for claim in all_artifact_claims(surface)]
    for split_path in [paths.run_dir / "authority-map.json", paths.run_dir / "dependency-graph.json"]:
        if split_path.exists():
            split_data = read_json(split_path)
            claim_refs.extend((str(split_path.relative_to(repo)), claim) for claim in all_artifact_claims(split_data))
    contestation_summary = contestation_summary_for_claim_refs(claim_refs)
    challenge_count = sum(len(live_challenges(claim)) for _, claim in claim_refs)
    resolved_challenge_count = sum(len(resolved_challenges(claim)) for _, claim in claim_refs)
    skeptic_artifacts_reviewed = sum(
        1
        for artifact in artifacts
        if artifact["artifact_type"] == "skeptic_review" and is_real_skeptic_producer(artifact_produced_by(repo, repo / artifact["path"]))
    )
    failed_artifacts = []
    for artifact in artifacts:
        artifact_path = repo / artifact["path"]
        try:
            artifact_data, _ = load_artifact_frontmatter(artifact_path)
            artifact_errors = validate_data(repo, artifact_data, artifact["artifact_type"])
        except Exception as exc:
            artifact_errors = [str(exc)]
        if artifact_errors:
            failed_artifacts.append(f"{artifact['path']}: {'; '.join(artifact_errors)}")
    handoff_coverage = surface.get("coverage", coverage_block(codebase_map["coverage"]["result"]["files_in_scope"], examined=1)) if promoted_runtime_surface else coverage_block(codebase_map["coverage"]["result"]["files_in_scope"], examined=1)
    runtime_coverage_caveats = list(surface.get("coverage", {}).get("limitations", [])) if promoted_runtime_surface else []
    next_action_kind = recommended_handoff_next_action_kind(
        promoted_runtime_surface,
        skeptic_artifacts_reviewed,
        contestation_summary,
        resolved_challenge_count,
    )
    handoff = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": "handoff",
        "run_id": paths.run_id,
        "produced_at": utc_now(),
        "produced_by": "cbm-baseline-handoff@0.1",
        "source_sha": sha,
        "inputs": handoff_inputs,
        "status": "draft",
        "coverage": handoff_coverage,
        "mode": intake["mode"],
        "user_goal": handoff_goal,
        "goal_class": handoff_goal_class,
        "research_only": handoff_research_only,
        "gate_summary": {
            "schema_validation": {"passed": len(artifacts) - len(failed_artifacts), "failed_artifacts": failed_artifacts},
            "citation_resolution": {
                "resolved": citation_resolution["resolved"],
                "unresolved_count": citation_resolution["unresolved_count"],
                "unresolved_examples": citation_resolution["unresolved_examples"],
            },
            "ledger_consistency": {
                "append_only_verified": ledger_append_only_ok and not missing_ledger_citations,
                "entry_count": ledger_count(ledger_path),
                "missing_citation_count": len(missing_ledger_citations),
                "missing_citation_examples": missing_ledger_citations[:5],
            },
            "staleness_check": input_staleness(repo, handoff_inputs),
            "skeptic_review": {"artifacts_reviewed": skeptic_artifacts_reviewed, "challenges_logged": challenge_count, "challenges_resolved": resolved_challenge_count},
        },
        "contestation_summary": contestation_summary,
        "artifacts": artifacts,
        "open_questions_count": 1,
        "coverage_caveats": runtime_coverage_caveats
        if promoted_runtime_surface and runtime_coverage_caveats
        else coverage_caveats(handoff_coverage)
        + ([] if promoted_runtime_surface else ["Phase A surface mapping is deterministic and has not performed language-level import/call extraction."]),
        "recommended_next_action_kind": next_action_kind,
        "recommended_next_action": render_recommended_handoff_next_action(next_action_kind),
    }
    errors = validate_data(repo, handoff, "handoff")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    write_json(paths.run_dir / "handoff.json", handoff)
    include_baseline_banner = handoff_includes_baseline_outputs(repo, artifacts)
    (paths.run_dir / "handoff.md").write_text(
        "---\n" + yaml.safe_dump(handoff, sort_keys=False) + "---\n" + render_handoff_body(include_baseline_banner, promoted_runtime_surface),
        encoding="utf-8",
    )
    print(paths.run_dir / "handoff.md")
    if failed_artifacts:
        print("artifact schema validation failed: " + "; ".join(failed_artifacts), file=sys.stderr)
        return 1
    if not ledger_append_only_ok:
        print(f"ledger append-only verification failed: {ledger_append_only_reason}", file=sys.stderr)
        return 1
    if missing_ledger_citations:
        print("missing ledger citations: " + ", ".join(missing_ledger_citations), file=sys.stderr)
        return 1
    return 0 if citation_resolution["unresolved_count"] == 0 else 1


def command_run(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    run_id = args.run_id or f"run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{source_sha(repo)}"
    paths = run_paths(repo, run_id)
    paths.run_dir.mkdir(parents=True, exist_ok=True)
    surface_artifact = Path(args.surface_artifact).expanduser().resolve() if getattr(args, "surface_artifact", None) else None
    if args.codex_surface_mode == "existing" and not surface_artifact:
        print("--codex-surface-mode existing requires --surface-artifact", file=sys.stderr)
        return 1
    existing_surface_producer = surface_artifact_producer_id(surface_artifact)
    write_json(
        paths.run_dir / "producer-registry.json",
        build_producer_registry(args.backend, args.codex_skeptic_mode, args.codex_surface_mode, existing_surface_producer),
    )
    if args.backend == "external" or (args.backend == "codex-cli" and not args.allow_live_codex):
        manifest = build_run_manifest(args, repo, run_id, "refused", [])
        write_json(paths.run_dir / "run-manifest.json", manifest)
        print(refusal_reason(args), file=sys.stderr)
        return 2
    init_args = argparse.Namespace(
        repo=str(repo),
        goal=args.goal,
        goal_class=args.goal_class,
        mode=args.mode,
        run_id=run_id,
        backend=args.backend,
        codex_skeptic_mode=args.codex_skeptic_mode,
        codex_surface_mode=args.codex_surface_mode,
    )
    map_args = argparse.Namespace(repo=str(repo), run_id=run_id)
    commands = [
        (run_manifest_step("init", "init", "project_type_report", DETERMINISTIC_PRODUCERS["project_type_report"]), command_init, init_args),
        (run_manifest_step("map", "map", "codebase_map", DETERMINISTIC_PRODUCERS["codebase_map"]), command_map, map_args),
    ]
    if args.backend == "codex-cli" and args.codex_surface_mode == "skill":
        surface_skill = load_skill("surface-mapping", repo)
        commands.append(
            (
                run_manifest_step(
                    "codex-cli-skill-surface-map",
                    codex_cli_surface_command_display(args.codex_command, repo, run_id, args.codex_model, args.codex_reasoning_effort),
                    "surface_map",
                    CODEX_CLI_SKILL_SURFACE_PRODUCER,
                    backend="codex-cli",
                    skill=skill_manifest(surface_skill),
                ),
                command_codex_cli_surface_map,
                argparse.Namespace(
                    repo=str(repo),
                    run_id=run_id,
                    codex_command=args.codex_command,
                    codex_model=args.codex_model,
                    codex_reasoning_effort=args.codex_reasoning_effort,
                    codex_timeout=args.codex_timeout,
                ),
            )
        )
    elif args.backend == "codex-cli" and args.codex_surface_mode == "existing":
        assert surface_artifact is not None
        commands.append(
            (
                run_manifest_step(
                    "import-surface-artifact",
                    f"import-surface-artifact {surface_artifact}",
                    "surface_map",
                    existing_surface_producer or CODEX_CLI_SKILL_SURFACE_PRODUCER,
                    backend="deterministic",
                )
                | {
                    "input_path": str(surface_artifact),
                    "input_sha256": sha256_file(surface_artifact),
                    "output_path": str((paths.run_dir / "surface-map.json").relative_to(repo)),
                },
                command_import_surface_artifact,
                argparse.Namespace(repo=str(repo), run_id=run_id, surface_artifact=str(surface_artifact)),
            )
        )
    else:
        commands.append((run_manifest_step("surface", "surface", "surface_map", DETERMINISTIC_PRODUCERS["surface_map"]), command_surface, map_args))
    if args.backend == "codex-cli" and args.codex_skeptic_mode != "none":
        skill = load_skill("skeptic", repo) if args.codex_skeptic_mode == "skill" else None
        commands.append(
            (
                run_manifest_step(
                    "codex-cli-skill-skeptic-review" if args.codex_skeptic_mode == "skill" else "codex-cli-smoke-skeptic-review",
                    codex_cli_smoke_command_display(args.codex_command, repo, run_id, args.codex_model, args.codex_reasoning_effort),
                    "skeptic_review",
                    codex_cli_skeptic_producer_id(args.codex_skeptic_mode),
                    backend="codex-cli",
                    skill=skill_manifest(skill) if skill else None,
                ),
                command_codex_cli_smoke_review,
                argparse.Namespace(
                    repo=str(repo),
                    run_id=run_id,
                    codex_command=args.codex_command,
                    codex_model=args.codex_model,
                    codex_reasoning_effort=args.codex_reasoning_effort,
                    codex_timeout=args.codex_timeout,
                    codex_skeptic_mode=args.codex_skeptic_mode,
                    goal=args.goal,
                ),
            )
        )
    if args.mode in {"standard", "deep"}:
        commands.append((run_manifest_step("authority-map", "authority-map", "authority_map", DETERMINISTIC_PRODUCERS["authority_map"]), command_authority_map, map_args))
        commands.append(
            (
                run_manifest_step("skeptic-review-authority-map", "skeptic-review", "skeptic_review", DETERMINISTIC_PRODUCERS["skeptic_review"]),
                command_skeptic_review,
                argparse.Namespace(
                    repo=str(repo),
                    run_id=run_id,
                    artifact=str(repo / ".research" / run_id / "authority-map.json"),
                ),
            )
        )
        commands.append((run_manifest_step("dependency-graph", "dependency-graph", "dependency_graph", DETERMINISTIC_PRODUCERS["dependency_graph"]), command_dependency_graph, map_args))
        commands.append(
            (
                run_manifest_step("skeptic-review-dependency-graph", "skeptic-review", "skeptic_review", DETERMINISTIC_PRODUCERS["skeptic_review"]),
                command_skeptic_review,
                argparse.Namespace(
                    repo=str(repo),
                    run_id=run_id,
                    artifact=str(repo / ".research" / run_id / "dependency-graph.json"),
                ),
            )
        )
        commands.append((run_manifest_step("verify-map", "verify-map", "verification_map", DETERMINISTIC_PRODUCERS["verification_map"]), command_verify_map, map_args))
        commands.append(
            (
                run_manifest_step("skeptic-review-verification-map", "skeptic-review", "skeptic_review", DETERMINISTIC_PRODUCERS["skeptic_review"]),
                command_skeptic_review,
                argparse.Namespace(
                    repo=str(repo),
                    run_id=run_id,
                    artifact=str(repo / ".research" / run_id / "verification-map.json"),
                ),
            )
        )
        commands.append((run_manifest_step("synthesis-index", "synthesis-index", "synthesis_index", DETERMINISTIC_PRODUCERS["synthesis_index"]), command_synthesis_index, map_args))
        commands.append(
            (
                run_manifest_step("skeptic-review-synthesis-index", "skeptic-review", "skeptic_review", DETERMINISTIC_PRODUCERS["skeptic_review"]),
                command_skeptic_review,
                argparse.Namespace(
                    repo=str(repo),
                    run_id=run_id,
                    artifact=str(repo / ".research" / run_id / "synthesis-index.json"),
                ),
            )
        )
    if args.mode == "deep":
        commands.append((run_manifest_step("bind", "bind", "goal_binding", DETERMINISTIC_PRODUCERS["goal_binding"]), command_bind, argparse.Namespace(repo=str(repo), run_id=run_id, goal=None, goal_class=None)))
        commands.append((run_manifest_step("trace-workflows", "trace-workflows", "workflow_trace", DETERMINISTIC_PRODUCERS["workflow_trace"]), command_trace_workflows, map_args))
        commands.append((run_manifest_step("refine", "refine", "refinement_report", DETERMINISTIC_PRODUCERS["refinement_report"]), command_refine, map_args))
        commands.append((run_manifest_step("approval-plan", "approval-plan", "approval_plan", DETERMINISTIC_PRODUCERS["approval_plan"]), command_approval_plan, map_args))
    else:
        commands.append((run_manifest_step("bind", "bind", "goal_binding", DETERMINISTIC_PRODUCERS["goal_binding"]), command_bind, argparse.Namespace(repo=str(repo), run_id=run_id, goal=None, goal_class=None)))
    commands.append((run_manifest_step("handoff", "handoff", "handoff", DETERMINISTIC_PRODUCERS["handoff"]), command_handoff, map_args))
    steps = [step for step, _, _ in commands]
    write_json(paths.run_dir / "run-manifest.json", build_run_manifest(args, repo, run_id, "running", steps))
    for step, command, ns in commands:
        step["status"] = "running"
        step["started_at"] = utc_now()
        write_json(paths.run_dir / "run-manifest.json", build_run_manifest(args, repo, run_id, "running", steps))
        rc = command(ns)
        step["exit_code"] = rc
        step["completed_at"] = utc_now()
        step["status"] = "succeeded" if rc == 0 else "interrupted" if rc == INTERRUPTED_EXIT_CODE else "failed"
        if rc == INTERRUPTED_EXIT_CODE:
            step["cause"] = "timeout"
        annotate_codex_step_outputs(repo, run_id, step)
        manifest_status = "running" if rc == 0 else "interrupted" if rc == INTERRUPTED_EXIT_CODE else "failed"
        write_json(paths.run_dir / "run-manifest.json", build_run_manifest(args, repo, run_id, manifest_status, steps))
        if rc != 0:
            return rc
    write_json(paths.run_dir / "run-manifest.json", build_run_manifest(args, repo, run_id, "succeeded", steps))
    print(repo / ".research" / run_id)
    return 0


def git_status_lines(repo: Path, paths: list[str]) -> list[str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "status", "--porcelain", "--", *paths],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f"git status failed: {exc.stderr.strip()}") from exc
    return [line for line in proc.stdout.splitlines() if line.strip()]


def checkpoint_files(repo: Path) -> list[Path]:
    reviews = repo / ".planning" / "reviews"
    if not reviews.exists():
        return []
    return sorted(reviews.glob("*/CHECKPOINT.md"), key=lambda path: path.stat().st_mtime, reverse=True)


def checkpoint_for_loop_scope(repo: Path, scope: str) -> Path | None:
    checkpoints = checkpoint_files(repo)
    if not checkpoints:
        return None
    if scope in SCOPES_REQUIRING_CROSS_MODEL:
        # Cross-model scopes require scope-label match (ADR-005 + W-NEW-1).
        # Select the most-recent checkpoint whose declared scope matches
        # the requested gate scope. If none match, fall through to the
        # most-recent overall so the gate can emit the specific
        # `checkpoint_scope_mismatch` issue rather than the generic
        # `missing_checkpoint` issue. This preserves the error vocabulary
        # for an operator who created a checkpoint for the wrong scope.
        for checkpoint in checkpoints:
            metadata = checkpoint_metadata(checkpoint)
            disposition = checkpoint_disposition_metadata(checkpoint)
            checkpoint_scope = (metadata.get("scope") or disposition.get("scope") or "").strip().lower()
            if checkpoint_scope == scope:
                return checkpoint
    if scope in SCOPES_REQUIRING_RESUME_GATE:
        for checkpoint in checkpoints:
            if checkpoint_satisfies_resume(checkpoint):
                return checkpoint
    return checkpoints[0]


ACCEPTED_DISPOSITION_VALUES = {"accept", "accepted", "waived-by-user"}


def checkpoint_satisfies_resume(path: Path) -> bool:
    # Verify-gates Warning 7 fix: previously this used substring `in`
    # matching against `Disposition: accept` and friends, which (a)
    # disagreed with checkpoint_pass_claim_issues (which lowercases and
    # exact-matches against {accept, accepted, waived-by-user}), and
    # (b) was case-fragile (`Disposition: Accept` failed satisfies but
    # passed pass_claim, while `Disposition: accepted` passed satisfies
    # only because "accept" is a prefix of "accepted"). Now both
    # functions read disposition via markdown_metadata + .lower() against
    # the same ACCEPTED_DISPOSITION_VALUES set. The explicit
    # "Satisfies resume gate: yes" marker remains as a legacy override
    # for older checkpoints that predate the disposition field.
    text = path.read_text(encoding="utf-8")
    if "Satisfies resume gate: yes" in text:
        return True
    metadata = checkpoint_metadata(path)
    disposition_md = checkpoint_disposition_metadata(path)
    disposition_value = (metadata.get("disposition") or disposition_md.get("disposition") or "").strip().lower()
    return disposition_value in ACCEPTED_DISPOSITION_VALUES


def load_loop_status_config() -> dict[str, Any]:
    try:
        config_text = resources.files("cbm").joinpath("loop_status_config.json").read_text(encoding="utf-8")
        config = json.loads(config_text)
    except (FileNotFoundError, json.JSONDecodeError, ModuleNotFoundError):
        config = {}
    families = config.get("current_dev_agent_model_families") or ["gpt", "openai", "codex"]
    return {
        "current_dev_agent_model_families": [str(item).lower() for item in families],
        "rework_warning_threshold": int(config.get("rework_warning_threshold", 6)),
    }


def markdown_metadata(text: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    if text.startswith("---\n"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            _, frontmatter, _ = parts
            parsed = yaml.safe_load(frontmatter) or {}
            if isinstance(parsed, dict):
                for key, value in parsed.items():
                    normalized_key = str(key).strip().lower().replace(" ", "_").replace("-", "_")
                    metadata[normalized_key] = "" if value is None else str(value).strip()
    for line in text.splitlines():
        if ":" not in line or line.startswith("#"):
            continue
        key, value = line.split(":", 1)
        normalized_key = key.strip().lower().replace(" ", "_").replace("-", "_")
        if normalized_key in {
            "reviewer_model_id",
            "same_model_fallback",
            "disposition",
            "status",
            "satisfies_resume_gate",
            "scope",
        }:
            metadata.setdefault(normalized_key, value.strip())
    return metadata


def model_matches_family(model_id: str, families: list[str]) -> bool:
    normalized = model_id.lower()
    return any(family and family in normalized for family in families)


def truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"true", "yes", "1"}


def checkpoint_metadata(path: Path | None) -> dict[str, str]:
    if not path:
        return {}
    return markdown_metadata(path.read_text(encoding="utf-8"))


def checkpoint_disposition_metadata(path: Path | None) -> dict[str, str]:
    if not path:
        return {}
    metadata: dict[str, str] = {}
    disposition_json = path.with_name("DISPOSITION.json")
    if nonempty(disposition_json):
        try:
            parsed = json.loads(disposition_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            parsed = {}
        if isinstance(parsed, dict):
            for key, value in parsed.items():
                normalized_key = str(key).strip().lower().replace(" ", "_").replace("-", "_")
                metadata[normalized_key] = "" if value is None else str(value).strip()
    disposition = path.with_name("DISPOSITION.md")
    if nonempty(disposition):
        markdown = markdown_metadata(disposition.read_text(encoding="utf-8"))
        metadata = {**markdown, **metadata}
    return metadata


CHECKPOINT_DIFF_PATHS = [
    "AGENTS.md",
    "VISION.md",
    "RUNTIME-CONSTITUTION.md",
    "docs/architecture.md",
    "docs/contracts.md",
    "docs/roadmap.md",
    "cbm/",
    "tests/",
    "schemas/",
    "cbm/schemas/",
    ".planning/STATE.md",
    ".planning/HORIZONS.md",
    ".planning/CURRENT-PLAN.md",
]


def last_checkpoint_commit(repo: Path) -> str | None:
    checkpoints = checkpoint_files(repo)
    if not checkpoints:
        return None
    rel_paths = [path.relative_to(repo).as_posix() for path in checkpoints]
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "log", "-1", "--format=%H", "--", *rel_paths],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except subprocess.CalledProcessError:
        return None
    commit = proc.stdout.strip()
    return commit or None


def checkpoint_diff(repo: Path) -> str:
    base = last_checkpoint_commit(repo)
    if not base:
        return "(No prior checkpoint commit found.)\n"
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "diff", f"{base}..HEAD", "--", *CHECKPOINT_DIFF_PATHS],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        return f"(git diff failed: {exc.stderr.strip()})\n"
    return proc.stdout or "(No diff since previous checkpoint across tracked paths.)\n"


def next_checkpoint_dir(repo: Path, pass_criterion: str) -> Path:
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    base = repo / ".planning" / "reviews" / f"{date}-{sanitize_slug(pass_criterion)}"
    candidate = base
    index = 2
    while candidate.exists():
        candidate = repo / ".planning" / "reviews" / f"{base.name}-{index}"
        index += 1
    return candidate


def command_checkpoint(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    # S-OP-2 fix (opus review): validate args before mkdir. Previously a
    # `cbm checkpoint --scope pass-claim` with no --reviewer would create
    # an empty packet directory that loop-status would later reject with
    # missing_reviewer_model_id, leaving mtime noise in .planning/reviews/
    # that the selector at checkpoint_for_loop_scope had to navigate.
    same_model_fallback = bool(args.reviewer_fallback_same_model)
    # Verify-gates Warning 8 fix: the S-OP-2 check only caught the
    # no-flag case. The partial-flag form
    # `--scope pass-claim --reviewer-fallback-same-model` (no --reviewer)
    # bypassed the required-reviewer check because same_model_fallback
    # made the original `not same_model_fallback` clause false, and then
    # only printed a stderr warning at line 5606 AFTER the packet
    # directory had already been mkdir'd. Be explicit: same-model fallback
    # is REJECTED at parse time for cross-model scopes, not just warned.
    if args.scope in SCOPES_REQUIRING_CROSS_MODEL and same_model_fallback:
        print(
            f"error: --reviewer-fallback-same-model is incompatible with --scope {args.scope} "
            "(ADR-005 requires a cross-model reviewer). The flag is valid only on "
            "--scope recovery-slice.",
            file=sys.stderr,
        )
        return 1
    if args.scope in SCOPES_REQUIRING_CROSS_MODEL and not args.reviewer:
        print(
            f"error: --scope {args.scope} requires --reviewer (cross-model checkpoint per ADR-005). "
            "Pass --reviewer <non-current-model-id>.",
            file=sys.stderr,
        )
        return 1
    packet = next_checkpoint_dir(repo, args.pass_criterion)
    packet.mkdir(parents=True, exist_ok=False)
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    reviewer = args.reviewer or ""
    # Note: the prior post-mkdir warning at this site ("same-model
    # fallback cannot clear pass-claim, main-merge, or
    # broad-goal-restart scope") is now dead code — the W8 fix above
    # hard-errors at arg-validation time before reaching this point.
    # Kept the comment as a marker so a future contributor doesn't
    # re-introduce the post-mkdir warn-then-continue pattern.
    state_path = repo / ".planning" / "STATE.md"
    horizons_path = repo / ".planning" / "HORIZONS.md"
    plan_path = repo / ".planning" / "CURRENT-PLAN.md"
    state_text = state_path.read_text(encoding="utf-8") if state_path.exists() else "(missing STATE.md)\n"
    horizons_text = horizons_path.read_text(encoding="utf-8") if horizons_path.exists() else "(missing HORIZONS.md)\n"
    plan_text = plan_path.read_text(encoding="utf-8") if plan_path.exists() else "(missing CURRENT-PLAN.md)\n"
    diff_text = checkpoint_diff(repo)
    prompt = f"""# Checkpoint Review Prompt

Status: pending
Date: {date}
Scope: {args.scope}
Pass criterion: {args.pass_criterion}

## Task

Review whether the pass criterion is supported by the current repo state. Return findings in CHECKPOINT.md and leave a clear disposition in DISPOSITION.md.

## Pass Criterion

{args.pass_criterion}

## STATE.md

```markdown
{state_text.rstrip()}
```

## HORIZONS.md

```markdown
{horizons_text.rstrip()}
```

## CURRENT-PLAN.md

```markdown
{plan_text.rstrip()}
```

## Diff Since Last Checkpoint

```diff
{diff_text.rstrip()}
```
"""
    checkpoint = f"""---
status: pending
date: {date}
reviewer_model_id: {reviewer}
same_model_fallback: {str(same_model_fallback).lower()}
scope: {args.scope}
pass_criterion: {args.pass_criterion}
confidence:
disposition:
---

# Checkpoint

"""
    disposition = """# Checkpoint Disposition

Status: pending
Disposition:
"""
    (packet / "PROMPT.md").write_text(prompt, encoding="utf-8")
    (packet / "CHECKPOINT.md").write_text(checkpoint, encoding="utf-8")
    (packet / "DISPOSITION.md").write_text(disposition, encoding="utf-8")
    print(packet)
    return 0


SCOPES_REQUIRING_CROSS_MODEL = {"pass-claim", "main-merge", "broad-goal-restart"}
# Verify-gates Warning 10 fix: name the scope sets used by command_loop_status
# so the three close-together inline literals at the call sites cannot drift.
SCOPES_TREATING_HORIZON_AS_HARD = {"broad-goal", "broad-goal-restart", "pass-claim", "main-merge"}
SCOPES_TREATING_MISSING_CHECKPOINT_AS_HARD = SCOPES_TREATING_HORIZON_AS_HARD
SCOPES_REQUIRING_RESUME_GATE = {"broad-goal", "broad-goal-restart"}


def checkpoint_pass_claim_issues(path: Path | None, config: dict[str, Any], scope: str) -> list[dict[str, str]]:
    if not path:
        return [{"code": "missing_checkpoint", "message": "no checkpoint review artifact found under .planning/reviews"}]
    metadata = checkpoint_metadata(path)
    disposition = checkpoint_disposition_metadata(path)
    reviewer_model_id = (metadata.get("reviewer_model_id") or disposition.get("reviewer_model_id") or "").strip()
    if not reviewer_model_id:
        return [
            {
                "code": "missing_reviewer_model_id",
                "message": f"{path} has no reviewer_model_id field for {scope} scope",
            }
        ]
    same_model = model_matches_family(reviewer_model_id, list(config["current_dev_agent_model_families"]))
    same_model_fallback = truthy(metadata.get("same_model_fallback") or disposition.get("same_model_fallback"))
    if same_model and scope in SCOPES_REQUIRING_CROSS_MODEL:
        return [
            {
                "code": "same_model_checkpoint",
                "message": f"{path} reviewer_model_id '{reviewer_model_id}' matches the current dev-agent model family",
            }
        ]
    if same_model and scope == "recovery-slice" and not same_model_fallback:
        return [
            {
                "code": "unlabeled_same_model_checkpoint",
                "message": f"{path} uses same-model reviewer '{reviewer_model_id}' without same_model_fallback: true",
            }
        ]
    if scope in SCOPES_REQUIRING_CROSS_MODEL:
        checkpoint_scope = (metadata.get("scope") or disposition.get("scope") or "").strip().lower()
        if checkpoint_scope != scope:
            return [
                {
                    "code": "checkpoint_scope_mismatch",
                    "message": f"{path} has scope '{checkpoint_scope or 'unset'}' but {scope} gate requires a checkpoint with scope: {scope}",
                }
            ]
    disposition_value = (metadata.get("disposition") or disposition.get("disposition") or "").lower()
    if scope in SCOPES_REQUIRING_CROSS_MODEL and disposition_value not in ACCEPTED_DISPOSITION_VALUES:
        return [
            {
                "code": "checkpoint_disposition_not_accepted",
                "message": f"{path} has no accepted disposition for {scope} scope",
            }
        ]
    return []


def nonempty(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 0


def review_session_completion_issues(repo: Path) -> list[dict[str, str]]:
    reviews = repo / ".planning" / "reviews"
    if not reviews.exists():
        return []
    issues: list[dict[str, str]] = []
    for session in sorted(path for path in reviews.iterdir() if path.is_dir()):
        rel = session.relative_to(repo).as_posix()
        files = [path for path in session.iterdir() if path.is_file()]
        dirs = [path for path in session.iterdir() if path.is_dir()]
        if not files and not dirs:
            issues.append({"code": "empty_review_session", "message": f"{rel} has no review artifacts or stop note"})
            continue
        stop_note = session / "STOP-NOTE.md"
        disposition = session / "DISPOSITION.md"
        disposition_text = disposition.read_text(encoding="utf-8") if nonempty(disposition) else ""
        session_aborted = "Status: aborted" in disposition_text or "status: aborted" in disposition_text
        prompts = sorted(session.glob("PROMPT*.md"))
        outputs = sorted(path for path in session.glob("OUTPUT*.md") if nonempty(path))
        if prompts and not outputs and not nonempty(stop_note) and not session_aborted:
            issues.append(
                {
                    "code": "incomplete_review_session",
                    "message": f"{rel} has prompt artifacts but no non-empty OUTPUT*.md, STOP-NOTE.md, or aborted disposition",
                }
            )
        checkpoint = session / "CHECKPOINT.md"
        if checkpoint.exists() and not nonempty(disposition):
            issues.append({"code": "missing_checkpoint_disposition", "message": f"{rel} has CHECKPOINT.md but no non-empty DISPOSITION.md"})
    return issues


def rework_pattern_warnings(repo: Path, threshold: int) -> list[dict[str, str]]:
    build_log = repo / "BUILD-LOG.md"
    if not build_log.exists():
        return []
    text = build_log.read_text(encoding="utf-8")
    slices = [block for block in re.split(r"(?=^##\s)", text, flags=re.MULTILINE) if block.startswith("##")]
    recent_slices = slices[-threshold:]
    path_counts: dict[str, int] = {}
    corrective_re = re.compile(r"\b(fix|fixed|repair|correct|corrective|retry|failed|failure|regression|rework|remediat)", re.IGNORECASE)
    path_re = re.compile(r"`((?:\.planning|\.research|cbm|tests|schemas|docs|skills|platform|VISION|AGENTS|RUNTIME-CONSTITUTION|BUILD-LOG)[^`]*\.(?:md|json|py|toml|txt|schema\.json))`")
    for block in recent_slices:
        if not corrective_re.search(block):
            continue
        for path in path_re.findall(block):
            path_counts[path] = path_counts.get(path, 0) + 1
    warnings: list[dict[str, str]] = []
    for path, count in sorted(path_counts.items()):
        if count >= threshold:
            warnings.append(
                {
                    "code": "repeated_rework_pattern",
                    "message": f"{path} appears in {count} corrective BUILD-LOG slices",
                }
            )
    return warnings


def horizon_plan_issues(repo: Path) -> list[dict[str, str]]:
    horizons = repo / ".planning" / "HORIZONS.md"
    current_plan = repo / ".planning" / "CURRENT-PLAN.md"
    issues: list[dict[str, str]] = []
    if not horizons.exists():
        return [{"code": "missing_horizons", "message": ".planning/HORIZONS.md is missing"}]
    if not current_plan.exists():
        return issues
    horizons_text = horizons.read_text(encoding="utf-8")
    plan_text = current_plan.read_text(encoding="utf-8")
    horizon_match = re.search(r"(?im)^Current horizon:\s*(H\d+)\b", plan_text)
    stage_match = re.search(r"(?im)^Current stage:\s*([A-Za-z0-9._-]+)\b", plan_text)
    if not horizon_match:
        issues.append(
            {
                "code": "missing_current_horizon",
                "message": ".planning/CURRENT-PLAN.md must name `Current horizon: H<N>` for autonomous /goal work",
            }
        )
    else:
        horizon_id = horizon_match.group(1)
        if not re.search(rf"(?m)^##\s+{re.escape(horizon_id)}\b", horizons_text):
            issues.append(
                {
                    "code": "unknown_current_horizon",
                    "message": f".planning/CURRENT-PLAN.md names {horizon_id}, but .planning/HORIZONS.md has no matching heading",
                }
            )
    if not stage_match:
        issues.append(
            {
                "code": "missing_current_stage",
                "message": ".planning/CURRENT-PLAN.md must name `Current stage: <stage-id>` for autonomous /goal work",
            }
        )
    elif stage_match.group(1) not in horizons_text:
        issues.append(
            {
                "code": "unknown_current_stage",
                "message": f".planning/CURRENT-PLAN.md names stage {stage_match.group(1)}, but .planning/HORIZONS.md does not contain that stage id",
            }
        )
    return issues


def command_loop_status(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    issues: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    config = load_loop_status_config()

    current_plan = repo / ".planning" / "CURRENT-PLAN.md"
    state = repo / ".planning" / "STATE.md"
    if not current_plan.exists():
        issues.append({"code": "missing_current_plan", "message": ".planning/CURRENT-PLAN.md is missing"})
    if not state.exists():
        issues.append({"code": "missing_state", "message": ".planning/STATE.md is missing"})

    dirty_authority = git_status_lines(repo, AUTHORITY_DOC_PATHS)
    if dirty_authority:
        issues.append(
            {
                "code": "dirty_authority_docs",
                "message": "authority/planning files have uncommitted changes: " + "; ".join(dirty_authority),
            }
        )

    if args.work_category and args.work_category not in RECOVERY_ALLOWED_WORK_CATEGORIES:
        issues.append(
            {
                "code": "work_category_blocked",
                "message": f"work category '{args.work_category}' is not in the recovery-allowed set",
            }
        )

    horizon_issues = horizon_plan_issues(repo)
    if args.scope in SCOPES_TREATING_HORIZON_AS_HARD:
        issues.extend(horizon_issues)
    else:
        warnings.extend(horizon_issues)

    checkpoint_path = checkpoint_for_loop_scope(repo, args.scope)
    checkpoint_ok = checkpoint_satisfies_resume(checkpoint_path) if checkpoint_path else False
    if not checkpoint_path:
        issue = {"code": "missing_checkpoint", "message": "no checkpoint review artifact found under .planning/reviews"}
        if args.scope in SCOPES_TREATING_MISSING_CHECKPOINT_AS_HARD:
            issues.append(issue)
        else:
            warnings.append(issue)
    elif not checkpoint_ok:
        issue = {
            "code": "checkpoint_pending",
            "message": f"checkpoint does not satisfy resume gate: {checkpoint_path.relative_to(repo).as_posix()}",
        }
        if args.scope in SCOPES_REQUIRING_RESUME_GATE:
            issues.append(issue)
        else:
            warnings.append(issue)

    if args.scope in SCOPES_REQUIRING_CROSS_MODEL and checkpoint_path is not None:
        # When checkpoint_path is None, the missing_checkpoint issue is
        # already appended above; skip the call to avoid emitting the
        # same issue twice.
        issues.extend(checkpoint_pass_claim_issues(checkpoint_path, config, args.scope))
    elif args.scope == "recovery-slice":
        # Verify-gates Critical 1 fix: ADR-005 requires recovery-slice
        # checkpoints to carry reviewer model identity (the same-model
        # fallback is only valid when LABELED, not when reviewer_model_id
        # is missing entirely). Retain both the unlabeled-fallback issue
        # AND the missing-reviewer-identity issue from the inner gate.
        # Other issue codes (scope_mismatch, disposition-not-accepted)
        # only fire for cross-model scopes and are correctly suppressed
        # for recovery-slice.
        recovery_model_issues = checkpoint_pass_claim_issues(checkpoint_path, config, args.scope)
        issues.extend(
            item
            for item in recovery_model_issues
            if item["code"] in {"unlabeled_same_model_checkpoint", "missing_reviewer_model_id"}
        )

    review_issues = review_session_completion_issues(repo)
    if args.scope == "broad-goal":
        issues.extend(review_issues)
    else:
        warnings.extend(review_issues)
    warnings.extend(rework_pattern_warnings(repo, int(config["rework_warning_threshold"])))

    result = {
        "status": "fail" if issues else "ok",
        "scope": args.scope,
        "work_category": args.work_category,
        "issues": issues,
        "warnings": warnings,
        "checkpoint": checkpoint_path.relative_to(repo).as_posix() if checkpoint_path else None,
    }
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"loop-status: {result['status']}")
        for item in issues:
            print(f"issue {item['code']}: {item['message']}", file=sys.stderr)
        for item in warnings:
            print(f"warning {item['code']}: {item['message']}", file=sys.stderr)
    return 1 if issues else 0


def latest_run_dir(repo: Path) -> Path | None:
    research = repo / ".research"
    if not research.exists():
        return None
    candidates = [path for path in research.iterdir() if path.is_dir()]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def hook_run_dir(repo: Path, run_id: str | None) -> Path | None:
    if run_id:
        candidate = repo / ".research" / run_id
        return candidate if candidate.is_dir() else None
    return latest_run_dir(repo)


def append_only_integrity_errors(run_dir: Path) -> list[str]:
    errors: list[str] = []
    ledger_path = run_dir / "evidence-ledger.jsonl"
    ledger_append_only_ok, ledger_append_only_reason = verify_ledger_append_only(ledger_path, require_manifest=True)
    if not ledger_append_only_ok:
        errors.append(f"ledger append-only verification failed: {ledger_append_only_reason}")
    uncertainty_path = run_dir / "uncertainty-register.jsonl"
    uncertainty_append_only_ok, uncertainty_append_only_reason = verify_ledger_append_only(uncertainty_path, require_manifest=True)
    if not uncertainty_append_only_ok:
        errors.append(f"uncertainty register append-only verification failed: {uncertainty_append_only_reason}")
    return errors


def command_hook_stop(args: argparse.Namespace) -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}
    repo = Path(payload.get("cwd") or args.repo).resolve()
    run_dir = hook_run_dir(repo, args.run_id)
    if not run_dir:
        if args.run_id:
            print(
                json.dumps(
                    {
                        "continue": False,
                        "stopReason": f"CBM run {args.run_id} was explicitly requested but does not exist.",
                        "systemMessage": f"CBM stop-hook gate failed: run {args.run_id} not found.",
                    }
                )
            )
            return 0
        detail = f"run {args.run_id} not found" if args.run_id else "no .research run found"
        print(json.dumps({"continue": True, "systemMessage": f"CBM: {detail} for stop-hook validation."}))
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
        for input_item in data.get("inputs", []):
            input_path = repo / input_item["path"]
            if not input_path.exists():
                errors.append(f"input missing: {input_item['path']}")
                continue
            if sha256_file(input_path) != input_item["sha256"]:
                errors.append(f"input hash changed: {input_item['path']}")
        surface_path = run_dir / "surface-map.json"
        if surface_path.exists():
            surface = read_json(surface_path)
            errors.extend(extractor_registry_errors_for_artifact(repo, surface))
            errors.extend(check_claim_evidence(surface, extractors_for_artifact(repo, surface)))
        errors.extend(append_only_integrity_errors(run_dir))
        for artifact in data.get("artifacts", []):
            if artifact.get("artifact_type") not in {"findings_card", "intervention_card"}:
                continue
            card_path = repo / artifact["path"]
            for failure in artifact_gate_failures(repo, card_path):
                errors.append(f"{artifact['path']}: {failure}")
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


def command_hook_start(args: argparse.Namespace) -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}
    repo = Path(payload.get("cwd") or args.repo).resolve()
    run_dir = hook_run_dir(repo, args.run_id)
    if not run_dir:
        if args.run_id:
            print(
                json.dumps(
                    {
                        "continue": False,
                        "stopReason": f"CBM run {args.run_id} was explicitly requested but does not exist.",
                        "systemMessage": f"CBM start-hook gate failed: run {args.run_id} not found.",
                    }
                )
            )
            return 0
        detail = f"run {args.run_id} not found" if args.run_id else "no .research run found"
        print(json.dumps({"continue": True, "systemMessage": f"CBM: {detail} for start-hook freshness validation."}))
        return 0
    handoff = run_dir / "handoff.md"
    if not handoff.exists():
        print(json.dumps({"continue": True, "systemMessage": f"CBM: run {run_dir.name} has no handoff.md for start-hook freshness validation."}))
        return 0
    try:
        data, _ = load_artifact_frontmatter(handoff)
        errors = append_only_integrity_errors(run_dir)
        for input_item in data.get("inputs", []):
            input_path = repo / input_item["path"]
            if not input_path.exists():
                errors.append(f"input missing: {input_item['path']}")
                continue
            if sha256_file(input_path) != input_item["sha256"]:
                errors.append(f"input hash changed: {input_item['path']}")
            for citation in artifact_citations(input_path):
                freshness = verify_citation_at_head(repo, citation)
                if freshness["status"] != "still_grounded":
                    errors.append(f"input citation stale: {input_item['path']}: {citation}: {freshness['reason']}")
    except Exception as exc:
        errors = [str(exc)]
    if errors:
        print(
            json.dumps(
                {
                    "continue": False,
                    "stopReason": f"CBM start freshness validation failed for {run_dir.name}.",
                    "systemMessage": "CBM start freshness gate failed: " + "; ".join(errors[:3]),
                }
            )
        )
        return 0
    print(json.dumps({"continue": True, "systemMessage": f"CBM start freshness gate passed for {run_dir.name}."}))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cbm")
    sub = parser.add_subparsers(dest="command", required=True)
    p_init = sub.add_parser("init")
    p_init.add_argument("--repo", default=".")
    p_init.add_argument("--goal", required=True)
    p_init.add_argument("--goal-class", default="understand_repo")
    p_init.add_argument("--mode", default="lightweight", choices=["lightweight", "standard", "deep"])
    p_init.add_argument("--backend", default="deterministic", choices=BACKEND_CHOICES)
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
    p_trace = sub.add_parser("trace-workflows")
    p_trace.add_argument("--repo", default=".")
    p_trace.add_argument("--run-id")
    p_trace.set_defaults(func=command_trace_workflows)
    p_refine = sub.add_parser("refine")
    p_refine.add_argument("--repo", default=".")
    p_refine.add_argument("--run-id")
    p_refine.set_defaults(func=command_refine)
    p_approval = sub.add_parser("approval-plan")
    p_approval.add_argument("--repo", default=".")
    p_approval.add_argument("--run-id")
    p_approval.set_defaults(func=command_approval_plan)
    p_validate = sub.add_parser("validate")
    p_validate.add_argument("artifact")
    p_validate.add_argument("--repo", default=".")
    p_validate.set_defaults(func=command_validate)
    p_extractor_registry = sub.add_parser("extractor-registry")
    p_extractor_registry_sub = p_extractor_registry.add_subparsers(dest="extractor_registry_command", required=True)
    p_extractor_registry_validate = p_extractor_registry_sub.add_parser("validate")
    p_extractor_registry_validate.add_argument("registry", nargs="?")
    p_extractor_registry_validate.add_argument("--repo", default=".")
    p_extractor_registry_validate.add_argument("--run-id")
    p_extractor_registry_validate.set_defaults(func=command_extractor_registry)
    p_check_evidence = sub.add_parser("check-evidence")
    p_check_evidence.add_argument("artifact")
    p_check_evidence.add_argument("--repo", default=".")
    p_check_evidence.set_defaults(func=command_check_evidence)
    p_verify = sub.add_parser("verify-citations")
    p_verify.add_argument("artifact")
    p_verify.add_argument("--repo", default=".")
    p_verify.set_defaults(func=command_verify_citations)
    p_gate_artifact = sub.add_parser("gate-artifact")
    p_gate_artifact.add_argument("artifact")
    p_gate_artifact.add_argument("--repo", default=".")
    p_gate_artifact.set_defaults(func=command_gate_artifact)
    p_challenge = sub.add_parser("challenge")
    p_challenge.add_argument("artifact")
    p_challenge.add_argument("--repo", default=".")
    p_challenge.add_argument("--claim-id", required=True)
    p_challenge.add_argument("--competing-reading", required=True)
    p_challenge.add_argument("--evidence", action="append", required=True)
    p_challenge.add_argument("--axis", default="other", choices=["centrality", "scope", "salience", "classification", "framing", "completeness", "other"])
    p_challenge.add_argument("--relation", default="competing", choices=["complementary", "competing", "reframing", "scope_dispute"])
    p_challenge.add_argument("--rationale", required=True)
    p_challenge.add_argument("--raised-by", default="human-reviewer")
    p_challenge.set_defaults(func=command_challenge)
    p_resolve_challenge = sub.add_parser("resolve-challenge")
    p_resolve_challenge.add_argument("artifact")
    p_resolve_challenge.add_argument("--repo", default=".")
    p_resolve_challenge.add_argument("--challenge-id", required=True)
    p_resolve_challenge.add_argument("--status", required=True, choices=["accepted_as_alternative", "accepted_as_replacement", "withdrawn", "resolved_to_contradiction"])
    p_resolve_challenge.add_argument("--resolution", required=True)
    p_resolve_challenge.add_argument("--response-note")
    p_resolve_challenge.add_argument("--resolved-by", default="human-reviewer")
    p_resolve_challenge.set_defaults(func=command_resolve_challenge)
    p_respond_challenge = sub.add_parser("respond-challenge")
    p_respond_challenge.add_argument("artifact")
    p_respond_challenge.add_argument("--repo", default=".")
    p_respond_challenge.add_argument("--challenge-id", required=True)
    p_respond_challenge.add_argument("--decision", required=True, choices=["accepted_as_alternative", "accepted_as_replacement", "withdrawn", "resolved_to_contradiction"])
    p_respond_challenge.add_argument("--resolution", required=True)
    p_respond_challenge.add_argument("--response-note", required=True)
    p_respond_challenge.add_argument("--resolved-by", default="surface-mapper@1.2")
    p_respond_challenge.set_defaults(func=lambda args: command_resolve_challenge(argparse.Namespace(**vars(args), status=args.decision)))
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
    p_run.add_argument("--backend", default="deterministic", choices=BACKEND_CHOICES)
    p_run.add_argument("--allow-live-codex", action="store_true")
    p_run.add_argument("--codex-command", default="codex")
    p_run.add_argument("--codex-model", default=DEFAULT_CODEX_CLI_MODEL)
    p_run.add_argument("--codex-reasoning-effort", default=DEFAULT_CODEX_CLI_REASONING_EFFORT, choices=["low", "medium", "high", "xhigh"])
    p_run.add_argument("--codex-surface-mode", default="baseline", choices=["baseline", "skill", "existing"])
    p_run.add_argument("--surface-artifact")
    p_run.add_argument("--codex-skeptic-mode", default="smoke", choices=["none", "smoke", "skill"])
    p_run.add_argument("--codex-timeout", type=positive_int, default=DEFAULT_CODEX_CLI_TIMEOUT_SECONDS)
    p_run.add_argument("--run-id")
    p_run.set_defaults(func=command_run)
    p_loop_status = sub.add_parser("loop-status")
    p_loop_status.add_argument("--repo", default=".")
    p_loop_status.add_argument("--scope", choices=["recovery-slice", "pass-claim", "main-merge", "broad-goal", "broad-goal-restart"], default="recovery-slice")
    p_loop_status.add_argument("--work-category")
    p_loop_status.add_argument("--json", action="store_true")
    p_loop_status.set_defaults(func=command_loop_status)
    p_checkpoint = sub.add_parser("checkpoint")
    p_checkpoint.add_argument("--repo", default=".")
    p_checkpoint.add_argument("--pass-criterion", required=True)
    p_checkpoint.add_argument("--scope", required=True, choices=["recovery-slice", "pass-claim", "main-merge", "broad-goal-restart"])
    p_checkpoint.add_argument("--reviewer")
    p_checkpoint.add_argument("--reviewer-fallback-same-model", action="store_true")
    p_checkpoint.set_defaults(func=command_checkpoint)
    p_hook_stop = sub.add_parser("hook-stop")
    p_hook_stop.add_argument("--repo", default=".")
    p_hook_stop.add_argument("--run-id")
    p_hook_stop.set_defaults(func=command_hook_stop)
    p_hook_start = sub.add_parser("hook-start")
    p_hook_start.add_argument("--repo", default=".")
    p_hook_start.add_argument("--run-id")
    p_hook_start.set_defaults(func=command_hook_start)
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


def trace_workflows_main() -> int:
    return main(["trace-workflows", *sys.argv[1:]])


def refine_main() -> int:
    return main(["refine", *sys.argv[1:]])


def approval_plan_main() -> int:
    return main(["approval-plan", *sys.argv[1:]])


def validate_main() -> int:
    return main(["validate", *sys.argv[1:]])


def extractor_registry_main() -> int:
    return main(["extractor-registry", *sys.argv[1:]])


def check_evidence_main() -> int:
    return main(["check-evidence", *sys.argv[1:]])


def verify_citations_main() -> int:
    return main(["verify-citations", *sys.argv[1:]])


def gate_artifact_main() -> int:
    return main(["gate-artifact", *sys.argv[1:]])


def challenge_main() -> int:
    return main(["challenge", *sys.argv[1:]])


def resolve_challenge_main() -> int:
    return main(["resolve-challenge", *sys.argv[1:]])


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


def loop_status_main() -> int:
    return main(["loop-status", *sys.argv[1:]])


def checkpoint_main() -> int:
    return main(["checkpoint", *sys.argv[1:]])


def hook_stop_main() -> int:
    return main(["hook-stop", *sys.argv[1:]])


def hook_start_main() -> int:
    return main(["hook-start", *sys.argv[1:]])


if __name__ == "__main__":
    raise SystemExit(main())
