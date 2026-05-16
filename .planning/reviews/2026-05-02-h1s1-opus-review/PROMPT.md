# H1.S1 Opus Review Prompt

You are Claude Opus running as an independent external reviewer for the CBM repository.

Review the committed H1.S1 slice on branch `intervention-goal-recovery`, especially commit `1b87ba7 feat: add real surface mapper producer`.

## Review Goal

Audit whether H1.S1 was actually completed and whether the implementation is a sound foundation for H1.S2. Do not assume the prior agent's framing is correct. Look for architectural, workflow, validation, evidence, and planning problems.

## Required Context

Read at minimum:

- `VISION.md`
- `RUNTIME-CONSTITUTION.md`
- `AGENTS.md`
- `.planning/HORIZONS.md`
- `.planning/CURRENT-PLAN.md`
- `.planning/STATE.md`
- `.planning/phases/01-first-runtime-producer-evidence/PLAN.md`
- `.planning/phases/01-first-runtime-producer-evidence/VERIFICATION.md`
- `.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/RESULT.md`
- `.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/surface-map.json`
- `.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/run-manifest.json`
- `cbm/cli.py`
- `tests/test_cli.py`
- `BUILD-LOG.md`

Use `git show --stat 1b87ba7` and inspect the changed code where needed.

## Questions To Answer

1. Does the implementation satisfy H1.S1 acceptance criteria in `.planning/HORIZONS.md`?
2. Is the produced benchmark artifact credible runtime Surface Mapper evidence, or is it overfitted/scaffolded in a way that should block acceptance?
3. Are the parent-side validation checks correctly placed and strong enough, or are they brittle, too permissive, or too tailored to handoff quirks?
4. Did the implementation introduce architectural debt that should be addressed before H1.S2?
5. Are the planning docs and `BUILD-LOG.md` honest and sufficient for an autonomous `/goal` loop to continue?
6. What risks should H1.S2 explicitly handle before running another live agent?

## Output Format

Write a structured review in Markdown with these sections:

- Verdict: one of `ACCEPT`, `ACCEPT_WITH_BLOCKERS_FOR_NEXT_STAGE`, `REVISE_BEFORE_H1S2`, or `REJECT_H1S1`.
- Executive Summary.
- Findings, ordered by severity. Each finding must include severity, evidence, and recommended action.
- Acceptance Criteria Audit: table mapping each H1.S1 criterion to pass/fail/partial and evidence.
- H1.S2 Readiness Risks.
- Suggested Disposition: accept, revise, park, or reject for each major recommendation.

Be direct. Prefer concrete file/line/command evidence over general impressions. Do not edit files.
