from __future__ import annotations

import json
import os
import stat
import subprocess
import textwrap
from pathlib import Path

import yaml

SOURCE_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SOURCE_ROOT / ".codex" / "skills" / "cross-vendor-review" / "scripts"
SKILL_DIR = SOURCE_ROOT / ".codex" / "skills" / "cross-vendor-review"


def run(args: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(args, cwd=cwd, env=merged_env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "test@example.invalid")
    git(repo, "config", "user.name", "Test User")
    (repo / "README.md").write_text("sample\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "initial")
    return repo


def write_review(repo: Path, name: str = "review", spec_extra: str = "", outputs: tuple[str, ...] = ("OUTPUT.md",)) -> Path:
    review_dir = repo / ".planning" / "reviews" / name
    review_dir.mkdir(parents=True)
    required = "\n".join(f"  - {item}" for item in outputs)
    spec = f"""\
review_id: {name}
review_type: architecture_review
runner: claude-code-cli
reviewer_requirement: cross_vendor
preferred_model: sonnet
writes_allowed: true
allowed_write_roots:
  - .planning/reviews/{name}/
required_outputs:
{required}
decision_required: false
raw_logs:
  retain_on_success: false
  retain_on_failure: true
"""
    if spec_extra:
        spec += spec_extra
    (review_dir / "REVIEW-SPEC.md").write_text(spec, encoding="utf-8")
    (review_dir / "PROMPT.md").write_text("Write the declared review output.\n", encoding="utf-8")
    for output in outputs:
        (review_dir / output).write_text("", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", f"add {name}")
    return review_dir


def install_fake_claude(tmp_path: Path, monkeypatch) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    fake = bin_dir / "claude"
    fake.write_text(
        textwrap.dedent(
            """\
            #!/usr/bin/env python3
            from __future__ import annotations

            import json
            import os
            import sys
            from pathlib import Path

            args = sys.argv[1:]
            if "--version" in args or "-v" in args:
                print("fake claude 0.1")
                raise SystemExit(0)
            if "--help" in args or "-h" in args:
                print("Usage: claude --name --resume --output-format stream-json --include-partial-messages --permission-mode --json-schema")
                raise SystemExit(0)

            mode = os.environ.get("XVR_FAKE_CLAUDE_MODE", "success")
            review_dir = None
            for index, arg in enumerate(args):
                if arg == "--add-dir" and index + 1 < len(args):
                    candidate = Path(args[index + 1])
                    if (candidate / "REVIEW-SPEC.md").exists():
                        review_dir = candidate
                        break
            if review_dir is None:
                review_dir = Path.cwd()
            session_id = "11111111-1111-4111-8111-111111111111"

            def emit(obj):
                print(json.dumps(obj), flush=True)

            if mode == "malformed":
                (review_dir / "OUTPUT.md").write_text("review output\\n", encoding="utf-8")
                print("{not-json", flush=True)
                raise SystemExit(0)

            emit({"type": "system", "subtype": "init", "session_id": session_id, "model": "claude-sonnet-fake", "permissionMode": "auto", "tools": ["Read", "Write", "Edit", "Bash"]})

            if mode == "nonzero":
                emit({"type": "result", "subtype": "error", "is_error": True, "session_id": session_id, "terminal_reason": "failed"})
                raise SystemExit(7)
            if mode == "no_output":
                emit({"type": "result", "subtype": "success", "is_error": False, "session_id": session_id, "terminal_reason": "completed", "permission_denials": []})
                raise SystemExit(0)
            if mode == "outside":
                (review_dir.parent.parent.parent / "outside.txt").write_text("outside\\n", encoding="utf-8")
                emit({"type": "result", "subtype": "success", "is_error": False, "session_id": session_id, "terminal_reason": "completed", "permission_denials": []})
                raise SystemExit(0)

            output = review_dir / "OUTPUT.md"
            if output.exists():
                output.write_text("review output\\nreviewer_model_id: claude-sonnet-fake\\n", encoding="utf-8")
            emit({"type": "assistant", "session_id": session_id, "message": {"model": "claude-sonnet-fake", "usage": {"input_tokens": 1, "output_tokens": 1}, "content": [{"type": "text", "text": "done"}]}})
            emit({"type": "result", "subtype": "success", "is_error": False, "session_id": session_id, "total_cost_usd": 0.01, "num_turns": 1, "stop_reason": "end_turn", "terminal_reason": "completed", "permission_denials": []})
            """
        ),
        encoding="utf-8",
    )
    fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setenv("PATH", f"{bin_dir}{os.pathsep}{os.environ['PATH']}")
    return fake


def test_preflight_fails_on_missing_review_dir(tmp_path: Path) -> None:
    result = run(["bash", str(SCRIPTS / "preflight.sh"), str(tmp_path / "missing")], cwd=SOURCE_ROOT)
    assert result.returncode != 0
    assert "review dir not found" in result.stderr


def test_skill_md_has_valid_frontmatter_and_progressive_disclosure() -> None:
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\n")
    _, frontmatter, body = text.split("---", 2)
    data = yaml.safe_load(frontmatter)
    assert data["name"] == "cross-vendor-review"
    assert "Claude Code CLI" in data["description"]
    assert "Progressive Disclosure" in body
    assert "Do not read every doc by default" in body
    assert "`review_type` is an open label" in body


def test_preflight_fails_on_missing_prompt(tmp_path: Path) -> None:
    review_dir = tmp_path / "review"
    review_dir.mkdir()
    (review_dir / "REVIEW-SPEC.md").write_text("review_id: missing-prompt\n", encoding="utf-8")
    result = run(["bash", str(SCRIPTS / "preflight.sh"), str(review_dir)], cwd=SOURCE_ROOT)
    assert result.returncode != 0
    assert "missing PROMPT.md" in result.stderr


def test_fake_success_writes_output_and_cleans_raw_logs(tmp_path: Path, monkeypatch) -> None:
    install_fake_claude(tmp_path, monkeypatch)
    repo = make_repo(tmp_path)
    review_dir = write_review(repo)
    result = run(["bash", str(SCRIPTS / "run-claude-code-review.sh"), str(review_dir)], cwd=repo)
    assert result.returncode == 0, result.stderr
    run_id = (review_dir / ".xvr-runs" / ".latest-run-id").read_text(encoding="utf-8").strip()
    run_dir = review_dir / ".xvr-runs" / run_id
    assert (review_dir / "OUTPUT.md").read_text(encoding="utf-8").startswith("review output")
    assert (run_dir / "REVIEW-RUN.json").exists()
    assert not (run_dir / "raw" / "claude.stdout.stream-json").exists()
    assert not (run_dir / "raw" / "claude.stderr.log").exists()
    command = (run_dir / "raw" / "claude.command.txt").read_text(encoding="utf-8")
    assert "--permission-mode auto" in command
    assert "--tools" in command
    assert "Read" in command
    assert "Write" in command
    assert "Edit" in command
    assert "Bash" in command
    assert "--max-turns" not in command
    assert "--max-budget-usd" not in command


def test_fake_nonzero_writes_recovery_and_preserves_raw_logs(tmp_path: Path, monkeypatch) -> None:
    install_fake_claude(tmp_path, monkeypatch)
    repo = make_repo(tmp_path)
    review_dir = write_review(repo)
    result = run(
        ["bash", str(SCRIPTS / "run-claude-code-review.sh"), str(review_dir)],
        cwd=repo,
        env={"XVR_FAKE_CLAUDE_MODE": "nonzero"},
    )
    assert result.returncode != 0
    run_id = (review_dir / ".xvr-runs" / ".latest-run-id").read_text(encoding="utf-8").strip()
    run_dir = review_dir / ".xvr-runs" / run_id
    recovery = (review_dir / "RECOVERY.md").read_text(encoding="utf-8")
    assert "`nonzero_exit`" in recovery
    assert "--resume" in recovery
    assert (run_dir / "raw" / "claude.stdout.stream-json").exists()
    assert (run_dir / "raw" / "claude.stderr.log").exists()


def test_fake_success_without_output_writes_recovery(tmp_path: Path, monkeypatch) -> None:
    install_fake_claude(tmp_path, monkeypatch)
    repo = make_repo(tmp_path)
    review_dir = write_review(repo)
    result = run(
        ["bash", str(SCRIPTS / "run-claude-code-review.sh"), str(review_dir)],
        cwd=repo,
        env={"XVR_FAKE_CLAUDE_MODE": "no_output"},
    )
    assert result.returncode != 0
    recovery = (review_dir / "RECOVERY.md").read_text(encoding="utf-8")
    assert "`partial_expected_output`" in recovery


def test_fake_outside_write_is_detected(tmp_path: Path, monkeypatch) -> None:
    install_fake_claude(tmp_path, monkeypatch)
    repo = make_repo(tmp_path)
    review_dir = write_review(repo)
    result = run(
        ["bash", str(SCRIPTS / "run-claude-code-review.sh"), str(review_dir)],
        cwd=repo,
        env={"XVR_FAKE_CLAUDE_MODE": "outside"},
    )
    assert result.returncode != 0
    assert (repo / "outside.txt").exists()
    recovery = (review_dir / "RECOVERY.md").read_text(encoding="utf-8")
    assert "`wrote_outside_allowed_scope`" in recovery


def test_checkpoint_disposition_requires_reviewer_identity(tmp_path: Path, monkeypatch) -> None:
    install_fake_claude(tmp_path, monkeypatch)
    repo = make_repo(tmp_path)
    review_dir = write_review(
        repo,
        "checkpoint",
        spec_extra="""\
review_type: pass_claim_checkpoint
decision_required: true
allowed_dispositions:
  - accept
""",
        outputs=("DISPOSITION.md",),
    )
    (review_dir / "DISPOSITION.md").write_text("disposition: accept\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "fill disposition without identity")
    preflight = run(["bash", str(SCRIPTS / "preflight.sh"), str(review_dir), "verify-checkpoint"], cwd=repo)
    assert preflight.returncode == 0, preflight.stderr
    verify = run(["bash", str(SCRIPTS / "verify-review-output.sh"), str(review_dir), "verify-checkpoint"], cwd=repo)
    assert verify.returncode != 0
    data = json.loads((review_dir / ".xvr-runs" / "verify-checkpoint" / "VERIFY.json").read_text(encoding="utf-8"))
    assert any(issue["code"] == "missing_reviewer_identity" for issue in data["issues"])


def test_structured_disposition_json_satisfies_checkpoint_verifier(tmp_path: Path, monkeypatch) -> None:
    install_fake_claude(tmp_path, monkeypatch)
    repo = make_repo(tmp_path)
    review_dir = write_review(
        repo,
        "checkpoint-json",
        spec_extra="""\
review_type: pass_claim_checkpoint
decision_required: true
allowed_dispositions:
  - accept
  - revise
""",
        outputs=("DISPOSITION.md",),
    )
    (review_dir / "DISPOSITION.md").write_text("Decision: accept\n\n## Final Disposition\n\naccept\n", encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "write prose disposition")
    preflight = run(["bash", str(SCRIPTS / "preflight.sh"), str(review_dir), "verify-json-checkpoint"], cwd=repo)
    assert preflight.returncode == 0, preflight.stderr

    writer = run(
        [
            "python3",
            str(SCRIPTS / "write-disposition.py"),
            str(review_dir),
            "--reviewer-model-id",
            "claude-opus-fake",
            "--disposition",
            "accept",
        ],
        cwd=repo,
    )
    assert writer.returncode == 0, writer.stderr
    payload = json.loads((review_dir / "DISPOSITION.json").read_text(encoding="utf-8"))
    assert payload["reviewer_model_id"] == "claude-opus-fake"
    assert payload["disposition"] == "accept"

    verify = run(["bash", str(SCRIPTS / "verify-review-output.sh"), str(review_dir), "verify-json-checkpoint"], cwd=repo)
    assert verify.returncode == 0, verify.stderr
    data = json.loads((review_dir / ".xvr-runs" / "verify-json-checkpoint" / "VERIFY.json").read_text(encoding="utf-8"))
    assert data["status"] == "ok"


def test_structured_disposition_writer_rejects_invalid_disposition(tmp_path: Path, monkeypatch) -> None:
    install_fake_claude(tmp_path, monkeypatch)
    repo = make_repo(tmp_path)
    review_dir = write_review(
        repo,
        "checkpoint-invalid-json",
        spec_extra="""\
review_type: pass_claim_checkpoint
decision_required: true
allowed_dispositions:
  - accept
""",
        outputs=("DISPOSITION.md",),
    )
    result = run(
        [
            "python3",
            str(SCRIPTS / "write-disposition.py"),
            str(review_dir),
            "--reviewer-model-id",
            "claude-opus-fake",
            "--disposition",
            "revise",
        ],
        cwd=repo,
    )
    assert result.returncode != 0
    assert "invalid disposition" in result.stderr


def test_malformed_stream_json_writes_recovery_without_success(tmp_path: Path, monkeypatch) -> None:
    install_fake_claude(tmp_path, monkeypatch)
    repo = make_repo(tmp_path)
    review_dir = write_review(repo)
    result = run(
        ["bash", str(SCRIPTS / "run-claude-code-review.sh"), str(review_dir)],
        cwd=repo,
        env={"XVR_FAKE_CLAUDE_MODE": "malformed"},
    )
    assert result.returncode != 0
    recovery = (review_dir / "RECOVERY.md").read_text(encoding="utf-8")
    assert "`malformed_stream_json`" in recovery


def _normalized_parser_lines(text: str, def_line_marker: str) -> list[str]:
    """Extract the parser function body by locating the `def` line marker,
    taking the four lines following (the function body is fixed-shape: one
    `payload = ...` line, one `if ...` line, one indented assignment line,
    one `return` line), and stripping each line's leading whitespace.

    Used to assert the duplicated git-status-payload parser stays in sync
    between preflight.sh and verify-review-output.sh (gates S5).
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if def_line_marker in line:
            return [line.strip() for line in lines[i + 1 : i + 5]]
    raise AssertionError(f"could not locate `{def_line_marker}` in given text")


def test_git_status_parser_stays_in_sync_between_preflight_and_verify() -> None:
    """Gates S5 regression: preflight.sh defines `git_status_payload(line)`;
    verify-review-output.sh defines `status_path(line)` with byte-identical
    body. Both are inside Python heredocs in shell scripts and cannot
    `import` each other; this test takes the four body lines after each
    function's `def` line, strips per-line whitespace, and asserts the
    bodies remain in sync. If this test fails, port the fix to BOTH
    locations (see the sync-marker comment in each script).
    """
    preflight_text = (SCRIPTS / "preflight.sh").read_text(encoding="utf-8")
    verify_text = (SCRIPTS / "verify-review-output.sh").read_text(encoding="utf-8")
    preflight_body = _normalized_parser_lines(preflight_text, "def git_status_payload(line: str) -> str:")
    verify_body = _normalized_parser_lines(verify_text, "def status_path(line: str) -> str:")
    assert preflight_body == verify_body, (
        "git-status-payload parser drift between preflight.sh and verify-review-output.sh. "
        "Both functions must stay byte-identical (modulo their function names + indentation) "
        "until they are extracted to a shared helper. See gates S5 sync-marker comments in "
        "both scripts.\n"
        f"preflight: {preflight_body}\n"
        f"verify: {verify_body}"
    )
