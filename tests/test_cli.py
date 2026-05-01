from __future__ import annotations

import json
import io
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from cbm.cli import main

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
    assert import_edges
    assert import_edges[0]["from"]["path"] == expected["surface_import_edge"]["from_path"]
    assert import_edges[0]["to"]["path"] == expected["surface_import_edge"]["to_path"]
    assert import_edges[0]["extractor_id"] == expected["surface_import_edge"]["extractor_id"]
    assert import_edges[0]["claim_register"] == expected["surface_import_edge"]["claim_register"]
    assert import_edges[0]["evidence_kinds"] == expected["surface_import_edge"]["evidence_kinds"]
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
    reviewed_unknown_edges = [edge for edge in reviewed_surface["edges"] if edge["kind"] == "unknown"]
    assert reviewed_import_edges[0]["claim_status"] == expected["surface_import_edge"]["claim_status"]
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


def test_validate_rejects_malformed_codebase_map(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    copy_contracts(SOURCE_ROOT, repo)
    bad = repo / "bad-codebase-map.json"
    bad.write_text(json.dumps({"schema_version": "1.2", "artifact_type": "codebase_map"}), encoding="utf-8")

    assert main(["validate", str(bad), "--repo", str(repo)]) == 1
