# CBM Horizons

Status: active
Last updated: 2026-05-07
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

Status: complete; H1.S2a, H1.S2b, and H1.S2c complete

Objective:

Run a real isolated Skeptic against the H1.S1 surface map and ingest its challenges structurally.

#### H1.S2a - Evidence-Bundle Repair

Status: complete

Objective:

Remediate accepted post-H1.S1 Opus review blockers before exposing the H1.S1 packet to a real isolated Skeptic.

Completion evidence:

- Handoff generation now describes non-baseline Surface Mapper output as runtime output and derives handoff coverage/caveats from `surface-map.json`.
- Dev-fixture Skeptic fallback output is not promoted or counted as real Skeptic review.
- Surface Mapper unknown-edge acceptance uses `kind: unknown`, not the literal `edge-unknown-001` id.
- Surface Mapper repair-pass tests preserve rejected output, repair prompt/output, stdout/stderr logs, and manifest repair metadata for success and failure.
- The H1.S1 benchmark `handoff.md` and `RESULT.md` record the existing packet limitation and avoid promoting unavailable dev-fixture Skeptic evidence.

#### H1.S2b - Real Isolated Skeptic Production

Status: complete

Objective:

Run a real isolated `skeptic@1.2` producer over the repaired H1.S1 Surface Mapper artifact without live mapper hidden reasoning or parent-session context.

Completion evidence:

- Benchmark artifact: `.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/RESULT.md`.
- Run id: `run-mcp-git-h1s2b-skeptic-1`.
- Producer: `skeptic@1.2` through backend `codex-cli`.
- Challenge: `auth-001` centrality/scope challenge grounded in `pyproject.toml`, `src/mcp_server_git/__main__.py`, and `src/mcp_server_git/__init__.py` citations.
- Boundary: H1.S2c remains pending; this run produced the Skeptic review and structural challenge but does not by itself claim H1 completion.

#### H1.S2c - Challenge Ingestion And Mapper Response

Status: complete

Objective:

Ingest the Skeptic output structurally and carry the Surface Mapper response as accepted, revised, or unresolved contestation.

Acceptance:

- The `auth-001` / `chl-10001` challenge is dispositioned as accepted, revised, or unresolved contestation.
- The Surface Mapper response is recorded on the claim without erasing the original reading.
- `surface-map.json` carries the final claim and challenge statuses.
- The handoff contestation summary counts accepted alternatives as contested, not open.
- A `challenge_resolved` evidence-ledger entry records the disposition when ledger integrity helpers are available.
- Schema validation, citation resolution, evidence validation, and regression tests pass.

Completion evidence:

- Benchmark artifact: `.planning/benchmarks/2026-05-07-mcp-git-h1s2c-disposition/RESULT.md`.
- Run id: `run-mcp-git-h1s2c-disposition-1`.
- Decision: `chl-10001` accepted as an alternative reading.
- Final state: `auth-001.claim_status` is `contested`; `chl-10001.status` is `accepted_as_alternative`.
- Handoff state: `open_challenges: 0`, `claims_by_status.contested: 1`, and H1.S3 is the recommended next action.

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

Status: current; handoff packet prepared, checkpoint pending

Objective:

Produce a handoff that carries the Surface Mapper output, Skeptic contestation, coverage honesty, and at least one non-trivial cited interpretive claim or challenge.

Acceptance:

- Handoff validates.
- Handoff clearly distinguishes baseline, mapper, and skeptic-produced artifacts.
- Handoff names unresolved unknowns and live disputes.
- Handoff contains no deterministic-baseline overclaim.
- Non-current-model checkpoint accepts the H1 completion claim.

Packet evidence prepared:

- H1.S3 handoff packet: `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/RESULT.md`.
- H1.S3 handoff: `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/HANDOFF.md`.
- H1.S3 lineage and ledger caveats: `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/LINEAGE.md`.
- H1.S3 verification record: `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/VERIFY.md`.
- Non-current-model checkpoint packet: `.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/`.

Pending evidence:

- Non-current-model reviewer fills `CHECKPOINT.md` and `DISPOSITION.md`.
- `cbm-loop-status --scope pass-claim --work-category runtime-producer` exits 0 after accepted non-current-model disposition.

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
