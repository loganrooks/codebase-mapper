# Current Plan

Status: active; recovery interventions complete, H1.S1 completed, H1.S2 pending
Last updated: 2026-05-02
Supersedes: direct use of `docs/roadmap.md` as current execution plan
Superseded by: none
Current horizon: H1
Current stage: H1.S2

## Objective

Recover the project to a state where `/goal` can run again without repeating the kernel-hardening drift, then advance through `.planning/HORIZONS.md` one executable stage at a time.

The current work is an intervention, not a product feature sprint. Its purpose is to install enough architecture clarity, planning discipline, and immediate code correction that the next autonomous loop has a narrow, falsifiable path.

Implementation phase bundle: `.planning/phases/01-first-runtime-producer-evidence/`.

Current boundary: the Tier 1 and Tier 5 R-OK interventions from `.planning/reviews/2026-05-02-opus-cross-vendor-audit/INTERVENTIONS.md` are implemented. The current runtime-producer/Skeptic slice is useful substrate evidence, not the full `VISION.md` minimum-useful CBM floor.

## Locked Decisions

- Runtime architecture default: CBM owns the run lifecycle through a producer registry. Each artifact type declares a producer backend and validation chain. See `ADR-001-cbm-owns-run-lifecycle` and `ADR-003-producer-registry-over-outer-orchestrator`.
- Backend default: test Codex CLI subprocesses first, but do not use Codex subprocesses for Skeptic unless isolation satisfies `RUNTIME-CONSTITUTION.md`.
- Hooks: adapter glue only. They may invoke validators; they are not the correctness source or deployment model. See `ADR-002-hooks-are-adapter-glue`.
- Vision scope: do not rewrite `VISION.md` or restructure graduation criteria now. `HORIZONS.md` is an execution bridge, not a split of the vision prose.
- Resume gate: checkpoint gate plus minimal `cbm-loop-status`. The full R6 loop-status check set can follow later, but a narrow preflight must exist before broad unattended `/goal` resumes.
- Review packets are gated artifacts. A review session with a prompt must produce a non-empty output, a stop note, or an aborted disposition before broad `/goal` can proceed.
- Pass-claim checkpoints require explicit reviewer model identity. Same-model fallback checkpoints can clear narrow recovery slices only when labeled; they cannot clear pass-claim scope. See `ADR-005-cross-model-checkpoint-mandatory-for-pass-claims`.
- Deterministic baseline output is not runtime-agent evidence. See `ADR-004-deterministic-baseline-is-not-runtime-evidence`.
- `VISION.md` remains the north star; `.planning/HORIZONS.md` is the autonomous execution ladder. `/goal` targets the current horizon/stage, not the raw vision document.

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
15. Package CBM schemas so installed validation does not depend on checkout layout. Status: completed.
16. Run live Codex CLI smoke on pinned MCP `src/git` benchmark. Status: completed.
17. Run cross-vendor Opus audit of the recovery work and next plan. Status: completed; disposition accepted with revisions.
18. Implement immediate readiness blockers from the audit: review-completion gate, run-id validation, and Codex subprocess timeout handling. Status: completed in `bd66d14`; final loop-status passed.
19. Run live Codex CLI isolation probe. Status: completed; probe reported no access to parent-only session context.
20. Add runtime skill loader and run skill-loaded Skeptic on MCP `src/git`. Status: completed as runtime-producer/Skeptic evidence in `run-mcp-git-codex-skeptic-skill-4`.
21. Apply all Tier 1 and Tier 5 R-OK interventions from the Opus cross-vendor audit. Status: completed across `f004657` through `65c19f2`.

H1.S1 is completed. Broad unattended `/goal` may proceed only to H1.S2 from `.planning/HORIZONS.md`. Phase B+ pass claims and minimum-useful-CBM claims remain blocked until their specific horizon evidence and checkpoint evidence exist.

## Next `/goal` Track

The next broad `/goal` track should execute H1.S2 from `.planning/HORIZONS.md`: run a real isolated Skeptic against the H1.S1 Surface Mapper artifact and ingest its challenges structurally.

Current status: the guarded `codex-cli` backend produced one live smoke review artifact on the pinned MCP `src/git` benchmark, the live isolation probe reported no access to parent-only session context, a skill-loaded `skeptic@1.2` subprocess produced an ingested interpretive challenge on the same pinned benchmark, and H1.S1 produced a real non-baseline `surface-mapper@1.2` surface map on MCP `src/git`.

The full `VISION.md` minimum-useful CBM floor is not met yet. It remains open until CBM produces a real isolated Skeptic review over the H1.S1 map, carries contestation into a validated handoff, and obtains a non-current-model checkpoint. The next proof target is H1.S2, then H1.S3.

This is not a Phase B+ pass claim and not a minimum-useful-CBM pass claim. It is the start of the H1 runtime-agent evidence track.

## Allowed Next Code Work

Only these code categories are allowed while executing H1.S2:

- Skeptic runtime producer implementation or dispatch;
- isolated context/backend checks required for Skeptic;
- challenge ingestion and contestation ledger fixes required by Skeptic output;
- `--backend` and run-manifest plumbing;
- benchmark harness or fixture work;
- Codex isolation spike support;
- minimal loop-status/preflight work that enforces this recovery plan;
- runtime-producer adapter hardening required before live agent dispatch;
- ADRs or review dispositions that preserve accepted recovery decisions.

Explicitly disallowed:

- new kernel-only validators, gates, rejection rules, or artifact strictness slices;
- new project packs unrelated to the benchmark;
- Phase B-F pass claims;
- hook policy expansion.

## Checkpoint Gate

Before unattended `/goal` resumes beyond H1.S1, a checkpoint review must exist at:

`.planning/reviews/2026-05-01-strategy-workflow-vision-audit/CHECKPOINT.md`

Status: accepted for recovery readiness. The original checkpoint gate is satisfied, and the cross-vendor audit's Tier 1 plus Tier 5 R-OK readiness blockers are closed.

The checkpoint must review:

- this plan;
- `.planning/STATE.md`;
- `AGENTS.md` checkpoint/proceed rules;
- `VISION.md` surgical edits;
- the fixed next code task.

The checkpoint can be produced by an external model or a bounded reviewer agent. Its disposition must be accepted, revised, parked, or rejected before broad `/goal` resumes. User override is allowed but must be recorded in `BUILD-LOG.md`.

Broad unattended `/goal` also requires `cbm-loop-status` to return success. Success means the command can see this active plan, confirm that it points to a valid horizon/stage, confirm the next work is in the allowed categories, detect uncommitted authority-doc changes, and confirm the checkpoint gate is accepted.

Pass-claim scope has a stricter gate: the latest relevant checkpoint must record a non-current-model `reviewer_model_id` and an accepted disposition. Same-model fallback checkpoints can only clear recovery-slice scope. Do not run pass-claim scope for H1 until H1.S1, H1.S2, and H1.S3 acceptance criteria are satisfied.

## Benchmark Default

Default benchmark candidate:

- Repository: `https://github.com/modelcontextprotocol/servers`
- Pinned SHA: `4503e2d12b799448cd05f789dd40f9643a8d1a6c`
- First target: a small server subtree, preferably `src/git` if size and language mix are workable.

If this target is too large or too noisy, choose a smaller MCP server snapshot and record the reason in `STATE.md`.

## Verification

For the completed recovery intervention track:

- `git diff --check -- .planning AGENTS.md VISION.md docs/architecture.md docs/roadmap.md BUILD-LOG.md`
- `TMPDIR=/var/tmp pytest -q`
- `python3 -m cbm.cli loop-status --repo . --scope recovery-slice --work-category runtime-producer --json`
- `python3 -m cbm.cli loop-status --repo . --scope broad-goal --work-category runtime-producer --json`
- expected block until H1.S3 is complete: `python3 -m cbm.cli loop-status --repo . --scope pass-claim --work-category runtime-producer --json`

For the next code slice:

- implement H1.S2 real isolated Skeptic review evidence over the H1.S1 surface map;
- validate the Skeptic artifact, citations, challenge ingestion, and run manifest;
- run `cbm-loop-status --scope broad-goal --work-category runtime-producer`;
- update `.planning/STATE.md`, `.planning/CURRENT-PLAN.md`, and `.planning/HORIZONS.md` before moving to H1.S3.
