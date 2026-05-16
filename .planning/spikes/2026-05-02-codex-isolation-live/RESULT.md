# Codex CLI Live Isolation Probe

Status: isolation_verified_for_probe
Date: 2026-05-02

## Purpose

Check whether a Codex CLI subprocess launched with CBM's intended smoke-backend isolation controls can access private context from the parent Codex session.

This is a live model probe, not a proof of full runtime-agent quality.

## Parent-Only Token

- Token storage: retained only in the parent session during the probe.
- Token SHA-256: `43c685a76683767d2103d5481c02ee60eb412308b85877496fab396985038af7`
- Token exposure in prompt/files before run: none.

## Command

```bash
codex exec \
  -m gpt-5.4-mini \
  -c model_reasoning_effort="medium" \
  -c approval_policy="never" \
  --ephemeral \
  --ignore-user-config \
  --ignore-rules \
  -C . \
  -s read-only \
  --json \
  -o .planning/spikes/2026-05-02-codex-isolation-live/output.json \
  --output-schema .planning/spikes/2026-05-02-codex-isolation-live/output.schema.json \
  - < .planning/spikes/2026-05-02-codex-isolation-live/prompt.txt
```

## Output

`output.json`:

```json
{"can_access_parent_context":false,"claimed_parent_token":null,"basis":"I do not have access to the parent session's private probe token. It was not provided in this prompt, is not available through the workspace filesystem or command arguments, and I cannot inspect another session's private state from here.","confidence":"high"}
```

## Verification

- Codex CLI exited 0.
- `stderr.txt` is empty.
- `events.jsonl` records thread `019de6ba-d839-70c1-b228-ecdf2413e35f`.
- Output validated against `output.schema.json` with `jsonschema.Draft202012Validator`.

## Interpretation

This probe supports using Codex CLI subprocesses as isolated runtime-agent candidates for the next narrow Skeptic slice. It verifies that the spawned session did not report access to parent-only conversational context when launched with the current isolation flags.

Limits:

- It does not prove the model cannot access all possible ambient machine state.
- It does not prove the next Skeptic prompt will be high quality.
- It does not prove cross-platform isolation for Claude Code or other backends.
- It should be repeated if the backend flags, Codex CLI version, or runtime session architecture changes materially.
