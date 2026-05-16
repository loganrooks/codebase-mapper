# H1 Minimum-Useful Checkpoint Disposition

Status: complete
Decision: accept

Reviewer model: `claude-opus-4-7`
Reviewer family: `claude` (not in the disallowed `gpt-5` or `codex` families)
Same-model fallback: false
Confidence: high
Date: 2026-05-07

## Reviewer Summary

The H1.S3 packet at `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/` clears the H1 minimum-useful CBM floor as defined in `VISION.md` and `PROMPT.md`. On the pinned external target — MCP `servers` `src/git` at SHA `4503e2d12b799448cd05f789dd40f9643a8d1a6c` — there is:

- a real runtime Surface Mapper output produced by `surface-mapper@1.2` through backend `codex-cli` (run `run-mcp-git-surface-mapper-h1s1-6`), schema-valid with 25 resolved source citations and a non-zero `unknowns` block;
- a real isolated Skeptic review produced by `skeptic@1.2` through `codex-cli` (run `run-mcp-git-h1s2b-skeptic-1`) launched with `--ephemeral --ignore-user-config --ignore-rules -s read-only` and a recorded skill SHA, with a substantive interpretive challenge `chl-10001` grounded in three byte-resolved citations and verified isolation-leak-clean by the packet's own audit;
- a structurally carried disposition: `auth-001.claim_status: contested`, `chl-10001.status: accepted_as_alternative`, original citations preserved, mapper response inline in the rationale, `challenge_resolved` ledger entry `lg-00035` recorded;
- a validated H1.S3 handoff at `HANDOFF.md` that resolves all promoted citations, preserves coverage honesty (7 of 12 directly examined; CI absent; MCP runtime dispatch partially opaque), reports `open_challenges: 0` and `claims_by_status.contested: 1`, and is `produced_by: cbm-handoff@0.1` rather than the baseline renderer;
- explicit producer honesty: runtime-agent evidence is named, deterministic and baseline material is labeled as support-only, and the boundary section disclaims H2, Phase B+, repeatability, standard mode, beta readiness, mature CBM, cross-platform parity, and broad product maturity.

Reviewer spot-checks of the three `chl-10001` competing-evidence spans against the local checkout at the pinned SHA confirmed the bytes materially support the alternative reading. The challenge is non-trivial (the centrality-vs-implementation distinction is exactly the kind of interpretive move `VISION.md`'s minimum-useful demonstration calls for).

The pass criterion is met. The packet is honest about what it does not yet prove.

## Required Revisions Or Blockers

None at the pass-claim gate.

## Suggested (Non-Blocking) Improvements For Subsequent Stages

These are not blockers and must not gate this acceptance. They are written here for the next-stage planner.

1. The promoted H1.S3 `surface-map.json` carries a `run_id` from H1.S2c with H1.S1-era `produced_at` and `inputs[]`. `LINEAGE.md` documents this consciously, and rewriting the validated successor would require a new artifact-production path. A future runtime-producer slice could add a true `refreshed_from` / refresh-delta path so the final-state artifact's frontmatter is internally consistent without losing chain-of-custody.
2. The H1.S2c source handoff is `produced_by: cbm-baseline-handoff@0.1` — the baseline renderer wrapping runtime evidence. The H1.S3 packet handles this correctly, but a runtime-format handoff producer would remove a category-edge that auditors have to think about.
3. Mixed run-id provenance on ledger entry `lg-00029` (challenge raised during H1.S2b but stamped with the H1.S1 mapper run id) is harmless given the durable `chl-10001` id, but a future ledger-writer fix to stamp the producing run id would simplify audits.

These are quality-of-evidence polish items for H2 or a later runtime-producer slice; they do not affect the H1 pass claim.

## Final Disposition

accept
