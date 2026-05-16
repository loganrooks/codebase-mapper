---
name: cross-vendor-review
description: Launch and recover repo-local cross-vendor or non-current-model review packets through Claude Code CLI. Use when a review directory contains PROMPT.md and REVIEW-SPEC.md and the reviewer must write declared outputs directly while the runner captures logs, verifies outputs, and preserves recovery evidence.
---

# Cross-Vendor Review

Use this skill when a repo-local review packet must be executed by Claude Code CLI or another non-current-model reviewer through the generic review-directory contract.

This skill manages launch and recovery only. It does not decide review outcomes, fill reviewer identity, fill confidence, disposition a checkpoint, mark phases complete, move horizons, or encode project-specific pass-claim semantics.

## Progressive Disclosure

Load only what the current task needs:

- Running an existing review packet: read this file, then run `scripts/run-claude-code-review.sh`.
- Creating or repairing `REVIEW-SPEC.md`: read `docs/REVIEW-SPEC-CONTRACT.md`.
- Debugging launch, permissions, resume, or raw-log lifecycle: read `docs/CLAUDE-CODE-RUNBOOK.md`.
- Classifying a failed or partial run: read `docs/FAILURE-MODES.md`, then run `scripts/recover-review.py`.
- Future CLI behavior spikes: use `docs/SPIKE-FINDINGS-TEMPLATE.md`.

Do not read every doc by default. Do not load every review-type example just because the review type exists.

## Contract

The review directory is the unit of work. It must contain `PROMPT.md` and `REVIEW-SPEC.md`.

The reviewer writes declared outputs directly, such as `OUTPUT.md`, `REVIEW.md`, `CHECKPOINT.md`, or `DISPOSITION.md`. Raw Claude logs are temporary recovery buffers, not the durable review artifact.

`review_type` is an open label. It can be `checkpoint`, `architecture_review`, `artifact_provenance_audit`, `code_diff_review`, or something not anticipated yet. The runner does not need to understand the review type except for generic output checks declared in the spec.

## Default Runner

The default runner is Claude Code CLI:

- uses documented CLI surfaces only;
- uses `--resume <session-name-or-id>` for explicit recovery;
- never uses `--continue` for automated recovery;
- never uses `--dangerously-skip-permissions`;
- defaults to `permission_mode: auto`;
- defaults to tools `Read,Write,Edit,Bash`;
- does not set `--max-turns` or `--max-budget-usd` unless the review spec explicitly declares them.

The default permission/tool envelope is intentionally permissive enough for real reviews to inspect code and run local commands. Safety comes from declared write roots, post-run write-scope verification, raw-log preservation on failure, and human disposition of the review output.

## Normal Run

From the repo root:

```bash
.codex/skills/cross-vendor-review/scripts/run-claude-code-review.sh .planning/reviews/<review-id>
```

The runner will:

- run preflight;
- create `.xvr-runs/<run-id>/`;
- capture `RUN-MANIFEST.json`;
- launch Claude Code with a unique session name;
- capture stdout/stderr stream logs;
- verify required output files;
- write `REVIEW-RUN.json`;
- delete raw stdout/stderr logs on success unless `raw_logs.retain_on_success: true`;
- write `RECOVERY.md` and preserve logs on failure.

## Manual Steps

For staged operation:

```bash
.codex/skills/cross-vendor-review/scripts/preflight.sh .planning/reviews/<review-id>
.codex/skills/cross-vendor-review/scripts/verify-review-output.sh .planning/reviews/<review-id> <run-id>
.codex/skills/cross-vendor-review/scripts/recover-review.py .planning/reviews/<review-id> <run-id>
```

## Recovery Rules

If Claude exits nonzero, writes partial files, omits required outputs, writes outside the allowed roots, produces malformed stream JSON, hits a declared hard limit, or leaves ambiguous session state:

- preserve raw logs;
- write `RECOVERY.md`;
- use the captured command envelope;
- prefer the copy-ready `--resume <session-name>` command from `RECOVERY.md` when safe;
- do not synthesize reviewer content from logs;
- do not fill reviewer identity, confidence, or disposition unless the reviewer actually wrote them.

## Boundaries

This skill is generic. Review-specific meaning belongs in `REVIEW-SPEC.md` and `PROMPT.md`.

It supports known and future review types by varying the spec and prompt. It does not hard-code CBM H1, Phase 01, minimum-useful-CBM, or pass-claim semantics.
