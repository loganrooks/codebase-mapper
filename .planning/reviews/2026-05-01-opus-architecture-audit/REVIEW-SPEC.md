# Review Spec: Opus Architecture Audit

Status: aborted - biased framing
Last updated: 2026-05-01
Supersedes: none
Superseded by: `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/`

## Abort Note

This review packet should not be used as independent audit evidence. Its prompt over-specified a suspected diagnosis around hooks, deterministic pipeline framing, and a "corrected architecture." That risks anchoring the reviewer to the current agent's interpretation instead of eliciting an independent diagnosis.

No `OUTPUT.md` was accepted from this packet. A replacement neutral review packet lives at:

`.planning/reviews/2026-05-01-strategy-workflow-vision-audit/`

## Purpose

Request a hostile, architecture-level audit of the CBM build so far, with emphasis on whether recent work has drifted from `VISION.md`, whether hooks were misplaced, and what should change before more implementation.

## Reviewer

Requested reviewer: Claude Opus, max reasoning/effort if available from local CLI.

## Scope

Review:

- `VISION.md`
- `RUNTIME-CONSTITUTION.md`
- `AGENTS.md`
- `.planning/STATE.md`
- `.planning/CURRENT-PLAN.md`
- `docs/roadmap.md`
- `docs/architecture.md`
- `docs/contracts.md`
- `platform/PORTABILITY.md`
- `platform/codex/*`
- `platform/claude-code/README.md`
- `BUILD-LOG.md`
- recent commits through `504fbba`
- `cbm/cli.py`
- `tests/test_cli.py`

## Audit Questions

1. Has the implementation drifted from the CBM vision? If yes, where and how severe is the drift?
2. Were Codex hooks overbuilt, misplaced, or incorrectly framed? What should their role be?
3. Is the corrected architecture in `.planning/CURRENT-PLAN.md` coherent?
4. Should CBM launch runtime agents through Codex CLI subprocesses, use an outer orchestrator, or choose another shape?
5. Which current docs are stale, misleading, or missing?
6. What implementation work should stop until architecture is corrected?
7. What implementation work remains valuable and should be preserved?
8. What verification/audit workflow changes are needed to prevent future drift?
9. Is the roadmap still useful? If not, how should it be revised?
10. What are the highest-risk design decisions before the next code slice?

## Expected Output

Write the review to:

`OUTPUT.md`

Use this structure:

- Executive verdict
- Critical findings
- Major findings
- Minor findings
- Architecture recommendation
- Roadmap/planning recommendation
- Verification/workflow recommendation
- Concrete next actions
- Questions that require user decision

Prioritize clear criticism over politeness. The point is to surface friction signals and design mistakes early.

## Disposition Plan

After review:

- summarize accepted/rejected/deferred findings in `DISPOSITION.md`;
- update `.planning/STATE.md` and `.planning/CURRENT-PLAN.md`;
- only then update durable docs or implement more code.
