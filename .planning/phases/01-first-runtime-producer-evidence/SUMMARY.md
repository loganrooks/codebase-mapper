# Phase 01 Summary

Status: complete; Phase 01 closed
Last updated: 2026-05-08

The recovery intervention track closed the accepted Tier 1 and Tier 5 R-OK items from the Opus cross-vendor audit.

Completed:

- Codex CLI runtime producer isolation was verified through `cbm run` on two scratch repos.
- The Codex adapter now records timeout cause, partial output, logs, and output/log hashes.
- `run_id` validation blocks path traversal before `.research/<run_id>` paths are constructed.
- Runtime skill loading has a formal `cbm.skills` compatibility module.
- `cbm checkpoint` can generate native checkpoint packets for cross-model review.
- `cbm-loop-status` blocks orphaned review packets and pass-claim checkpoints from the current model family.
- Deterministic baseline/dev-fixture outputs are labeled in handoffs and card titles.
- Per-phase planning artifacts now exist under `.planning/phases/`.
- `.planning/HORIZONS.md` now translates `VISION.md` into autonomous `/goal` stages.
- H1.S1 real Surface Mapper evidence passed on pinned MCP `src/git`: `surface-mapper@1.2` produced a non-baseline schema-valid `surface-map.json` with source citations and honest coverage.
- H1.S2a evidence-bundle repair completed the accepted post-H1.S1 Opus review blockers before real Skeptic review.
- H1.S2b real isolated Skeptic evidence exists on pinned MCP `src/git`: `skeptic@1.2` reviewed the H1.S1 surface map and raised cited challenge `chl-10001`.
- H1.S2c challenge disposition exists: `auth-001` is `contested`, and `chl-10001` is `accepted_as_alternative`.
- H1.S3 packet is accepted at `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/`; the non-current-model checkpoint at `.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/` accepted the H1 pass claim.

Not yet complete:

- Phase B+ runtime-agent orchestration is still not implemented.
- The next runtime-producer track should prove repeatability on another small external target before broader maturity claims.

Phase 01 is closed. H2 repeatability planning is next.
