# Current Plan

Status: active
Last updated: 2026-05-01
Supersedes: direct use of `docs/roadmap.md` as current execution plan
Superseded by: none

## Objective

Recover the project to a state where `/goal` can run again without repeating the kernel-hardening drift.

The current work is an intervention, not a product feature sprint. Its purpose is to install enough architecture clarity, planning discipline, and immediate code correction that the next autonomous loop has a narrow, falsifiable path.

## Locked Decisions

- Runtime architecture default: CBM owns the run lifecycle through a producer registry. Each artifact type declares a producer backend and validation chain.
- Backend default: test Codex CLI subprocesses first, but do not use Codex subprocesses for Skeptic unless isolation satisfies `RUNTIME-CONSTITUTION.md`.
- Hooks: adapter glue only. They may invoke validators; they are not the correctness source or deployment model.
- Vision scope: surgical edits only for this intervention. Do not split `HORIZONS.md` or rewrite all graduation criteria now.
- Resume gate: checkpoint gate plus minimal `cbm-loop-status`. The full R6 loop-status check set can follow later, but a narrow preflight must exist before broad unattended `/goal` resumes.

## Active Recovery Sequence

1. Preserve pre-reset dirty work as a scoped checkpoint. Status: completed in `692e9ef`.
2. Synthesize and disposition review outputs. Status: completed in `f98605d`.
3. Update live planning/state/governance docs. Status: completed in `f98605d`.
4. Install surgical `VISION.md` corrections. Status: completed in `f98605d`.
5. Update architecture/roadmap docs so they no longer overclaim runtime orchestration. Status: completed in `f98605d`.
6. Add recovery checkpoint artifact. Status: completed in `f98605d`; accepted in pending readiness commit.
7. Commit the planning/governance reset. Status: completed in `f98605d`.
8. Add minimal `cbm-loop-status` preflight. Status: completed in `5d47a7a`.
9. Fix false provenance and coverage honesty in code. Status: completed in `ebf43d7`.
10. Add `cbm run --backend deterministic|external` and `run-manifest.json`. Status: completed in `5368a33`.
11. Spike Codex CLI isolation and document the result. Status: completed in `20af433`.
12. Pin and run the first external benchmark baseline. Status: completed in `9f618b2`.
13. Add guarded `cbm run --backend codex-cli` smoke backend with fake-executable regression coverage. Status: completed.
14. Remove benchmark harness requirement to copy CBM schemas into target repositories. Status: completed.

Recovery implementation is complete. Broad unattended `/goal` is allowed only for the next runtime-producer evidence slice after final `cbm-loop-status` success.

## Next `/goal` Track

The next broad `/goal` track should produce the first real agent-produced benchmark artifact. The first implementation target is a narrow live Codex CLI smoke or equivalent external producer backend that writes one schema-valid artifact, records its subprocess invocation in `run-manifest.json`, and passes parent-side validation.

Current status: the guarded `codex-cli` backend is implemented for a surface-map smoke review and is covered with a fake executable. The benchmark schema-source pollution gap is being closed so the live smoke can run against a clean target checkout. The remaining proof is a user-approved live Codex CLI smoke on a pinned external benchmark. Do not treat the fake-executable regression as runtime-agent evidence.

This is not a Phase B+ pass claim. It is the first runtime-producer evidence slice.

## Allowed Next Code Work

Only these code categories are allowed before the first real agent-produced benchmark artifact exists:

- false-provenance and coverage-honesty repair;
- producer-registry scaffolding;
- `--backend` and run manifest plumbing;
- benchmark harness or fixture work;
- Codex isolation spike support;
- minimal loop-status/preflight work that enforces this recovery plan.

Explicitly disallowed:

- new kernel-only validators, gates, rejection rules, or artifact strictness slices;
- new project packs unrelated to the benchmark;
- Phase B-F pass claims;
- hook policy expansion.

## Checkpoint Gate

Before unattended `/goal` resumes, a checkpoint review must exist at:

`.planning/reviews/2026-05-01-strategy-workflow-vision-audit/CHECKPOINT.md`

Status: accepted. Resume gate satisfied for the narrow runtime-producer evidence track.

The checkpoint must review:

- this plan;
- `.planning/STATE.md`;
- `AGENTS.md` checkpoint/proceed rules;
- `VISION.md` surgical edits;
- the fixed next code task.

The checkpoint can be produced by an external model or a bounded reviewer agent. Its disposition must be accepted, revised, parked, or rejected before broad `/goal` resumes. User override is allowed but must be recorded in `BUILD-LOG.md`.

Broad unattended `/goal` also requires `cbm-loop-status` to return success. Success means the command can see this active plan, confirm the next work is in the allowed categories, detect uncommitted authority-doc changes, and confirm the checkpoint gate is accepted.

## Benchmark Default

Default benchmark candidate:

- Repository: `https://github.com/modelcontextprotocol/servers`
- Pinned SHA: `4503e2d12b799448cd05f789dd40f9643a8d1a6c`
- First target: a small server subtree, preferably `src/git` if size and language mix are workable.

If this target is too large or too noisy, choose a smaller MCP server snapshot and record the reason in `STATE.md`.

## Verification

For this intervention commit:

- `git diff --check -- .planning AGENTS.md VISION.md docs/architecture.md docs/roadmap.md BUILD-LOG.md`

For the next code slice:

- focused regression for minimal `cbm-loop-status`;
- focused regression tests for honest `produced_by`;
- focused regression tests for `files_examined_directly`;
- smoke artifact inspection for deterministic `baseline_only`;
- full `pytest -q`.
