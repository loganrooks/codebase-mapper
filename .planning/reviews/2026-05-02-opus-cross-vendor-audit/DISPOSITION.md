# Cross-Vendor Audit Disposition

Status: accepted with revisions
Last updated: 2026-05-02
Source: `.planning/reviews/2026-05-02-opus-cross-vendor-audit/OUTPUT-CLAUDE-OPUS.md`

## Run Notes

- First launch attempt was terminated before output because the cmux Claude wrapper injected hook settings. The accepted run used `CMUX_CLAUDE_HOOKS_DISABLED=1`, `--setting-sources project,local`, Opus, and `--effort max`.
- The accepted run produced `OUTPUT-CLAUDE-OPUS.md` and `INTERVENTIONS.md` inside this review directory. No writes outside the review session are accepted as reviewer edits.
- The Claude process did not exit after the output ended with `End of audit`; it was terminated after the complete-looking artifact was captured. `STDERR.txt` is empty.
- The audit's statement that this packet's output was 0 bytes was true during its own inspection window but is stale after capture.
- Claims based on the reviewer's own "sub-agent" or external research are treated as recommendations, not verified facts, unless independently checked in this repo.

## Accepted Now

| Finding | Disposition | Implementation |
|---|---|---|
| B1: `cbm-loop-status` misses orphaned review packets | Accept | Add review-session completion checks. Broad `/goal` fails if review folders have prompts without non-empty outputs, stop notes, or aborted dispositions; empty review folders fail. |
| B2: Codex CLI subprocess has no timeout | Accept | Add configurable Codex CLI timeout, return code 124 on timeout, and `interrupted` run/step manifest status. |
| B3: unsafe `run_id` path construction | Accept | Validate run IDs against a bounded allowlist before constructing `.research/<run_id>` paths. |
| O4: dispatch evidence is not minimum-useful CBM | Accept | Keep STATE/CURRENT-PLAN language separated; next runtime slice must target minimum-useful evidence explicitly. |

## Accepted For Next Slices

| Finding | Disposition | Planned action |
|---|---|---|
| A3/S1: live Codex isolation probe | Accept | Run before relying on Codex CLI for a real Skeptic. |
| N3/A2/S2: skill loader and real Skeptic artifact | Accept | Implement `skills/<name>.md` loading, prompt hashing, manifest recording, and first real Skeptic benchmark artifact. |
| W3/S5: ADR ledger | Accept | Create ADRs for run lifecycle ownership, hooks as adapter glue, producer registry, deterministic-baseline boundary, and cross-model pass gates. |
| N14/S6: Codex failure-mode regressions | Accept | Add regressions for invalid JSON, missing output, schema rejection, stderr noise, and timeout coverage beyond the initial timeout test. |
| A6/S7: honest-baseline banner | Accept | Add presentation banner to deterministic baseline handoffs/cards after the minimum readiness blockers are committed. |

## Parked Or Revised

| Finding | Disposition | Reason |
|---|---|---|
| B4: `RefResolver` deprecation | Park | Real risk, but not a blocker before the next runtime-producer evidence slice. Track as a validation-maintenance slice before jsonschema 5. |
| GSDR adoption | Park | Potentially useful developer-workflow substrate, but should not be migrated during active recovery. Verify against local install before adoption. |
| GSD-2 poor-fit claim | Park | Plausible architecture concern, but external-research-backed and not needed for immediate recovery. |
| BUILD-LOG historical annotation | Park | Useful for audit readability, not required before the next runtime-producer evidence slice. |
| Full `cli.py` split | Park | Still deferred until producer-registry and first real runtime artifact reduce churn risk. |

## Verification Required

- Focused regressions for B1/B2/B3.
- Full `pytest -q`.
- `cbm-loop-status --scope broad-goal --work-category loop-status` after committing authority docs and review artifacts.
