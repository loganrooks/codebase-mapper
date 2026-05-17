# Phase 02: Runtime Producer Repeatability

Status: active; H2.S1 brief drafted, awaiting `/goal` execution
Last updated: 2026-05-17
Supersedes: none
Superseded by: none

## Objective

Prove the H1 minimum-useful demonstration was not an MCP `src/git`-specific artifact by repeating real Surface Mapper + isolated Skeptic + validated handoff + non-current-model cross-vendor pass-claim checkpoint on a second pinned external target. The Skeptic pass must run and produce a structurally ingested result, but per the H2.A2 contract in `GOAL-H2S1-REPEATABILITY-PLAN.md` and the "non-trivial claim/challenge" wording in `.planning/HORIZONS.md` H2 acceptance, a valid run may produce either a carried challenge or a "no-challenge" disposition; the surviving artifact may be a non-trivial cited claim, a Skeptic challenge, or both — H2 does not require a manufactured challenge.

Acceptance criterion: H2.A1–A5 are defined as templates in `GOAL-H2S1-REPEATABILITY-PLAN.md` and concretized into `H2-PLAN.md` by the H2.S1 `/goal` once the user confirms the target.

## Track

- H2.S1 — Repeatability plan. Status: brief drafted at `GOAL-H2S1-REPEATABILITY-PLAN.md`; awaiting `/goal` execution.
- H2.S2 — Live Surface Mapper + Skeptic run on chosen target. Status: pending H2.S1 completion (target lock + `H2-PLAN.md` filled).
- H2.S3 — Validated handoff + cross-vendor pass-claim checkpoint. Status: pending H2.S2 completion.

## Verification

Verification commands and acceptance bullets are templates in `GOAL-H2S1-REPEATABILITY-PLAN.md` and get concretized in `H2-PLAN.md` once the target is locked. See `.planning/phases/01-first-runtime-producer-evidence/VERIFICATION.md` for the H1 shape this phase mirrors.

Live verification record accrues in `VERIFICATION.md` alongside this file.

## Stop Conditions

Follow `AGENTS.md` and the stop-and-surface conditions enumerated in `GOAL-H2S1-REPEATABILITY-PLAN.md`. Do not advance H2.S1 to "complete" without `cbm-loop-status --scope broad-goal` passing and the user-confirmed target captured in `H2-TARGET-SELECTION.md`. Do not advance H2 to "complete" without an accepted non-current-model cross-vendor pass-claim checkpoint.
