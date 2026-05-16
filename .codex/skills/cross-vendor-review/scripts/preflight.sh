#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf 'usage: preflight.sh <review-dir> [run-id]\n' >&2
}

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  usage
  exit 2
fi

REVIEW_DIR_INPUT=$1
if [ ! -d "$REVIEW_DIR_INPUT" ]; then
  printf 'cross-vendor-review preflight: review dir not found: %s\n' "$REVIEW_DIR_INPUT" >&2
  exit 2
fi

REVIEW_DIR=$(cd "$REVIEW_DIR_INPUT" && pwd -P)
PROMPT_PATH="$REVIEW_DIR/PROMPT.md"
SPEC_PATH="$REVIEW_DIR/REVIEW-SPEC.md"

if [ ! -f "$PROMPT_PATH" ]; then
  printf 'cross-vendor-review preflight: missing PROMPT.md in %s\n' "$REVIEW_DIR" >&2
  exit 2
fi

if [ ! -f "$SPEC_PATH" ]; then
  printf 'cross-vendor-review preflight: missing REVIEW-SPEC.md in %s\n' "$REVIEW_DIR" >&2
  exit 2
fi

CLAUDE_PATH=$(command -v claude || true)
if [ -z "$CLAUDE_PATH" ]; then
  printf 'cross-vendor-review preflight: claude not found on PATH\n' >&2
  exit 3
fi

RUN_ID=${2:-${XVR_RUN_ID:-xvr-$(date -u +%Y%m%dT%H%M%SZ)-$$}}
RUN_DIR="$REVIEW_DIR/.xvr-runs/$RUN_ID"
RAW_DIR="$RUN_DIR/raw"
LOG_DIR="$RUN_DIR/logs"
mkdir -p "$RAW_DIR" "$LOG_DIR"

printf '%s\n' "$CLAUDE_PATH" > "$RAW_DIR/claude.path.txt"
claude --version > "$LOG_DIR/claude.version.txt" 2> "$LOG_DIR/claude.version.stderr.txt" || true
claude --help > "$LOG_DIR/claude.help.txt" 2> "$LOG_DIR/claude.help.stderr.txt" || true

GIT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || true)
if [ -n "$GIT_ROOT" ]; then
  git rev-parse --abbrev-ref HEAD > "$RAW_DIR/git-branch-before.txt" 2>/dev/null || true
  git rev-parse HEAD > "$RAW_DIR/git-sha-before.txt" 2>/dev/null || true
  git status --short --branch > "$RAW_DIR/git-status-before.txt" 2>/dev/null || true
else
  : > "$RAW_DIR/git-branch-before.txt"
  : > "$RAW_DIR/git-sha-before.txt"
  : > "$RAW_DIR/git-status-before.txt"
fi

python3 - "$REVIEW_DIR" "$RUN_DIR" "$RUN_ID" "$CLAUDE_PATH" "$GIT_ROOT" <<'PY'
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

try:
    import yaml
except Exception as exc:  # pragma: no cover - fallback is for bare hosts
    yaml = None

review_dir = Path(sys.argv[1]).resolve()
run_dir = Path(sys.argv[2]).resolve()
run_id = sys.argv[3]
claude_path = sys.argv[4]
git_root = Path(sys.argv[5]).resolve() if sys.argv[5] else None
spec_path = review_dir / "REVIEW-SPEC.md"
prompt_path = review_dir / "PROMPT.md"
raw_dir = run_dir / "raw"

def load_spec(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(text) or {}
        if not isinstance(data, dict):
            raise SystemExit("REVIEW-SPEC.md must parse to a mapping")
        return data
    # Verify-gates Critical 2 fix (gates review): the bare-host fallback
    # parser drops every indented line, which is exactly how YAML
    # expresses lists. Without pyyaml, allowed_dispositions,
    # disallowed_reviewer_model_families, allowed_write_roots,
    # required_outputs, and tools silently become empty in the manifest
    # and the corresponding verify-review-output.sh gates lose their
    # input. The previous W2 fix only printed a warning and let the
    # script proceed; this is fail-open behavior. The classification of
    # the run as checkpointish is computed by the caller using the
    # parsed spec dict that this function returns, so checkpointish
    # gating cannot happen here. Conservative line-mode parsing is
    # acceptable for non-checkpoint reviews; the caller (below) must
    # fail-closed for checkpointish.
    sys.stderr.write(
        "preflight: warning: pyyaml unavailable; falling back to line-mode parser. "
        "List-valued spec fields (allowed_dispositions, disallowed_reviewer_model_families, "
        "allowed_write_roots, required_outputs, tools) will be EMPTY in this run. "
        "Checkpointish reviews will be REJECTED downstream; non-checkpointish reviews "
        "will proceed with degraded gate coverage. Install pyyaml for full spec enforcement.\n"
    )
    data: dict[str, object] = {}
    for line in text.splitlines():
        if ":" not in line or line.lstrip().startswith("#") or line.startswith(" "):
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def as_bool(value: object, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}

def as_list(value: object, default: list[str]) -> list[str]:
    if value is None:
        return list(default)
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        sep = "," if "," in value else None
        return [item.strip() for item in value.split(sep) if item.strip()]
    return [str(value).strip()]

def resolve_path(value: str) -> str:
    p = Path(value)
    if not p.is_absolute():
        base = git_root if git_root is not None else review_dir
        p = base / p
    return str(p.resolve(strict=False))

spec = load_spec(spec_path)
review_type = str(spec.get("review_type", "") or "")
raw_logs = spec.get("raw_logs") if isinstance(spec.get("raw_logs"), dict) else {}
required_outputs = as_list(spec.get("required_outputs"), ["OUTPUT.md"])
allowed_roots = as_list(spec.get("allowed_write_roots"), [str(review_dir)])
additional_read_roots = as_list(spec.get("additional_read_roots"), [])
tools = as_list(spec.get("tools"), ["Read", "Write", "Edit", "Bash"])
permission_mode = str(spec.get("permission_mode") or "auto")
model = str(spec.get("preferred_model") or spec.get("model") or "opus")
status_before = (raw_dir / "git-status-before.txt").read_text(encoding="utf-8")

def git_status_payload(line: str) -> str:
    payload = line[3:] if len(line) > 3 else line
    if " -> " in payload:
        payload = payload.split(" -> ", 1)[1]
    return payload.strip().strip('"')

xvr_status_prefix = ""
if git_root is not None:
    try:
        xvr_status_prefix = str((review_dir / ".xvr-runs").resolve(strict=False).relative_to(git_root))
    except ValueError:
        xvr_status_prefix = ""

dirty_lines = []
for line in status_before.splitlines():
    if not line or line.startswith("##"):
        continue
    payload = git_status_payload(line)
    if xvr_status_prefix and (payload == xvr_status_prefix or payload.startswith(xvr_status_prefix + "/")):
        continue
    dirty_lines.append(line)
# W3 fix (gates review): align preflight's checkpointish predicate to
# verify-review-output.sh:92. Verify includes decision_required so a spec
# with decision_required: true and a non-checkpoint review_type is
# correctly recognized as checkpointish. Same vocabulary, one definition.
# Also match both pass_claim (XVR) and pass-claim (CBM scope vocab) so
# a spec written with either form is treated consistently.
decision_required = as_bool(spec.get("decision_required"), False)
review_type_lower = review_type.lower()
checkpointish = (
    decision_required
    or "checkpoint" in review_type_lower
    or "pass_claim" in review_type_lower
    or "pass-claim" in review_type_lower
)
# Verify-gates Critical 2 fix: fail-closed on bare hosts for checkpointish
# reviews. Without pyyaml the load_spec fallback yields empty lists for
# every gate-relevant field, and downstream verify-review-output.sh
# would silently pass every list-shaped gate. A checkpoint that may
# clear pass-claim, main-merge, or broad-goal-restart scope MUST be
# enforced; warn-and-proceed is not acceptable for those scopes.
if checkpointish and yaml is None:
    (run_dir / "PREFLIGHT-FAILED.txt").write_text(
        "pyyaml is unavailable on this host; spec list-valued fields cannot be parsed reliably. "
        "Checkpointish reviews (review_type contains 'checkpoint' / 'pass_claim' / 'pass-claim' "
        "or decision_required: true) refuse to proceed in degraded mode. Install pyyaml.\n",
        encoding="utf-8",
    )
    (review_dir / ".xvr-runs" / ".latest-run-id").write_text(
        "PREFLIGHT-FAILED:" + run_id + "\n", encoding="utf-8"
    )
    raise SystemExit(11)
allow_dirty = as_bool(spec.get("allow_dirty_worktree"), False)
if checkpointish and dirty_lines and not allow_dirty:
    (run_dir / "PREFLIGHT-FAILED.txt").write_text(
        "Dirty worktree before checkpoint/pass-claim review. Set allow_dirty_worktree: true only if this is intentional.\n",
        encoding="utf-8",
    )
    # S4 fix (gates review): mark .latest-run-id with a sentinel so a
    # subsequent verify-review-output.sh without an explicit run-id
    # does not silently fall back to a prior successful run.
    (review_dir / ".xvr-runs" / ".latest-run-id").write_text(
        "PREFLIGHT-FAILED:" + run_id + "\n", encoding="utf-8"
    )
    raise SystemExit(10)

manifest = {
    "schema_version": 1,
    "run_id": run_id,
    "review_dir": str(review_dir),
    "review_id": str(spec.get("review_id") or review_dir.name),
    "review_type": review_type or "unspecified",
    "runner": str(spec.get("runner") or "claude-code-cli"),
    "reviewer_requirement": str(spec.get("reviewer_requirement") or ""),
    "model": model,
    "permission_mode": permission_mode,
    "tools": tools,
    "max_turns": spec.get("max_turns"),
    "max_budget_usd": spec.get("max_budget_usd"),
    "soft_budget_guidance": str(spec.get("soft_budget_guidance") or ""),
    "writes_allowed": as_bool(spec.get("writes_allowed"), True),
    "allowed_write_roots": [resolve_path(root) for root in allowed_roots],
    "additional_read_roots": [resolve_path(root) for root in additional_read_roots],
    "required_outputs": required_outputs,
    "decision_required": as_bool(spec.get("decision_required"), False),
    "allowed_dispositions": as_list(spec.get("allowed_dispositions"), []),
    "disallowed_reviewer_model_families": as_list(spec.get("disallowed_reviewer_model_families"), []),
    "raw_logs": {
        "retain_on_success": as_bool(raw_logs.get("retain_on_success") if raw_logs else None, False),
        "retain_on_failure": as_bool(raw_logs.get("retain_on_failure") if raw_logs else None, True),
    },
    "paths": {
        "prompt": str(prompt_path),
        "review_spec": str(spec_path),
        "run_dir": str(run_dir),
        "raw_dir": str(raw_dir),
        "logs_dir": str(run_dir / "logs"),
    },
    "hashes": {
        "prompt_sha256": sha256(prompt_path),
        "review_spec_sha256": sha256(spec_path),
    },
    "git": {
        "repo_root": str(git_root) if git_root else "",
        "branch_before": (raw_dir / "git-branch-before.txt").read_text(encoding="utf-8").strip(),
        "sha_before": (raw_dir / "git-sha-before.txt").read_text(encoding="utf-8").strip(),
        "status_before": status_before,
        "dirty_before": bool(dirty_lines),
    },
    "claude": {
        "path": claude_path,
        "session_name": f"xvr-{run_id}",
    },
    "status": "preflight_ok",
}
(run_dir / "RUN-MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
(review_dir / ".xvr-runs" / ".latest-run-id").write_text(run_id + "\n", encoding="utf-8")
PY

printf '%s\n' "$RUN_ID"
