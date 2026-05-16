# CBM Build State

Status: current operational state
Last updated: 2026-05-16
Supersedes: none
Superseded by: none

## Summary

CBM currently has a real deterministic kernel and a substantial artifact-validation surface. It does not yet have the runtime agent layer required by `VISION.md`.

Current product state:

- deterministic baseline extraction exists;
- artifact schemas and validation gates exist;
- citation, freshness, ledger, registry, contestation, reuse, and refresh scaffolding exist;
- deterministic smoke artifacts exist under `.research/`;
- a guarded `codex-cli` smoke backend exists and can be tested with a fake executable;
- the `codex-cli` smoke backend defaults to `gpt-5.4-mini` with medium reasoning for harness tests;
- the first live Codex CLI smoke artifact has passed on the pinned MCP `src/git` benchmark;
- `cbm-loop-status` now checks review-session completion for broad `/goal`;
- `cbm-loop-status` now blocks pass-claim scope unless the latest checkpoint records a reviewer model from a configured non-current model family;
- `cbm run` rejects unsafe run IDs before constructing `.research/<run_id>` paths;
- Codex CLI subprocess calls now have a configurable timeout, interrupted manifest status, timeout cause recording, partial-output preservation, stdout/stderr log teeing, and manifest hashes for logs/output files;
- a live Codex CLI isolation probe reported no access to parent-only session context under current backend flags;
- runtime skill loading exists for Codex CLI skill mode, and run manifests record the loaded Skeptic skill hash;
- the first skill-loaded `skeptic@1.2` run on MCP `src/git` produced a structurally ingested interpretive challenge;
- the first runtime-producer/Skeptic evidence slice has passed on one pinned external benchmark;
- H1.S1 produced a real non-baseline `surface-mapper@1.2` surface map on the pinned MCP `src/git` benchmark through the `codex-cli` backend;
- post-H1.S1 Opus review returned `ACCEPT_WITH_BLOCKERS_FOR_NEXT_STAGE`; H1.S2a evidence-bundle remediation is complete, H1.S2b real isolated Skeptic production is complete, H1.S2c challenge ingestion plus mapper response disposition is complete, and H1.S3 validated handoff/checkpoint evidence is accepted by non-current-model checkpoint review;
- all Tier 1 and Tier 5 R-OK recovery interventions from the 2026-05-02 Opus cross-vendor audit have been implemented and committed;
- `.planning/HORIZONS.md` now translates `VISION.md` into autonomous `/goal` stages;
- CBM schemas are packaged under `cbm/schemas/` so installed validation does not depend on a repo checkout or target-local schema copies;
- full runtime Surface Mapper/Skeptic/Synthesizer/Planner orchestration does not exist;
- H1 real Surface Mapper, isolated Skeptic, carried challenge disposition, validated handoff, and non-current-model checkpoint evidence exists for one pinned external target;
- one real isolated `skeptic@1.2` pass has run over the H1.S1 Surface Mapper artifact, and the resulting `auth-001` challenge has been accepted as an alternative reading;
- a non-current-model checkpoint accepted the H1 minimum-useful pass claim; repeatability and full orchestration are not proven;
- PR #1 (the H1 minimum-useful close merge-vehicle) is merged to `main` as `76db3bc` on 2026-05-16, after extensive review-discovery iterations across Codex, Claude survey, Claude gates at Opus/MAX, Claude opus at Opus/MAX, verify-gates, and final-opus passes; the merged branch contains 14 fix commits addressing F3/F1/S2/W2/W-NEW-1/S-NEW-1/W-OP-1/W-OP-2/S-OP-1/F2/F4/W3/W4 (gates)/W1/W2 (gates)/S-OP-2/S2/S4/S6 (gates)/S3 (gates)/C1/C2/W4/W8/W7/W10/S12/S15/W-OPUS-1/W-OPUS-2/W-OPUS-3/W-OPUS-4 plus the workflow uplift caller-stub + ADR-010 effort_level dial (agentic-ops PR #21 merged and v1 fast-forwarded; CBM caller stub reverted to `agentic-ops@v1` in PR #12 as `bf277dc`); post-H1 P3 cleanup PR #13 merged as `6b5e502` draining gates S1/S5 + verify-gates W5/W6/S11/S13/S14 + opus S-OPUS-1/2/3/4;
- H2.S1 `/goal` brief drafted at `.planning/phases/02-runtime-producer-repeatability/GOAL-H2S1-REPEATABILITY-PLAN.md` on 2026-05-16; the brief specifies H2.S1 as planning-only with stop-and-surface for user target pick; H2.S2 live producer run and H2.S3 validated handoff + cross-vendor pass-claim checkpoint are downstream slices, each with their own `/goal` and ADR-005 cross-model checkpoint;
- ADR-005 cross-model gate enforcement is now load-bearing on the `pass-claim`, `main-merge`, and `broad-goal-restart` scopes via `SCOPES_REQUIRING_CROSS_MODEL`, with scope-label match enforced both at the selector and at the gate, and ledger writes deferred until BOTH surface AND card validation pass; verified by 14 new regression tests added across the session;
- current deterministic artifacts must not be treated as proof of nuanced codebase understanding.

## Authority

- `VISION.md`: destination and maturity target; committed in `e309eaa`; surgically amended during the recovery intervention.
- `RUNTIME-CONSTITUTION.md`: runtime-agent discipline; committed in `e309eaa`.
- `.planning/STATE.md`: factual current state.
- `.planning/HORIZONS.md`: autonomous execution ladder from vision to bounded `/goal` targets.
- `.planning/CURRENT-PLAN.md`: active recovery plan and allowed next work.
- `.planning/phases/`: implementation phase bundles with archived plans, verification, and summaries.
- `BUILD-LOG.md`: chronological audit evidence, not a live plan.
- `docs/roadmap.md`: original phase taxonomy and acceptance context; not current pass/fail status.

## Phase Status

Phase A is partially implemented as a deterministic foundation.

Phases B-F are not passed. Some deterministic substitutes and later-phase scaffolding exist, but the roadmap acceptance criteria name agentic deliverables and benchmark behavior that have not yet been demonstrated.

Important examples:

- deterministic `cbm run` is not an agent orchestrator;
- deterministic trace/refine/skeptic artifacts are not runtime agent output;
- project-type packs exist as scaffolding, not mature Phase E evidence;
- Claude Code portability is not verified;
- no external benchmark run proves mapping adequacy.

## Recent Checkpoints

- `e309eaa` `docs: commit CBM authority documents`
- `3ce5ae7` `docs: add external review comparison artifacts`
- `5742c18` `docs: add independent strategy audit outputs`
- `a086749` `docs: replace biased review with neutral audit plan`
- `5a2ceb5` `docs: add live planning and review surface`
- `692e9ef` `docs: preserve pre-reset reuse refresh work`
- `f98605d` `docs: install recovery governance gate`
- `5d47a7a` `feat: add recovery loop status preflight`
- `ebf43d7` `feat: label deterministic artifacts honestly`
- `5368a33` `feat: add run producer manifest`
- `20af433` `docs: record codex cli isolation spike`
- `9f618b2` `test: add external deterministic benchmark baseline`
- `bd66d14` `feat: harden goal readiness after audit`
- `1803acb` `feat: gate pass claims on cross model checkpoints`
- `6c52a84` `feat: record codex timeout cause and partial output`
- `c165f79` `feat: tee codex logs and hash output files`
- `8d0239f` `docs: seed adr ledger for recovery decisions`
- `dc6b43b` `docs: introduce per phase artifact bundles`
- `f0efb2e` `feat: add native checkpoint packet command`
- `879afb7` `test: complete codex cli failure mode regressions`
- `91f1f95` `feat: render baseline banner on handoff and cards`
- `021a004` `docs: verify codex isolation through cbm run`
- `65c19f2` `feat: add formal skill loader compatibility module`
- `f09fcef` `fix: align checkpoint scope and DISPOSITION template with gate` (PR #1 F3/F1/S2/W2)
- `5cdbdbf` `feat(review): pin to effort_level=max + add playbook + PR template` (workflow uplift)
- `10c6d05` `fix: extend ADR-005 cross-model gate to main-merge + broad-goal-restart` (W-NEW-1/S-NEW-1)
- `7b06771` `fix: filter checkpoint selector by scope label for cross-model scopes` (W-OP-1/W-OP-2/S-OP-1)
- `75022a4` `fix: stage ledger writes + align cross-vendor-review skill gates` (F2/F4/W3/W4)
- `ce03c35` `fix(review-skill): stderr warning when pyyaml is unavailable` (gates W1/W2)
- `75919cf` `fix(cli): require --reviewer for cross-model checkpoint scopes` (S-OP-2)
- `4911546` `fix(review-skill): S2 + S4 + S6 cross-vendor-review robustness`
- `8627fab` `fix(review-skill): S3 narrow recover-review failure-classification regex`
- `2326555` `fix: verify-gates iteration — C1 + C2 + W4 + W8`
- `091e21b` `refactor: name disposition + scope-set predicates (verify-gates W7+W10)`
- `59ef0be` `fix: cbm.skills.load_skill repo passthrough + work-category message wording` (S12/S15)
- `b66d5d5` `fix: second-order cleanup of verify-gates remediation (W4 floor + W8 deadcode + docs)`
- `a571ac9` `fix: complete F4 ledger staging + loud config errors + stage anchor` (W-OPUS-1/2/3/4)
- `76db3bc` `Merge pull request #1 from loganrooks/intervention-goal-recovery` (H1 minimum-useful close, 2026-05-16)
- pending next work: execute the H2.S1 `/goal` against the brief at `.planning/phases/02-runtime-producer-repeatability/GOAL-H2S1-REPEATABILITY-PLAN.md` to produce H2-TARGET-SELECTION.md (with stop-and-surface for user target pick), H2-PLAN.md, H2-BENCHMARK-PACKET-SKELETON.md, H2-PREFLIGHT.md, and phase 02 PLAN/SUMMARY/VERIFICATION skeletons. Do NOT start the H2.S2 live Surface Mapper or Skeptic run against the new target until the H2 target is user-confirmed and H2-PLAN.md is filled. Per-slice `/goal` invocation: H2.S1 then H2.S2 then H2.S3, each with its own `token_budget` and its own ADR-005 cross-model checkpoint. The CBM caller-stub revert to `agentic-ops@v1` landed in PR #12 as `bf277dc`; the P3 cleanup landed in PR #13 as `6b5e502`.

## Active Architecture Decision

Accepted default for recovery:

CBM should own the run lifecycle through a producer registry. A producer entry chooses whether an artifact is produced by the deterministic baseline, an external host-agent handoff, or a CLI-launched agent backend. Parent-side CBM validation remains mandatory after each produced artifact. See `ADR-001-cbm-owns-run-lifecycle` and `ADR-003-producer-registry-over-outer-orchestrator`.

Codex CLI subprocesses are now a proven runtime-producer backend for bounded Skeptic artifacts. The local CLI capability spike showed useful isolation controls, the live MCP `src/git` smoke proved cheap-model selection, output-schema use, read-only subprocess dispatch, manifest recording, parent-side validation, and ledger integration, the live isolation probe reported no access to parent-only session context, and the first skill-loaded `skeptic@1.2` run produced a structurally ingested interpretive challenge. This does not yet prove full Skeptic quality or Surface Mapper adequacy.

Hooks remain optional adapter glue. They are not the deployment model and not the correctness mechanism. See `ADR-002-hooks-are-adapter-glue`.

Deterministic baseline output is not runtime-agent evidence. See `ADR-004-deterministic-baseline-is-not-runtime-evidence`.

Pass-claim checkpoints require a non-current model family unless explicitly waived by the user. See `ADR-005-cross-model-checkpoint-mandatory-for-pass-claims`.

## Benchmark State

The tiny fixture in `tests/fixtures/sample_repo/` is useful for tests only.

Default benchmark candidate:

- `https://github.com/modelcontextprotocol/servers`
- SHA `4503e2d12b799448cd05f789dd40f9643a8d1a6c`
- first target subtree to evaluate: `src/git`, if workable.

No Phase B+ pass claim is allowed until a real agent-produced artifact passes existing gates on a pinned external benchmark.

First deterministic external baseline:

- Target: MCP servers `src/git` at `4503e2d12b799448cd05f789dd40f9643a8d1a6c`.
- Result artifact: `.planning/benchmarks/2026-05-01-mcp-git-baseline/RESULT.md`.
- Status: deterministic baseline passed validation, but benchmark scope was polluted by copied CBM schemas at the time because schema loading expected `<target-repo>/schemas`. The harness gap is now fixed for future runs: validation can use CBM's own schema source without copying schemas into the target checkout.

First live runtime-producer smoke:

- Target: MCP servers `src/git` at `4503e2d12b799448cd05f789dd40f9643a8d1a6c`.
- Result artifact: `.planning/benchmarks/2026-05-02-mcp-git-codex-smoke/RESULT.md`.
- Status: live Codex CLI smoke review passed validation and handoff gates with honest producer identity. This is runtime-producer dispatch evidence for one bounded smoke artifact.

First skill-loaded runtime Skeptic run:

- Target: MCP servers `src/git` at `4503e2d12b799448cd05f789dd40f9643a8d1a6c`.
- Result artifact: `.planning/benchmarks/2026-05-02-mcp-git-skeptic-skill/RESULT.md`.
- Status: skill-loaded `skeptic@1.2` produced a structurally ingested interpretive challenge and passed handoff gates. This is the first runtime-producer/Skeptic evidence slice, not the full `VISION.md` minimum-useful floor.

First real runtime Surface Mapper run:

- Target: MCP servers `src/git` at `4503e2d12b799448cd05f789dd40f9643a8d1a6c`.
- Result artifact: `.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/RESULT.md`.
- Run id: `run-mcp-git-surface-mapper-h1s1-6`.
- Status: `surface-mapper@1.2` produced a non-baseline `surface-map.json` through backend `codex-cli`; the map, manifest, citations, evidence checks, and handoff validation passed. This satisfies H1.S1 only. The run deliberately skipped a real Skeptic pass with `--codex-skeptic-mode none`.

First real isolated Skeptic review over the H1.S1 Surface Mapper map:

- Target: MCP servers `src/git` at `4503e2d12b799448cd05f789dd40f9643a8d1a6c`.
- Result artifact: `.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/RESULT.md`.
- Run id: `run-mcp-git-h1s2b-skeptic-1`.
- Status: `skeptic@1.2` reviewed the repaired H1.S1 `surface-map.json`, produced one cited interpretive challenge against `auth-001`, and passed Skeptic artifact, citation, manifest, handoff, and evidence validation. This satisfies H1.S2b only.

First H1.S2c mapper response and challenge disposition:

- Target: MCP servers `src/git` at `4503e2d12b799448cd05f789dd40f9643a8d1a6c`.
- Result artifact: `.planning/benchmarks/2026-05-07-mcp-git-h1s2c-disposition/RESULT.md`.
- Run id: `run-mcp-git-h1s2c-disposition-1`.
- Status: `auth-001` / `chl-10001` was accepted as an alternative reading. The updated surface map records `auth-001.claim_status: contested` and `chl-10001.status: accepted_as_alternative`; the handoff reports `open_challenges: 0`, `claims_by_status.contested: 1`, and recommends H1.S3.

Accepted H1.S3 minimum-useful handoff packet:

- Target: MCP servers `src/git` at `4503e2d12b799448cd05f789dd40f9643a8d1a6c`.
- Result artifact: `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/RESULT.md`.
- Handoff artifact: `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/HANDOFF.md`.
- Checkpoint packet: `.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/`.
- Status: accepted by non-current-model checkpoint review at `.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/`; `DISPOSITION.json` records reviewer model `claude-opus-4-7` and disposition `accept`.

Runtime-producer evidence status:

- The first runtime-producer/Skeptic evidence slice passed once on MCP servers `src/git` at `4503e2d12b799448cd05f789dd40f9643a8d1a6c`.
- H1.S1 real Surface Mapper evidence passed once on MCP servers `src/git` at `4503e2d12b799448cd05f789dd40f9643a8d1a6c`.
- This clears H1's minimum-useful floor for one pinned external target only.
- Still not a Phase B+ pass claim. Repeatability, quality review, and broader runtime-agent orchestration remain open.

Operational note:

- Commit `39b4c6c` removed main-session `.codex/hooks.json` because hooks were attached to the wrong execution surface. Future hook work must be scoped to launched CBM runtime-agent sessions or explicit platform adapter templates, not repo-local main-session hooks.

## Known Risks

- Deterministic artifact provenance was misleading; the recovery slice now labels deterministic baseline and dev-fixture producers explicitly.
- Direct-examination coverage was overreported in deterministic surface, verification, and trace paths; the recovery slice now reports zero direct examination for those baseline artifacts.
- `cbm/cli.py` remains a large monolith; splitting should follow producer-registry work, not precede it as churn.
- Planning docs can become process theater if they are not tied to checkpoint review and concrete verification.
- Review packets can become orphaned artifacts if prompt/output/disposition completion is not mechanically gated; the current `loop-status` slice addresses this for broad `/goal`.
- Pass-claim checkpoints can be accidentally cleared by a same-model fallback if reviewer identity is not explicit; `loop-status` now requires `reviewer_model_id` and blocks configured same-model families for pass-claim scope.

## `/goal` Readiness

Recovery readiness is restored through H1 closure in `.planning/HORIZONS.md`: the validated minimum-useful handoff packet is accepted by non-current-model checkpoint review, the earlier recovery checkpoint gate is accepted, cross-vendor audit blockers have been dispositioned, H1.S1-H1.S3 are complete, and H2 planning is the next focus.

Post-H1.S1 review gate: `.planning/reviews/2026-05-02-h1s1-opus-review/OUTPUT.md` returned `ACCEPT_WITH_BLOCKERS_FOR_NEXT_STAGE`; `.planning/reviews/2026-05-02-h1s1-opus-review/DISPOSITION.md` accepted blockers for handoff honesty, dev-fixture Skeptic fallback labeling/removal, `edge-unknown-001` hardcoding, repair-pass tests/evidence preservation, and complete benchmark evidence preservation. H1.S2a remediated that group, H1.S2b produced a real isolated Skeptic review, H1.S2c dispositioned the resulting contestation, and H1.S3 prepared the reviewable handoff/checkpoint packet. The H1 pass-claim checkpoint at `.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/` accepted the H1 minimum-useful claim. Phase B+ claims remain blocked.

Broad unattended `/goal` is restored only for the current horizon/stage named by `.planning/CURRENT-PLAN.md`. It is not restored for Phase B+ pass claims, repeatability claims, unrelated kernel hardening, or treating deterministic baseline artifacts as runtime-agent output.

Pass-claim scope for H1 now passes after structured disposition capture. Future pass claims remain blocked until their own non-current-model checkpoint artifacts and loop-status gates pass.

## Verification Status

Last known full suite after the false-provenance recovery slice: `pytest -q` reported `53 passed, 2 warnings`.

Last known full suite after the producer-registry/run-manifest slice: `pytest -q` reported `55 passed, 2 warnings`.

Last known full suite after the benchmark/ledger fix slice: `pytest -q` reported `56 passed, 2 warnings`.

Last known full suite after the guarded Codex CLI backend slice: `pytest -q` reported `58 passed, 2 warnings`.

Last known full suite after the schema-source benchmark-harness slice: `pytest -q` reported `59 passed, 2 warnings`.

Last known full suite after the Codex CLI smoke model-control slice: `pytest -q` reported `59 passed, 2 warnings`.

Last known full suite after the schema packaging slice: `pytest -q` reported `60 passed, 2 warnings`.

Last known packaging verification: `python3 -m pip wheel . --no-deps -w /tmp/cbm-wheel-check` built `cbm-0.1.0-py3-none-any.whl`; wheel inspection found 19 `cbm/schemas/*.schema.json` entries and no unintended top-level packages beyond `cbm` and dist-info. Installed-package smoke also passed from `/tmp` with `PYTHONPATH` pointing only at the wheel target; import came from `/tmp/.../pkg/cbm/cli.py`, `cbm run` completed, and `cbm validate handoff.md` passed without target-local schemas.

Last known live benchmark smoke: `python3 -m cbm.cli run --repo /tmp/cbm-live-mcp-servers-4503e2d/src/git --goal "understand MCP git server surfaces" --backend codex-cli --allow-live-codex --codex-model gpt-5.4-mini --codex-reasoning-effort medium --mode lightweight --run-id run-mcp-git-codex-smoke-4` exited 0.

Last known full suite after the live Codex CLI smoke remediation slice: `pytest -q` reported `61 passed, 2 warnings`.

Last known focused suite after the cross-vendor audit readiness blockers: `pytest -q tests/test_cli.py::test_loop_status_blocks_incomplete_review_sessions_for_broad_goal tests/test_cli.py::test_run_rejects_unsafe_run_id_before_writing_outside_research tests/test_cli.py::test_run_backend_codex_cli_timeout_marks_manifest_interrupted tests/test_cli.py::test_run_backend_codex_cli_fake_producer_writes_agent_review tests/test_cli.py::test_package_schema_resources_match_root_schemas` reported `5 passed, 2 warnings`.

Last known full suite after the cross-vendor audit readiness blockers: `pytest -q` reported `64 passed, 2 warnings`.

Last known broad-goal preflight after committing readiness blockers: `python3 -m cbm.cli loop-status --repo . --scope broad-goal --work-category loop-status --json` reported `status: ok`, no issues, and no warnings.

Last known live isolation probe: `codex exec -m gpt-5.4-mini -c model_reasoning_effort="medium" -c approval_policy="never" --ephemeral --ignore-user-config --ignore-rules -C . -s read-only --json -o .planning/spikes/2026-05-02-codex-isolation-live/output.json --output-schema .planning/spikes/2026-05-02-codex-isolation-live/output.schema.json - < .planning/spikes/2026-05-02-codex-isolation-live/prompt.txt` exited 0; output schema validation passed; result artifact is `.planning/spikes/2026-05-02-codex-isolation-live/RESULT.md`.

Last known skill-loader focused suite: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_package_runtime_skill_resources_match_root_skills tests/test_cli.py::test_load_skill_records_skeptic_hash tests/test_cli.py::test_run_backend_codex_cli_skill_mode_loads_skeptic_skill tests/test_cli.py::test_run_backend_codex_cli_fake_producer_writes_agent_review tests/test_cli.py::test_package_schema_resources_match_root_schemas` reported `5 passed, 2 warnings`.

Last known full suite after skill-loader slice: `TMPDIR=/var/tmp pytest -q` reported `67 passed, 2 warnings`.

Last known full suite after structured runtime challenge ingestion: `TMPDIR=/var/tmp pytest -q` reported `68 passed, 2 warnings`.

Last known full suite after PR #1 review remediation (F3 pass-claim scope match + F1 DISPOSITION template vocabulary): `TMPDIR=/var/tmp pytest -q` reported `134 passed, 2 warnings`.

Last known full suite after PR #1 review remediation pass 2 (W-NEW-1 cross-model parity for main-merge/broad-goal-restart + S-NEW-1 markdown_metadata frontmatter guard): `TMPDIR=/var/tmp pytest -q` reported `140 passed, 2 warnings`.

Last known full suite after PR #1 review remediation pass 3 (W-OP-1 selector parity for cross-model scopes — checkpoint_for_loop_scope filters by declared scope before falling back to mtime-only; S-OP-1 dedup of missing_checkpoint issue): `TMPDIR=/var/tmp pytest -q` reported `141 passed, 2 warnings`.

Last known full suite after PR #1 follow-up slice 1 (F2 + F4 ledger-before-validation ordering; gates W3 + W4 cross-vendor-review skill drift + observed_model cross-check; F4 regression test): `TMPDIR=/var/tmp pytest -q` reported `142 passed, 2 warnings`.

Last known full suite after PR #1 verify-gates iteration (C1 recovery-slice missing-reviewer fired; C2 pyyaml fail-closed for checkpointish; W4 observed_model prefix-compare; W8 same-model fallback rejected for cross-model scopes; scaffold updated): `TMPDIR=/var/tmp pytest -q` reported `144 passed, 2 warnings`.

Last known full suite after PR #1 final-opus iteration (W-OPUS-1 ledger writes now buffer until BOTH surface AND card validation pass; W-OPUS-2 loop_status_config malformed-JSON loud signal; W-OPUS-3 DISPOSITION.json malformed-JSON loud signal; W-OPUS-4 stage validation upgraded from substring to anchored regex; W-OPUS-1 regression test asserts ledger byte-identical when verify_card_confidence is mocked to fail): `TMPDIR=/var/tmp pytest -q` reported `145 passed, 2 warnings`.

Last known full suite after post-H1 P3 cleanup (gates S1 RECOVERY.md scope-respect; gates S5 parser sync marker + drift regression; verify-gates W5 gate-artifact non-git fail-loud; W6 preflight non-git fail-closed; S11/S-OPUS-1 rework_pattern slice-membership semantics; S13 dead ternary; S14 envelope_refusal KeyError guard; S-OPUS-2 broad-goal-restart issue-code dedupe; S-OPUS-3 legacy resume marker anchored; S-OPUS-4 scope constants reordered): `TMPDIR=/var/tmp pytest -q` reported `146 passed, 2 warnings`.

Last known H2.S1 plan brief drafting (no code change; planning docs only): pre-commit `git status` showed only `.planning/phases/02-runtime-producer-repeatability/` as untracked. Post-edit working tree contains `.planning/phases/02-runtime-producer-repeatability/GOAL-H2S1-REPEATABILITY-PLAN.md` plus updates to `.planning/CURRENT-PLAN.md`, `.planning/STATE.md`, `.planning/HORIZONS.md`, and `BUILD-LOG.md`. No test suite run (no source change); no loop-status run required for a planning-doc-only slice. H2.S1 acceptance and verification commands are templates inside the brief, to be filled by the H2.S1 `/goal` once the user confirms the target. The phase 02 PLAN.md/SUMMARY.md/VERIFICATION.md skeletons are intentionally NOT pre-created — they are H2.S1 `/goal` deliverables.

Last known PR #14 CodeRabbit-finding remediation (no code change; planning docs only): CodeRabbit flagged the H2.S1 brief PR for (1) missing `Last updated:` / `Supersedes:` / `Superseded by:` metadata on the GOAL doc per the `.planning/**/*.md` AGENTS.md rule and (2) missing required `PLAN.md` / `SUMMARY.md` / `VERIFICATION.md` files in the phase 02 directory per the `.planning/phases/<NN-slug>/` contract. Fix: added the three metadata fields to the GOAL doc frontmatter; created minimal contract-compliant stubs (Status + Last updated + Supersedes + Superseded by metadata, brief body) for PLAN.md, SUMMARY.md, and VERIFICATION.md in the phase 02 dir; updated the GOAL doc's Deliverables / Planning-Doc-Update / Completion-Criteria sections from "create" to "expand existing stubs". Second-order audit applied per the [feedback memory](#feedback-pr-review-discipline): every Required Reading path in the GOAL doc was bash-verified (all resolve, no hallucinated refs); flagged that H1.S3 / H1.S2 / H1.S2C GOAL docs on main carry the same metadata gap (out-of-scope for PR #14, separate decision); confirmed CURRENT-PLAN / STATE / HORIZONS top-of-file metadata already compliant after the prior commit; noted the PR-template vs CodeRabbit-check conflict on the `Why: / Verification: / Boundary:` labels (separate decision). No test suite run.

Last known skill package verification: a temp wheel built under `/var/tmp` contained 7 `cbm/runtime_skills/*.md` package entries.

Last known skill-loaded live benchmark run: `TMPDIR=/var/tmp python3 -m cbm.cli run --repo /tmp/cbm-live-mcp-servers-4503e2d/src/git --goal "understand MCP git server surfaces" --backend codex-cli --allow-live-codex --codex-skeptic-mode skill --codex-model gpt-5.4-mini --codex-reasoning-effort medium --mode lightweight --run-id run-mcp-git-codex-skeptic-skill-4` exited 0; `handoff.md` reported `skeptic_review.challenges_logged: 1` and `contestation_summary.open_challenges: 1`.

Last known H1.S1 live Surface Mapper benchmark run: `TMPDIR=/var/tmp python3 -m cbm.cli run --repo /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git --goal "produce real Surface Mapper map for MCP git server surfaces" --backend codex-cli --allow-live-codex --codex-surface-mode skill --codex-skeptic-mode none --codex-model gpt-5.4-mini --codex-reasoning-effort medium --mode lightweight --run-id run-mcp-git-surface-mapper-h1s1-6 --codex-timeout 600` exited 0. Validation passed for `surface-map.json`, `run-manifest.json`, and `handoff.md`; `verify-citations surface-map.json` resolved all source citations; `check-evidence surface-map.json` passed.

Last known full suite after H1.S1 Surface Mapper slice: `TMPDIR=/var/tmp pytest -q` reported `105 passed, 2 warnings`.

Last known full suite after all Tier 1 and Tier 5 R-OK interventions: `TMPDIR=/var/tmp pytest -q` reported `100 passed, 2 warnings`.

Last known loop-status after all Tier 1 and Tier 5 R-OK interventions:

- `python3 -m cbm.cli loop-status --repo . --scope recovery-slice --work-category runtime-producer --json` reported `status: ok`, no issues, and no warnings.
- `python3 -m cbm.cli loop-status --repo . --scope broad-goal --work-category runtime-producer --json` reported `status: ok`, no issues, and no warnings.
- `python3 -m cbm.cli loop-status --repo . --scope pass-claim --work-category runtime-producer --json` reported `status: fail` with `same_model_checkpoint`; this is the intended block before cross-model pass-claim review.

This verifies the test suite, not `VISION.md` maturity.

Required next verification:

- planning reset: `git diff --check -- .planning AGENTS.md VISION.md docs/architecture.md docs/roadmap.md BUILD-LOG.md`;
- provenance/coverage slice: focused regressions passed; full `pytest -q` passed;
- producer-registry/run-manifest slice: focused regressions passed; full `pytest -q` passed;
- Codex isolation spike: local CLI help/version evidence recorded; no live model subprocess was run;
- benchmark baseline: deterministic MCP `src/git` run passed handoff and run-manifest validation; scope pollution by copied schemas recorded as a harness gap;
- benchmark/ledger fix slice: focused regressions passed; full `pytest -q` passed;
- guarded Codex CLI backend slice: fake executable regressions passed; full `pytest -q` passed;
- schema-source benchmark-harness slice: focused no-pollution regression passed; full `pytest -q` passed;
- Codex CLI smoke model-control slice: focused fake-executable regression passed; full `pytest -q` passed;
- schema packaging slice: package resource regression passed; wheel build/inspection passed; full `pytest -q` passed;
- live Codex CLI smoke slice: focused regressions passed; MCP `src/git` live smoke passed; full `pytest -q` passed;
- benchmark slice: generated artifacts must validate and show honest producer identity and coverage.
