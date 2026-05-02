# Recovery Intervention Summary

Status: archived, not fully closed
Last updated: 2026-05-02

## Scope

This phase archives the recovery intervention that reset CBM from deterministic-kernel drift toward runtime-producer evidence. The recovery was informed by the strategy/workflow/vision audit and the cross-vendor Opus audit at `.planning/reviews/2026-05-02-opus-cross-vendor-audit/OUTPUT-CLAUDE-OPUS.md`.

## Shipped Evidence

- Recovery governance reset and same-model fallback checkpoint.
- Honest deterministic producer labels and coverage corrections.
- Producer registry and run-manifest scaffolding.
- Packaged schema resources and benchmark harness cleanup.
- Guarded Codex CLI backend with live smoke evidence.
- Live Codex CLI isolation probe.
- Runtime Skeptic skill loading with skill hash provenance.
- First skill-loaded `skeptic@1.2` benchmark on MCP `src/git` with one structurally ingested interpretive challenge.
- Cross-model/pass-claim checkpoint gate in `cbm-loop-status`.
- Codex timeout cause, partial-output preservation, stdout/stderr logs, and output hashes.
- ADR ledger for the load-bearing recovery decisions.

## Official Close Criterion

Recovery is eligible for closure only after:

- I-S2 minimum-useful runtime-producer evidence exists; and
- a pass-claim checkpoint produced through the I-X1 primitive is dispositioned `accept` by a non-current-model reviewer.

The first condition is met once, narrowly. The second remains pending until I-X1 exists and the user arranges the actual cross-model review.
