from __future__ import annotations

import json
import io
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from cbm.cli import goal_pack, load_goal_packs, main

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
    surface_map = run_dir / "surface-map.json"
    goal_binding = run_dir / "goal-binding.json"
    assert codebase_map.exists()
    assert surface_map.exists()
    assert goal_binding.exists()
    assert main(["validate", str(codebase_map), "--repo", str(repo)]) == 0
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
    assert expected["findings_card"]["role_contains"] in card_frontmatter["primary_files"][0]["role"]
    assert card_frontmatter["confidence"] == expected["findings_card"]["confidence"]
    assert card_frontmatter["dependent_challenges"][0]["challenge_ids"] == [expected["findings_card"]["dependent_challenge_id"]]
    assert card_frontmatter["related_dependencies"]["certain"][0].endswith("/edges/0")

    frontmatter = yaml.safe_load(handoff.read_text(encoding="utf-8").split("---", 2)[1])
    assert frontmatter["gate_summary"]["citation_resolution"]["unresolved_count"] == 0
    assert frontmatter["gate_summary"]["ledger_consistency"]["append_only_verified"] is True
    assert frontmatter["gate_summary"]["ledger_consistency"]["entry_count"] >= 3
    assert frontmatter["gate_summary"]["skeptic_review"]["challenges_logged"] == 1
    assert frontmatter["contestation_summary"]["claims_by_register"]["interpretive"] >= 1
    assert "goal_binding" in [artifact["artifact_type"] for artifact in frontmatter["artifacts"]]
    assert any(input_item["path"].endswith("goal-binding.json") for input_item in frontmatter["inputs"])
    reviewed_surface = json.loads(surface_map.read_text(encoding="utf-8"))
    reviewed_import_edges = [edge for edge in reviewed_surface["edges"] if edge["kind"] == "import"]
    reviewed_call_edges = [edge for edge in reviewed_surface["edges"] if edge["kind"] == "call"]
    reviewed_unknown_edges = [edge for edge in reviewed_surface["edges"] if edge["kind"] == "unknown"]
    assert reviewed_import_edges[0]["claim_status"] == expected["surface_import_edge"]["claim_status"]
    assert reviewed_call_edges[0]["claim_status"] == "active"
    assert reviewed_unknown_edges[0]["id"] == expected["surface_unknown_edge"]["id"]
    assert reviewed_unknown_edges[0]["claim_status"] == expected["surface_unknown_edge"]["claim_status_after_handoff"]
    assert reviewed_unknown_edges[0]["challenges"][0]["challenges_claim_id"] == "edge-unknown-001"
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
    assert data["ci_gates"]
    assert data["ci_gates"][0]["command"]["safety_envelope"]["requires_network"] is False
    synthesis_data = json.loads(synthesis_index.read_text(encoding="utf-8"))
    assert synthesis_data["claim_counts"]["authorities"] == len(authority_data["authorities"])
    assert synthesis_data["claim_counts"]["dependencies"] == len(dependency_data["edges"])
    assert synthesis_data["contestation"]["open_challenges"] >= 1


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
    assert any(item["challenge_id"] == "chl-00001" and item["post_refresh_status"] == "still_active" for item in delta_data["challenges_carried_forward"])


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

    assert main(["consult", "nonexistent_surface_zzz", "--repo", str(repo)]) == 2
    consultations = sorted((repo / ".research" / "consultations").glob("*.md"))
    refused = consultations[-1]
    refused_frontmatter = yaml.safe_load(refused.read_text(encoding="utf-8").split("---", 2)[1])
    assert refused_frontmatter["status"] == "refused"
    assert refused_frontmatter["matches"] == []


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
        "produced_by": "verification-mapper@0.1",
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
    assert review_frontmatter["findings_logged"] == 1
    graph = json.loads(dependency_graph.read_text(encoding="utf-8"))
    unknown = next(edge for edge in graph["edges"] if edge["kind"] == "unknown")
    assert unknown["claim_status"] == "challenged"
    assert unknown["challenges"][0]["challenge_id"] == "chl-10001"
    ledger_entries = [
        json.loads(line)
        for line in (repo / ".research" / run_id / "evidence-ledger.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert any(entry["entry_kind"] == "skeptic_challenge" and entry["claim_id"] == unknown["id"] for entry in ledger_entries)


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
    assert data["contestation"]["open_challenges"] == 1
    assert data["contestation"]["challenged_claims"][0]["claim_id"] == "edge-unknown-001"


def test_validate_rejects_malformed_codebase_map(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    bad = repo / "bad-codebase-map.json"
    bad.write_text(json.dumps({"schema_version": "1.2", "artifact_type": "codebase_map"}), encoding="utf-8")

    assert main(["validate", str(bad), "--repo", str(repo)]) == 1
