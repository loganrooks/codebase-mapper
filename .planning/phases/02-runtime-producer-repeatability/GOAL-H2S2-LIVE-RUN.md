# Agent Execution Brief — H2.S2 Live Producer Run

Status: proposed
Date: 2026-05-29
Last updated: 2026-05-29
Supersedes: none
Superseded by: none
Audience: AI agent executing the work, and human reviewer auditing the result
Primary horizon: H2 — Runtime Producer Repeatability
Current stage: H2.S2
Goal type: live producer dispatch
Input baseline: `.planning/phases/02-runtime-producer-repeatability/H2-PLAN.md` (locked H2 target + acceptance)
Expected result: a schema-valid H2.S2 benchmark packet at `.planning/benchmarks/<run-date>-h11-h2s2/` produced by a real `surface-mapper@1.2` + `skeptic@1.2` run on `codex-cli` against `python-hyper/h11` at SHA `62c5068c971579d61fa1b55373390e12f25fd856`, with the `.research/` tree preserved and authority docs updated; **without** requesting the cross-vendor pass-claim checkpoint (that is H2.S3).

## One-Sentence Mission

Dispatch a single real `cbm run` that produces both the H2.S2 surface map and Skeptic review against h11, validate the packet at absolute paths, preserve the `.research/` tree, and update the planning docs — without claiming H2 complete and without requesting the H2.S3 cross-vendor pass-claim checkpoint.

## Non-Negotiable Scope

This goal is **H2.S2 live producer dispatch only**.

Do **not** request a cross-vendor pass-claim checkpoint. H2.S3 produces the pass-claim packet; H2.S2 does not. The `cross-vendor-review` skill is not invoked at scope `pass-claim` in this goal.
Do **not** claim H2 complete or repeatability proven. H2 completion requires the H2.S3 packet and a non-current-model checkpoint disposition per ADR-005.
Do **not** claim Phase B+ or beta readiness.
Do **not** rewrite `VISION.md` or `RUNTIME-CONSTITUTION.md`.
Do **not** broaden kernel validators, project packs, or hook policy beyond what H2.S2 requires.
Do **not** revise the accepted H1 packet, the H1 checkpoint disposition, or the locked H2-PLAN.md.
Do **not** re-pick the H2 target. The target is locked: `python-hyper/h11@62c5068c971579d61fa1b55373390e12f25fd856`, scope `h11/` (excluding `h11/tests/`).
Do **not** raise the `--codex-timeout` envelope above 600 seconds without a stop-and-surface to the user. H2-PREFLIGHT Concern 2 prescribes the abort discipline; blind-retry-with-larger-budget is rejected.
Do **not** promote a dev-fixture, baseline, or smoke-anchor artifact. H1 LINEAGE caveat 2 documents the failure mode; H2.S2 promotes only the final Skeptic markdown and only a non-baseline surface map (`produced_by: surface-mapper@1.2`).
Do **not** publish the H2.S2 packet without the `.research/run-h11-h2s2-1/` subtree preserved. H2-PREFLIGHT Concern 9 makes preservation a publication-completeness gate.

The output of this goal makes the H2.S3 handoff packet dispatchable, not the pass-claim disposition itself.

## Required Reading

Read these before editing:

- `VISION.md`
- `RUNTIME-CONSTITUTION.md` (especially §2 evidence ledger, §10 unknowns, §13 artifacts-on-disk, §17 Skeptic three modes, §22 recovery, §25 reuse and refresh discipline)
- `.planning/HORIZONS.md` (H2 / H2.S2 sections)
- `.planning/CURRENT-PLAN.md`
- `.planning/STATE.md`
- `.planning/phases/02-runtime-producer-repeatability/GOAL-H2S1-REPEATABILITY-PLAN.md` (the prior `/goal` that locked the target)
- `.planning/phases/02-runtime-producer-repeatability/H2-PLAN.md` — **the binding plan; H2.S2 implements this**
- `.planning/phases/02-runtime-producer-repeatability/H2-TARGET-SELECTION.md`
- `.planning/phases/02-runtime-producer-repeatability/H2-PREFLIGHT.md` — concerns 1–9 mitigations
- `.planning/phases/02-runtime-producer-repeatability/H2-BENCHMARK-PACKET-SKELETON.md` — the H2.S2 artifact contracts table
- `.planning/phases/02-runtime-producer-repeatability/PLAN.md`, `SUMMARY.md`, `VERIFICATION.md`
- H1 packet for shape reference: `.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/RESULT.md` and `.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/RESULT.md`
- `.planning/decisions/ADR-001-cbm-owns-run-lifecycle.md`
- `.planning/decisions/ADR-003-producer-registry-over-outer-orchestrator.md`
- `.planning/decisions/ADR-004-deterministic-baseline-is-not-runtime-evidence.md`
- `.planning/decisions/ADR-005-cross-model-checkpoint-mandatory-for-pass-claims.md` (informs why H2.S2 does **not** request a checkpoint)
- `schemas/surface-map.schema.json`, `schemas/handoff.schema.json`, `schemas/evidence-ledger.schema.json`, `schemas/run-manifest.schema.json`, `schemas/skeptic-review.schema.json`, `schemas/producer-registry.schema.json`
- `cbm/runtime_skills/surface-mapping.md` and `cbm/runtime_skills/skeptic.md`
- Failure-mode citation for relative-path artifact validation: `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/VERIFY.md:15`

Interpretation order:

1. `H2-PLAN.md` is the binding plan; this brief implements it.
2. `H2-PREFLIGHT.md` is the resolved set of concerns; it tells H2.S2 what is allowed and what triggers stop-and-surface.
3. `H2-BENCHMARK-PACKET-SKELETON.md` is the artifact-contracts table; H2.S2 produces those artifacts exactly.
4. RUNTIME-CONSTITUTION sections govern artifact discipline at the per-claim level.
5. ADR-005 governs the H2.S3 pass-claim checkpoint, which is NOT in H2.S2 scope but the cross-vendor review skill's repeatability is downstream-dependent on H2.S2's output shape.

## Current Facts To Preserve

H2 target (locked on 2026-05-22 via the H2.S1 stop-and-surface gate, recorded in `H2-PLAN.md` and `H2-TARGET-SELECTION.md`):

- Repository: `https://github.com/python-hyper/h11`
- Pinned SHA: `62c5068c971579d61fa1b55373390e12f25fd856`
- Scope: `h11/` package source, excluding `h11/tests/`
- License: MIT
- Approximate LOC: 2,568 across 11 source files
- Target slug: `h11`

Schemas (verified unchanged since H1 merge `76db3bc` per H2-PREFLIGHT Concern 4): `surface-map.schema.json`, `handoff.schema.json`, `evidence-ledger.schema.json`, `run-manifest.schema.json`, `skeptic-review.schema.json`, `producer-registry.schema.json`.

H2.S2 must preserve all of:

- H1 acceptance at `76db3bc` (PR #1).
- The H2.S1 plan-only deliverables (`H2-PLAN.md`, `H2-PREFLIGHT.md`, `H2-BENCHMARK-PACKET-SKELETON.md`, `H2-TARGET-SELECTION.md`) without rewriting them.
- The `H2-PLAN.md` "Variant slice structure — no H2.S2a evidence-bundle-repair pre-step planned" sign-off. H2.S2 is a single `cbm run`; no pre-emptive S2a slice.
- The H2-PREFLIGHT Concern 5 / Concern 8 / Concern 9 obligations (caveat carryover, H2.A4 diff capture, `.research/` preservation).

What is **not** yet proven and must remain open until H2.S3:

- H2 cross-vendor pass-claim checkpoint (ADR-005 gate at `loop-status --scope pass-claim`).
- That `surface-mapper@1.2` / `skeptic@1.2` survive a second packet validation across a different target-shape.
- Repeatability of the `cross-vendor-review` skill at scope `pass-claim` (its second use; first was H1.S3).

## H2.S2 Deliverables

Produce a complete H2.S2 benchmark packet matching `H2-BENCHMARK-PACKET-SKELETON.md` exactly:

```text
.planning/benchmarks/<run-date>-h11-h2s2/
  RESULT.md
  surface-map.json
  skeptic-review-surface-map.md
  evidence-ledger.jsonl
  run-manifest.json
  producer-registry.json
  handoff.md
  .research/run-h11-h2s2-1/
    logs/
    codex_outputs/
    surface-map.json
    skeptic-review/surface-map.md
    evidence-ledger.jsonl
    evidence-ledger.jsonl.integrity.json
    producer-registry.json
    run-manifest.json
    handoff.md
    handoff.json
```

`<run-date>` is the actual date the packet directory is created (the date of this `/goal` invocation, not 2026-05-29 from this brief's "Date" header).

Update these existing authority docs as part of the H2.S2 commit:

```text
.planning/CURRENT-PLAN.md
.planning/HORIZONS.md
.planning/STATE.md
.planning/phases/02-runtime-producer-repeatability/PLAN.md
.planning/phases/02-runtime-producer-repeatability/SUMMARY.md
.planning/phases/02-runtime-producer-repeatability/VERIFICATION.md
BUILD-LOG.md
```

`HORIZONS.md` may move H2.S1 to `complete` (post-loop-status pass) and H2.S2 to `current; live evidence produced` (not `complete` — H2.S2 is complete only when its loop-status pass and a downstream H2.S3 packet have produced the pass-claim checkpoint). Do **not** mark H2 complete.

Do **not** create H2.S3 artifacts. The H2.S3 packet, the cross-vendor review packet, and the pass-claim disposition are H2.S3 deliverables, not H2.S2.

## Dispatch Plan

### Phase 1 — Probe re-verification (read-only)

Re-run the H2-PLAN.md probe (no `cbm run`, no Surface Mapper, no Skeptic):

```bash
git ls-remote https://github.com/python-hyper/h11.git | grep 62c5068c971579d61fa1b55373390e12f25fd856
# expect: 62c5068c971579d61fa1b55373390e12f25fd856	HEAD
# expect: 62c5068c971579d61fa1b55373390e12f25fd856	refs/heads/master
```

If the SHA is no longer present at HEAD or the LOC count drifts, stop-and-surface to the user. Do **not** silently re-pick.

Clone the target into the probe workspace per H2-PLAN.md probe pattern (use a date-stamped path under `/var/tmp/` for isolation):

```bash
PROBE_DIR=/var/tmp/cbm-h2-h11-62c5068
mkdir -p "$PROBE_DIR"
git clone --filter=blob:none --no-checkout https://github.com/python-hyper/h11.git "$PROBE_DIR/h11"
git -C "$PROBE_DIR/h11" checkout 62c5068c971579d61fa1b55373390e12f25fd856
git -C "$PROBE_DIR/h11" rev-parse HEAD
# expect: 62c5068c971579d61fa1b55373390e12f25fd856
```

### Phase 2 — Live producer dispatch

Single `cbm run` invocation producing both `surface-map.json` and `skeptic-review-surface-map.md` in one packet. Run-id: `run-h11-h2s2-1`.

Codex envelope (from H2-PREFLIGHT Concern 2):

- Backend: `codex-cli`
- Model: `gpt-5.4-mini`
- Surface Mapper reasoning effort: `medium`
- Skeptic reasoning effort: `high`
- `--codex-timeout`: `600`
- Isolation flags (set by `cbm` at the Codex subprocess level, not by the brief): `--ephemeral --ignore-user-config --ignore-rules -s read-only`

The exact `cbm run` invocation (final form is what the agent constructs from `cbm run --help` and the producer-registry contract; this is the shape, not a script):

```bash
python3 -m cbm.cli run \
  --target-repo /var/tmp/cbm-h2-h11-62c5068/h11 \
  --target-sha 62c5068c971579d61fa1b55373390e12f25fd856 \
  --target-scope h11/ \
  --packet-dir .planning/benchmarks/<run-date>-h11-h2s2 \
  --run-id run-h11-h2s2-1 \
  --producer surface_map=surface-mapper@1.2 \
  --producer skeptic_review=skeptic@1.2 \
  --backend codex-cli \
  --codex-model gpt-5.4-mini \
  --codex-timeout 600
```

(If `cbm run` expects different flag names, follow `cbm run --help` and reconcile with the producer-registry shape recorded at `H2-BENCHMARK-PACKET-SKELETON.md` rows for `producer-registry.json` and `run-manifest.json`.)

Stop-and-surface mid-dispatch if any of the following fires:

- Codex subprocess hits the timeout (`run-manifest.json` records `status: interrupted` + `cause: timeout`). Hard abort per H2-PREFLIGHT Concern 2. Root-cause before any retry.
- Surface Mapper produces a baseline-shaped artifact (`produced_by` starts with `cbm-baseline-*` or `dev-fixture-*`). H2-BENCHMARK-PACKET-SKELETON H2.S2 stop-and-surface row 1. Stop.
- Skeptic output cites prohibited parent-session context, is generic without competing evidence, or relies on hidden mapper reasoning. H1 LINEAGE caveat patterns — stop and either re-prompt or surface to the user.
- Citation resolution fails at the pinned SHA (any cited `path:lines@sha` does not resolve). Stop; document an `uncertainty-register.jsonl` entry per RUNTIME-CONSTITUTION §10 only after user confirms the response shape.
- Wall clock exceeds 8 minutes per producer for two consecutive retries (H2-PREFLIGHT Concern 2 soft abort).

### Phase 3 — Validate the packet at absolute paths

All artifact paths in validation commands MUST be absolute (re H1.S3 VERIFY.md:15 failure mode):

```bash
PACKET=/Users/rookslog/Development/cbm/.planning/benchmarks/<run-date>-h11-h2s2
TARGET=/var/tmp/cbm-h2-h11-62c5068/h11

python3 -m cbm.cli validate           "$PACKET/surface-map.json"                --repo "$TARGET"
python3 -m cbm.cli verify-citations   "$PACKET/surface-map.json"                --repo "$TARGET"
python3 -m cbm.cli check-evidence     "$PACKET/surface-map.json"                --repo "$TARGET"
python3 -m cbm.cli validate           "$PACKET/skeptic-review-surface-map.md"   --repo "$TARGET"
python3 -m cbm.cli verify-citations   "$PACKET/skeptic-review-surface-map.md"   --repo "$TARGET"
python3 -m cbm.cli validate           "$PACKET/run-manifest.json"               --repo "$TARGET"
python3 -m cbm.cli validate           "$PACKET/producer-registry.json"          --repo "$TARGET"
python3 -m cbm.cli validate           "$PACKET/handoff.md"                      --repo "$TARGET"
python3 -m cbm.cli verify-citations   "$PACKET/handoff.md"                      --repo "$TARGET"
```

Each command must exit 0. Record exit codes, surface counts, and citation counts in `RESULT.md` and `VERIFICATION.md`.

### Phase 4 — Preserve `.research/` tree

Confirm `$PACKET/.research/run-h11-h2s2-1/` contains `logs/`, `codex_outputs/`, and the per-step ledgers and manifests listed in H2-BENCHMARK-PACKET-SKELETON. If the runtime wrote `.research/` outside the packet, copy it in. The packet is **not complete** until the tree is in place (H2-PREFLIGHT Concern 9).

### Phase 5 — Write `RESULT.md` and `handoff.md`

`RESULT.md` mirrors the shape of `.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/RESULT.md` and `.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/RESULT.md` combined (since H2.S2 produces both in one packet). It records:

- Target (`python-hyper/h11@62c5068c`, scope, LOC, license).
- Commands and run-id (`run-h11-h2s2-1`).
- Surface summary (authority count, edge count, register mix, unknown-edge count per §10).
- Skeptic outcome (challenge IDs and titles, or schema-carried no-challenge note).
- Validation command outputs (exit codes, citation counts).
- H2.A4 diff fields from H2-PREFLIGHT Concern 8 (skill SHAs, backend version, target shape, surface depth, claim/challenge density, citation success rate, runtime cost).
- Boundary: H2.S2 evidence only; no H2 completion claim; no pass-claim checkpoint requested.

`handoff.md` is the per-run handoff produced by `cbm-handoff@0.1` from the H2.S2 run. It is preserved as a source-stage artifact for H2.S3 (which produces its own `HANDOFF.md` for the pass-claim packet). It validates against `schemas/handoff.schema.json` and declares `recommended_next_action_kind: prepare_pass_claim_review` (the cross-vendor reviewer is dispatched in H2.S3, not H2.S2).

### Phase 6 — H2.A4 diff record discipline

Record the H2-vs-H1 diff fields in `.planning/STATE.md` per H2-PREFLIGHT Concern 8 (skill SHAs vs H1 `356cda1f...` and `1d676f7d...`, backend, target shape, surface depth, claim/challenge density, citation success rate, runtime cost). Read these from the H2.S2 `run-manifest.json` directly — do not rely on H2.S3 to re-derive them.

## Authority-Doc Updates

After the packet is complete and validated:

### `.planning/CURRENT-PLAN.md`

- Update Active Recovery Sequence item 27 (the H2.S2 item authored at H2.S1 close) to "completed: H2.S2 packet at `<commit-hash>` and packet path `<absolute path>`".
- Add item 28: "Author `GOAL-H2S3-HANDOFF-AND-CHECKPOINT.md` against H2.S2 evidence."
- Update `Next /goal Track` to reference H2.S3 (validated handoff + cross-vendor pass-claim checkpoint).
- Keep `Current horizon: H2` and `Current stage: H2.S2` until completion; then advance to H2.S3.

### `.planning/HORIZONS.md`

- H2.S1 may now be marked `complete` (post-H2.S2 loop-status pass on `broad-goal`).
- H2.S2 status becomes `current; live evidence produced` (do NOT mark H2.S2 complete until loop-status broad-goal passes on this commit).
- Do **not** mark H2 complete.

### `.planning/STATE.md`

- Add Phase 02 Recent Checkpoints entry for the H2.S2 commit hash.
- Replace the H2.S1 verification footer's "expected status" templated placeholders with the actual H2.S2 post-commit `loop-status` JSON shape per the H2.S1 brief's two-commit pattern.
- Append the H2.A4 diff fields from H2-PREFLIGHT Concern 8.
- Update `pending next work` to reference H2.S3.

### Phase 02 files (`PLAN.md`, `SUMMARY.md`, `VERIFICATION.md`)

- `PLAN.md`: bump `Last updated`. Move H2.S2 track to "completed" with packet pointer.
- `SUMMARY.md`: orienting paragraph + factual state list updated to reflect H2.S2 evidence produced. Never overclaim. Bump `Last updated`.
- `VERIFICATION.md`: append the H2.S2 verification record (commands run, exit codes, test counts, loop-status outcomes). Bump `Last updated`.

### `BUILD-LOG.md`

Add a slice entry for H2.S2. Shape: H2.S1 slice entry but with H2.S2-specific Context / Implemented / Tests / Verification / Boundary fields.

## H2.S2 Verification Commands

Follows H2-PLAN.md's H2 Verification Commands template, with concrete absolute paths.

Pre-dispatch:

```bash
TMPDIR=/var/tmp pytest -q
git diff --check -- .planning BUILD-LOG.md cbm tests schemas
python3 -m cbm.cli loop-status --repo . --scope broad-goal --work-category runtime-producer --json
python3 -m cbm.cli loop-status --repo . --scope recovery-slice --work-category runtime-producer --json
```

Pre-dispatch loop-status outputs are recorded into `RESULT.md` and the H2.S1 verification footer in `STATE.md` (the templated placeholders from the H2.S1 commit are now resolved against the H2.S2 commit's post-state).

Post-dispatch (after the packet is written and authority docs are staged):

```bash
PACKET=/Users/rookslog/Development/cbm/.planning/benchmarks/<run-date>-h11-h2s2
TARGET=/var/tmp/cbm-h2-h11-62c5068/h11

python3 -m cbm.cli validate           "$PACKET/surface-map.json"                --repo "$TARGET"
python3 -m cbm.cli verify-citations   "$PACKET/surface-map.json"                --repo "$TARGET"
python3 -m cbm.cli check-evidence     "$PACKET/surface-map.json"                --repo "$TARGET"
python3 -m cbm.cli validate           "$PACKET/skeptic-review-surface-map.md"   --repo "$TARGET"
python3 -m cbm.cli verify-citations   "$PACKET/skeptic-review-surface-map.md"   --repo "$TARGET"
python3 -m cbm.cli validate           "$PACKET/run-manifest.json"               --repo "$TARGET"
python3 -m cbm.cli validate           "$PACKET/producer-registry.json"          --repo "$TARGET"
python3 -m cbm.cli validate           "$PACKET/handoff.md"                      --repo "$TARGET"
python3 -m cbm.cli verify-citations   "$PACKET/handoff.md"                      --repo "$TARGET"

TMPDIR=/var/tmp pytest -q
git diff --check -- .planning BUILD-LOG.md cbm tests schemas
```

Post-commit (after the H2.S2 commit lands):

```bash
python3 -m cbm.cli loop-status --repo . --scope broad-goal      --work-category runtime-producer --json
python3 -m cbm.cli loop-status --repo . --scope recovery-slice  --work-category runtime-producer --json
```

Expected behavior at the H2.S2 post-commit state:

- `broad-goal` must pass with `status: ok`, no issues, no warnings.
- `recovery-slice` must pass.
- `pass-claim` is **not** in the H2.S2 verification command list. It continues to pass on the accepted H1 minimum-useful checkpoint at `.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/`, which is correct for H1 and is not H2 evidence. H2.A5 is satisfied only when H2.S3 produces a non-current-model pass-claim checkpoint that becomes the most-recent accepted pass-claim checkpoint per `checkpoint_for_loop_scope` (`cbm/cli.py:5430-5452`).

## Two-Commit Verification Pattern

Same shape as the H2.S1 brief (Commit 1 = H2.S2 work with templated placeholders; Commit 2 = post-commit loop-status record only if the placeholders diverged from actuals). The dirty-authority-docs gate makes a single pre-commit `loop-status` deterministically fail on the H2.S2 commit boundary; that is the gate firing correctly, not an H2 regression.

**Commit 1 — H2.S2 work** (substantive slice):

```bash
TMPDIR=/var/tmp pytest -q
git diff --check -- .planning BUILD-LOG.md cbm tests schemas
git add <H2.S2 packet directory + authority-doc edits + BUILD-LOG.md entry>
git commit -m "<scoped subject>"
```

`STATE.md` and `BUILD-LOG.md` in Commit 1 carry templated placeholders for the post-commit loop-status JSON (e.g., `status: ok`, `issues: []`, `warnings: []`). The H2.S1 commit's templated placeholders are also resolved in this commit if H2.S2 advances H2.S1's status.

**Post-Commit-1 verification**:

```bash
python3 -m cbm.cli loop-status --repo . --scope broad-goal      --work-category runtime-producer --json
python3 -m cbm.cli loop-status --repo . --scope recovery-slice  --work-category runtime-producer --json
```

**Commit 2 — audit-only verification record** (only if the templated placeholders diverged from the actuals):

```bash
git add .planning/STATE.md BUILD-LOG.md
git commit -m "docs: record H2.S2 post-commit loop-status output"
```

Break the recursion at Commit 2: do **not** re-run `loop-status` after Commit 2 unless verifying an external claim about repo state.

## Suggested Tests If Code Changes Are Needed

Only add code tests if H2.S2 surfaces a tooling gap that must close before H2.S3 (e.g., a citation-resolver bug, a packet-validator bug, a Codex-subprocess-isolation regression). Most of H2.S2 is producer-output, not code. Possible tests:

```text
test_h2s2_packet_paths_match_skeleton
test_run_manifest_records_h2_envelope
test_evidence_ledger_integrity_round_trips
```

Do **not** add tests just to increase test count.

## Completion Criteria

H2.S2 is complete when:

- The H2.S2 packet at `.planning/benchmarks/<run-date>-h11-h2s2/` matches the artifact-contracts table in `H2-BENCHMARK-PACKET-SKELETON.md` exactly.
- Every artifact validates: `cbm validate`, `cbm verify-citations`, `cbm check-evidence` exit 0 at absolute paths against the h11 target checkout.
- The `.research/run-h11-h2s2-1/` subtree is preserved in the packet (H2-PREFLIGHT Concern 9 gate).
- `surface-map.json` is non-baseline (`produced_by: surface-mapper@1.2`).
- `skeptic-review-surface-map.md` is the promoted final Skeptic markdown (not a smoke-anchor exploratory version).
- The H2.A4 diff fields per H2-PREFLIGHT Concern 8 are captured in `.planning/STATE.md` from the H2.S2 `run-manifest.json`.
- `TMPDIR=/var/tmp pytest -q` passes.
- `cbm loop-status --scope broad-goal --work-category runtime-producer` passes post-commit with `status: ok`, no issues, no warnings.
- `cbm loop-status --scope recovery-slice --work-category runtime-producer` passes post-commit.
- No `--scope pass-claim` invocation occurs against H2 evidence in H2.S2 (that is H2.S3 work).
- No cross-vendor reviewer is launched against the H2.S2 packet in this `/goal`. The `cross-vendor-review` skill is dispatched in H2.S3.
- Authority docs (`CURRENT-PLAN.md`, `HORIZONS.md`, `STATE.md`, phase 02 `PLAN.md` / `SUMMARY.md` / `VERIFICATION.md`, `BUILD-LOG.md`) reflect H2.S2 status without overclaiming H2 complete.

## Stop And Surface Conditions

Stop and surface to the user if:

- The h11 target SHA `62c5068c971579d61fa1b55373390e12f25fd856` does not resolve on the public remote at probe time.
- The Codex subprocess hits `--codex-timeout 600` (`run-manifest.json` records `interrupted`/`timeout`) — H2-PREFLIGHT Concern 2 hard abort.
- The Surface Mapper produces a baseline / dev-fixture / smoke-anchor artifact instead of a real `surface-mapper@1.2` output.
- The Skeptic output cites parent-session context, hidden mapper reasoning, or is generic without competing evidence.
- A schema between this brief and dispatch changes (re-verify `git log 76db3bc..HEAD -- schemas cbm/schemas` before dispatch; H2-PREFLIGHT Concern 4 mitigation).
- The `.research/` subtree cannot be located or preserved.
- Citation resolution fails at the pinned SHA for any promoted claim (do not auto-promote to `uncertainty-register.jsonl` without user confirmation).
- The agent is tempted to request a cross-vendor pass-claim checkpoint in this `/goal` (that is H2.S3).
- The agent is tempted to mark H2 complete, claim repeatability proven, or claim Phase B+.
- The agent is tempted to bypass `--codex-timeout 600` by raising it without root-causing the abort.
- `cbm loop-status --scope broad-goal` fails post-commit.
- The full test suite fails outside the H2.S2 blast radius.
- The agent thinks `VISION.md` or `RUNTIME-CONSTITUTION.md` should be rewritten.

## Expected Commit

Suggested commit message:

```text
feat(h2): h2.s2 live producer run — surface-mapper + skeptic vs h11@62c5068c
```

If small tooling fixes are needed in the same commit (only if H2.S2 surfaced a gap that blocked dispatch):

```text
feat(h2): h2.s2 live run + <single-line-tooling-fix-scope>
```

Do **not** bundle unrelated cleanup. Do **not** bundle H2.S3 work. Do **not** bundle the H2.S3 brief (that is its own follow-up commit, parallel to how H2.S1 produced H2-PLAN.md without an H2.S2 brief in the same commit).

## Post-Goal Follow-Up

After this `/goal` completes, the next action is **not** a single H2 pass-claim bundle.

The next action is:

```text
Open a fresh /goal for H2.S3 using a new GOAL-H2S3-HANDOFF-AND-CHECKPOINT.md
authored against the H2.S2 packet and against H2-PLAN.md's H2.S3 slice.
H2.S3 produces the validated handoff packet at
.planning/benchmarks/<run-date>-h11-h2s3-handoff/ and dispatches the
cross-vendor pass-claim checkpoint review at
.planning/reviews/<run-date>-h2-repeatability-checkpoint/ via the
cross-vendor-review skill. Only H2.S3 makes the H2 pass claim.
```

Per-slice `/goal` invocations remain deliberate: H2.S3 carries the ADR-005 cross-model pass-claim checkpoint mandate; H2.S2 does not, and bundling the slices would conflate the boundaries.
