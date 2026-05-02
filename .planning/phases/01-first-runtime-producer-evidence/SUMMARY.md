# Phase 01 Summary

Status: partial; intervention track and H1.S1 complete
Last updated: 2026-05-02

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

Not yet complete:

- The true minimum-useful-CBM floor still needs isolated Skeptic review over the H1.S1 map, a minimum-useful handoff with contestation state, and a non-current-model checkpoint disposition.
- Phase B+ runtime-agent orchestration is still not implemented.
- The next runtime-producer track should prove repeatability on another small external target before broader maturity claims.
