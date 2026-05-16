#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path


def usage() -> None:
    print("usage: recover-review.py <review-dir> [run-id]", file=sys.stderr)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def q(value: object) -> str:
    return shlex.quote("" if value is None else str(value))


def classify(manifest: dict, verify: dict | None, raw_dir: Path) -> list[str]:
    classes: list[str] = []
    claude = manifest.get("claude", {})
    exit_code = claude.get("exit_code")
    subtype = str(claude.get("result_subtype") or "")
    terminal = str(claude.get("terminal_reason") or "")
    stderr = (raw_dir / "claude.stderr.log").read_text(encoding="utf-8", errors="replace") if (raw_dir / "claude.stderr.log").exists() else ""
    stdout = (
        (raw_dir / "claude.stdout.stream-json").read_text(encoding="utf-8", errors="replace")
        if (raw_dir / "claude.stdout.stream-json").exists()
        else ""
    )
    combined = f"{stderr}\n{stdout}".lower()

    if exit_code is None:
        classes.append("launch_failed")
    elif int(exit_code) != 0:
        classes.append("nonzero_exit")
    if not claude.get("stream_json_valid", True):
        classes.append("malformed_stream_json")
    if "max_turns" in subtype or "max_budget" in subtype or terminal in {"max_turns", "max_budget"}:
        classes.append("max_turns_or_budget")
    # S3 fix (gates review): bare substring matches for "auth"/"login"/
    # "permission" produced false positives when reviewer logs incidentally
    # mentioned those words (e.g., reading a `permissions.md` doc). Use
    # targeted patterns that match the actual error phrasing.
    if re.search(r"\b(auth(entication)?|login)\s+(failed|required|expired|denied)\b", combined):
        classes.append("auth_failed")
    if "model" in combined and ("unavailable" in combined or "not available" in combined or "unknown model" in combined):
        classes.append("model_unavailable")
    if re.search(r"\bpermission\s+denied\b", combined) or claude.get("permission_denials"):
        classes.append("permission_blocked")

    if verify:
        for issue in verify.get("issues", []):
            code = issue.get("code")
            if code == "missing_expected_output":
                classes.append("missing_expected_output")
            elif code == "partial_expected_output":
                classes.append("partial_expected_output")
            elif code == "wrote_outside_allowed_scope":
                classes.append("wrote_outside_allowed_scope")
            elif code == "missing_reviewer_identity":
                classes.append("missing_reviewer_identity")
            elif code == "invalid_disposition":
                classes.append("invalid_disposition")
            elif code == "same_model_disallowed":
                classes.append("same_model_disallowed")

    if not manifest.get("claude", {}).get("session_name") and not manifest.get("claude", {}).get("session_id"):
        classes.append("ambiguous_session")

    if not classes:
        classes.append("review_output_verification_failed")
    return sorted(set(classes))


def command_args(manifest: dict, resume: bool) -> list[str]:
    claude = manifest.get("claude", {})
    review_dir = manifest["review_dir"]
    session = claude.get("session_name") or claude.get("session_id")
    model = manifest.get("model") or "opus"
    permission = manifest.get("permission_mode") or "auto"
    tools = ",".join(manifest.get("tools") or ["Read", "Write", "Edit", "Bash"])
    if resume and session:
        prompt = (
            f"Resume the cross-vendor review in {review_dir}. Read REVIEW-SPEC.md and PROMPT.md again. "
            "Write only missing or incomplete declared outputs inside allowed roots. Do not use chat output as the durable artifact."
        )
        args = ["claude", "--resume", str(session), "-p", prompt]
    else:
        prompt = (
            f"Run the cross-vendor review in {review_dir}. Read REVIEW-SPEC.md and PROMPT.md. "
            "Write declared outputs directly and only inside allowed roots."
        )
        args = ["claude", "-p", prompt, "--name", str(claude.get("session_name") or f"xvr-{manifest['run_id']}")]
    args += [
        "--model",
        str(model),
        "--permission-mode",
        str(permission),
        "--output-format",
        "stream-json",
        "--include-partial-messages",
        "--verbose",
        "--tools",
        tools,
        "--add-dir",
        review_dir,
        "--setting-sources",
        "project",
    ]
    for extra in manifest.get("additional_read_roots") or []:
        args += ["--add-dir", str(extra)]
    if manifest.get("max_turns") not in (None, ""):
        args += ["--max-turns", str(manifest["max_turns"])]
    if manifest.get("max_budget_usd") not in (None, ""):
        args += ["--max-budget-usd", str(manifest["max_budget_usd"])]
    return args


def main(argv: list[str]) -> int:
    if len(argv) not in {2, 3}:
        usage()
        return 2
    review_dir = Path(argv[1]).resolve()
    if len(argv) == 3:
        run_id = argv[2]
    else:
        run_id = (review_dir / ".xvr-runs" / ".latest-run-id").read_text(encoding="utf-8").strip()
    run_dir = review_dir / ".xvr-runs" / run_id
    manifest_path = run_dir / "RUN-MANIFEST.json"
    if not manifest_path.exists():
        print(f"recover-review: missing run manifest: {manifest_path}", file=sys.stderr)
        return 2
    manifest = load_json(manifest_path)
    raw_dir = Path(manifest["paths"]["raw_dir"])
    verify_path = run_dir / "VERIFY.json"
    verify = load_json(verify_path) if verify_path.exists() else None
    classes = classify(manifest, verify, raw_dir)
    session_available = bool(manifest.get("claude", {}).get("session_name") or manifest.get("claude", {}).get("session_id"))
    unsafe_resume = any(item in classes for item in {"wrote_outside_allowed_scope", "same_model_disallowed"})
    resume_safe = session_available and not unsafe_resume
    captured_files = []
    for path in sorted(raw_dir.glob("*")):
        if path.is_file():
            captured_files.append(str(path.relative_to(review_dir)))
    if verify:
        output_lines = [
            f"- `{item['path']}`: exists={item['exists']} size={item['size']}"
            for item in verify.get("required_outputs", [])
        ]
    else:
        output_lines = ["- Verification summary unavailable."]
    resume_args = command_args(manifest, resume=True)
    rerun_args = command_args(manifest, resume=False)
    recovery = [
        "# Cross-Vendor Review Recovery",
        "",
        f"Run id: `{run_id}`",
        f"Review id: `{manifest.get('review_id', '')}`",
        "",
        "## Classification",
        "",
        *[f"- `{item}`" for item in classes],
        "",
        "## Expected Outputs",
        "",
        *output_lines,
        "",
        "## Captured Files",
        "",
        *[f"- `{item}`" for item in captured_files],
        "",
        "## Recovery Command",
        "",
    ]
    if resume_safe:
        recovery += [
            "Explicit resume is available from the captured session envelope:",
            "",
            "```bash",
            " ".join(q(arg) for arg in resume_args),
            "```",
        ]
    else:
        recovery += [
            "Explicit resume is not considered safe for this failure. Use a fresh rerun after reviewing the captured files:",
            "",
            "```bash",
            " ".join(q(arg) for arg in rerun_args),
            "```",
        ]
    recovery += [
        "",
        "## Boundary",
        "",
        "This recovery note does not synthesize reviewer content, reviewer identity, confidence, or disposition from raw logs.",
        "",
    ]
    text = "\n".join(recovery)
    (run_dir / "RECOVERY.md").write_text(text, encoding="utf-8")
    (review_dir / "RECOVERY.md").write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
