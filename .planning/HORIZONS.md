# CBM Horizons

Status: active
Last updated: 2026-05-02
Supersedes: direct execution from `VISION.md`
Superseded by: none

## Purpose

`VISION.md` is the north star. This file is the autonomous execution ladder that translates the vision into bounded `/goal` targets.

Each horizon defines a stage of evidence the implementation must clear before broader claims are allowed. `/goal` should execute the current horizon one stage at a time, update `.planning/CURRENT-PLAN.md` as reality changes, and checkpoint before claiming a horizon is complete.

## Consumption Rules For `/goal`

- Read `VISION.md`, `.planning/STATE.md`, this file, and `.planning/CURRENT-PLAN.md` before choosing work.
- Execute only the current horizon and current stage named in `.planning/CURRENT-PLAN.md`.
- If verification or reviewer pushback invalidates the current stage, classify it as `bug`, `plan_gap`, `vision_ambiguity`, `tooling_gap`, or `out_of_scope`.
- For `bug`, `plan_gap`, or `tooling_gap`, write a small intervention into `.planning/CURRENT-PLAN.md`, implement, verify, commit, and continue.
- For `vision_ambiguity`, stop unless the user explicitly authorizes a `VISION.md` revision.
- For `out_of_scope`, stop and write a stop note or park it in a later horizon.
- Do not claim a horizon complete until its acceptance criteria and checkpoint requirements are satisfied.

## H0 - Recovery-Ready Runtime Producer Substrate

Status: complete

### H0.S1 - Recovery Intervention Closure

Status: complete

Acceptance:

- Runtime-producer substrate exists for bounded Codex CLI backend runs.
- Run manifests record producer identity, timeout/interruption state, logs, and hashes.
- Review packet completion and pass-claim checkpoint gates exist.
- Baseline/dev-fixture outputs are labeled honestly.
- Planning docs name the current state and forbid deterministic baseline overclaims.

Verification:

- Full suite passed with `100 passed, 2 warnings`.
- `cbm-loop-status --scope recovery-slice` passed.
- `cbm-loop-status --scope broad-goal` passed.
- `cbm-loop-status --scope pass-claim` remained blocked on same-model checkpoint, as intended.

## H1 - True Minimum-Useful CBM

Status: active

Vision link: `VISION.md` requires one runtime-agent-produced run on a pinned external codebase: real Surface Mapper output, reviewed by a real isolated Skeptic, with at least one non-trivial cited interpretive claim or challenge and a validated handoff.

### H1.S1 - Real Surface Mapper Producer

Status: completed

Objective:

Implement or dispatch a real Surface Mapper producer for one pinned external repo target. The producer must create a schema-valid surface map that is not a deterministic baseline or templated patch.

Allowed work:

- producer-registry scaffolding;
- Surface Mapper runtime skill loading or backend dispatch;
- run-manifest producer metadata;
- benchmark harness support;
- citation and validation fixes required by the runtime output;
- narrow loop-status checks required to keep the horizon executable.

Disallowed work:

- Phase B+ pass claims;
- new kernel-only validators unrelated to runtime producer evidence;
- project-type pack expansion;
- hook policy expansion;
- broad `VISION.md` rewrites.

Acceptance:

- Target repository and SHA are pinned.
- Surface Mapper producer identity and backend are recorded in `run-manifest.json`.
- Surface map validates against the schema.
- Every cited claim resolves to source bytes at the pinned SHA.
- Coverage distinguishes direct examination from extractor-only inspection.
- Output contains at least one substantive factual, inferential, or interpretive claim grounded in citations.
- Output is not labeled or structured as `cbm-baseline-*` or `dev-fixture-*`.

Verification:

- focused producer-registry or Surface Mapper regression tests;
- artifact schema validation;
- citation resolution;
- handoff validation if a handoff is produced;
- `TMPDIR=/var/tmp pytest -q`;
- `cbm-loop-status --scope broad-goal --work-category runtime-producer`.

Completion evidence:

- Benchmark artifact: `.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/RESULT.md`.
- Run id: `run-mcp-git-surface-mapper-h1s1-6`.
- Producer: `surface-mapper@1.2` through backend `codex-cli`.
- Boundary: H1.S2 remains pending; this run deliberately used `--codex-skeptic-mode none`.

Pushback handling:

- If the map is templated or shallow, revise the producer contract or skill and rerun.
- If citations fail, stop runtime expansion and repair citation generation/resolution first.
- If the runtime backend cannot produce usable output, record the failure and either choose another backend with user authorization or park the horizon.

### H1.S2 - Isolated Skeptic Review

Status: current; blocked until post-H1.S1 Opus review blockers are remediated

Objective:

Run a real isolated Skeptic against the H1.S1 surface map and ingest its challenges structurally.

Acceptance:

- Skeptic context excludes the mapper's hidden reasoning and parent-session context.
- Skeptic producer identity, backend, skill hash, and output path are recorded.
- At least one non-trivial challenge or explicit no-challenge finding is grounded in citations.
- Challenges are ingested into the contestation ledger.
- The Surface Mapper response path either accepts, revises, or records unresolved contestation.

Verification:

- isolation-sensitive fake backend regression;
- live or recorded runtime Skeptic run on the pinned external target;
- challenge ingestion validation;
- citation resolution;
- `TMPDIR=/var/tmp pytest -q`.

Pushback handling:

- If Skeptic output is generic, revise the Skeptic contract and rerun.
- If the Skeptic can see prohibited context, stop and do not continue with that backend.
- If challenge ingestion fails, repair ingestion before producing cards.

### H1.S3 - Validated Minimum-Useful Handoff

Status: pending

Objective:

Produce a handoff that carries the Surface Mapper output, Skeptic contestation, coverage honesty, and at least one non-trivial cited interpretive claim or challenge.

Acceptance:

- Handoff validates.
- Handoff clearly distinguishes baseline, mapper, and skeptic-produced artifacts.
- Handoff names unresolved unknowns and live disputes.
- Handoff contains no deterministic-baseline overclaim.
- Non-current-model checkpoint accepts the H1 completion claim.

Verification:

- `cbm validate <handoff>`;
- citation resolution for all promoted artifacts;
- `cbm-loop-status --scope pass-claim --work-category runtime-producer`;
- non-current-model checkpoint disposition `accept`.

Pushback handling:

- If the checkpoint asks for revision, classify the finding and update `.planning/CURRENT-PLAN.md` before implementing the revision.
- If the checkpoint rejects the claim as too weak, keep H1 active and choose the narrowest missing stage.

## H2 - Runtime Producer Repeatability

Status: pending

Objective:

Repeat H1 on at least one additional small external target or a materially different subtree so CBM does not overfit to MCP `src/git`.

Acceptance:

- Second pinned target validates.
- Surface Mapper and Skeptic both run with recorded producer identities.
- At least one non-trivial claim/challenge survives citation and review.
- Differences from H1 are recorded in `.planning/STATE.md`.

## H3 - Goal-Bound Cards And Intervention Handoff

Status: pending

Objective:

Produce goal-bound findings or intervention cards from runtime-produced maps and contestation, not from deterministic baseline alone.

Acceptance:

- Cards carry dependent challenges.
- Cards cite source bytes and upstream map claims.
- Cards recommend concrete next slices without pretending to mutate the codebase.

## H4 - Reuse And Refresh

Status: pending

Objective:

Demonstrate that a second run against the same repo/SHA or a changed SHA reuses prior artifacts, detects staleness, and preserves contestation.

Acceptance:

- Reuse avoids unnecessary remapping.
- Refresh marks stale claims and carries forward still-valid claims.
- Consultation or handoff reads from the corpus without freshness overclaim.

## H5 - Beta Graduation Measurement

Status: pending

Objective:

Turn `VISION.md` graduation criteria into measured beta-exit evidence across a representative repo sample.

Acceptance:

- Repository sample is defined.
- Metrics are collected rather than asserted.
- Expert review protocol exists for factual-defect catch rate and interpretive-challenge precision.
