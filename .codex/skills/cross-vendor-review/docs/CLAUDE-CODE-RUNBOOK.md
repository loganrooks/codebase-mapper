# Claude Code Cross-Vendor Review Runbook

Status: initial runbook from local spike

## Preflight

Run from the repo root:

```bash
.codex/skills/cross-vendor-review/scripts/preflight.sh .planning/reviews/<review-id>
```

Preflight checks:

- review directory exists;
- `PROMPT.md` exists;
- `REVIEW-SPEC.md` exists;
- `claude` is on `PATH`;
- `claude --version` and `claude --help` are captured;
- git branch, SHA, and status are captured;
- prompt/spec hashes are captured;
- `.xvr-runs/<run-id>/RUN-MANIFEST.json` is written.

For checkpoint/pass-claim-style reviews, dirty worktrees fail unless `allow_dirty_worktree: true` is explicitly declared.

## Default Launch Shape

The runner launches Claude Code approximately as:

```bash
claude -p "<generated runner prompt>" \
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

Defaults:

- `MODEL` comes from `preferred_model`, defaulting to `opus`.
- `PERMISSION_MODE` defaults to `auto`.
- `TOOLS` defaults to `Read,Write,Edit,Bash`.
- hard `--max-turns` and `--max-budget-usd` are omitted unless the review spec explicitly sets `max_turns` or `max_budget_usd`.

This is intentionally more permissive than `acceptEdits` so real reviews can run local inspection commands. The runner still verifies required outputs and write scope after Claude exits.

## Permission Modes

Use `permission_mode: auto` by default.

Use narrower modes such as `acceptEdits` only when the review truly only needs to read and write declared artifacts.

Use `bypassPermissions` only when the human explicitly authorizes that review packet and the write-root verification risk is understood. This skill does not pass `--dangerously-skip-permissions`.

Do not install global Claude settings for CBM review behavior. Keep permissions in the review spec or, if needed later, a documented project-local settings file referenced by the spec.

## Raw Log Lifecycle

During the run, raw files live under:

```text
<review-dir>/.xvr-runs/<run-id>/raw/
```

Important files:

- `claude.command.txt`
- `claude.stdout.stream-json`
- `claude.stderr.log`
- `claude.exit-code.txt`
- `git-status-before.txt`
- `git-status-after.txt`
- `git-diff-after.patch`

On success:

- keep reviewer-written outputs;
- keep `RUN-MANIFEST.json`;
- keep `REVIEW-RUN.json`;
- delete raw stdout/stderr logs unless `raw_logs.retain_on_success: true`.

On failure:

- preserve raw logs;
- write `RECOVERY.md`;
- do not synthesize review output from logs.

## Resume

Use explicit resume only:

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

Local spike result:

- `--name <session-name>` worked.
- `--resume <session-name>` worked.
- Resume reused the same session id and saw prior context.
- Resume must include the original requested model; otherwise Claude may use the local default model.

Never use `--continue` for automated recovery.

## Verification

Run:

```bash
.codex/skills/cross-vendor-review/scripts/verify-review-output.sh .planning/reviews/<review-id> <run-id>
```

Verification checks:

- required outputs exist;
- required outputs are non-empty;
- new git status entries are inside allowed write roots;
- checkpoint/disposition reviews include actual reviewer model identity and allowed disposition when declared.

Verification does not mark any project horizon complete.
