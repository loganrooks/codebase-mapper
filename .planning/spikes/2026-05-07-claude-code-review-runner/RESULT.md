# Claude Code Review Runner Spike Result

Status: complete
Observed: 2026-05-07 local / 2026-05-08 UTC
Scope: generic Claude Code CLI runner behavior for cross-vendor review launch and recovery

## Summary

Claude Code CLI is available locally and can run non-interactive review tasks that write declared files directly. The useful runner shape is `claude -p` with `--output-format stream-json`, `--include-partial-messages`, `--verbose`, `--permission-mode auto`, `--name`, explicit `--model`, explicit `--tools`, and `--add-dir <review-dir>`.

Hard CLI cutoffs such as `--max-turns` and `--max-budget-usd` are useful failure probes but should not be default runner settings. They can terminate a review before the reviewer writes the required artifact, increasing recovery cost. If a review needs budget management, prefer soft prompt guidance or an explicit review-spec override; otherwise run without hard turn/cost limits.

The run envelope is recoverable from captured command, stdout stream-json, stderr, exit code, timestamps, git state, prompt/spec hashes, session name, and session id. Raw stream output is useful for diagnosis but should not be treated as the durable review artifact; the reviewer-written output files remain the authoritative review deliverable.

## CLI Capability Check

Commands run:

```bash
command -v claude
claude --version
claude --help
```

Observed:

- CLI path: `/Applications/cmux.app/Contents/Resources/bin/claude`
- Version: `2.1.126 (Claude Code)`
- `claude --help` includes `-p` / `--print`, `--model`, `--output-format stream-json`, `--include-partial-messages`, `--verbose`, `--max-turns`, `--max-budget-usd`, `--permission-mode` with `acceptEdits`, `auto`, `bypassPermissions`, `default`, `dontAsk`, and `plan`, `--name`, `--resume`, `--json-schema`, `--tools`, `--add-dir`, and `--setting-sources`.
- `--continue` exists but was not used.
- `--dangerously-skip-permissions` exists but was not used.

## Scratch Runs

Raw logs were kept under `/var/tmp` scratch directories and are not committed.

| Probe | Scratch directory | Command shape | Exit | Result |
| --- | --- | --- | --- | --- |
| Opus budget failure | `/var/tmp/cbm-xvr-spike-20260508T014855Z` | `--model opus --permission-mode acceptEdits --output-format stream-json --include-partial-messages --verbose --max-turns 6 --max-budget-usd 0.25 --add-dir <scratch>` | 1 | No output file written; final stream result was `subtype: error_max_budget_usd`. This is evidence against hard budget defaults. |
| Normal write | `/var/tmp/cbm-xvr-spike-success-20260508T014955Z` | `--model sonnet --permission-mode acceptEdits --output-format stream-json --include-partial-messages --verbose --max-turns 6 --max-budget-usd 0.50 --tools Read,Write,Edit --add-dir <scratch> --setting-sources project` | 0 | `OUTPUT.md` written directly; final result `subtype: success`; no permission denials. |
| Resume by session name | same success scratch directory | `--resume <session-name> -p ... --permission-mode acceptEdits --output-format stream-json --include-partial-messages --verbose --max-turns 4 --max-budget-usd 0.35 --tools Read,Write,Edit --add-dir <scratch> --setting-sources project` | 0 | Resume by display name worked, reused the same session id, saw prior context, and appended to `OUTPUT.md`. |
| Missing output | `/var/tmp/cbm-xvr-spike-missing-output-20260508T015143Z` | No file tools | 0 | Process succeeded but `OUTPUT.md` remained empty. Verification must catch this as failed review output. |
| Outside-write malformed probe | `/var/tmp/cbm-xvr-spike-outside-write-20260508T015143Z` | `--tools Write` without Read | 0 | Process succeeded but could not read `PROMPT.md`; created an undeclared scratch file and left `OUTPUT.md` empty. Verification must not trust process success alone. |
| Max turns | `/var/tmp/cbm-xvr-spike-max-turns-20260508T015143Z` | `--max-turns 1 --tools Read,Write` | 1 | Final stream result was `subtype: error_max_turns`, `terminal_reason: max_turns`, `stop_reason: tool_use`; `OUTPUT.md` empty. |
| Outside-write controlled probe | `/var/tmp/cbm-xvr-spike-outside-write2-20260508T015313Z` | `--tools Read,Write`, prompt asked for write outside declared root | 0 | Claude refused to write outside `allowed_write_roots`; no outside file was created; `OUTPUT.md` remained empty. Verification must classify this as missing expected output, not success. |

## Stream JSON Observations

- `stream-json` includes system init records with `session_id`, `model`, `permissionMode`, tool list, Claude Code version, and environment metadata.
- Assistant message records include `message.model` and `message.usage`.
- Final `result` records include `subtype`, `is_error`, `session_id`, `total_cost_usd`, `usage`, `modelUsage`, `num_turns`, `stop_reason`, `terminal_reason`, and `permission_denials`.
- Partial message chunks are useful for recovery because they expose streamed tool input deltas, text deltas, tool results, refusal text, and the point where a max-turn failure occurred.
- `--include-partial-messages` increases raw log size but makes partial-output recovery meaningfully better.
- Empty stderr was normal for both success and observed failures; stderr alone is not sufficient.

## Session And Resume Observations

- `--name <session-name>` works for labeling a run.
- `--resume <session-name>` worked in non-interactive mode and reused the original `session_id`.
- The resumed run saw prior context and wrote correctly.
- A recovery command should include the originally requested `--model`; the resume probe omitted `--model` and the resumed run used the local default Opus model instead of the original Sonnet model.
- No `--fork-session` flag was needed for this recovery shape.
- `--continue` was not used and should remain disallowed for automated recovery because it is less explicit than the captured run's session name/id.

## Permission And Tool Observations

- `acceptEdits` allowed direct writes to the scratch review directory in non-interactive mode without prompting, but it is narrower than many real review tasks need. The skill should default to a more permissive review envelope: `permission_mode: auto` and tools `Read,Write,Edit,Bash`, while still verifying output files and write scope after the run.
- Limiting tools matters. A run with only `Write` could not read `PROMPT.md` and still exited 0 after producing a textual failure. The runner should pass an explicit tool envelope instead of assuming the default tool set.
- A controlled prompt-in-content attempt to write outside `allowed_write_roots` was refused by Claude, but the process still exited 0 and required output remained empty. The runner must verify files and write scope after every process result.
- `permission_denials` was empty in observed runs, including the outside-write refusal. The runner cannot rely on `permission_denials` alone to detect scope issues.

## Recommended Command Shape

For normal launch:

```bash
claude -p "<runner prompt naming review dir, spec, outputs, and write roots>" \
  --name "$SESSION_NAME" \
  --model "$MODEL" \
  --permission-mode "$PERMISSION_MODE" \
  --output-format stream-json \
  --include-partial-messages \
  --verbose \
  --tools "$TOOLS" \
  --add-dir "$REVIEW_DIR" \
  --setting-sources project
```

Default values:

- `PERMISSION_MODE=auto`
- `TOOLS=Read,Write,Edit,Bash`
- no `--max-turns` unless `REVIEW-SPEC.md` explicitly sets `max_turns`
- no `--max-budget-usd` unless `REVIEW-SPEC.md` explicitly sets `max_budget_usd`

For recovery:

```bash
claude --resume "$SESSION_NAME" -p "<bounded recovery prompt>" \
  --model "$MODEL" \
  --permission-mode "$PERMISSION_MODE" \
  --output-format stream-json \
  --include-partial-messages \
  --verbose \
  --tools "$TOOLS" \
  --add-dir "$REVIEW_DIR" \
  --setting-sources project
```

Recovery should preserve the original explicit model, permission mode, and tools from the manifest. It should not add hard turn/cost limits unless they were explicitly declared in the review spec.

## Script Decisions

- Preflight should fail if `PROMPT.md` is missing and should require `REVIEW-SPEC.md` for scripted runs.
- The runner should capture a `RUN-MANIFEST.json` with branch, SHA, git status, prompt/spec hashes, declared outputs, allowed write roots, command, session name, session id if observed, and timestamps.
- The runner should treat Claude exit 0 as necessary but not sufficient; verification must check required outputs, non-empty output files, and write-scope drift.
- Raw stdout/stderr logs should be kept during the run, summarized in `REVIEW-RUN.json`, cleaned on success unless `raw_logs.retain_on_success: true`, and preserved on failure.
- Recovery should classify failures from process result plus post-run verification. Important classifications observed here: `max_turns_or_budget`, `missing_expected_output`, `partial_expected_output`, and `wrote_outside_allowed_scope` or undeclared-write drift when post-run file/diff checks detect it. `max_turns_or_budget` should remain a supported recovery classification, not a default launch behavior.
- Recovery must not synthesize reviewer content or fill identity/disposition from logs. It may provide a copy-ready explicit `--resume <session-name>` command when the manifest has a session name and the failure is safe to resume.
