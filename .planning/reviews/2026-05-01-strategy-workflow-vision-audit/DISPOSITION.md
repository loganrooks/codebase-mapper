# Review Disposition

Status: accepted recovery plan
Last updated: 2026-05-01

## Accepted Now

| Recommendation | Disposition | Required change |
|---|---|---|
| Commit authority docs | Done | `VISION.md` and `RUNTIME-CONSTITUTION.md` committed in `e309eaa`. |
| Fix false provenance | Accept | Deterministic outputs must use `cbm-baseline/...`; templated stand-ins must use `dev-fixture/...`; runtime-agent names are reserved for real runtime agents. |
| Fix coverage honesty | Accept | Deterministic runs must not report files as directly examined unless an agent or human opened them. |
| Producer registry architecture | Accept with spike gate | Default direction is CBM-owned run lifecycle plus per-artifact producers; `codex exec` isolation must be tested before using it for Skeptic. |
| Runtime benchmark | Accept | First benchmark target is a pinned small MCP server snapshot; no Phase B+ pass claims without benchmark evidence. |
| `cbm run --backend` and manifest | Accept | Add `--backend deterministic|external` and `run-manifest.json`; deterministic runs are `baseline_only`. |
| Kernel-freeze guard | Accept | No new kernel-only validators/gates until a real agent-produced benchmark artifact passes current gates. |
| Checkpoint reviewer protocol | Accept | Phase pass, main merge, and `/goal` restart require an accepted checkpoint review or explicit user override. |
| Minimal `cbm-loop-status` | Accept now | Add a narrow preflight before broad `/goal`: active-plan authorization, uncommitted authority-doc detection, kernel-freeze guard, and checkpoint status. |
| Self-critique cadence change | Accept | Self-critique moves to boundary moments; per-slice self-critique is no longer sufficient evidence. |
| Surgical `VISION.md` edits | Accept | Add minimum useful CBM, deployment shape, measurement honesty, revision protocol, and v1-blocking conjectures. |

## Deferred By This Recovery Plan

These are not all direct deferrals from the source dispositions. This table records the recovery implementation decision after negotiating the architecture, workflow, and vision dispositions with the user's selected defaults: producer registry, surgical vision edits, and checkpoint gate before broad `/goal`.

| Recommendation | Source disposition status | Recovery decision |
|---|---|
| Full `VISION.md` restructure and `HORIZONS.md` split | Vision disposition marked this as user-decides/reversible. | Defer for this intervention; surgical edits are enough before `/goal` recovery. |
| Full `cbm-loop-status` R6 implementation | Workflow disposition recommended a broad R6 command with branch hygiene, freshness, entropy, repeated-failure, benchmark, direct-examination, and critique-streak checks. | Implement a minimal pre-resume version now; defer the full R6 check set until after false-provenance repair and first benchmark plumbing. |
| Full `cbm/cli.py` modular split | Architecture disposition endorsed the split, coupled to producer-registry work. | Defer standalone split; implement boundaries when producer registry work makes them real. |
| Full graduation-criteria table | Vision disposition marked form as user-decides. | Defer until benchmark/runtime evidence exists; avoid inventing measurement policy early. |
| Extra `.planning/templates`, `incidents`, `decisions`, `phase-reviews` directories | Workflow disposition deliberately did not recommend these now. | Keep deferred; add only when first real artifact needs them. |

## Rejected

| Recommendation | Rationale |
|---|---|
| Treat hooks as core correctness | Correctness belongs in explicit CBM validation and run-level validation. Hooks may call validators but must not contain unique policy. |
| Revise vision downward to deterministic mapping | The user chose to keep the runtime-agent/hermeneutic ambition. |
| Loosen anti-vision marketplace/confidence-aggregator commitments | No current evidence shows those commitments caused the drift. |

## Resume Criteria

Unattended `/goal` may resume only after:

- `.planning/STATE.md` and `.planning/CURRENT-PLAN.md` describe the current recovery state.
- `AGENTS.md` defines the checkpoint gate and the narrowed proceed rule.
- a minimal `cbm-loop-status` command exists and fails when broad `/goal` is blocked by the recovery plan.
- `VISION.md` has the surgical recovery edits.
- The next code task is fixed to false-provenance/coverage repair.
- A checkpoint review artifact exists for the recovery reset, or the user explicitly waives it.

## Verification Required

Planning reset:
- `git diff --check -- .planning AGENTS.md VISION.md docs/architecture.md docs/roadmap.md BUILD-LOG.md`

Code recovery:
- minimal `cbm-loop-status` regression covering the pre-resume block;
- focused regression tests for provenance and coverage honesty;
- full `pytest -q`;
- artifact smoke verifying deterministic outputs are labeled as baseline-only.
