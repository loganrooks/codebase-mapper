# Temporary Engineering Plan — Cross-Vendor Review Skill Spike And Minimal Implementation

Status: proposed temporary plan
Date: 2026-05-07
Intended repo path: `.planning/spikes/2026-05-07-cross-vendor-review-skill/PLAN.md`
Audience: Codex implementation agent, human reviewer, future senior-engineering audit
Purpose: plan and constrain the construction of a generic repo-local Codex skill for launching and recovering cross-vendor reviews through Claude Code CLI.

## Why This Plan Exists

We need a repeatable way to launch cross-vendor / non-current-model reviews without relying on ad hoc chat instructions.

However, we should not implement a large review framework from assumptions. Before building the skill, the agent must run a small spike to observe the local Claude Code CLI behavior: output shape, session naming, resume behavior, failure modes, permissions, and what can be recovered from captured logs.

This plan is temporary. It should be superseded by the final skill package and spike result.

## Core Design Position

The skill should be an operational envelope, not a review ontology.

The skill is responsible for:

- launching a cross-vendor reviewer;
- constraining write scope;
- capturing a temporary recovery envelope;
- verifying expected outputs;
- cleaning temporary raw logs after success;
- preserving enough information to recover from failure;
- preventing fake reviewer dispositions.

The skill is not responsible for:

- deciding the review outcome;
- encoding H1, Phase 01, or CBM-specific pass-claim semantics;
- moving horizons;
- marking pass claims accepted;
- rewriting planning docs after a review;
- becoming a generalized multi-vendor framework.

Review-specific meaning belongs in the review directory:

```text
.planning/reviews/<review-id>/
  REVIEW-SPEC.md
  PROMPT.md
  CHECKPOINT.md        # only for checkpoint/pass-claim reviews
  DISPOSITION.md       # only for gated/disposition reviews
  OUTPUT.md            # optional general review output
```

The reusable operational skill belongs in:

```text
.codex/skills/cross-vendor-review/
```

## Important Correction To Earlier Thinking

The reviewer should usually write the declared output files directly.

Raw Claude output is not the primary durable review artifact. Raw output is a transactional recovery buffer.

Expected lifecycle:

```text
Claude writes declared output files directly:
  CHECKPOINT.md / DISPOSITION.md / OUTPUT.md / REVIEW.md

The skill captures raw command/stdout/stderr/stream/diff temporarily:
  .planning/reviews/<review-id>/.xvr-runs/<run-id>/

On success:
  keep reviewer-written files;
  keep a small REVIEW-RUN.json or REVIEW-RUN.md summary;
  clean raw logs unless configured otherwise.

On failure:
  preserve raw logs locally;
  write RECOVERY.md or STOP-NOTE.md;
  do not synthesize a successful review.
```

## What We Must Not Assume

Do not assume raw logs are sufficient unless the launcher captures enough context.

A recoverable run envelope must include:

- review directory;
- review id;
- git branch and SHA before the run;
- git status before the run;
- exact Claude command;
- prompt path and prompt hash;
- review spec path and hash, if present;
- declared expected outputs;
- allowed write scope;
- stdout/stderr or stream-json;
- exit code;
- start and completion timestamps;
- git diff after the run;
- hashes of expected output files if written;
- Claude session name or id if available;
- Claude model identity if observable.

Do not inspect undocumented Claude Code session storage. Use documented CLI controls only.

## Documented Claude Code CLI Surfaces To Verify Locally

The plan may rely only on documented surfaces, but the agent must verify local availability with `claude --help` and a spike.

Expected useful CLI surfaces:

- `claude -p` / `--print` for non-interactive mode;
- `--model` for model selection;
- `--output-format json` or `--output-format stream-json`;
- `--include-partial-messages` with stream-json;
- `--verbose`;
- `--max-turns`;
- `--max-budget-usd`, if available;
- `--permission-mode acceptEdits`;
- `--name` / `-n` for session naming, if available;
- `--resume <session>` / `-r <session>` for explicit recovery;
- `--json-schema`, if available and useful.

Do not use `--continue` for automated recovery. It resumes the most recent conversation in the current directory and is less explicit than `--resume <session>`.

Do not use `--dangerously-skip-permissions` unless the user explicitly authorizes it in an isolated throwaway environment.

## Review Directory Contract

The skill must work against a review directory supplied as an argument.

Minimum required files:

```text
REVIEW-SPEC.md      # preferred; required for scripted reviews after this skill exists
PROMPT.md           # always required
```

For checkpoint/pass-claim reviews:

```text
CHECKPOINT.md
DISPOSITION.md
```

For general reviews:

```text
OUTPUT.md           # may be pre-created as a placeholder, depending on spec
```

Suggested minimal `REVIEW-SPEC.md` shape:

```yaml
review_id: 2026-05-07-h1-minimum-useful-checkpoint
review_type: pass_claim_checkpoint
runner: claude-code-cli
reviewer_requirement: cross_vendor
preferred_model: opus
writes_allowed: true
allowed_write_roots:
  - .planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/
required_outputs:
  - CHECKPOINT.md
  - DISPOSITION.md
raw_logs:
  retain_on_success: false
  retain_on_failure: true
decision_required: true
allowed_dispositions:
  - accept
  - accept_with_blockers
  - revise
  - reject
```

For non-gated reviews:

```yaml
review_type: architecture_review
required_outputs:
  - OUTPUT.md
decision_required: false
```

Do not overbuild this into a large schema unless a real failure demonstrates the need.

## Planned Package

Create:

```text
.codex/skills/cross-vendor-review/
  SKILL.md
  docs/
    REVIEW-SPEC-CONTRACT.md
    CLAUDE-CODE-RUNBOOK.md
    FAILURE-MODES.md
    SPIKE-FINDINGS-TEMPLATE.md
  scripts/
    preflight.sh
    run-claude-code-review.sh
    verify-review-output.sh
    recover-review.py
```

Do not create a broad multi-vendor abstraction yet. The first runner is Claude Code CLI. The generic part is the review directory contract and recovery envelope.

## Phase A — Spike Claude Code CLI Behavior

Before implementing production scripts, run a scratch spike.

### A1. Create Scratch Review Directory

Use a non-committed scratch directory:

```text
/tmp/cbm-xvr-spike-<timestamp>/
```

or a repo-local gitignored directory:

```text
.tmp/cross-vendor-review-spike-<timestamp>/
```

Do not commit raw scratch logs unless needed for the spike result.

Files:

```text
REVIEW-SPEC.md
PROMPT.md
OUTPUT.md
```

Prompt should ask Claude to:

- read `PROMPT.md`;
- write `OUTPUT.md`;
- include model/reviewer identity if possible;
- make a small, harmless review judgment;
- write only inside the scratch review directory.

### A2. Verify CLI Capabilities

Run and record:

```bash
command -v claude
claude --version
claude --help
```

Record whether help includes:

- `--name`;
- `--resume`;
- `--output-format stream-json`;
- `--include-partial-messages`;
- `--permission-mode`;
- `--max-turns`;
- `--max-budget-usd`;
- `--json-schema`.

Write summary to:

```text
.planning/spikes/2026-05-07-claude-code-review-runner/RESULT.md
```

### A3. Test Normal Non-Interactive Write

Use a unique session name:

```bash
SESSION_NAME="xvr-spike-$(date -u +%Y%m%dT%H%M%SZ)"
```

Run a bounded non-interactive review. The exact command may need adjustment based on local `claude --help`.

Preferred command shape:

```bash
claude -p "Read the review directory at <scratch-review-dir>. Follow PROMPT.md. Write only the declared output files in that directory." \
  --name "$SESSION_NAME" \
  --model opus \
  --permission-mode acceptEdits \
  --output-format stream-json \
  --include-partial-messages \
  --verbose \
  --max-turns 6
```

If `--max-budget-usd` is available, include a small explicit budget for the spike.

Capture:

```text
raw/claude.command.txt
raw/claude.stdout.stream-json
raw/claude.stderr.log
raw/claude.exit-code.txt
raw/claude.started-at.txt
raw/claude.completed-at.txt
raw/git-status-before.txt
raw/git-status-after.txt
raw/git-diff-after.patch
raw/session-name.txt
```

### A4. Observe Output Shape

Answer in `RESULT.md`:

- Does `stream-json` include a session id?
- Does output include model identity?
- Does output include usage/cost?
- Are partial messages useful for recovery?
- Does `--name` work?
- Does the run write the expected output file?
- Does `acceptEdits` work in non-interactive mode without prompts?
- Does the run block on permissions?
- What does a successful exit look like?

### A5. Test Explicit Resume By Session Name

Do not use `--continue`.

Run:

```bash
claude --resume "$SESSION_NAME" -p "Continue the scratch review. Append a short 'Resume check passed' line to OUTPUT.md. Write only in the scratch review directory." \
  --permission-mode acceptEdits \
  --output-format stream-json \
  --include-partial-messages \
  --verbose \
  --max-turns 4
```

Record:

- whether resume by name works;
- whether the resumed run sees prior context;
- whether it writes correctly;
- whether it creates a new session id or reuses the session;
- whether a fork/resume flag is needed or undesirable.

### A6. Failure Mode Observations

Run only safe, cheap, bounded failure probes:

1. Missing required output:
   - prompt Claude to summarize but not write a file;
   - verify detection logic.

2. Permission/write-scope violation:
   - ask Claude to write outside the scratch review directory in a controlled way;
   - verify that post-run diff/write-scope detection catches it.

3. Max-turns / interrupted behavior:
   - set `--max-turns 1` with a task that likely needs more than one step;
   - record exit code and output shape.

Do not run expensive or destructive probes.

### A7. Spike Result

Commit a concise spike result, not raw logs:

```text
.planning/spikes/2026-05-07-claude-code-review-runner/RESULT.md
```

Include:

- commands attempted;
- observed CLI support;
- observed output structure;
- whether session id/name can be captured;
- whether `--resume <session-name>` works;
- recommended command shape;
- known caveats;
- decisions for scripts.

## Phase B — Implement Minimal Skill

Only after the spike result exists.

### B1. `SKILL.md`

Must state:

- this skill manages review launch/recovery only;
- it does not decide review outcomes;
- it never fills reviewer identity/disposition without actual reviewer output;
- it defaults to Claude Code CLI;
- it uses documented CLI surfaces only;
- it recovers from its own captured run envelope, not private Claude session files;
- it prefers `--resume <session-name>` over `--continue`;
- it cleans raw logs on success by default;
- it preserves raw logs on failure for recovery.

### B2. `docs/REVIEW-SPEC-CONTRACT.md`

Describe minimal review spec fields and examples.

Must support at least:

- pass-claim checkpoint review;
- general architecture/design review;
- artifact/provenance audit;
- code/diff review.

Do not require `CHECKPOINT.md` unless `review_type` is a checkpoint or `required_outputs` declares it.

### B3. `docs/CLAUDE-CODE-RUNBOOK.md`

Document the observed command shape from the spike.

Must include:

- auth/model preflight;
- permission mode;
- session naming;
- resume by session name;
- raw log lifecycle;
- success cleanup;
- failure preservation.

### B4. `docs/FAILURE-MODES.md`

Include at least:

- missing CLI;
- unauthenticated CLI;
- model unavailable;
- permission prompt/block;
- nonzero exit;
- max turns / max budget;
- missing expected output;
- partial expected output;
- malformed stream-json;
- writes outside allowed scope;
- dirty worktree before run;
- dirty worktree after unexpected files;
- ambiguous session/resume state.

### B5. `scripts/preflight.sh`

Arguments:

```bash
preflight.sh <review-dir>
```

Responsibilities:

- fail if review dir missing;
- fail if `PROMPT.md` missing;
- warn or fail if `REVIEW-SPEC.md` missing, depending chosen policy;
- check `claude` is on PATH;
- capture `claude --version`;
- capture `claude --help`;
- create `.xvr-runs/<run-id>/raw/` and `.xvr-runs/<run-id>/logs/`;
- capture git branch/SHA/status;
- detect dirty tree;
- compute prompt/spec hashes;
- write `RUN-MANIFEST.json` or `RUN-MANIFEST.md`.

For pass-claim reviews, dirty worktree should fail unless the review spec explicitly allows it.

### B6. `scripts/run-claude-code-review.sh`

Arguments:

```bash
run-claude-code-review.sh <review-dir>
```

Responsibilities:

- call `preflight.sh` or require a preflight manifest;
- compute unique session name;
- launch Claude Code CLI using observed safe command shape;
- set permission mode to `acceptEdits` unless spec overrides;
- constrain the prompt to write only declared outputs inside allowed write roots;
- capture raw stdout/stderr/exit code/timestamps/command;
- capture git diff after run;
- verify whether writes occurred outside allowed roots;
- on success, call verify;
- on failure, call recovery.

Raw logs are temporary:

- if success and spec says `retain_on_success: false`, delete raw stdout/stderr after writing a small run summary;
- if failure, preserve raw logs.

### B7. `scripts/verify-review-output.sh`

Arguments:

```bash
verify-review-output.sh <review-dir> [run-id]
```

Responsibilities:

- ensure required outputs exist;
- ensure required outputs are non-empty;
- ensure no writes outside allowed write roots;
- for checkpoint reviews:
  - ensure reviewer identity is present if disposition is filled;
  - ensure same-model fallback rules are not violated if declared;
  - ensure disposition is one of allowed values;
- do not mark project horizons complete.

### B8. `scripts/recover-review.py`

Arguments:

```bash
recover-review.py <review-dir> [run-id]
```

Responsibilities:

- inspect run manifest/raw logs;
- classify failure:
  - preflight_failed;
  - launch_failed;
  - auth_failed;
  - model_unavailable;
  - permission_blocked;
  - nonzero_exit;
  - max_turns_or_budget;
  - missing_expected_output;
  - partial_expected_output;
  - malformed_stream_json;
  - wrote_outside_allowed_scope;
  - ambiguous_session;
- write `RECOVERY.md` with:
  - what happened;
  - captured files;
  - expected outputs present/missing;
  - whether `--resume <session-name>` is available;
  - a copy-ready resume command if safe;
  - otherwise a copy-ready rerun command.

Do not synthesize final review content from logs.

## Phase C — Tests And Edge Cases

Use fake Claude commands for deterministic tests.

Recommended tests:

1. `preflight` fails on missing review dir.
2. `preflight` fails on missing `PROMPT.md`.
3. successful fake Claude writes required output:
   - verification passes;
   - raw logs are cleaned if configured;
   - run summary remains.
4. fake Claude exits nonzero:
   - recovery file written;
   - raw logs preserved;
   - no success status written.
5. fake Claude writes no required output:
   - recovery file written.
6. fake Claude writes outside allowed root:
   - verification fails;
   - diff preserved;
   - recovery file written.
7. checkpoint review output missing reviewer identity:
   - verification fails for pass-claim type.
8. malformed stream-json:
   - recovery file written;
   - no fake disposition.

Do not build large test scaffolding. Keep fake Claude as a small shell or Python fixture.

## Phase D — AGENTS.md Pointer

Add a short pointer:

```markdown
## Cross-vendor reviews

For cross-vendor or non-current-model reviews, use:

`.codex/skills/cross-vendor-review/SKILL.md`

If Codex does not auto-discover repo-local skills, read that file directly. Do not improvise review execution from chat context. Do not fill reviewer identity or disposition without actual reviewer output. Use the skill's recovery workflow if Claude Code fails, writes partial files, or writes outside the review directory.
```

## Verification For This Plan

When implementing this plan, run:

```bash
bash -n .codex/skills/cross-vendor-review/scripts/*.sh
python3 -m py_compile .codex/skills/cross-vendor-review/scripts/*.py
```

If tests are added:

```bash
TMPDIR=/var/tmp pytest -q <focused test path>
```

Then:

```bash
git diff --check -- .codex .planning AGENTS.md BUILD-LOG.md tests
python3 -m cbm.cli loop-status --repo . --scope broad-goal --work-category runtime-producer --json
```

Do not run the H1 checkpoint review during this implementation unless a later explicit goal requests it.

## Stop Conditions

Stop and surface if:

- Claude Code CLI is unavailable;
- Claude Code CLI help does not support the required documented flags;
- `--resume <session-name>` behavior cannot be verified;
- `acceptEdits` cannot write declared review files non-interactively;
- the only way to run the review is `--dangerously-skip-permissions`;
- raw logs contain secrets that cannot be safely handled;
- fake tests require a broad testing framework;
- implementation requires a generalized multi-vendor abstraction;
- implementation starts to encode H1-specific logic;
- the agent is tempted to run the H1 checkpoint review in this goal.

## Commit Expectations

This plan should normally produce two commits:

1. Spike result:

```text
docs: record claude code review runner spike
```

2. Skill package:

```text
feat: add cross-vendor review skill
```

If the repo prefers one commit, include both Why and Verification in the commit body.

## Brief `/goal` Prompt Pointing To This Plan

```text
/goal implement the cross-vendor review skill by following .planning/spikes/2026-05-07-cross-vendor-review-skill/PLAN.md.

Do not draft the skill from assumptions. First run the Claude Code CLI spike described in the plan and record observed behavior in .planning/spikes/2026-05-07-claude-code-review-runner/RESULT.md. Then implement only the minimal repo-local Codex skill described by the plan.

The skill must be generic, not H1-specific. It must default to Claude Code CLI, allow the reviewer to write declared review files, capture raw logs as temporary recovery buffers, clean raw logs on success, preserve recovery material on failure, and never fake reviewer identity or disposition.

Do not run the H1 checkpoint review. Do not mark H1 complete. Do not move to H2. Stop and surface if Claude Code CLI behavior, permission mode, resume behavior, or recovery assumptions are ambiguous.
```
