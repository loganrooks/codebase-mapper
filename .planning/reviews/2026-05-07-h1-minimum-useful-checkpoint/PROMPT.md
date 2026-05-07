# H1 Minimum-Useful CBM Checkpoint Prompt

Status: pending non-current-model review
Date: 2026-05-07
Scope: pass-claim

## Task

Review whether H1 clears the minimum-useful CBM floor. Write findings into `CHECKPOINT.md` and leave the final decision in `DISPOSITION.md`.

The current dev-agent model must not fill in reviewer identity, confidence, or disposition.

## Pass Criterion

H1 minimum-useful CBM floor: one pinned external target has a real runtime Surface Mapper output, a real isolated Skeptic review over that output, a structurally carried challenge/no-challenge result, a validated handoff with contestation and coverage honesty, and no deterministic-baseline overclaim.

## Explicit Non-Claims

- Not Phase B.
- Not standard mode.
- Not repeatability.
- Not beta readiness.
- Not mature CBM.
- Not cross-platform parity.
- Not broad product maturity.

## Artifacts To Inspect

- `VISION.md`
- `RUNTIME-CONSTITUTION.md`
- `.planning/HORIZONS.md`
- `.planning/CURRENT-PLAN.md`
- `.planning/STATE.md`
- `.planning/phases/01-first-runtime-producer-evidence/PLAN.md`
- `.planning/phases/01-first-runtime-producer-evidence/VERIFICATION.md`
- `.planning/phases/01-first-runtime-producer-evidence/SUMMARY.md`
- `.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/RESULT.md`
- `.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/RESULT.md`
- `.planning/benchmarks/2026-05-07-mcp-git-h1s2c-disposition/RESULT.md`
- `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/RESULT.md`
- `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/HANDOFF.md`
- `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/VERIFY.md`
- `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/LINEAGE.md`
- `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/INCLUDED-ARTIFACTS.md`
- `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/surface-map.json`
- `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/skeptic-review-surface-map.md`
- `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/source-h1s2c-handoff.md`
- `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/evidence-ledger.jsonl`

## Questions

1. Did H1.S1 use a real runtime Surface Mapper producer?
2. Did H1.S2b use a real isolated Skeptic producer?
3. Was the H1.S2b challenge grounded in citations?
4. Was the H1.S2c disposition structurally carried into the surface/handoff path?
5. Does the final handoff preserve coverage honesty and unknowns?
6. Does the final handoff distinguish runtime evidence from deterministic/dev-fixture evidence?
7. Are artifact lineage and ledger caveats clear enough to audit?
8. Is the H1 pass claim scoped correctly?
9. Should the disposition be `accept`, `accept_with_blockers`, `revise`, or `reject`?

## Allowed Dispositions

- `accept`
- `accept_with_blockers`
- `revise`
- `reject`

Only `accept` clears the current pass-claim gate unless the repo policy is explicitly changed by the user and logged.
