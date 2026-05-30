# Phase 02: Runtime Producer Repeatability

Status: active; H2.S1 deliverables produced; H2 target locked as h11; H2.S2 dispatch unblocked pending its own `/goal`
Last updated: 2026-05-22
Supersedes: none
Superseded by: none

## Objective

Prove the H1 minimum-useful demonstration was not an MCP `src/git`-specific artifact by repeating real Surface Mapper + isolated Skeptic + validated handoff + non-current-model cross-vendor pass-claim checkpoint on a second pinned external target. The Skeptic pass must run and produce a structurally ingested result, but per the H2.A2 contract in `GOAL-H2S1-REPEATABILITY-PLAN.md` and the "non-trivial claim/challenge" wording in `.planning/HORIZONS.md` H2 acceptance, a valid run may produce either a carried challenge or a "no-challenge" disposition; the surviving artifact may be a non-trivial cited claim, a Skeptic challenge, or both — H2 does not require a manufactured challenge.

Acceptance criterion: H2.A1–A5 are defined as templates in `GOAL-H2S1-REPEATABILITY-PLAN.md` and are now concretized for `python-hyper/h11@62c5068c` in `H2-PLAN.md`.

## Track

- **H2.S1** — Repeatability plan. Status: completed. Deliverables: `H2-TARGET-SELECTION.md` (locked pick recorded on 2026-05-22 with re-verification probe), `H2-PLAN.md` (binding H2 plan with concrete A1–A5 and verification commands), `H2-BENCHMARK-PACKET-SKELETON.md` (H2.S2 + H2.S3 packet contracts), `H2-PREFLIGHT.md` (concerns 1–9, including h11-specific protocol-state-machine and public-API concerns). Authority docs `.planning/CURRENT-PLAN.md`, `.planning/HORIZONS.md`, `.planning/STATE.md`, and `BUILD-LOG.md` updated.
- **H2.S2** — Live Surface Mapper + Skeptic run against `python-hyper/h11` at SHA `62c5068c971579d61fa1b55373390e12f25fd856`, scope `h11/` package (excluding `h11/tests/`), via a single `cbm run` with `surface-mapper@1.2` + `skeptic@1.2` on backend `codex-cli`. Status: pending its own `/goal`. Packet path: `.planning/benchmarks/<run-date>-h11-h2s2/`. Contract: `H2-BENCHMARK-PACKET-SKELETON.md`.
- **H2.S3** — Validated handoff + cross-vendor pass-claim checkpoint at scope `pass-claim` per ADR-005 (`SCOPES_REQUIRING_CROSS_MODEL` in `cbm/cli.py`). Status: pending H2.S2 completion. Packet paths: `.planning/benchmarks/<run-date>-h11-h2s3-handoff/` and `.planning/reviews/<run-date>-h2-repeatability-checkpoint/`. Contract: `H2-BENCHMARK-PACKET-SKELETON.md`.

## Verification

H2.S1 verification (this slice):

- `TMPDIR=/var/tmp pytest -q` — expected: ≥146 passed, 2 warnings (the H1-final count). H2.S1 added no code; no test regression expected.
- `git diff --check -- .planning BUILD-LOG.md` — expected: exit 0.
- Post-commit `python3 -m cbm.cli loop-status --repo . --scope broad-goal --work-category runtime-producer --json` — expected: `status: ok`, no issues, no warnings.
- Post-commit `python3 -m cbm.cli loop-status --repo . --scope recovery-slice --work-category runtime-producer --json` — expected: `status: ok`, no issues, no warnings.
- `pass-claim` scope is **not** part of H2.S1 verification — it is currently green on H1 evidence and carries no information about H2.S1 progress.

H2 verification commands (post-S2 and post-S3, with absolute artifact paths) — concrete shape in `H2-PLAN.md` "H2 Verification Commands". Live verification record accrues in `VERIFICATION.md` alongside this file.

## Stop Conditions

Follow `AGENTS.md` and the stop-and-surface conditions enumerated in `GOAL-H2S1-REPEATABILITY-PLAN.md`. Do not advance H2 to "complete" without an accepted non-current-model cross-vendor pass-claim checkpoint at H2.S3. The H2.S1 work is complete with the deliverables enumerated under "Track" and the authority-doc updates landed in this commit.
