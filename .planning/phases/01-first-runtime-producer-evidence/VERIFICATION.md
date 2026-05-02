# Phase 01 Verification

Status: partial; intervention track closed, H1.S1 complete, H1 minimum-useful floor pending
Last updated: 2026-05-02

## Completed Intervention Evidence

- I-S1 live Codex CLI isolation through `cbm run`: completed in `021a004`; artifact `.planning/spikes/2026-05-02-codex-isolation-live.md`; outcome `verified`.
- I-S3 plus I-X3 loop-status and cross-model checkpoint gates: completed in `1803acb`.
- I-S4a timeout, timeout cause, partial output, and run-id validation: completed in `6c52a84`.
- I-S4b output-path enforcement, stdout/stderr logs, and manifest hashes: completed in `c165f79`.
- I-S5 ADR ledger seed: completed in `8d0239f`.
- I-X2 per-phase artifact bundle convention: completed in `dc6b43b`.
- I-X1 native checkpoint packet command: completed in `f0efb2e`.
- I-S2 formal skill-loader compatibility surface: completed in `65c19f2`; runtime skill-loaded Skeptic evidence exists in `3748d72` and `0a2b6f0`.
- I-S6 Codex CLI failure-mode regression set: completed in `879afb7`.
- I-S7 honest baseline banner on handoffs/cards: completed in `91f1f95`.

## Final Checks

- `TMPDIR=/var/tmp pytest -q` reported `100 passed, 2 warnings`.
- `python3 -m cbm.cli loop-status --repo . --scope recovery-slice --work-category runtime-producer --json` reported `status: ok`, no issues, and no warnings.
- `python3 -m cbm.cli loop-status --repo . --scope broad-goal --work-category runtime-producer --json` reported `status: ok`, no issues, and no warnings.
- `python3 -m cbm.cli loop-status --repo . --scope pass-claim --work-category runtime-producer --json` reported `status: fail` with `same_model_checkpoint`. This remains expected; the repo should not seek pass-claim success until H1.S1-H1.S3 in `.planning/HORIZONS.md` are complete.

## Remaining Close Evidence

- Real Surface Mapper artifact exists for H1.S1. Status: completed in `.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/RESULT.md`.
- Real isolated Skeptic review exists for H1.S2.
- Validated handoff exists for H1.S3.
- `cbm checkpoint` packet exists for the H1 minimum-useful-CBM pass claim.
- A non-current-model reviewer dispositions the pass claim as `accept`.
- `cbm-loop-status --scope pass-claim` exits 0.
- At least one additional small external runtime-producer target validates if the next phase chooses repeatability before broader roadmap work.
