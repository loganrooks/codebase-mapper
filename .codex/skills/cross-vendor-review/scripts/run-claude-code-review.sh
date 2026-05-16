#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf 'usage: run-claude-code-review.sh <review-dir> [run-id]\n' >&2
}

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  usage
  exit 2
fi

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
REVIEW_DIR_INPUT=$1
RUN_ID_ARG=${2:-}

if [ -n "$RUN_ID_ARG" ]; then
  RUN_ID=$("$SCRIPT_DIR/preflight.sh" "$REVIEW_DIR_INPUT" "$RUN_ID_ARG")
else
  RUN_ID=$("$SCRIPT_DIR/preflight.sh" "$REVIEW_DIR_INPUT")
fi

REVIEW_DIR=$(cd "$REVIEW_DIR_INPUT" && pwd -P)
RUN_DIR="$REVIEW_DIR/.xvr-runs/$RUN_ID"
RAW_DIR="$RUN_DIR/raw"
MANIFEST="$RUN_DIR/RUN-MANIFEST.json"
ENV_FILE="$RUN_DIR/run-env.sh"
ADD_DIRS_FILE="$RUN_DIR/add-dirs.txt"

python3 - "$MANIFEST" "$ENV_FILE" "$ADD_DIRS_FILE" <<'PY'
from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
env_path = Path(sys.argv[2])
add_dirs_path = Path(sys.argv[3])

def q(value: object) -> str:
    return shlex.quote("" if value is None else str(value))

tools = ",".join(manifest.get("tools") or ["Read", "Write", "Edit", "Bash"])
add_dirs = [manifest["review_dir"]] + list(manifest.get("additional_read_roots") or [])
env_path.write_text(
    "\n".join(
        [
            f"MODEL={q(manifest.get('model') or 'opus')}",
            f"PERMISSION_MODE={q(manifest.get('permission_mode') or 'auto')}",
            f"TOOLS={q(tools)}",
            f"SESSION_NAME={q(manifest.get('claude', {}).get('session_name') or ('xvr-' + manifest['run_id']))}",
            # S2 fix (gates review): an explicitly declared `max_turns: 0`
            # or `max_budget_usd: 0` is a deliberate override (recover-review
            # already handles this case). The `or ''` form collapsed 0 to
            # empty string, silently dropping the cap. Use explicit None / ''
            # checks so 0 reaches MAX_TURNS / MAX_BUDGET_USD in the env file.
            f"MAX_TURNS={q('' if manifest.get('max_turns') in (None, '') else str(manifest['max_turns']))}",
            f"MAX_BUDGET_USD={q('' if manifest.get('max_budget_usd') in (None, '') else str(manifest['max_budget_usd']))}",
            f"SOFT_BUDGET_GUIDANCE={q(manifest.get('soft_budget_guidance') or '')}",
            f"REQUIRED_OUTPUTS={q(', '.join(manifest.get('required_outputs') or []))}",
            f"ALLOWED_WRITE_ROOTS={q(', '.join(manifest.get('allowed_write_roots') or []))}",
        ]
    )
    + "\n",
    encoding="utf-8",
)
add_dirs_path.write_text("\n".join(add_dirs) + "\n", encoding="utf-8")
PY

# shellcheck disable=SC1090
. "$ENV_FILE"

RUNNER_PROMPT=$(cat <<EOF
You are executing a cross-vendor review packet.

Review directory: $REVIEW_DIR
Review spec: $REVIEW_DIR/REVIEW-SPEC.md
Prompt: $REVIEW_DIR/PROMPT.md

Read REVIEW-SPEC.md and PROMPT.md. Follow PROMPT.md exactly unless it conflicts with the review spec or these runner constraints.

Declared required outputs: $REQUIRED_OUTPUTS
Allowed write roots: $ALLOWED_WRITE_ROOTS

Write the declared review output files directly. Do not treat raw chat output as the durable review artifact. Do not write outside the allowed write roots. Do not fill reviewer identity, confidence, or disposition unless you are actually providing them as the reviewer. If you cannot complete the review, leave the required outputs absent or clearly incomplete so the recovery workflow can preserve logs.

You may use local inspection commands when needed for the review. Do not modify source files or project state outside the allowed write roots.
EOF
)

if [ -n "$SOFT_BUDGET_GUIDANCE" ]; then
  RUNNER_PROMPT="$RUNNER_PROMPT

Soft budget guidance: $SOFT_BUDGET_GUIDANCE"
else
  RUNNER_PROMPT="$RUNNER_PROMPT

Soft budget guidance: if the review is becoming too broad, write the strongest supported review artifact with explicit coverage limits instead of continuing indefinitely."
fi

CMD=(claude -p "$RUNNER_PROMPT"
  --name "$SESSION_NAME"
  --model "$MODEL"
  --permission-mode "$PERMISSION_MODE"
  --output-format stream-json
  --include-partial-messages
  --verbose
  --tools "$TOOLS"
  --setting-sources project)

while IFS= read -r add_dir; do
  [ -n "$add_dir" ] || continue
  CMD+=(--add-dir "$add_dir")
done < "$ADD_DIRS_FILE"

if [ -n "$MAX_TURNS" ]; then
  CMD+=(--max-turns "$MAX_TURNS")
fi

if [ -n "$MAX_BUDGET_USD" ]; then
  CMD+=(--max-budget-usd "$MAX_BUDGET_USD")
fi

printf '%q ' "${CMD[@]}" > "$RAW_DIR/claude.command.txt"
printf '\n' >> "$RAW_DIR/claude.command.txt"
date -u +%Y-%m-%dT%H:%M:%SZ > "$RAW_DIR/claude.started-at.txt"

set +e
"${CMD[@]}" > "$RAW_DIR/claude.stdout.stream-json" 2> "$RAW_DIR/claude.stderr.log"
CLAUDE_EXIT=$?
set -e

printf '%s\n' "$CLAUDE_EXIT" > "$RAW_DIR/claude.exit-code.txt"
date -u +%Y-%m-%dT%H:%M:%SZ > "$RAW_DIR/claude.completed-at.txt"

if git rev-parse --show-toplevel >/dev/null 2>&1; then
  git status --short --branch > "$RAW_DIR/git-status-after.txt" 2>/dev/null || true
  # S6 fix (gates review): `git diff --` captures only unstaged changes.
  # A misbehaving reviewer that stages writes via `git add` would leave
  # no record in the human-inspection patch even though git status (used
  # by verify-review-output.sh) sees the staged paths. `git diff HEAD --`
  # captures staged + unstaged.
  git diff HEAD -- > "$RAW_DIR/git-diff-after.patch" 2>/dev/null || true
else
  : > "$RAW_DIR/git-status-after.txt"
  : > "$RAW_DIR/git-diff-after.patch"
fi

python3 - "$MANIFEST" "$CLAUDE_EXIT" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

manifest_path = Path(sys.argv[1])
exit_code = int(sys.argv[2])
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
raw_dir = Path(manifest["paths"]["raw_dir"])
stream_path = raw_dir / "claude.stdout.stream-json"

stream_valid = True
session_id = ""
observed_model = ""
result = {}
errors = []
line_count = 0
try:
    for line in stream_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        line_count += 1
        item = json.loads(line)
        session_id = item.get("session_id") or session_id
        if item.get("type") == "system" and item.get("subtype") == "init":
            observed_model = item.get("model") or observed_model
        if item.get("type") == "assistant":
            observed_model = item.get("message", {}).get("model") or observed_model
        if item.get("type") == "result":
            result = item
            session_id = item.get("session_id") or session_id
except Exception as exc:
    stream_valid = False
    errors.append(str(exc))

manifest.setdefault("claude", {})
manifest["claude"].update(
    {
        "exit_code": exit_code,
        "session_id": session_id,
        "observed_model": observed_model,
        "result_subtype": result.get("subtype", ""),
        "terminal_reason": result.get("terminal_reason", ""),
        "stop_reason": result.get("stop_reason", ""),
        "total_cost_usd": result.get("total_cost_usd"),
        "num_turns": result.get("num_turns"),
        "permission_denials": result.get("permission_denials", []),
        "stream_json_valid": stream_valid,
        "stream_json_line_count": line_count,
        "stream_json_errors": errors,
    }
)
manifest["git"]["status_after"] = (raw_dir / "git-status-after.txt").read_text(encoding="utf-8")
manifest["status"] = "claude_completed" if exit_code == 0 and stream_valid else "claude_failed"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

summary = {
    "run_id": manifest["run_id"],
    "status": manifest["status"],
    "review_id": manifest.get("review_id"),
    "review_dir": manifest.get("review_dir"),
    "session_name": manifest.get("claude", {}).get("session_name"),
    "session_id": session_id,
    "requested_model": manifest.get("model"),
    "observed_model": observed_model,
    "permission_mode": manifest.get("permission_mode"),
    "tools": manifest.get("tools"),
    "exit_code": exit_code,
    "result_subtype": result.get("subtype", ""),
    "terminal_reason": result.get("terminal_reason", ""),
    "total_cost_usd": result.get("total_cost_usd"),
    "stream_json_valid": stream_valid,
}
(Path(manifest["paths"]["run_dir"]) / "REVIEW-RUN.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
PY

set +e
"$SCRIPT_DIR/verify-review-output.sh" "$REVIEW_DIR" "$RUN_ID"
VERIFY_EXIT=$?
set -e

python3 - "$MANIFEST" "$VERIFY_EXIT" <<'PY'
from __future__ import annotations

import json
import sys
from pathlib import Path

manifest_path = Path(sys.argv[1])
verify_exit = int(sys.argv[2])
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
claude = manifest.get("claude", {})
success = claude.get("exit_code") == 0 and bool(claude.get("stream_json_valid")) and verify_exit == 0
manifest["verification_exit_code"] = verify_exit
manifest["status"] = "success" if success else "failed"
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
summary_path = Path(manifest["paths"]["run_dir"]) / "REVIEW-RUN.json"
summary = json.loads(summary_path.read_text(encoding="utf-8"))
summary["status"] = manifest["status"]
summary["verification_exit_code"] = verify_exit
summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
PY

if [ "$CLAUDE_EXIT" -eq 0 ] && [ "$VERIFY_EXIT" -eq 0 ] && python3 - "$MANIFEST" <<'PY'
from __future__ import annotations
import json, sys
from pathlib import Path
m=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
raise SystemExit(0 if m.get("claude", {}).get("stream_json_valid") else 1)
PY
then
  RETAIN=$(python3 - "$MANIFEST" <<'PY'
from __future__ import annotations
import json, sys
from pathlib import Path
m=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print("true" if m.get("raw_logs", {}).get("retain_on_success") else "false")
PY
)
  if [ "$RETAIN" != "true" ]; then
    rm -f "$RAW_DIR/claude.stdout.stream-json" "$RAW_DIR/claude.stderr.log"
  fi
  exit 0
fi

"$SCRIPT_DIR/recover-review.py" "$REVIEW_DIR" "$RUN_ID"
exit 1
