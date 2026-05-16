# H1.S1 Opus Review Disposition

Status: accepted with blockers for next stage
Reviewer: Claude Opus via local `claude` CLI
Model invocation: `claude --setting-sources project -p --model opus --effort max --tools Read,Bash --permission-mode dontAsk --output-format text`
Prompt: `PROMPT.md`
Output: `OUTPUT.md`

## Summary

The review accepts H1.S1 narrowly: the `surface-map.json` produced by `surface-mapper@1.2` satisfies the H1.S1 surface-map acceptance criteria.

The review does not clear H1.S2 readiness. It identifies several blockers in the surrounding bundle and validation path that could mislead a Skeptic or weaken the checkpoint evidence trail.

## Accepted Blockers Before H1.S2

| Finding | Disposition | Required Action |
|---|---|---|
| F1: Handoff misrepresents runtime mapper output as deterministic Phase A | accept | Make handoff summaries, caveats, coverage, and next action derive from the runtime surface map when the producer is non-baseline. |
| F2: Dev-fixture skeptic review is silently included in the H1.S1 handoff | accept | When no real Skeptic ran, either omit the dev-fixture skeptic stub or label/count it unmistakably as a dev fixture. |
| F3: `edge-unknown-001` is a hard-coded scaffolding requirement | accept | Replace literal-id dependency with a lookup for at least one `kind: unknown` edge; update prompt and handoff code accordingly. |
| F8: Repair-pass behavior lacks regression coverage and live evidence preservation | accept | Add repair success/failure regressions; preserve `logs/` and `codex_outputs/` for future live benchmark runs. |
| F9: Benchmark evidence is incomplete relative to handoff hashes | accept | Preserve the full `.research/<run_id>/` tree or remove non-preserved artifact references from the evidence packet. |

## Accepted Follow-Ups During H1.S2

| Finding | Disposition | Required Action |
|---|---|---|
| F4: `source_sha` validation accepts short trivial prefixes | accept | Require exact short SHA match or a minimum safe prefix length. |
| F5: `inputs[].sha256` is not re-hashed by the parent validator | accept | Recompute declared input hashes during parent-side validation. |
| F6: Ledger `skill_version` is hard-coded to `0.1` | accept | Thread the runtime skill version into citation ledger entries. |
| F12: Producer registry lacks explicit partial-runtime configuration | accept | Record selected runtime modes or equivalent run configuration. |
| F13: Build log lacks design-choice rationale | accept | Backfill concise rationale for `surface_map_json`, one repair pass, `--codex-skeptic-mode none`, and the temporary unknown-edge constraint. |

## Parked

| Finding | Disposition | Reason |
|---|---|---|
| F7: Standalone validation does not enforce runtime producer identity | park | Useful but can wait for producer-registry consumer work if documented. |
| F10: `surface-map.json` remains `status: draft` | park | Clarify semantics by H1.S3; do not block H1.S1 acceptance. |
| F11: Coverage direct-examination count is unverifiable beyond citation sanity | park | Add sanity checks later; the current lower-bound check is acceptable for H1.S1. |

## Operational Decision

Do not start H1.S2 live Skeptic work until the accepted blocker group is remediated and committed.

H1.S1 remains accepted narrowly. The blockers are next-stage readiness blockers, not a rejection of the H1.S1 surface map itself.
