# Review Synthesis

Status: synthesized
Last updated: 2026-05-01
Inputs:
- `OUTPUT-ARCHITECTURE-DISPOSITION-CLAUDE-COWORK.md`
- `OUTPUT-WORKFLOW-DISPOSITION-CLAUDE-COWORK.md`
- `OUTPUT-VISION-DISPOSITION-CLAUDE-COWORK.md`

## Shared Findings

The review packet converged on one central diagnosis: CBM has a useful deterministic kernel, but the project let deterministic substitutes stand in for the runtime agent layer that `VISION.md` requires.

Load-bearing agreements:

- Runtime Surface Mapper/Skeptic/Synthesizer/Planner orchestration does not exist yet.
- Several generated artifacts have misleading provenance, especially `produced_by: surface-mapper@0.1` and `skeptic@0.1` on deterministic or templated output.
- Direct-examination coverage is overstated in deterministic runs; extractor inspection is being blurred with files an agent or human actually opened.
- `cbm run` is currently an in-process deterministic runner, not a true agent orchestrator.
- Hooks can be adapter glue, but they are not the product guarantee and should not be the core correctness mechanism.
- `docs/roadmap.md`, `docs/architecture.md`, and `docs/contracts.md` describe more agentic behavior than the implementation currently provides.
- The workflow encouraged local kernel-hardening slices and self-validation, while the runtime-agent gap remained open.
- There is no meaningful external benchmark. Smoke runs against this repo and the tiny fixture cannot demonstrate nuanced mapping.
- `VISION.md` is valuable but too easy to satisfy with mechanical artifacts unless the minimum useful runtime-agent demonstration is made explicit.

## Already Resolved

- `VISION.md` and `RUNTIME-CONSTITUTION.md` were untracked authority documents. They are now committed in `e309eaa`.
- Raw cross-vendor review outputs and Cowork disposition prompts/outputs are now committed in `3ce5ae7`.
- Pre-reset v1.2 reuse/refresh work is preserved separately in `692e9ef` so recovery commits can stay scoped.

## Main Tradeoffs

Runtime architecture:
- Accepted default: producer registry inside CBM. `cbm run` owns the run lifecycle and dispatches per-artifact producers.
- Backend consequence: Codex CLI subprocesses are allowed only after an isolation spike; host-platform agents remain the fallback for roles that require isolated context.

Vision edits:
- Accepted default: surgical edits. Preserve the literary force of `VISION.md`, but add a minimum useful CBM floor, deployment-shape statement, measurement honesty, revision protocol, and v1-blocking conjecture classification.
- Deferred: splitting `HORIZONS.md` and full graduation-criteria restructuring.

Workflow recovery:
- Accepted default: checkpoint gate first. `/goal` should not resume into open-ended work until live plan/state are current, a checkpoint-review protocol exists, and the next task is bounded to runtime/benchmark recovery.
- Deferred: `cbm-loop-status` automation. It is important, but it follows the checkpoint gate rather than blocking the immediate reset.

## Immediate Recovery Order

1. Install the planning and governance reset in `.planning/`, `AGENTS.md`, `VISION.md`, and architecture/roadmap docs.
2. Fix false provenance and direct-examination coverage in code.
3. Add `cbm run --backend deterministic|external` and `run-manifest.json`.
4. Spike `codex exec` isolation and record the result.
5. Pin the external benchmark and produce the first benchmark baseline.
6. Only then resume broader `/goal` execution.

## Non-Promoted Recommendations

- Do not add a large template directory tree yet.
- Do not add a full L0-L5 incident taxonomy yet.
- Do not loosen the anti-vision items about marketplaces or confidence aggregation.
- Do not claim Phase B-F pass status from deterministic substitutes.
- Do not add new kernel-only gates before the first real agent-produced benchmark artifact exists.
