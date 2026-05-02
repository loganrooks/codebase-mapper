---
Status: accepted
Date: 2026-05-02
Context: The cross-vendor audit found that same-model or prose-only checkpoints could accidentally clear stronger claims than they justified.
Decision: Same-model-only checkpoints are valid only for narrow recovery slices when labeled `same_model_fallback: true`. Pass-claim, main-merge, and minimum-useful-CBM claims require explicit reviewer model identity from a non-current model family unless the user logs a waiver.
Consequences: `cbm-loop-status --scope pass-claim` blocks missing reviewer identity and configured same-model families. The future `cbm checkpoint` primitive must preserve this metadata.
Supersedes: none
Superseded by: none
---

# ADR-005: Cross-Model Checkpoint Mandatory For Pass Claims

Recovery slices can proceed with a labeled same-model fallback when the risk is bounded. Stronger claims need an actual independent checkpoint.

The gate is mechanical: the checkpoint must identify the reviewer model, and pass-claim scope must reject the current dev-agent model family.
