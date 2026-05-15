---
Status: accepted
Date: 2026-05-02
Context: The cross-vendor audit found that same-model or prose-only checkpoints could accidentally clear stronger claims than they justified.
Decision: Same-model-only checkpoints are valid only for narrow recovery slices when labeled `same_model_fallback: true`. Pass-claim, main-merge, and minimum-useful-CBM claims require explicit reviewer model identity from a non-current model family unless the user logs a waiver. The minimum-useful-CBM claim is gated under the `pass-claim` scope in the implementation (the H1 packet at `.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/CHECKPOINT.md` declares `scope: pass-claim`). The implementation enforces this gate for the set `SCOPES_REQUIRING_CROSS_MODEL = {"pass-claim", "main-merge", "broad-goal-restart"}` in `cbm/cli.py`; `broad-goal-restart` is included because restart-after-incident scope warrants the same independent-reviewer rigor.
Consequences: `cbm-loop-status --scope pass-claim` blocks missing reviewer identity and configured same-model families. The same gate fires for `--scope main-merge` and `--scope broad-goal-restart`. The selector at `checkpoint_for_loop_scope` filters checkpoints by declared scope before returning, so a newer checkpoint for a different scope does not silently shadow a valid scope-matching one. The `cbm checkpoint` primitive preserves this metadata at packet creation time.
Supersedes: none
Superseded by: none
---

# ADR-005: Cross-Model Checkpoint Mandatory For Pass Claims

Recovery slices can proceed with a labeled same-model fallback when the risk is bounded. Stronger claims need an actual independent checkpoint.

The gate is mechanical: the checkpoint must identify the reviewer model, and pass-claim scope must reject the current dev-agent model family.
