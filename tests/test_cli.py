from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml

from cbm.cli import main


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "sample"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname = \"sample\"\n", encoding="utf-8")
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("def hello():\n    return 'hello'\n", encoding="utf-8")
    (repo / "tests").mkdir()
    (repo / "tests" / "test_app.py").write_text("from src.app import hello\n\ndef test_hello():\n    assert hello() == 'hello'\n", encoding="utf-8")
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
    source_root = Path(__file__).resolve().parents[1]
    repo = make_repo(tmp_path)
    copy_contracts(source_root, repo)
    git(repo, "add", "schemas")
    git(repo, "commit", "-m", "add schemas")

    run_id = "run-test"
    assert main(["init", "--repo", str(repo), "--goal", "understand this repo", "--run-id", run_id]) == 0
    assert main(["map", "--repo", str(repo), "--run-id", run_id]) == 0
    assert main(["surface", "--repo", str(repo), "--run-id", run_id]) == 0

    run_dir = repo / ".research" / run_id
    codebase_map = run_dir / "codebase-map.json"
    surface_map = run_dir / "surface-map.json"
    assert codebase_map.exists()
    assert surface_map.exists()
    assert main(["validate", str(codebase_map), "--repo", str(repo)]) == 0
    assert main(["validate", str(surface_map), "--repo", str(repo)]) == 0

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

    frontmatter = yaml.safe_load(handoff.read_text(encoding="utf-8").split("---", 2)[1])
    assert frontmatter["gate_summary"]["citation_resolution"]["unresolved_count"] == 0
    assert frontmatter["gate_summary"]["ledger_consistency"]["append_only_verified"] is True
    assert frontmatter["gate_summary"]["ledger_consistency"]["entry_count"] >= 3
    assert frontmatter["gate_summary"]["skeptic_review"]["challenges_logged"] == 1
    assert frontmatter["contestation_summary"]["claims_by_register"]["interpretive"] >= 1
    reviewed_surface = json.loads(surface_map.read_text(encoding="utf-8"))
    assert reviewed_surface["edges"][0]["claim_status"] == "challenged"


def test_validate_rejects_malformed_codebase_map(tmp_path: Path) -> None:
    source_root = Path(__file__).resolve().parents[1]
    repo = make_repo(tmp_path)
    copy_contracts(source_root, repo)
    bad = repo / "bad-codebase-map.json"
    bad.write_text(json.dumps({"schema_version": "1.2", "artifact_type": "codebase_map"}), encoding="utf-8")

    assert main(["validate", str(bad), "--repo", str(repo)]) == 1
