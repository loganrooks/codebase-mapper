# Current Plan

Status: active; H1 minimum-useful close merged to main as `76db3bc` on 2026-05-16; next focus is H2 planning
Last updated: 2026-05-16
Supersedes: direct use of `docs/roadmap.md` as current execution plan
Superseded by: none
Current horizon: H2
Current stage: H2.S1

## Objective

Advance from the accepted H1 minimum-useful demonstration into H2 repeatability planning, one executable stage at a time.

The current work is an intervention, not a product feature sprint. Its purpose is to install enough architecture clarity, planning discipline, and immediate code correction that the next autonomous loop has a narrow, falsifiable path.

Implementation phase bundle: `.planning/phases/01-first-runtime-producer-evidence/`.

Current boundary: H1 is accepted for one pinned external target only. This is not Phase B+, repeatability, beta readiness, or broad runtime orchestration. H2 must plan the second target before running it.

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
22. Run post-H1.S1 Opus review. Status: completed; disposition accepted with blockers at `.planning/reviews/2026-05-02-h1s1-opus-review/DISPOSITION.md`.
23. PR #1 merge-vehicle review-discovery remediation: address Codex inline findings (F1-F4), Claude survey findings (W-NEW-1, S-NEW-1), Claude gates findings at Opus/MAX (W1-W4 + S1-S6), Claude opus findings at Opus/MAX (W-OP-1/2, S-OP-1/2/3), verify-gates findings (C1, C2, W3-W10, S11-S15), final-opus findings (W-OPUS-1/2/3/4, S-OPUS-1-4). Status: completed across `f09fcef` through `a571ac9` (14 fix commits + workflow uplift). All P1 (6) and P2 (11) findings fixed; 14 regression tests added; 145 tests passing. 10 P3 deferrals remain for a follow-up cleanup PR.
24. Land workflow uplift on `main`: `effort_level` dial input (agentic-ops PR #21, branch `feat-effort-level` SHA `f0046cb`), `effort_level: max` caller-stub config, `docs/review-playbook.md`, `.github/PULL_REQUEST_TEMPLATE.md`. Status: PR #10 merged to main as `14ede4c`; agentic-ops PR #21 awaiting user review approval; CBM caller stub temporarily pins to the feat-effort-level SHA until #21 merges and `v1` is fast-forwarded.
25. Merge PR #1 to main. Status: completed as merge commit `76db3bc` on 2026-05-16.

H1.S1 is completed narrowly. H1.S2a evidence-bundle repair is complete. H1.S2b real isolated Skeptic production is complete. H1.S2c challenge disposition and mapper response are complete. H1.S3 validated handoff and non-current-model checkpoint review are complete. H1 minimum-useful close (PR #1) is merged to main. Phase B+ and repeatability claims remain blocked until their specific horizon evidence and checkpoint evidence exist.

## Next `/goal` Track

The current `/goal` track is H2.S1 from `.planning/HORIZONS.md`: plan the runtime-producer repeatability run.

Current status: the guarded `codex-cli` backend produced one live smoke review artifact on the pinned MCP `src/git` benchmark, the live isolation probe reported no access to parent-only session context, a skill-loaded `skeptic@1.2` subprocess produced an ingested interpretive challenge on the same pinned benchmark, H1.S1 produced a real non-baseline `surface-mapper@1.2` surface map on MCP `src/git`, H1.S2b produced a real isolated `skeptic@1.2` review over that H1.S1 map, H1.S2c accepted the `auth-001` / `chl-10001` challenge as an alternative reading carried into handoff contestation, and H1.S3 prepared a handoff/checkpoint packet at `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/` plus `.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/`.

The H1 minimum-useful floor is accepted for one pinned external target. The next proof target is repeatability planning, not another H1 checkpoint and not a second-target run without a plan.

This is not a Phase B+ pass claim, not repeatability, and not beta readiness. It is an accepted H1 pass claim scoped to the MCP `src/git` target.

## H1.S2a Review Blocker Remediation

Accepted blockers from `.planning/reviews/2026-05-02-h1s1-opus-review/DISPOSITION.md`:

- fixed: handoff coverage, summaries, caveats, and next action now derive from non-baseline Surface Mapper output;
- fixed: dev-fixture Skeptic fallback output is not promoted or counted as real review when no real Skeptic ran;
- fixed: Surface Mapper unknown-edge acceptance uses `kind: unknown` lookup instead of literal `edge-unknown-001`;
- fixed: repair-pass regressions preserve rejected output, repair prompt/output, logs, and manifest repair metadata;
- repaired/limited: the existing H1.S1 convenience benchmark handoff now avoids unavailable dev-fixture Skeptic references and records the original packet's missing full `.research/<run_id>/` tree limitation in `RESULT.md`. Future runtime benchmark packets must preserve the full run tree, including `logs/` and `codex_outputs/`, or avoid citing unpreserved files.

## Allowed Next Code Work

Only these work categories are allowed while H2.S1 planning is current:

- choose and justify the second pinned external target or materially different subtree;
- define H2 acceptance and verification commands;
- identify which H1 packet caveats matter for repeatability;
- update benchmark planning artifacts and authority docs required for H2;
- narrow verifier/tooling fixes required to keep the H2 plan executable.

Explicitly disallowed:

- new kernel-only validators, gates, rejection rules, or artifact strictness slices;
- new project packs unrelated to the benchmark;
- running the H2 live producer before the H2 plan is written;
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
- expected block until H1.S3 checkpoint is accepted: `python3 -m cbm.cli loop-status --repo . --scope pass-claim --work-category runtime-producer --json`

For the next code slice:

- run the non-current-model checkpoint review using `.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/PROMPT.md`;
- do not fill reviewer identity, confidence, or disposition from the current dev-agent model;
- run `cbm-loop-status --scope broad-goal --work-category runtime-producer`;
- after non-current-model acceptance only, update `.planning/STATE.md`, `.planning/CURRENT-PLAN.md`, and `.planning/HORIZONS.md` before any H1 completion claim.
