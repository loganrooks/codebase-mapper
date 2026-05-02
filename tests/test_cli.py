from __future__ import annotations

import json
import io
import shutil
import subprocess
import sys
from importlib import resources
from pathlib import Path

import yaml

from cbm.cli import extract_citations, goal_pack, load_goal_packs, load_project_packs, main, sha256_file

SOURCE_ROOT = Path(__file__).resolve().parents[1]


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "sample"
    shutil.copytree(SOURCE_ROOT / "tests" / "fixtures" / "sample_repo", repo)
    git(repo, "init")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "config", "user.name", "Test User")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "initial")
    return repo


def copy_contracts(source_root: Path, repo: Path) -> None:
    target = repo / "schemas"
    target.mkdir()
    for schema in (source_root / "schemas").glob("*.schema.json"):
        target.joinpath(schema.name).write_text(schema.read_text(encoding="utf-8"), encoding="utf-8")


def test_package_schema_resources_match_root_schemas() -> None:
    root_schemas = {path.name: path.read_text(encoding="utf-8") for path in (SOURCE_ROOT / "schemas").glob("*.schema.json")}
    package_schemas = {
        item.name: item.read_text(encoding="utf-8")
        for item in resources.files("cbm").joinpath("schemas").iterdir()
        if item.name.endswith(".schema.json")
    }
    assert package_schemas == root_schemas


def test_extract_citations_ignores_markdown_backticks() -> None:
    assert extract_citations("anchor `.gitignore:1@4503e2d12b79`") == [".gitignore:1@4503e2d12b79"]


def test_init_map_handoff_and_citation_resolution(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    expected = json.loads((SOURCE_ROOT / "tests" / "fixtures" / "expected_phase_a.json").read_text(encoding="utf-8"))
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-test"
    assert main(["init", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    assert main(["map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["surface", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["bind", "--repo", str(repo), "--run-id", run_id]) == 0

    run_dir = repo / ".research" / run_id
    codebase_map = run_dir / "codebase-map.json"
    project_type = run_dir / "project-type.json"
    extractor_registry = run_dir / "extractor-registry.json"
    surface_map = run_dir / "surface-map.json"
    goal_binding = run_dir / "goal-binding.json"
    assert codebase_map.exists()
    assert project_type.exists()
    assert surface_map.exists()
    assert goal_binding.exists()
    assert main(["validate", str(codebase_map), "--repo", str(repo)]) == 0
    assert main(["validate", str(project_type), "--repo", str(repo)]) == 0
    assert main(["validate", str(extractor_registry), "--repo", str(repo)]) == 0
    assert main(["validate", str(surface_map), "--repo", str(repo)]) == 0
    assert main(["validate", str(goal_binding), "--repo", str(repo)]) == 0
    initial_surface = json.loads(surface_map.read_text(encoding="utf-8"))
    import_edges = [edge for edge in initial_surface["edges"] if edge["kind"] == "import"]
    call_edges = [edge for edge in initial_surface["edges"] if edge["kind"] == "call"]
    assert import_edges
    assert call_edges
    assert import_edges[0]["from"]["path"] == expected["surface_import_edge"]["from_path"]
    assert import_edges[0]["to"]["path"] == expected["surface_import_edge"]["to_path"]
    assert import_edges[0]["extractor_id"] == expected["surface_import_edge"]["extractor_id"]
    assert import_edges[0]["claim_register"] == expected["surface_import_edge"]["claim_register"]
    assert import_edges[0]["evidence_kinds"] == expected["surface_import_edge"]["evidence_kinds"]
    assert call_edges[0]["from"]["path"] == "tests/test_app.py"
    assert call_edges[0]["to"]["path"] == "src/app.py"
    assert call_edges[0]["to"]["symbol"] == "hello"
    assert call_edges[0]["extractor_id"] == "ext-python-calls-v1"
    binding = json.loads(goal_binding.read_text(encoding="utf-8"))
    assert binding["artifact_type"] == "goal_binding"
    assert binding["goal"] == "understand this repo"
    assert binding["candidates"][0]["surface_ref"].endswith("/edges/0")
    assert binding["candidates"][0]["surface_kind"] == "import"
    project_data = json.loads(project_type.read_text(encoding="utf-8"))
    assert any(item["project_type"] == "python_package" for item in project_data["detections"])
    registry_data = json.loads(extractor_registry.read_text(encoding="utf-8"))
    assert any(item["project_type"] == "python_package" for item in registry_data["project_pack_annotations"])

    assert main(["handoff", "--repo", str(repo), "--run-id", run_id]) == 0
    card = run_dir / "findings" / "int-0001.md"
    handoff = run_dir / "handoff.md"
    skeptic_review = run_dir / "skeptic-review" / "surface-map.md"
    assert card.exists()
    assert handoff.exists()
    assert skeptic_review.exists()
    assert main(["validate", str(card), "--repo", str(repo)]) == 0
    assert main(["validate", str(surface_map), "--repo", str(repo)]) == 0
    assert main(["verify-citations", str(card), "--repo", str(repo)]) == 0
    assert main(["validate", str(handoff), "--repo", str(repo)]) == 0
    card_frontmatter = yaml.safe_load(card.read_text(encoding="utf-8").split("---", 2)[1])
    assert card_frontmatter["produced_by"] == "dev-fixture-planner@0.1"
    assert expected["findings_card"]["role_contains"] in card_frontmatter["primary_files"][0]["role"]
    assert card_frontmatter["confidence"] == expected["findings_card"]["confidence"]
    assert card_frontmatter["dependent_challenges"] == []
    assert card_frontmatter["related_dependencies"]["certain"][0].endswith("/edges/0")
    assert card_frontmatter["verification_strategy"]["hard_gates"][0]["implementation"].startswith("Run cbm-gate-artifact")

    frontmatter = yaml.safe_load(handoff.read_text(encoding="utf-8").split("---", 2)[1])
    assert frontmatter["produced_by"] == "cbm-baseline-handoff@0.1"
    assert frontmatter["gate_summary"]["schema_validation"]["passed"] == len(frontmatter["artifacts"])
    assert frontmatter["gate_summary"]["schema_validation"]["failed_artifacts"] == []
    assert frontmatter["gate_summary"]["staleness_check"]["fresh"] == len(frontmatter["inputs"])
    assert frontmatter["gate_summary"]["staleness_check"]["stale_artifacts"] == []
    assert frontmatter["gate_summary"]["citation_resolution"]["unresolved_count"] == 0
    bundle_citations = set()
    for artifact in frontmatter["artifacts"]:
        artifact_path = repo / artifact["path"]
        if artifact_path.suffix == ".md":
            _, artifact_frontmatter, artifact_body = artifact_path.read_text(encoding="utf-8").split("---", 2)
            artifact_data = yaml.safe_load(artifact_frontmatter)
            bundle_citations.update(extract_citations(artifact_body))
        else:
            artifact_data = json.loads(artifact_path.read_text(encoding="utf-8"))
        bundle_citations.update(extract_citations(artifact_data))
    assert frontmatter["gate_summary"]["citation_resolution"]["resolved"] == len(bundle_citations)
    assert frontmatter["gate_summary"]["ledger_consistency"]["append_only_verified"] is True
    assert frontmatter["gate_summary"]["ledger_consistency"]["entry_count"] >= 3
    assert frontmatter["gate_summary"]["ledger_consistency"]["missing_citation_count"] == 0
    assert frontmatter["gate_summary"]["ledger_consistency"]["missing_citation_examples"] == []
    assert frontmatter["gate_summary"]["skeptic_review"]["challenges_logged"] == 0
    assert frontmatter["contestation_summary"]["claims_by_register"]["interpretive"] >= 1
    assert any("were directly examined" in caveat and "remain unread" in caveat for caveat in frontmatter["coverage_caveats"])
    assert any("deterministic extractors only" in caveat for caveat in frontmatter["coverage_caveats"])
    assert "goal_binding" in [artifact["artifact_type"] for artifact in frontmatter["artifacts"]]
    assert "project_type_report" in [artifact["artifact_type"] for artifact in frontmatter["artifacts"]]
    assert any(input_item["path"].endswith("goal-binding.json") for input_item in frontmatter["inputs"])
    assert any(input_item["path"].endswith("project-type.json") for input_item in frontmatter["inputs"])
    reviewed_surface = json.loads(surface_map.read_text(encoding="utf-8"))
    assert reviewed_surface["produced_by"] == "cbm-baseline-surface@0.1"
    assert reviewed_surface["coverage"]["result"]["files_examined_directly"] == 0
    reviewed_import_edges = [edge for edge in reviewed_surface["edges"] if edge["kind"] == "import"]
    reviewed_call_edges = [edge for edge in reviewed_surface["edges"] if edge["kind"] == "call"]
    reviewed_unknown_edges = [edge for edge in reviewed_surface["edges"] if edge["kind"] == "unknown"]
    assert reviewed_import_edges[0]["claim_status"] == expected["surface_import_edge"]["claim_status"]
    assert reviewed_call_edges[0]["claim_status"] == "active"
    assert reviewed_unknown_edges[0]["id"] == expected["surface_unknown_edge"]["id"]
    assert reviewed_unknown_edges[0]["claim_status"] == expected["surface_unknown_edge"]["claim_status_after_handoff"]
    assert reviewed_unknown_edges[0].get("challenges", []) == []
    assert "competing_reading" not in "\n".join(
        path.read_text(encoding="utf-8")
        for path in run_dir.rglob("*")
        if path.is_file() and path.suffix in {".json", ".jsonl", ".md"}
    )
    ledger_entries = [
        json.loads(line)
        for line in (run_dir / "evidence-ledger.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    ledger_citations = {entry.get("citation") for entry in ledger_entries if entry.get("citation")}
    surface_citations = {
        citation
        for edge in reviewed_surface["edges"]
        for citation in edge.get("citations", [])
    }
    assert surface_citations <= ledger_citations
    integrity_manifest = json.loads((run_dir / "evidence-ledger.jsonl.integrity.json").read_text(encoding="utf-8"))
    assert integrity_manifest["line_count"] == len(ledger_entries)
    assert len(integrity_manifest["line_hashes"]) == len(ledger_entries)
    uncertainty_entries = [
        json.loads(line)
        for line in (run_dir / "uncertainty-register.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    uncertainty_integrity = json.loads((run_dir / "uncertainty-register.jsonl.integrity.json").read_text(encoding="utf-8"))
    assert uncertainty_integrity["line_count"] == len(uncertainty_entries)
    assert len(uncertainty_integrity["line_hashes"]) == len(uncertainty_entries)


def test_run_orchestrates_phase_a_flow(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--run-id", "run-orchestrated"]) == 0

    run_dir = repo / ".research" / "run-orchestrated"
    assert (run_dir / "codebase-map.json").exists()
    assert (run_dir / "surface-map.json").exists()
    assert (run_dir / "goal-binding.json").exists()
    assert (run_dir / "findings" / "int-0001.md").exists()
    assert (run_dir / "handoff.md").exists()


def test_run_backend_deterministic_writes_manifest_and_producer_registry(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-backend-manifest"
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--backend", "deterministic", "--run-id", run_id]) == 0

    run_dir = repo / ".research" / run_id
    producer_registry = run_dir / "producer-registry.json"
    run_manifest = run_dir / "run-manifest.json"
    assert producer_registry.exists()
    assert run_manifest.exists()
    assert main(["validate", str(producer_registry), "--repo", str(repo)]) == 0
    assert main(["validate", str(run_manifest), "--repo", str(repo)]) == 0
    registry_data = json.loads(producer_registry.read_text(encoding="utf-8"))
    manifest_data = json.loads(run_manifest.read_text(encoding="utf-8"))
    assert registry_data["backend"] == "deterministic"
    assert any(
        item["artifact_type"] == "surface_map"
        and item["producer_id"] == "cbm-baseline-surface@0.1"
        and item["execution_contract"] == "deterministic_baseline"
        for item in registry_data["producers"]
    )
    assert any(
        item["artifact_type"] == "skeptic_review"
        and item["producer_id"] == "dev-fixture-skeptic@0.1"
        and item["execution_contract"] == "dev_fixture"
        for item in registry_data["producers"]
    )
    assert manifest_data["backend"] == "deterministic"
    assert manifest_data["status"] == "succeeded"
    assert manifest_data["producer_registry"]["sha256"] == sha256_file(producer_registry)
    assert [step["step_id"] for step in manifest_data["steps"]] == ["init", "map", "surface", "bind", "handoff"]
    assert all(step["status"] == "succeeded" and step["exit_code"] == 0 for step in manifest_data["steps"])


def test_run_validates_with_cbm_schema_source_without_polluting_target_repo(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)

    run_id = "run-packaged-schemas"
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0

    run_dir = repo / ".research" / run_id
    assert not (repo / "schemas").exists()
    assert main(["validate", str(run_dir / "handoff.md"), "--repo", str(repo)]) == 0
    codebase_map = json.loads((run_dir / "codebase-map.json").read_text(encoding="utf-8"))
    assert not any(item["path"].startswith("schemas/") for item in codebase_map["files"])


def test_run_backend_external_refuses_without_fake_agent_outputs(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-external-refused"
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--backend", "external", "--run-id", run_id]) == 2

    run_dir = repo / ".research" / run_id
    producer_registry = run_dir / "producer-registry.json"
    run_manifest = run_dir / "run-manifest.json"
    assert producer_registry.exists()
    assert run_manifest.exists()
    assert not (run_dir / "surface-map.json").exists()
    assert main(["validate", str(producer_registry), "--repo", str(repo)]) == 0
    assert main(["validate", str(run_manifest), "--repo", str(repo)]) == 0
    registry_data = json.loads(producer_registry.read_text(encoding="utf-8"))
    manifest_data = json.loads(run_manifest.read_text(encoding="utf-8"))
    assert registry_data["backend"] == "external"
    assert all(item["execution_contract"] == "external_agent" for item in registry_data["producers"])
    assert manifest_data["backend"] == "external"
    assert manifest_data["status"] == "refused"
    assert manifest_data["steps"] == []


def test_run_backend_codex_cli_requires_explicit_live_flag(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-codex-cli-refused"
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--backend", "codex-cli", "--run-id", run_id]) == 2

    run_dir = repo / ".research" / run_id
    producer_registry = run_dir / "producer-registry.json"
    run_manifest = run_dir / "run-manifest.json"
    assert producer_registry.exists()
    assert run_manifest.exists()
    assert not (run_dir / "surface-map.json").exists()
    assert main(["validate", str(producer_registry), "--repo", str(repo)]) == 0
    assert main(["validate", str(run_manifest), "--repo", str(repo)]) == 0
    registry_data = json.loads(producer_registry.read_text(encoding="utf-8"))
    manifest_data = json.loads(run_manifest.read_text(encoding="utf-8"))
    assert registry_data["backend"] == "codex-cli"
    assert any(
        item["artifact_type"] == "skeptic_review"
        and item["producer_id"] == "codex-cli-smoke@0.1"
        and item["backend"] == "codex-cli"
        and item["execution_contract"] == "external_agent"
        for item in registry_data["producers"]
    )
    assert manifest_data["backend"] == "codex-cli"
    assert manifest_data["status"] == "refused"
    assert "requires --allow-live-codex" in manifest_data["refusal_reason"]
    assert manifest_data["steps"] == []


def test_run_backend_codex_cli_fake_producer_writes_agent_review(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)

    fake_codex = tmp_path / "fake-codex"
    fake_codex.write_text(
        "#!/usr/bin/env python3\n"
        "import json\n"
        "import sys\n"
        "from pathlib import Path\n"
        "assert '-m' in sys.argv\n"
        "assert sys.argv[sys.argv.index('-m') + 1] == 'gpt-5.4-mini'\n"
        "assert '-c' in sys.argv\n"
        "assert sys.argv[sys.argv.index('-c') + 1] == 'model_reasoning_effort=\"medium\"'\n"
        "assert 'approval_policy=\"never\"' in sys.argv\n"
        "output_path = Path(sys.argv[sys.argv.index('-o') + 1])\n"
        "prompt = sys.stdin.read()\n"
        "assert 'surface-map.json' in prompt\n"
        "output_path.write_text(json.dumps({\n"
        "    'body': 'The smoke reviewer confirms the artifact is readable and cites the supplied anchor.',\n"
        "    'findings_logged': 0,\n"
        "    'challenge_ids': []\n"
        "}) + '\\n', encoding='utf-8')\n",
        encoding="utf-8",
    )
    fake_codex.chmod(0o755)

    run_id = "run-codex-cli-fake"
    assert (
        main(
            [
                "run",
                "--repo",
                str(repo),
                "--goal",
                "understand this repo",
                "--backend",
                "codex-cli",
                "--allow-live-codex",
                "--codex-command",
                str(fake_codex),
                "--run-id",
                run_id,
            ]
        )
        == 0
    )

    run_dir = repo / ".research" / run_id
    skeptic_review = run_dir / "skeptic-review" / "surface-map.md"
    run_manifest = run_dir / "run-manifest.json"
    assert skeptic_review.exists()
    assert main(["validate", str(skeptic_review), "--repo", str(repo)]) == 0
    assert main(["validate", str(run_manifest), "--repo", str(repo)]) == 0
    review_text = skeptic_review.read_text(encoding="utf-8")
    review_frontmatter = yaml.safe_load(review_text.split("---", 2)[1])
    assert review_frontmatter["produced_by"] == "codex-cli-smoke@0.1"
    assert review_frontmatter["findings_logged"] == 0
    assert "dev-fixture-skeptic@0.1" not in review_text
    review_citations = set(extract_citations(review_text))
    ledger_entries = [
        json.loads(line)
        for line in (run_dir / "evidence-ledger.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    ledger_citations = {entry.get("citation") for entry in ledger_entries if entry.get("citation")}
    assert review_citations <= ledger_citations
    manifest_data = json.loads(run_manifest.read_text(encoding="utf-8"))
    assert manifest_data["backend"] == "codex-cli"
    assert manifest_data["status"] == "succeeded"
    codex_steps = [step for step in manifest_data["steps"] if step["backend"] == "codex-cli"]
    assert [step["step_id"] for step in codex_steps] == ["codex-cli-smoke-skeptic-review"]
    assert codex_steps[0]["producer_id"] == "codex-cli-smoke@0.1"
    assert codex_steps[0]["status"] == "succeeded"
    assert "-m gpt-5.4-mini -c model_reasoning_effort=\"medium\" -c approval_policy=\"never\"" in codex_steps[0]["command"]
    assert "--ephemeral --ignore-user-config --ignore-rules" in codex_steps[0]["command"]
    assert "-s read-only" in codex_steps[0]["command"]
    handoff_frontmatter = yaml.safe_load((run_dir / "handoff.md").read_text(encoding="utf-8").split("---", 2)[1])
    assert handoff_frontmatter["gate_summary"]["skeptic_review"]["challenges_logged"] == 0


def test_init_records_project_type_citations_in_ledger(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-project-type-ledger"
    assert main(["init", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0

    run_dir = repo / ".research" / run_id
    project_type = json.loads((run_dir / "project-type.json").read_text(encoding="utf-8"))
    project_type_citations = set(extract_citations(project_type))
    ledger_entries = [
        json.loads(line)
        for line in (run_dir / "evidence-ledger.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    ledger_citations = {entry.get("citation") for entry in ledger_entries if entry.get("citation")}
    assert project_type_citations
    assert project_type_citations <= ledger_citations


def test_goal_packs_rank_same_surface_differently(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-goal-packs"
    assert main(["init", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    assert main(["map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["surface", "--repo", str(repo), "--run-id", run_id]) == 0
    surface_mtime = (repo / ".research" / run_id / "surface-map.json").stat().st_mtime_ns

    assert main(["bind", "--repo", str(repo), "--run-id", run_id, "--goal", "add greeting behavior", "--goal-class", "feature_add"]) == 0
    feature_binding = json.loads((repo / ".research" / run_id / "goal-binding.json").read_text(encoding="utf-8"))
    assert feature_binding["research_only"] is False
    assert feature_binding["candidates"][0]["surface_kind"] == "call"
    assert feature_binding["candidates"][0]["recommended_card_type"] == "intervention_card"

    assert main(["bind", "--repo", str(repo), "--run-id", run_id, "--goal", "audit verification posture", "--goal-class", "audit"]) == 0
    audit_binding = json.loads((repo / ".research" / run_id / "goal-binding.json").read_text(encoding="utf-8"))
    assert audit_binding["research_only"] is False
    assert audit_binding["candidates"][0]["surface_kind"] == "authority"
    assert audit_binding["candidates"][0]["path"] == "tests/test_app.py"
    assert (repo / ".research" / run_id / "surface-map.json").stat().st_mtime_ns == surface_mtime


def test_goal_packs_load_from_package_data() -> None:
    packs = load_goal_packs()
    assert {"understand_repo", "research_only", "feature_add", "refactor", "audit"} <= packs.keys()
    assert goal_pack("feature_add")["priority"]["call"] == 0
    assert goal_pack("audit")["priority"]["authority:test_suite"] == 0
    assert goal_pack("research_only")["card_type"] == "findings_card"
    assert goal_pack("unknown_goal")["card_type"] == "intervention_card"


def test_project_packs_load_from_package_data() -> None:
    packs = load_project_packs()
    assert {"django", "rails", "phoenix", "mcp_server", "agent_orchestration", "monorepo"} <= packs.keys()
    assert packs["django"]["authority_hints"]
    assert packs["mcp_server"]["extractor_annotations"]


def test_hook_console_scripts_are_declared() -> None:
    pyproject = (SOURCE_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'cbm-extractor-registry = "cbm.cli:extractor_registry_main"' in pyproject
    assert 'cbm-hook-start = "cbm.cli:hook_start_main"' in pyproject
    assert 'cbm-hook-stop = "cbm.cli:hook_stop_main"' in pyproject


def test_extractor_registry_validate_command_enforces_blind_spots(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-registry-validate"
    assert main(["init", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    registry = repo / ".research" / run_id / "extractor-registry.json"
    assert main(["extractor-registry", "validate", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["extractor-registry", "validate", str(registry), "--repo", str(repo)]) == 0

    data = json.loads(registry.read_text(encoding="utf-8"))
    data["extractors"][0]["known_blind_spots"] = []
    bad_registry = repo / ".research" / run_id / "extractor-registry.bad.json"
    bad_registry.write_text(json.dumps(data, indent=2), encoding="utf-8")
    assert main(["extractor-registry", "validate", str(bad_registry), "--repo", str(repo)]) == 2

    data = json.loads(registry.read_text(encoding="utf-8"))
    data["project_pack_annotations"][0]["extractor_annotations"] = []
    bad_annotation = repo / ".research" / run_id / "extractor-registry.bad-annotation.json"
    bad_annotation.write_text(json.dumps(data, indent=2), encoding="utf-8")
    assert main(["extractor-registry", "validate", str(bad_annotation), "--repo", str(repo)]) == 2

    data = json.loads(registry.read_text(encoding="utf-8"))
    data["extractors"][1]["id"] = data["extractors"][0]["id"]
    duplicate_id = repo / ".research" / run_id / "extractor-registry.duplicate-id.json"
    duplicate_id.write_text(json.dumps(data, indent=2), encoding="utf-8")
    assert main(["extractor-registry", "validate", str(duplicate_id), "--repo", str(repo)]) == 2

    data = json.loads(registry.read_text(encoding="utf-8"))
    data["project_pack_annotations"].append(dict(data["project_pack_annotations"][0]))
    duplicate_annotation = repo / ".research" / run_id / "extractor-registry.duplicate-annotation.json"
    duplicate_annotation.write_text(json.dumps(data, indent=2), encoding="utf-8")
    assert main(["extractor-registry", "validate", str(duplicate_annotation), "--repo", str(repo)]) == 2


def test_handoff_emits_goal_pack_card_type(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-feature-handoff"
    assert main(["init", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    assert main(["map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["surface", "--repo", str(repo), "--run-id", run_id]) == 0
    run_dir = repo / ".research" / run_id
    surface_map = run_dir / "surface-map.json"
    assert main(["bind", "--repo", str(repo), "--run-id", run_id, "--goal", "add greeting behavior", "--goal-class", "feature_add"]) == 0
    assert main(["handoff", "--repo", str(repo), "--run-id", run_id]) == 0

    card = run_dir / "interventions" / "int-0001.md"
    handoff = run_dir / "handoff.md"
    assert card.exists()
    assert not (run_dir / "findings" / "int-0001.md").exists()
    assert main(["validate", str(card), "--repo", str(repo)]) == 0
    assert main(["verify-citations", str(card), "--repo", str(repo)]) == 0

    card_frontmatter = yaml.safe_load(card.read_text(encoding="utf-8").split("---", 2)[1])
    assert card_frontmatter["artifact_type"] == "intervention_card"
    assert card_frontmatter["goal"] == "add greeting behavior"
    assert card_frontmatter["goal_class"] == "feature_add"
    assert card_frontmatter["research_only"] is False
    assert "Calls src/app.py::hello" in card_frontmatter["primary_files"][0]["role"]
    assert card_frontmatter["related_dependencies"]["certain"][0].endswith("/edges/1")
    assert any(input_item["path"].endswith("goal-binding.json") for input_item in card_frontmatter["inputs"])

    frontmatter = yaml.safe_load(handoff.read_text(encoding="utf-8").split("---", 2)[1])
    assert frontmatter["user_goal"] == "add greeting behavior"
    assert frontmatter["goal_class"] == "feature_add"
    assert frontmatter["research_only"] is False
    artifact_types = [artifact["artifact_type"] for artifact in frontmatter["artifacts"]]
    assert "intervention_card" in artifact_types
    assert "findings_card" not in artifact_types
    assert any(input_item["path"].endswith("interventions/int-0001.md") for input_item in frontmatter["inputs"])

    surface_mtime_after_feature = surface_map.stat().st_mtime_ns
    assert main(["bind", "--repo", str(repo), "--run-id", run_id, "--goal", "audit verification posture", "--goal-class", "audit"]) == 0
    assert surface_map.stat().st_mtime_ns == surface_mtime_after_feature
    assert main(["handoff", "--repo", str(repo), "--run-id", run_id]) == 0
    audit_frontmatter = yaml.safe_load(card.read_text(encoding="utf-8").split("---", 2)[1])
    assert audit_frontmatter["goal"] == "audit verification posture"
    assert audit_frontmatter["goal_class"] == "audit"
    assert audit_frontmatter["primary_files"][0]["path"] == "tests/test_app.py"
    assert audit_frontmatter["primary_files"][0]["role"] != card_frontmatter["primary_files"][0]["role"]


def test_standard_run_writes_verification_map(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--mode", "standard", "--run-id", "run-standard"]) == 0

    run_dir = repo / ".research" / "run-standard"
    authority_map = run_dir / "authority-map.json"
    dependency_graph = run_dir / "dependency-graph.json"
    verification_map = run_dir / "verification-map.json"
    synthesis_index = run_dir / "synthesis-index.json"
    skeptic_reviews = [
        run_dir / "skeptic-review" / "authority-map.md",
        run_dir / "skeptic-review" / "dependency-graph.md",
        run_dir / "skeptic-review" / "verification-map.md",
        run_dir / "skeptic-review" / "synthesis-index.md",
    ]
    assert authority_map.exists()
    assert dependency_graph.exists()
    assert verification_map.exists()
    assert synthesis_index.exists()
    assert all(review.exists() for review in skeptic_reviews)
    assert main(["validate", str(authority_map), "--repo", str(repo)]) == 0
    assert main(["validate", str(dependency_graph), "--repo", str(repo)]) == 0
    assert main(["validate", str(verification_map), "--repo", str(repo)]) == 0
    assert main(["validate", str(synthesis_index), "--repo", str(repo)]) == 0
    for review in skeptic_reviews:
        assert main(["validate", str(review), "--repo", str(repo)]) == 0
    authority_data = json.loads(authority_map.read_text(encoding="utf-8"))
    assert authority_data["authorities"]
    dependency_data = json.loads(dependency_graph.read_text(encoding="utf-8"))
    assert dependency_data["partition_counts"]["unknown"] >= 1
    data = json.loads(verification_map.read_text(encoding="utf-8"))
    assert data["produced_by"] == "cbm-baseline-verification@0.1"
    assert data["coverage"]["result"]["files_examined_directly"] == 0
    assert data["ci_gates"]
    assert data["ci_gates"][0]["command"]["safety_envelope"]["requires_network"] is False
    synthesis_data = json.loads(synthesis_index.read_text(encoding="utf-8"))
    assert synthesis_data["claim_counts"]["authorities"] == len(authority_data["authorities"])
    assert synthesis_data["claim_counts"]["dependencies"] == len(dependency_data["edges"])
    assert synthesis_data["contestation"]["open_challenges"] == 0
    handoff_frontmatter = yaml.safe_load((run_dir / "handoff.md").read_text(encoding="utf-8").split("---", 2)[1])
    assert handoff_frontmatter["contestation_summary"]["open_challenges"] == 0
    assert handoff_frontmatter["contestation_summary"]["claims_by_status"]["challenged"] == 0
    assert handoff_frontmatter["gate_summary"]["skeptic_review"]["challenges_logged"] == 0
    assert handoff_frontmatter["gate_summary"]["skeptic_review"]["artifacts_reviewed"] == len(
        [artifact for artifact in handoff_frontmatter["artifacts"] if artifact["artifact_type"] == "skeptic_review"]
    )


def test_synthesis_index_includes_surface_challenges(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-synthesis-surface-challenge"
    assert main(["init", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    assert main(["map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["surface", "--repo", str(repo), "--run-id", run_id]) == 0
    run_dir = repo / ".research" / run_id
    surface = run_dir / "surface-map.json"
    surface_data = json.loads(surface.read_text(encoding="utf-8"))
    import_edge = next(edge for edge in surface_data["edges"] if edge["kind"] == "import")
    assert (
        main(
            [
                "challenge",
                str(surface),
                "--repo",
                str(repo),
                "--claim-id",
                import_edge["id"],
                "--competing-reading",
                "The surface import may not represent the intervention path and should remain visible in synthesis.",
                "--evidence",
                import_edge["citations"][0],
                "--rationale",
                "A challenged surface relation should not disappear between surface mapping and handoff.",
            ]
        )
        == 0
    )
    challenged = json.loads(surface.read_text(encoding="utf-8"))
    challenged_edge = next(edge for edge in challenged["edges"] if edge["id"] == import_edge["id"])
    withdrawn_challenge_id = challenged_edge["challenges"][0]["challenge_id"]
    assert (
        main(
            [
                "challenge",
                str(surface),
                "--repo",
                str(repo),
                "--claim-id",
                import_edge["id"],
                "--competing-reading",
                "The same surface import may indicate a second live runtime interpretation.",
                "--evidence",
                import_edge["citations"][0],
                "--rationale",
                "A second reviewer wants a live competing reading preserved.",
            ]
        )
        == 0
    )
    challenged = json.loads(surface.read_text(encoding="utf-8"))
    challenged_edge = next(edge for edge in challenged["edges"] if edge["id"] == import_edge["id"])
    live_challenge_id = challenged_edge["challenges"][1]["challenge_id"]
    assert (
        main(
            [
                "resolve-challenge",
                str(surface),
                "--repo",
                str(repo),
                "--challenge-id",
                withdrawn_challenge_id,
                "--status",
                "withdrawn",
                "--resolution",
                "The first reviewer withdrew this reading; the second challenge remains live.",
            ]
        )
        == 0
    )
    assert main(["authority-map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["dependency-graph", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["verify-map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["synthesis-index", "--repo", str(repo), "--run-id", run_id]) == 0

    synthesis_data = json.loads((run_dir / "synthesis-index.json").read_text(encoding="utf-8"))
    challenged_claims = synthesis_data["contestation"]["challenged_claims"]
    assert any(
        item["artifact_path"].endswith("surface-map.json") and item["claim_id"] == import_edge["id"]
        for item in challenged_claims
    )
    surface_claim = next(
        item
        for item in challenged_claims
        if item["artifact_path"].endswith("surface-map.json") and item["claim_id"] == import_edge["id"]
    )
    assert surface_claim["challenge_ids"] == [live_challenge_id]


def test_check_evidence_enforces_claim_requirements(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-evidence-check"
    assert main(["init", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    assert main(["map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["surface", "--repo", str(repo), "--run-id", run_id]) == 0

    surface = repo / ".research" / run_id / "surface-map.json"
    assert main(["check-evidence", str(surface), "--repo", str(repo)]) == 0
    data = json.loads(surface.read_text(encoding="utf-8"))
    import_edge = next(edge for edge in data["edges"] if edge["kind"] == "import")
    import_edge["evidence_kinds"] = ["static_structure"]
    invalid_surface = repo / ".research" / run_id / "surface-map.invalid-evidence.json"
    invalid_surface.write_text(json.dumps(data, indent=2), encoding="utf-8")
    assert main(["validate", str(invalid_surface), "--repo", str(repo)]) == 0
    assert main(["check-evidence", str(invalid_surface), "--repo", str(repo)]) == 2

    data = json.loads(surface.read_text(encoding="utf-8"))
    import_edge = next(edge for edge in data["edges"] if edge["kind"] == "import")
    import_edge["extractor_id"] = "ext-unregistered-v1"
    invalid_extractor = repo / ".research" / run_id / "surface-map.invalid-extractor.json"
    invalid_extractor.write_text(json.dumps(data, indent=2), encoding="utf-8")
    assert main(["validate", str(invalid_extractor), "--repo", str(repo)]) == 0
    assert main(["check-evidence", str(invalid_extractor), "--repo", str(repo)]) == 2
    assert main(["gate-artifact", str(invalid_extractor), "--repo", str(repo)]) == 2

    data = json.loads(surface.read_text(encoding="utf-8"))
    import_edge = next(edge for edge in data["edges"] if edge["kind"] == "import")
    import_edge["evidence_kinds"] = ["static_relation", "command_output"]
    unsupported_evidence = repo / ".research" / run_id / "surface-map.unsupported-extractor-evidence.json"
    unsupported_evidence.write_text(json.dumps(data, indent=2), encoding="utf-8")
    assert main(["validate", str(unsupported_evidence), "--repo", str(repo)]) == 0
    assert main(["check-evidence", str(unsupported_evidence), "--repo", str(repo)]) == 2
    assert main(["gate-artifact", str(unsupported_evidence), "--repo", str(repo)]) == 2
    report = repo / ".research" / run_id / "verify-report.json"
    assert main(["verify", str(unsupported_evidence), "--repo", str(repo), "--output", str(report)]) == 2
    verify_report = json.loads(report.read_text(encoding="utf-8"))
    assert verify_report["summary"]["claim_evidence_errors"] >= 1

    registry = repo / ".research" / run_id / "extractor-registry.json"
    registry_data = json.loads(registry.read_text(encoding="utf-8"))
    registry_data["extractors"][1]["id"] = registry_data["extractors"][0]["id"]
    registry.write_text(json.dumps(registry_data, indent=2), encoding="utf-8")
    assert main(["validate", str(surface), "--repo", str(repo)]) == 0
    assert main(["check-evidence", str(surface), "--repo", str(repo)]) == 2
    assert main(["gate-artifact", str(surface), "--repo", str(repo)]) == 2
    assert main(["verify", str(surface), "--repo", str(repo), "--output", str(report)]) == 2
    verify_report = json.loads(report.read_text(encoding="utf-8"))
    assert verify_report["summary"]["extractor_registry_errors"] == 1


def test_gate_artifact_runs_schema_citation_and_evidence_checks(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-gate-artifact"
    assert main(["init", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    assert main(["map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["surface", "--repo", str(repo), "--run-id", run_id]) == 0

    surface = repo / ".research" / run_id / "surface-map.json"
    assert main(["gate-artifact", str(surface), "--repo", str(repo)]) == 0
    data = json.loads(surface.read_text(encoding="utf-8"))
    call_edge = next(edge for edge in data["edges"] if edge["kind"] == "call")
    call_edge["citations"] = ["missing.py:1@abcdef1"]
    call_edge["evidence_kinds"] = ["static_structure"]
    bad_surface = repo / ".research" / run_id / "surface-map.bad-gate.json"
    bad_surface.write_text(json.dumps(data, indent=2), encoding="utf-8")
    assert main(["gate-artifact", str(bad_surface), "--repo", str(repo)]) == 2


def test_challenge_adds_human_challenge_to_claim(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-human-challenge"
    assert main(["init", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    assert main(["map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["surface", "--repo", str(repo), "--run-id", run_id]) == 0

    surface = repo / ".research" / run_id / "surface-map.json"
    data = json.loads(surface.read_text(encoding="utf-8"))
    import_edge = next(edge for edge in data["edges"] if edge["kind"] == "import")
    citation = import_edge["citations"][0]
    assert (
        main(
            [
                "challenge",
                str(surface),
                "--repo",
                str(repo),
                "--claim-id",
                import_edge["id"],
                "--competing-reading",
                "The import relation may be setup-only rather than evidence of the primary runtime path.",
                "--evidence",
                citation,
                "--axis",
                "scope",
                "--relation",
                "scope_dispute",
                "--rationale",
                "A reviewer needs this alternative preserved before using the import as a planning dependency.",
                "--raised-by",
                "human-reviewer",
            ]
        )
        == 0
    )
    challenged = json.loads(surface.read_text(encoding="utf-8"))
    updated = next(edge for edge in challenged["edges"] if edge["id"] == import_edge["id"])
    assert updated["claim_status"] == "challenged"
    assert updated["challenges"][0]["raised_by"] == "human-reviewer"
    challenge_id = updated["challenges"][0]["challenge_id"]
    assert main(["gate-artifact", str(surface), "--repo", str(repo)]) == 0
    assert (
        main(
            [
                "resolve-challenge",
                str(surface),
                "--repo",
                str(repo),
                "--challenge-id",
                challenge_id,
                "--status",
                "withdrawn",
                "--resolution",
                "Reviewer withdrew the challenge after confirming the import is the relevant planning relation.",
                "--resolved-by",
                "human-reviewer",
            ]
        )
        == 0
    )
    resolved = json.loads(surface.read_text(encoding="utf-8"))
    resolved_edge = next(edge for edge in resolved["edges"] if edge["id"] == import_edge["id"])
    assert resolved_edge["claim_status"] == "active"
    assert resolved_edge["challenges"][0]["status"] == "withdrawn"
    ledger_entries = [
        json.loads(line)
        for line in (repo / ".research" / run_id / "evidence-ledger.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert any(entry["entry_kind"] == "claim_challenged" and entry["claim_id"] == import_edge["id"] for entry in ledger_entries)
    assert any(entry["entry_kind"] == "challenge_resolved" and entry["challenge_id"] == challenge_id for entry in ledger_entries)
    assert main(["handoff", "--repo", str(repo), "--run-id", run_id]) == 0
    card_frontmatter = yaml.safe_load(
        (repo / ".research" / run_id / "findings" / "int-0001.md").read_text(encoding="utf-8").split("---", 2)[1]
    )
    dependent_claim_ids = {item["claim_id"] for item in card_frontmatter["dependent_challenges"]}
    assert import_edge["id"] not in dependent_claim_ids
    assert dependent_claim_ids == set()
    assert card_frontmatter["confidence_rationale"] == "Confidence is low because dependency closure remains unknown at edge-unknown-001."


def test_handoff_rejects_evidence_invalid_surface(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-handoff-evidence-check"
    assert main(["init", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    assert main(["map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["surface", "--repo", str(repo), "--run-id", run_id]) == 0

    surface = repo / ".research" / run_id / "surface-map.json"
    data = json.loads(surface.read_text(encoding="utf-8"))
    call_edge = next(edge for edge in data["edges"] if edge["kind"] == "call")
    call_edge["evidence_kinds"] = ["static_structure"]
    surface.write_text(json.dumps(data, indent=2), encoding="utf-8")
    assert main(["handoff", "--repo", str(repo), "--run-id", run_id]) == 1


def test_handoff_rejects_schema_invalid_listed_artifact(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-handoff-listed-artifact-schema-check"
    assert main(["init", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    assert main(["map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["surface", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["bind", "--repo", str(repo), "--run-id", run_id]) == 0

    project_type = repo / ".research" / run_id / "project-type.json"
    data = json.loads(project_type.read_text(encoding="utf-8"))
    data["artifact_type"] = "not_project_type_report"
    project_type.write_text(json.dumps(data, indent=2), encoding="utf-8")

    assert main(["handoff", "--repo", str(repo), "--run-id", run_id]) == 1
    handoff_frontmatter = yaml.safe_load((repo / ".research" / run_id / "handoff.md").read_text(encoding="utf-8").split("---", 2)[1])
    failed = handoff_frontmatter["gate_summary"]["schema_validation"]["failed_artifacts"]
    assert len(failed) == 1
    assert failed[0].endswith("project-type.json: artifact_type: 'project_type_report' was expected")


def test_handoff_summarizes_human_challenges(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-handoff-human-challenge"
    assert main(["init", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    assert main(["map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["surface", "--repo", str(repo), "--run-id", run_id]) == 0

    surface = repo / ".research" / run_id / "surface-map.json"
    data = json.loads(surface.read_text(encoding="utf-8"))
    import_edge = next(edge for edge in data["edges"] if edge["kind"] == "import")
    assert (
        main(
            [
                "challenge",
                str(surface),
                "--repo",
                str(repo),
                "--claim-id",
                import_edge["id"],
                "--competing-reading",
                "The import relation could be setup-only and should remain challenged in handoff.",
                "--evidence",
                import_edge["citations"][0],
                "--rationale",
                "A human reviewer wants this dependency interpretation preserved in final handoff.",
            ]
        )
        == 0
    )
    assert main(["handoff", "--repo", str(repo), "--run-id", run_id]) == 0
    run_dir = repo / ".research" / run_id
    frontmatter = yaml.safe_load((run_dir / "handoff.md").read_text(encoding="utf-8").split("---", 2)[1])
    assert frontmatter["contestation_summary"]["open_challenges"] == 1
    assert frontmatter["contestation_summary"]["claims_by_status"]["challenged"] == 1
    assert frontmatter["gate_summary"]["skeptic_review"]["challenges_logged"] == 1
    card_frontmatter = yaml.safe_load((run_dir / "findings" / "int-0001.md").read_text(encoding="utf-8").split("---", 2)[1])
    dependent_claim_ids = {item["claim_id"] for item in card_frontmatter["dependent_challenges"]}
    assert import_edge["id"] in dependent_claim_ids
    assert "edge-unknown-001" not in dependent_claim_ids
    assert card_frontmatter["confidence"] == "low"
    assert "selected goal-bound surface has live challenge(s)" in card_frontmatter["confidence_rationale"]


def test_deep_run_writes_workflow_trace(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    assert main(["run", "--repo", str(repo), "--goal", "add greeting behavior", "--goal-class", "feature_add", "--mode", "deep", "--run-id", "run-deep"]) == 0

    run_dir = repo / ".research" / "run-deep"
    trace = run_dir / "workflow-traces" / "trace-0001.json"
    handoff = run_dir / "handoff.md"
    assert trace.exists()
    assert main(["validate", str(trace), "--repo", str(repo)]) == 0
    assert main(["verify-citations", str(trace), "--repo", str(repo)]) == 0
    data = json.loads(trace.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "workflow_trace"
    assert data["goal_class"] == "feature_add"
    assert data["trigger"]["kind"] == "goal_binding"
    assert data["steps"][0]["path"] == "tests/test_app.py"
    assert data["steps"][1]["path"] == "src/app.py"
    assert data["steps"][1]["symbol"] == "hello"
    assert data["confidence"] == "low"

    frontmatter = yaml.safe_load(handoff.read_text(encoding="utf-8").split("---", 2)[1])
    assert "workflow_trace" in [artifact["artifact_type"] for artifact in frontmatter["artifacts"]]
    assert any(input_item["path"].endswith("workflow-traces/trace-0001.json") for input_item in frontmatter["inputs"])


def test_tracer_skill_is_shipped() -> None:
    skill = SOURCE_ROOT / "skills" / "tracer.md"
    text = skill.read_text(encoding="utf-8")
    assert "# Skill: Tracer" in text
    assert "schemas/workflow-trace.schema.json" in text
    assert "Do not mark challenges resolved without new evidence." in text


def test_platform_portability_docs_are_shipped() -> None:
    assert (SOURCE_ROOT / "platform" / "PORTABILITY.md").exists()
    assert (SOURCE_ROOT / "platform" / "codex" / "hooks.json").exists()
    live_hooks = json.loads((SOURCE_ROOT / ".codex" / "hooks.json").read_text(encoding="utf-8"))
    live_hook_commands = json.dumps(live_hooks)
    assert "python3 -m cbm hook-start" in live_hook_commands
    assert "python3 -m cbm hook-stop" in live_hook_commands
    hooks = json.loads((SOURCE_ROOT / "platform" / "codex" / "hooks.json").read_text(encoding="utf-8"))
    hook_commands = json.dumps(hooks)
    assert "python3 -m cbm hook-start" in hook_commands
    assert "python3 -m cbm hook-stop" in hook_commands
    codex_readme = (SOURCE_ROOT / "platform" / "codex" / "README.md").read_text(encoding="utf-8")
    assert "python3 -m cbm hook-start" in codex_readme
    assert "python3 -m cbm hook-stop" in codex_readme
    codex_gate = (SOURCE_ROOT / "platform" / "codex" / "gate-artifact.sh").read_text(encoding="utf-8")
    assert "python3 -m cbm gate-artifact" in codex_gate
    claude_readme = (SOURCE_ROOT / "platform" / "claude-code" / "README.md").read_text(encoding="utf-8")
    assert "python3 -m cbm hook-start" in claude_readme
    assert "python3 -m cbm hook-stop" in claude_readme
    assert "python3 -m cbm gate-artifact" in claude_readme
    assert "Artifact schemas, skills, CLI behavior, and citation format are unchanged." in claude_readme
    portability = (SOURCE_ROOT / "platform" / "PORTABILITY.md").read_text(encoding="utf-8")
    assert "python3 -m cbm hook-start" in portability
    assert "python3 -m cbm hook-stop" in portability


def test_deep_run_writes_refinement_report(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    assert main(["run", "--repo", str(repo), "--goal", "audit verification posture", "--goal-class", "audit", "--mode", "deep", "--run-id", "run-deep-refine"]) == 0

    run_dir = repo / ".research" / "run-deep-refine"
    report = run_dir / "refinements" / "refinement-0001.json"
    handoff = run_dir / "handoff.md"
    assert report.exists()
    assert main(["validate", str(report), "--repo", str(repo)]) == 0
    assert main(["verify-citations", str(report), "--repo", str(repo)]) == 0
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "refinement_report"
    assert data["next_round_required"] is True
    assert not any(item["source_kind"] == "skeptic_challenge" for item in data["refinements"])
    assert any(item["source_kind"] == "trace_unknown" and item["disposition"] == "needs_runtime_trace" for item in data["refinements"])
    assert any("tracer" in item["reentry_targets"] for item in data["refinements"])

    frontmatter = yaml.safe_load(handoff.read_text(encoding="utf-8").split("---", 2)[1])
    assert "refinement_report" in [artifact["artifact_type"] for artifact in frontmatter["artifacts"]]
    assert any(input_item["path"].endswith("refinements/refinement-0001.json") for input_item in frontmatter["inputs"])


def test_deep_run_writes_approval_plan(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    assert main(["run", "--repo", str(repo), "--goal", "add greeting behavior", "--goal-class", "feature_add", "--mode", "deep", "--run-id", "run-deep-approval"]) == 0

    run_dir = repo / ".research" / "run-deep-approval"
    plan = run_dir / "approvals" / "approval-plan.json"
    handoff = run_dir / "handoff.md"
    assert plan.exists()
    assert main(["validate", str(plan), "--repo", str(repo)]) == 0
    data = json.loads(plan.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "approval_plan"
    assert any(item["approval_kind"] == "command_execution" and item["approval_status"] == "pending" for item in data["approval_items"])
    assert any(item["approval_kind"] == "manual_review" and item["approval_status"] == "pending" for item in data["approval_items"])
    assert all("safety_envelope" in item for item in data["approval_items"])

    frontmatter = yaml.safe_load(handoff.read_text(encoding="utf-8").split("---", 2)[1])
    assert "approval_plan" in [artifact["artifact_type"] for artifact in frontmatter["artifacts"]]
    assert any(input_item["path"].endswith("approvals/approval-plan.json") for input_item in frontmatter["inputs"])


def test_stop_hook_validates_latest_handoff(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--run-id", "run-hook"]) == 0

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"cwd": str(repo)})))
    assert main(["hook-stop", "--repo", str(repo)]) == 0
    output = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert output["continue"] is True
    assert "passed" in output["systemMessage"]


def test_stop_hook_rejects_stale_handoff_inputs(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--run-id", "run-hook-stale"]) == 0

    surface = repo / ".research" / "run-hook-stale" / "surface-map.json"
    data = json.loads(surface.read_text(encoding="utf-8"))
    data["unknowns"]["summary"] = "mutated after handoff"
    surface.write_text(json.dumps(data, indent=2), encoding="utf-8")

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"cwd": str(repo)})))
    assert main(["hook-stop", "--repo", str(repo)]) == 0
    output = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert output["continue"] is False
    assert "input hash changed" in output["systemMessage"]


def test_stop_hook_rejects_card_gate_failure_even_with_fresh_hash(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")
    run_id = "run-hook-card-gate"
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0

    run_dir = repo / ".research" / run_id
    card = run_dir / "findings" / "int-0001.md"
    text = card.read_text(encoding="utf-8")
    _, frontmatter, body = text.split("---", 2)
    card_data = yaml.safe_load(frontmatter)
    card_data["confidence"] = "high"
    card.write_text("---\n" + yaml.safe_dump(card_data, sort_keys=False) + "---" + body, encoding="utf-8")

    handoff = run_dir / "handoff.md"
    handoff_text = handoff.read_text(encoding="utf-8")
    _, handoff_frontmatter, handoff_body = handoff_text.split("---", 2)
    handoff_data = yaml.safe_load(handoff_frontmatter)
    for input_item in handoff_data["inputs"]:
        if input_item["path"].endswith("findings/int-0001.md"):
            input_item["sha256"] = sha256_file(card)
    handoff.write_text("---\n" + yaml.safe_dump(handoff_data, sort_keys=False) + "---" + handoff_body, encoding="utf-8")

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"cwd": str(repo)})))
    assert main(["hook-stop", "--repo", str(repo)]) == 0
    output = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert output["continue"] is False
    assert "confidence" in output["systemMessage"]


def test_stop_hook_rejects_mutated_evidence_ledger(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")
    run_id = "run-hook-ledger-tamper"
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0

    ledger = repo / ".research" / run_id / "evidence-ledger.jsonl"
    lines = ledger.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["claim_id"] = "tampered-after-handoff"
    lines[0] = json.dumps(first)
    ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"cwd": str(repo)})))
    assert main(["hook-stop", "--repo", str(repo)]) == 0
    output = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert output["continue"] is False
    assert "ledger append-only verification failed" in output["systemMessage"]


def test_start_hook_rejects_stale_input_citations(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")
    run_id = "run-hook-start"
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"cwd": str(repo)})))
    assert main(["hook-start", "--repo", str(repo)]) == 0
    output = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert output["continue"] is True
    assert "passed" in output["systemMessage"]

    (repo / "tests" / "test_app.py").write_text(
        "from src.app import hello\n\n# changed after handoff\n\ndef test_hello():\n    assert hello() == 'hello'\n",
        encoding="utf-8",
    )
    git(repo, "add", "tests/test_app.py")
    git(repo, "commit", "-m", "change cited source after handoff")

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"cwd": str(repo)})))
    assert main(["hook-start", "--repo", str(repo)]) == 0
    output = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert output["continue"] is False
    assert "input citation stale" in output["systemMessage"]


def test_start_hook_rejects_mutated_evidence_ledger(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")
    run_id = "run-hook-start-ledger-tamper"
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0

    ledger = repo / ".research" / run_id / "evidence-ledger.jsonl"
    lines = ledger.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["claim_id"] = "tampered-before-resume"
    lines[0] = json.dumps(first)
    ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"cwd": str(repo)})))
    assert main(["hook-start", "--repo", str(repo)]) == 0
    output = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert output["continue"] is False
    assert "ledger append-only verification failed" in output["systemMessage"]


def test_hooks_can_validate_explicit_run_id(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--run-id", "run-explicit-old"]) == 0
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--run-id", "run-explicit-new"]) == 0

    ledger = repo / ".research" / "run-explicit-old" / "evidence-ledger.jsonl"
    lines = ledger.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["claim_id"] = "tampered-explicit-run"
    lines[0] = json.dumps(first)
    ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"cwd": str(repo)})))
    assert main(["hook-start", "--repo", str(repo), "--run-id", "run-explicit-old"]) == 0
    output = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert output["continue"] is False
    assert "run-explicit-old" in output["stopReason"]
    assert "ledger append-only verification failed" in output["systemMessage"]

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"cwd": str(repo)})))
    assert main(["hook-stop", "--repo", str(repo), "--run-id", "run-explicit-new"]) == 0
    output = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert output["continue"] is True
    assert "run-explicit-new" in output["systemMessage"]


def test_hooks_reject_missing_explicit_run_id(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"cwd": str(repo)})))
    assert main(["hook-start", "--repo", str(repo), "--run-id", "run-missing"]) == 0
    output = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert output["continue"] is False
    assert "run-missing" in output["stopReason"]

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"cwd": str(repo)})))
    assert main(["hook-stop", "--repo", str(repo), "--run-id", "run-missing"]) == 0
    output = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert output["continue"] is False
    assert "run-missing" in output["stopReason"]


def test_ledger_integrity_detects_mutated_existing_line(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-ledger-tamper"
    assert main(["init", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    assert main(["map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["surface", "--repo", str(repo), "--run-id", run_id]) == 0

    ledger = repo / ".research" / run_id / "evidence-ledger.jsonl"
    lines = ledger.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["claim_id"] = "tampered"
    lines[0] = json.dumps(first)
    ledger.write_text("\n".join(lines) + "\n", encoding="utf-8")

    assert main(["handoff", "--repo", str(repo), "--run-id", run_id]) == 1


def test_handoff_rejects_missing_ledger_integrity_manifest(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-ledger-sidecar-missing"
    assert main(["init", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    assert main(["map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["surface", "--repo", str(repo), "--run-id", run_id]) == 0

    (repo / ".research" / run_id / "evidence-ledger.jsonl.integrity.json").unlink()

    assert main(["handoff", "--repo", str(repo), "--run-id", run_id]) == 1


def test_stop_hook_rejects_mutated_uncertainty_register(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")
    run_id = "run-uncertainty-tamper"
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0

    register = repo / ".research" / run_id / "uncertainty-register.jsonl"
    lines = register.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["status"] = "closed"
    lines[0] = json.dumps(first)
    register.write_text("\n".join(lines) + "\n", encoding="utf-8")

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"cwd": str(repo)})))
    assert main(["hook-stop", "--repo", str(repo)]) == 0
    output = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert output["continue"] is False
    assert "uncertainty register append-only verification failed" in output["systemMessage"]


def test_stop_hook_rejects_missing_uncertainty_integrity_manifest(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")
    run_id = "run-uncertainty-sidecar-missing"
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0

    (repo / ".research" / run_id / "uncertainty-register.jsonl.integrity.json").unlink()

    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({"cwd": str(repo)})))
    assert main(["hook-stop", "--repo", str(repo)]) == 0
    output = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert output["continue"] is False
    assert "uncertainty register append-only verification failed" in output["systemMessage"]
    assert "integrity manifest is missing" in output["systemMessage"]


def test_stale_detects_changed_input_and_dependent_path(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-stale"
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    run_dir = repo / ".research" / run_id
    card = run_dir / "findings" / "int-0001.md"
    surface = run_dir / "surface-map.json"
    assert main(["stale", str(card), "--repo", str(repo)]) == 0

    (repo / "tests" / "test_app.py").write_text("from src.app import hello\n\n# changed\n", encoding="utf-8")
    assert main(["stale", str(surface), "--repo", str(repo)]) == 2
    assert main(["stale", str(card), "--repo", str(repo)]) == 2


def test_validate_fresh_and_verify_track_head_movement(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-freshness"
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    card = repo / ".research" / run_id / "findings" / "int-0001.md"
    report = repo / ".research" / run_id / "verify-report.json"
    assert main(["validate-fresh", str(card), "--repo", str(repo)]) == 0
    assert main(["verify", str(card), "--repo", str(repo), "--output", str(report)]) == 0

    (repo / "tests" / "test_app.py").write_text("from src.app import hello\n\n# changed but line survives\n", encoding="utf-8")
    git(repo, "add", "tests/test_app.py")
    git(repo, "commit", "-m", "change cited file")
    assert main(["validate-fresh", str(card), "--repo", str(repo)]) == 2
    assert main(["verify", str(card), "--repo", str(repo), "--output", str(report)]) == 2
    verify_report = json.loads(report.read_text(encoding="utf-8"))
    assert verify_report["summary"]["needs_review"] == 1
    assert verify_report["summary"]["broken"] == 0

    git(repo, "rm", "tests/test_app.py")
    git(repo, "commit", "-m", "remove cited file")
    assert main(["verify", str(card), "--repo", str(repo), "--output", str(report)]) == 2
    verify_report = json.loads(report.read_text(encoding="utf-8"))
    assert verify_report["summary"]["broken"] == 1


def test_verify_commands_reject_artifacts_without_citations(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-no-citations"
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    run_dir = repo / ".research" / run_id
    report = run_dir / "verify-report.json"
    artifact = run_dir / "uncited.md"
    artifact.write_text(
        "---\n"
        "schema_version: '1.2'\n"
        "artifact_type: consultation\n"
        "consultation_id: con-no-citations\n"
        "produced_at: '2026-05-01T00:00:00Z'\n"
        "question: uncited\n"
        "status: answered\n"
        "matches: []\n"
        "---\n# Uncited\n\nThis artifact has no citations.\n",
        encoding="utf-8",
    )

    assert main(["verify-citations", str(artifact), "--repo", str(repo)]) == 1
    assert main(["validate-fresh", str(artifact), "--repo", str(repo)]) == 2
    assert main(["gate-artifact", str(artifact), "--repo", str(repo)]) == 2
    assert main(["verify", str(artifact), "--repo", str(repo), "--output", str(report)]) == 2
    verify_report = json.loads(report.read_text(encoding="utf-8"))
    assert verify_report["summary"]["missing_citations"] == 1


def test_verify_reports_missing_card_contestation(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-verify-contestation"
    assert main(["init", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    assert main(["map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["surface", "--repo", str(repo), "--run-id", run_id]) == 0
    run_dir = repo / ".research" / run_id
    surface = run_dir / "surface-map.json"
    surface_data = json.loads(surface.read_text(encoding="utf-8"))
    import_edge = next(edge for edge in surface_data["edges"] if edge["kind"] == "import")
    assert (
        main(
            [
                "challenge",
                str(surface),
                "--repo",
                str(repo),
                "--claim-id",
                import_edge["id"],
                "--competing-reading",
                "The import relation should remain challenged for card propagation verification.",
                "--evidence",
                import_edge["citations"][0],
                "--rationale",
                "The verify command should fail if the card drops this live challenge.",
            ]
        )
        == 0
    )
    assert main(["bind", "--repo", str(repo), "--run-id", run_id, "--goal", "understand this repo"]) == 0
    assert main(["handoff", "--repo", str(repo), "--run-id", run_id]) == 0
    card = run_dir / "findings" / "int-0001.md"
    report = run_dir / "verify-report.json"
    assert main(["verify", str(card), "--repo", str(repo), "--output", str(report)]) == 0

    text = card.read_text(encoding="utf-8")
    _, frontmatter, body = text.split("---", 2)
    card_data = yaml.safe_load(frontmatter)
    primary_path = card_data["primary_files"][0]["path"]
    wrong_citation = next(
        citation
        for claim in [*surface_data["authorities"], *surface_data["edges"]]
        for citation in claim.get("citations", [])
        if not citation.startswith(f"{primary_path}:")
    )
    card_data["primary_files"][0]["citations"] = [wrong_citation]
    card.write_text("---\n" + yaml.safe_dump(card_data, sort_keys=False) + "---" + body, encoding="utf-8")
    assert main(["gate-artifact", str(card), "--repo", str(repo)]) == 2
    assert main(["verify", str(card), "--repo", str(repo), "--output", str(report)]) == 2
    verify_report = json.loads(report.read_text(encoding="utf-8"))
    assert verify_report["summary"]["coverage_violations"] == 1

    card.write_text(text, encoding="utf-8")
    _, frontmatter, body = text.split("---", 2)
    card_data = yaml.safe_load(frontmatter)
    card_data["coverage"]["result"]["files_unread_in_scope"] = 0
    card.write_text("---\n" + yaml.safe_dump(card_data, sort_keys=False) + "---" + body, encoding="utf-8")
    assert main(["gate-artifact", str(card), "--repo", str(repo)]) == 2
    assert main(["verify", str(card), "--repo", str(repo), "--output", str(report)]) == 2
    verify_report = json.loads(report.read_text(encoding="utf-8"))
    assert verify_report["summary"]["coverage_violations"] == 1

    card.write_text(text, encoding="utf-8")
    _, frontmatter, body = text.split("---", 2)
    card_data = yaml.safe_load(frontmatter)
    card_data["coverage"]["result"]["files_examined_directly"] = 0
    card_data["coverage"]["result"]["files_unread_in_scope"] = card_data["coverage"]["result"]["files_in_scope"]
    card.write_text("---\n" + yaml.safe_dump(card_data, sort_keys=False) + "---" + body, encoding="utf-8")
    assert main(["gate-artifact", str(card), "--repo", str(repo)]) == 2
    assert main(["verify", str(card), "--repo", str(repo), "--output", str(report)]) == 2
    verify_report = json.loads(report.read_text(encoding="utf-8"))
    assert verify_report["summary"]["coverage_violations"] == 1

    card.write_text(text, encoding="utf-8")
    _, frontmatter, body = text.split("---", 2)
    card_data = yaml.safe_load(frontmatter)
    for item in card_data["dependent_challenges"]:
        if item["claim_id"] == import_edge["id"]:
            item["challenge_ids"].append("chl-99999")
    card.write_text("---\n" + yaml.safe_dump(card_data, sort_keys=False) + "---" + body, encoding="utf-8")
    assert main(["gate-artifact", str(card), "--repo", str(repo)]) == 2
    assert main(["verify", str(card), "--repo", str(repo), "--output", str(report)]) == 2
    verify_report = json.loads(report.read_text(encoding="utf-8"))
    assert verify_report["summary"]["contestation_stale"] == 1
    assert verify_report["contestation_propagation"]["stale"][0]["stale_challenge_ids"] == ["chl-99999"]

    card.write_text(text, encoding="utf-8")
    _, frontmatter, body = text.split("---", 2)
    card_data = yaml.safe_load(frontmatter)
    card_data["confidence"] = "high"
    card.write_text("---\n" + yaml.safe_dump(card_data, sort_keys=False) + "---" + body, encoding="utf-8")
    assert main(["gate-artifact", str(card), "--repo", str(repo)]) == 2
    assert main(["verify", str(card), "--repo", str(repo), "--output", str(report)]) == 2
    verify_report = json.loads(report.read_text(encoding="utf-8"))
    assert verify_report["summary"]["confidence_violations"] == 2
    card_data["confidence"] = "low"
    card_data["dependent_challenges"] = [
        item for item in card_data["dependent_challenges"] if item["claim_id"] != import_edge["id"]
    ]
    card.write_text("---\n" + yaml.safe_dump(card_data, sort_keys=False) + "---" + body, encoding="utf-8")
    assert main(["gate-artifact", str(card), "--repo", str(repo)]) == 2
    assert main(["verify", str(card), "--repo", str(repo), "--output", str(report)]) == 2
    verify_report = json.loads(report.read_text(encoding="utf-8"))
    assert verify_report["summary"]["contestation_missing"] == 1
    missing = verify_report["contestation_propagation"]["missing"][0]
    assert missing["claim_id"] == import_edge["id"]


def test_corpus_status_writes_manifest(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-corpus"
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    manifest = repo / ".research" / "corpus-status.json"
    assert main(["corpus-status", "--repo", str(repo), "--output", str(manifest)]) == 0
    status = json.loads(manifest.read_text(encoding="utf-8"))
    assert status["summary"]["fresh"] >= 1
    assert status["summary"]["missing_citations"] == 0
    assert any(item["artifact_type"] == "goal_binding" for item in status["artifacts"])

    (repo / "tests" / "test_app.py").write_text(
        "from src.app import hello\n\n# changed for corpus status\n\ndef test_hello():\n    assert hello() == 'hello'\n",
        encoding="utf-8",
    )
    git(repo, "add", "tests/test_app.py")
    git(repo, "commit", "-m", "move head for corpus status")
    assert main(["corpus-status", "--repo", str(repo), "--output", str(manifest)]) == 0
    status = json.loads(manifest.read_text(encoding="utf-8"))
    assert status["summary"]["stale"] >= 1
    stale_items = [item for item in status["artifacts"] if item["freshness"] == "stale"]
    assert all(item["historical_valid"] for item in stale_items)


def test_corpus_status_marks_uncited_answered_artifacts_broken(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-corpus-uncited"
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    uncited = repo / ".research" / run_id / "consultation-uncited.md"
    uncited.write_text(
        "---\n"
        "schema_version: '1.2'\n"
        "artifact_type: consultation\n"
        "consultation_id: con-corpus-uncited\n"
        "produced_at: '2026-05-01T00:00:00Z'\n"
        "question: uncited\n"
        "status: answered\n"
        "matches: []\n"
        "---\n# Uncited\n\nThis answered consultation has no citations.\n",
        encoding="utf-8",
    )
    manifest = repo / ".research" / "corpus-status.json"
    assert main(["corpus-status", "--repo", str(repo), "--output", str(manifest)]) == 2
    status = json.loads(manifest.read_text(encoding="utf-8"))
    uncited_status = next(item for item in status["artifacts"] if item["path"].endswith("consultation-uncited.md"))
    assert uncited_status["freshness"] == "broken"
    assert uncited_status["historical_valid"] is False
    assert uncited_status["citation_summary"]["missing_citations"] == 1
    assert status["summary"]["missing_citations"] == 1


def test_structural_refresh_emits_successor_and_delta(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-refresh"
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    old_map = repo / ".research" / run_id / "codebase-map.json"

    (repo / "src" / "new_module.py").write_text("VALUE = 1\n", encoding="utf-8")
    git(repo, "add", "src/new_module.py")
    git(repo, "commit", "-m", "add new module")
    assert main(["refresh", str(old_map), "--repo", str(repo), "--mode", "structural"]) == 0

    refresh_dir = repo / ".research" / run_id / "refreshes"
    successor = next(refresh_dir.glob("codebase-map-*.json"))
    delta = next(refresh_dir.glob("refresh-delta-structural-*.json"))
    assert main(["validate", str(successor), "--repo", str(repo)]) == 0
    assert main(["validate", str(delta), "--repo", str(repo)]) == 0
    delta_data = json.loads(delta.read_text(encoding="utf-8"))
    assert any(item["successor_claim_id"] == "file:src/new_module.py" for item in delta_data["newly_added"])
    assert any(item["register_id"] == "unc-00001" and item["post_refresh_status"] == "still_open" for item in delta_data["open_questions_reconciled"])
    successor_data = json.loads(successor.read_text(encoding="utf-8"))
    assert successor_data["refreshed_from"]["refresh_delta_path"].endswith(delta.name)


def test_interpretive_refresh_emits_successor_surface_and_delta(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-interpretive-refresh"
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    old_surface = repo / ".research" / run_id / "surface-map.json"
    old_surface_data = json.loads(old_surface.read_text(encoding="utf-8"))
    unknown_edge = next(edge for edge in old_surface_data["edges"] if edge["kind"] == "unknown")
    import_edge = next(edge for edge in old_surface_data["edges"] if edge["kind"] == "import")
    assert (
        main(
            [
                "challenge",
                str(old_surface),
                "--repo",
                str(repo),
                "--claim-id",
                unknown_edge["id"],
                "--competing-reading",
                "The unknown dependency edge should remain explicit across refresh until a later mapper resolves it.",
                "--evidence",
                import_edge["citations"][0],
                "--rationale",
                "Refresh should carry forward unresolved human challenges instead of fabricating Skeptic output.",
            ]
        )
        == 0
    )
    challenged_surface = json.loads(old_surface.read_text(encoding="utf-8"))
    challenge_id = next(edge for edge in challenged_surface["edges"] if edge["id"] == unknown_edge["id"])["challenges"][0]["challenge_id"]

    (repo / "src" / "util.py").write_text("VALUE = 'hello'\n", encoding="utf-8")
    (repo / "src" / "app.py").write_text("from src.util import VALUE\n\n\ndef hello():\n    return VALUE\n", encoding="utf-8")
    (repo / "tests" / "test_app.py").write_text("from src.app import hello\n\n# changed evidence file\n\ndef test_hello():\n    assert hello() == 'hello'\n", encoding="utf-8")
    git(repo, "add", "src/app.py", "src/util.py", "tests/test_app.py")
    git(repo, "commit", "-m", "change app import surface")

    assert main(["refresh", str(old_surface), "--repo", str(repo), "--mode", "interpretive"]) == 0

    refresh_dir = repo / ".research" / run_id / "refreshes"
    successor = next(refresh_dir.glob("surface-map-*.json"))
    delta = next(refresh_dir.glob("refresh-delta-interpretive-*.json"))
    assert main(["validate", str(successor), "--repo", str(repo)]) == 0
    assert main(["validate", str(delta), "--repo", str(repo)]) == 0
    successor_data = json.loads(successor.read_text(encoding="utf-8"))
    delta_data = json.loads(delta.read_text(encoding="utf-8"))
    assert successor_data["refreshed_from"]["refresh_mode"] == "interpretive"
    assert successor_data["refreshed_from"]["refresh_delta_path"].endswith(delta.name)
    assert any(edge["to"]["path"] == "src/util.py" for edge in successor_data["edges"] if edge["kind"] == "import")
    assert delta_data["refresh_mode"] == "interpretive"
    assert any(item["claim_id"] == "edge-import-001" for item in delta_data["updated"])
    assert any(item["successor_claim_id"].startswith("edge-import-") for item in delta_data["newly_added"])
    assert any(item["challenge_id"] == challenge_id and item["post_refresh_status"] == "still_active" for item in delta_data["challenges_carried_forward"])
    assert any(item["register_id"] == "unc-00001" and item["post_refresh_status"] == "still_open" for item in delta_data["open_questions_reconciled"])


def test_interpretive_refresh_marks_replaced_challenge_resolved(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-refresh-replacement"
    assert main(["init", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    assert main(["map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["surface", "--repo", str(repo), "--run-id", run_id]) == 0
    old_surface = repo / ".research" / run_id / "surface-map.json"
    surface_data = json.loads(old_surface.read_text(encoding="utf-8"))
    import_edge = next(edge for edge in surface_data["edges"] if edge["kind"] == "import")
    assert (
        main(
            [
                "challenge",
                str(old_surface),
                "--repo",
                str(repo),
                "--claim-id",
                import_edge["id"],
                "--competing-reading",
                "The imported target may be a placeholder that refresh should replace if the test imports a different module.",
                "--evidence",
                import_edge["citations"][0],
                "--rationale",
                "A refresh should preserve whether this disputed edge survives or is replaced.",
            ]
        )
        == 0
    )
    challenged_surface = json.loads(old_surface.read_text(encoding="utf-8"))
    challenged_import = next(edge for edge in challenged_surface["edges"] if edge["id"] == import_edge["id"])
    challenge_id = challenged_import["challenges"][0]["challenge_id"]

    (repo / "src" / "util.py").write_text("def hello():\n    return 'hello'\n", encoding="utf-8")
    (repo / "tests" / "test_app.py").write_text("from src.util import hello\n\n\ndef test_hello():\n    assert hello() == 'hello'\n", encoding="utf-8")
    git(repo, "add", "src/util.py", "tests/test_app.py")
    git(repo, "commit", "-m", "replace test import target")

    assert main(["refresh", str(old_surface), "--repo", str(repo), "--mode", "interpretive"]) == 0

    delta = next((repo / ".research" / run_id / "refreshes").glob("refresh-delta-interpretive-*.json"))
    assert main(["validate", str(delta), "--repo", str(repo)]) == 0
    delta_data = json.loads(delta.read_text(encoding="utf-8"))
    replaced = next(item for item in delta_data["retracted"] if item["claim_id"] == import_edge["id"])
    assert replaced["superseded_by"].startswith("edge-import-")
    assert any(
        item["challenge_id"] == challenge_id and item["post_refresh_status"] == "resolved_by_refresh"
        for item in delta_data["challenges_carried_forward"]
    )


def test_consult_answers_from_fresh_corpus_and_refuses_missing_question(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--run-id", "run-consult"]) == 0

    assert main(["consult", "src/app.py", "--repo", str(repo)]) == 0
    consultations = sorted((repo / ".research" / "consultations").glob("*.md"))
    answered = consultations[-1]
    answered_frontmatter = yaml.safe_load(answered.read_text(encoding="utf-8").split("---", 2)[1])
    assert answered_frontmatter["status"] == "answered"
    assert answered_frontmatter["matches"]
    assert all(match["citations"] for match in answered_frontmatter["matches"])
    assert any("src/app.py" in json.dumps(match) for match in answered_frontmatter["matches"])
    surfaced = {
        citation
        for match in answered_frontmatter["matches"]
        for citation in match["citations"]
    }
    ledger_entries = [
        json.loads(line)
        for line in (repo / ".research" / "run-consult" / "evidence-ledger.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    reused = [
        entry
        for entry in ledger_entries
        if entry["entry_kind"] == "citation_reused" and entry["agent"] == "cbm-consult"
    ]
    assert surfaced <= {entry["citation"] for entry in reused}
    assert all(entry["artifact_path"] for entry in reused)
    integrity = json.loads((repo / ".research" / "run-consult" / "evidence-ledger.jsonl.integrity.json").read_text(encoding="utf-8"))
    assert integrity["line_count"] == len(ledger_entries)

    surface = repo / ".research" / "run-consult" / "surface-map.json"
    surface_data = json.loads(surface.read_text(encoding="utf-8"))
    unknown_edge = next(edge for edge in surface_data["edges"] if edge["id"] == "edge-unknown-001")
    import_edge = next(edge for edge in surface_data["edges"] if edge["kind"] == "import")
    assert (
        main(
            [
                "challenge",
                str(surface),
                "--repo",
                str(repo),
                "--claim-id",
                unknown_edge["id"],
                "--competing-reading",
                "The unknown dependency edge should remain visible to consultation users.",
                "--evidence",
                import_edge["citations"][0],
                "--rationale",
                "Consult should surface live human challenges from the corpus.",
            ]
        )
        == 0
    )
    assert main(["consult", "edge-unknown-001", "--repo", str(repo)]) == 0
    consultations = sorted((repo / ".research" / "consultations").glob("*.md"))
    challenged_answer = consultations[-1]
    challenged_text = challenged_answer.read_text(encoding="utf-8")
    challenged_frontmatter = yaml.safe_load(challenged_text.split("---", 2)[1])
    assert any(match.get("live_challenges") for match in challenged_frontmatter["matches"])
    assert "chl-" in challenged_text

    assert main(["consult", "nonexistent_surface_zzz", "--repo", str(repo)]) == 2
    consultations = sorted((repo / ".research" / "consultations").glob("*.md"))
    refused = consultations[-1]
    refused_frontmatter = yaml.safe_load(refused.read_text(encoding="utf-8").split("---", 2)[1])
    assert refused_frontmatter["status"] == "refused"
    assert refused_frontmatter["refusal_reason"] == "no_grounded_match"
    assert refused_frontmatter["matches"] == []
    uncertainties = [
        json.loads(line)
        for line in (repo / ".research" / "run-consult" / "uncertainty-register.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    refused_uncertainty = [
        item
        for item in uncertainties
        if item.get("registered_by") == "cbm-consult@0.1" and item.get("consultation_id") == refused_frontmatter["consultation_id"]
    ]
    assert refused_uncertainty
    uncertainty_integrity = json.loads((repo / ".research" / "run-consult" / "uncertainty-register.jsonl.integrity.json").read_text(encoding="utf-8"))
    assert uncertainty_integrity["line_count"] == len(uncertainties)
    ledger_entries = [
        json.loads(line)
        for line in (repo / ".research" / "run-consult" / "evidence-ledger.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert any(
        entry["entry_kind"] == "uncertainty_logged"
        and entry["agent"] == "cbm-consult"
        and entry["claim_id"] == refused_uncertainty[0]["entry_id"]
        for entry in ledger_entries
    )

    (repo / "src" / "app.py").write_text("def hello():\n    return 'hello changed'\n", encoding="utf-8")
    (repo / "tests" / "test_app.py").write_text(
        "from src.app import hello\n\n\ndef test_hello():\n    assert hello() == 'hello changed'\n",
        encoding="utf-8",
    )
    git(repo, "add", "src/app.py", "tests/test_app.py")
    git(repo, "commit", "-m", "change consulted source")
    assert main(["consult", "src/app.py", "--repo", str(repo)]) == 2
    consultations = sorted((repo / ".research" / "consultations").glob("*.md"))
    stale_refusal = consultations[-1]
    stale_text = stale_refusal.read_text(encoding="utf-8")
    stale_frontmatter = yaml.safe_load(stale_text.split("---", 2)[1])
    assert stale_frontmatter["status"] == "refused"
    assert stale_frontmatter["refusal_reason"] == "stale_corpus_match"
    assert stale_frontmatter["stale_matches"]
    assert "cbm-refresh" in stale_text


def test_run_gate_executes_declared_command_and_refuses_outside_envelope(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-gate"
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    surface = repo / ".research" / run_id / "surface-map.json"
    surface_data = json.loads(surface.read_text(encoding="utf-8"))
    citation = surface_data["edges"][0]["citations"][0]
    surface_data["verification"]["ci_gates"].extend(
        [
            {
                "name": "unit",
                "path": "tests/test_app.py",
                "kind": "test",
                "citations": [citation],
                "command": {
                    "runner": sys.executable,
                    "argv": ["-c", "print('gate-ok')"],
                    "cwd": ".",
                    "safety_envelope": {
                        "requires_network": False,
                        "requires_install": False,
                        "mutates_filesystem": False,
                        "max_duration_seconds": 5,
                    },
                },
            },
            {
                "name": "networked",
                "path": "tests/test_app.py",
                "kind": "test",
                "citations": [citation],
                "command": {
                    "runner": sys.executable,
                    "argv": ["-c", "print('network')"],
                    "cwd": ".",
                    "safety_envelope": {
                        "requires_network": True,
                        "requires_install": False,
                        "mutates_filesystem": False,
                        "max_duration_seconds": 5,
                    },
                },
            },
        ]
    )
    surface.write_text(json.dumps(surface_data, indent=2) + "\n", encoding="utf-8")
    assert main(["validate", str(surface), "--repo", str(repo)]) == 0

    assert main(["run-gate", "unit", "--repo", str(repo), "--run-id", run_id, "--max-duration", "10"]) == 0
    output = next((repo / ".research" / run_id / "command-outputs").glob("unit-*.txt"))
    assert "gate-ok" in output.read_text(encoding="utf-8")
    ledger_entries = [
        json.loads(line)
        for line in (repo / ".research" / run_id / "evidence-ledger.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert any(entry["entry_kind"] == "command_executed" and entry["command_id"] == "unit" for entry in ledger_entries)

    assert main(["run-gate", "networked", "--repo", str(repo), "--run-id", run_id, "--max-duration", "10"]) == 2


def test_verification_map_schema_can_drive_run_gate(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-verification-map"
    assert main(["run", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    run_dir = repo / ".research" / run_id
    surface = run_dir / "surface-map.json"
    surface_data = json.loads(surface.read_text(encoding="utf-8"))
    verification_map = {
        "schema_version": "1.2",
        "artifact_type": "verification_map",
        "run_id": run_id,
        "produced_at": "2026-05-01T00:00:00Z",
        "produced_by": "cbm-baseline-verification@0.1",
        "source_sha": surface_data["source_sha"],
        "inputs": [{"path": str(surface.relative_to(repo)), "sha256": "0" * 64}],
        "status": "draft",
        "coverage": surface_data["coverage"],
        "staleness": surface_data["staleness"],
        "ci_gates": [
            {
                "id": "vm-unit",
                "name": "Fixture unit gate",
                "path": "tests/test_app.py",
                "kind": "test",
                "citations": [surface_data["edges"][0]["citations"][0]],
                "command": {
                    "runner": sys.executable,
                    "argv": ["-c", "print('verification-map-ok')"],
                    "cwd": ".",
                    "safety_envelope": {
                        "requires_network": False,
                        "requires_install": False,
                        "mutates_filesystem": False,
                        "max_duration_seconds": 5,
                    },
                },
            }
        ],
    }
    verification_path = run_dir / "verification-map.json"
    verification_path.write_text(json.dumps(verification_map, indent=2) + "\n", encoding="utf-8")
    assert main(["validate", str(verification_path), "--repo", str(repo)]) == 0
    assert main(["run-gate", "vm-unit", "--repo", str(repo), "--run-id", run_id]) == 0
    output = next((run_dir / "command-outputs").glob("vm-unit-*.txt"))
    assert "verification-map-ok" in output.read_text(encoding="utf-8")


def test_verify_map_command_generates_declared_test_gate(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-verify-map"
    assert main(["init", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    assert main(["map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["verify-map", "--repo", str(repo), "--run-id", run_id]) == 0
    verification_map = repo / ".research" / run_id / "verification-map.json"
    assert main(["validate", str(verification_map), "--repo", str(repo)]) == 0
    data = json.loads(verification_map.read_text(encoding="utf-8"))
    assert data["ci_gates"][0]["id"] == "test-001"
    assert data["ci_gates"][0]["command"]["argv"][-1] == "tests/test_app.py"
    assert main(["run-gate", "test-001", "--repo", str(repo), "--run-id", run_id, "--max-duration", "120"]) == 0
    output = next((repo / ".research" / run_id / "command-outputs").glob("test-001-*.txt"))
    assert "1 passed" in output.read_text(encoding="utf-8")


def test_authority_map_command_splits_surface_authorities(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-authority-map"
    assert main(["init", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    assert main(["map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["surface", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["authority-map", "--repo", str(repo), "--run-id", run_id]) == 0
    authority_map = repo / ".research" / run_id / "authority-map.json"
    assert main(["validate", str(authority_map), "--repo", str(repo)]) == 0
    data = json.loads(authority_map.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "authority_map"
    assert data["inputs"][0]["path"].endswith("surface-map.json")
    assert data["authorities"][0]["claim_register"] in {"factual", "interpretive"}


def test_dependency_graph_command_splits_surface_edges(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-dependency-graph"
    assert main(["init", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    assert main(["map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["surface", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["dependency-graph", "--repo", str(repo), "--run-id", run_id]) == 0
    dependency_graph = repo / ".research" / run_id / "dependency-graph.json"
    assert main(["validate", str(dependency_graph), "--repo", str(repo)]) == 0
    data = json.loads(dependency_graph.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "dependency_graph"
    assert data["inputs"][0]["path"].endswith("surface-map.json")
    assert data["partition_counts"]["certain"] >= 1
    assert data["partition_counts"]["unknown"] >= 1
    assert any(edge["kind"] == "unknown" for edge in data["edges"])


def test_skeptic_review_challenges_dependency_unknowns(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-skeptic-review"
    assert main(["init", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    assert main(["map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["surface", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["dependency-graph", "--repo", str(repo), "--run-id", run_id]) == 0
    dependency_graph = repo / ".research" / run_id / "dependency-graph.json"

    assert main(["skeptic-review", str(dependency_graph), "--repo", str(repo), "--run-id", run_id]) == 0

    review = repo / ".research" / run_id / "skeptic-review" / "dependency-graph.md"
    assert main(["validate", str(review), "--repo", str(repo)]) == 0
    review_frontmatter = yaml.safe_load(review.read_text(encoding="utf-8").split("---", 2)[1])
    assert review_frontmatter["produced_by"] == "dev-fixture-skeptic@0.1"
    assert review_frontmatter["findings_logged"] == 0
    assert review_frontmatter["challenge_ids"] == []
    graph = json.loads(dependency_graph.read_text(encoding="utf-8"))
    unknown = next(edge for edge in graph["edges"] if edge["kind"] == "unknown")
    assert unknown["claim_status"] == "active"
    assert unknown.get("challenges", []) == []
    ledger_entries = [
        json.loads(line)
        for line in (repo / ".research" / run_id / "evidence-ledger.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert not any(entry["entry_kind"] == "skeptic_challenge" and entry["claim_id"] == unknown["id"] for entry in ledger_entries)


def test_synthesis_index_connects_standard_maps(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-synthesis-index"
    assert main(["init", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    assert main(["map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["surface", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["handoff", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["authority-map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["dependency-graph", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["verify-map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["synthesis-index", "--repo", str(repo), "--run-id", run_id]) == 0
    synthesis_index = repo / ".research" / run_id / "synthesis-index.json"
    assert main(["validate", str(synthesis_index), "--repo", str(repo)]) == 0
    data = json.loads(synthesis_index.read_text(encoding="utf-8"))
    assert data["artifact_type"] == "synthesis_index"
    assert {artifact["artifact_type"] for artifact in data["artifacts"]} == {
        "surface_map",
        "authority_map",
        "dependency_graph",
        "verification_map",
    }
    assert data["contestation"]["open_challenges"] == 0
    challenged_refs = {(item["artifact_path"], item["claim_id"]) for item in data["contestation"]["challenged_claims"]}
    assert not any(path.endswith("surface-map.json") and claim_id == "edge-unknown-001" for path, claim_id in challenged_refs)
    assert not any(path.endswith("dependency-graph.json") and claim_id == "edge-unknown-001" for path, claim_id in challenged_refs)


def write_loop_status_scaffold(repo: Path, *, checkpoint_satisfies: bool) -> None:
    (repo / ".planning" / "reviews" / "checkpoint").mkdir(parents=True)
    (repo / ".planning" / "CURRENT-PLAN.md").write_text("# Current Plan\n\nStatus: active\n", encoding="utf-8")
    (repo / ".planning" / "STATE.md").write_text("# State\n\nStatus: current\n", encoding="utf-8")
    gate_value = "yes" if checkpoint_satisfies else "no"
    (repo / ".planning" / "reviews" / "checkpoint" / "CHECKPOINT.md").write_text(
        f"# Checkpoint\n\nSatisfies resume gate: {gate_value}\n",
        encoding="utf-8",
    )
    for name in ["AGENTS.md", "VISION.md", "RUNTIME-CONSTITUTION.md"]:
        (repo / name).write_text(f"# {name}\n", encoding="utf-8")
    git(repo, "add", ".planning", "AGENTS.md", "VISION.md", "RUNTIME-CONSTITUTION.md")
    git(repo, "commit", "-m", "add recovery planning")


def test_loop_status_blocks_broad_goal_until_checkpoint_satisfies_resume(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_loop_status_scaffold(repo, checkpoint_satisfies=False)

    assert main(["loop-status", "--repo", str(repo), "--scope", "broad-goal", "--work-category", "false-provenance"]) == 1
    assert main(["loop-status", "--repo", str(repo), "--scope", "recovery-slice", "--work-category", "false-provenance"]) == 0


def test_loop_status_blocks_dirty_authority_docs_and_disallowed_work(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    write_loop_status_scaffold(repo, checkpoint_satisfies=True)

    (repo / "VISION.md").write_text("# VISION\n\nchanged\n", encoding="utf-8")
    assert main(["loop-status", "--repo", str(repo), "--scope", "broad-goal", "--work-category", "false-provenance"]) == 1

    git(repo, "add", "VISION.md")
    git(repo, "commit", "-m", "update vision")
    assert main(["loop-status", "--repo", str(repo), "--scope", "broad-goal", "--work-category", "new-kernel-gate"]) == 1
    assert main(["loop-status", "--repo", str(repo), "--scope", "broad-goal", "--work-category", "false-provenance"]) == 0


def test_validate_rejects_malformed_codebase_map(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    bad = repo / "bad-codebase-map.json"
    bad.write_text(json.dumps({"schema_version": "1.2", "artifact_type": "codebase_map"}), encoding="utf-8")

    assert main(["validate", str(bad), "--repo", str(repo)]) == 1
