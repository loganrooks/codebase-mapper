# Claude Opus Cross-Vendor Audit Prompt

You are auditing the CBM repository at `/Users/rookslog/Development/cbm`.

Use Claude Opus with maximum reasoning. Do not edit files. Do not write outside this review session directory. Prefer read-only inspection commands and direct file reads. If a claim cannot be verified from the repo, mark it as unverified instead of assuming it.

## Purpose

Review the recent recovery work and the current plan for returning CBM to reliable unattended `/goal` execution. The desired outcome is not praise or rubber-stamping. Surface defects, weak assumptions, overclaims, architecture problems, workflow drift, missing verification, and better next moves.

Avoid adopting the prior agent's framing as authoritative. Treat the documents, code, tests, git history, and benchmark artifacts as evidence. It is acceptable to conclude that the current direction is mostly sound, seriously flawed, or needs reframing.

## Primary Evidence Surfaces

Read these first:

- `VISION.md`
- `RUNTIME-CONSTITUTION.md`
- `AGENTS.md`
- `.planning/STATE.md`
- `.planning/CURRENT-PLAN.md`
- `BUILD-LOG.md`
- `docs/architecture.md`
- `docs/contracts.md`
- `docs/roadmap.md`
- `.planning/benchmarks/2026-05-02-mcp-git-codex-smoke/RESULT.md`
- `.planning/benchmarks/2026-05-02-mcp-git-codex-smoke/run-manifest.json`
- `.planning/benchmarks/2026-05-02-mcp-git-codex-smoke/skeptic-review-surface-map.md`
- `cbm/cli.py`
- `tests/test_cli.py`
- `pyproject.toml`

Recent commits to inspect:

- `f98605d docs: install recovery governance gate`
- `5d47a7a feat: add recovery loop status preflight`
- `ebf43d7 feat: label deterministic artifacts honestly`
- `5368a33 feat: add run producer manifest`
- `20af433 docs: record codex cli isolation spike`
- `9f618b2 test: add external deterministic benchmark baseline`
- `dd31760 feat: add guarded codex cli smoke backend`
- `05f0534 fix: validate with cbm schema source`
- `3649b5a feat: pin codex cli smoke model`
- `a1770cc fix: package cbm schemas`
- `038a79e docs: record installed package schema smoke`
- `3c0953a feat: record live codex cli smoke`

## Questions To Answer

1. Does the repo's current state honestly reflect what has and has not been built?
2. Are there important defects in the code, tests, packaging, benchmark harness, or CLI subprocess design?
3. Are the planning/governance artifacts likely to help `/goal` run productively, or are they adding process without control?
4. Are there overclaims, stale docs, hidden assumptions, or contradictions across `VISION.md`, `docs/roadmap.md`, `.planning/STATE.md`, `.planning/CURRENT-PLAN.md`, and `BUILD-LOG.md`?
5. Is the Codex CLI backend the right next architectural direction? If yes, what must be tightened before leaning on it? If no, what alternative should be prioritized?
6. What should the next concrete implementation slice be to move toward the `VISION.md` minimum useful CBM?
7. What workflow or governance changes, if any, should be made before broad unattended `/goal` continues?

## Required Output

Write a Markdown review with these sections:

- `# Cross-Vendor Audit`
- `## Verdict`
- `## Blocking Findings`
- `## Nonblocking Findings`
- `## Overclaim Or Drift Risks`
- `## Architecture Recommendations`
- `## Workflow Recommendations`
- `## Verification Gaps`
- `## Recommended Next Slice`
- `## Evidence Reviewed`
- `## Uncertainties`

For each finding, include:

- severity: blocking, high, medium, low;
- evidence: file path and line or commit/command evidence where possible;
- recommendation: concrete next action;
- disposition suggestion: accept, revise, park, or reject.

If there are no blocking findings, say so explicitly and identify the strongest nonblocking risk.
