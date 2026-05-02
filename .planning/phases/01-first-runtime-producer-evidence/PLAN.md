# Phase 01: First Runtime Producer Evidence

Status: active
Last updated: 2026-05-02

## Objective

Clear the minimum-useful CBM floor with runtime-producer evidence, then make the claim auditable through a cross-model pass-claim checkpoint.

Acceptance criterion: the minimum-useful-CBM floor in `VISION.md:41-43` is cleared with a substantive Skeptic artifact and the first cross-model-reviewed pass-claim checkpoint is dispositioned `accept`.

## Intervention Track

- I-S1: Live Codex CLI isolation probe. Status: completed before this phase bundle was formalized; evidence at `.planning/spikes/2026-05-02-codex-isolation-live/RESULT.md`.
- I-S3 plus I-X3: loop-status review-completion and checkpoint gates. Status: completed in `1803acb`.
- I-S4a: Codex CLI timeout and run-id validation. Status: completed across `bd66d14` and `6c52a84`.
- I-S4b: Codex CLI output-path enforcement and stderr/stdout tee. Status: completed in `c165f79`.
- I-S5: ADR ledger seed. Status: completed in `8d0239f`.
- I-X2: per-phase artifact bundle convention. Status: completed in `dc6b43b`.
- I-X1: CBM-native cross-model checkpoint primitive. Status: completed in `f0efb2e`; actual pass-claim review packet remains out of scope.
- I-S2: skill loader and first real Skeptic artifact on MCP `src/git`. Status: completed early in `3748d72` and `0a2b6f0`; must be reconciled with I-X1 before any pass claim.
- I-S6: Codex CLI failure-mode regression set. Status: completed in `879afb7`.
- I-S7: honest-baseline banner on handoff/cards. Status: completed in `91f1f95`.

## Verification

- Per-slice focused regressions and cross-regressions as listed in `.planning/reviews/2026-05-02-opus-cross-vendor-audit/INTERVENTIONS.md`.
- Full `TMPDIR=/var/tmp pytest -q` after each intervention.
- Post-commit `python3 -m cbm.cli loop-status --repo . --scope recovery-slice --work-category <category> --json`.

## Stop Conditions

Follow `.planning/reviews/2026-05-02-opus-cross-vendor-audit/INTERVENTIONS.md` and `AGENTS.md`.
