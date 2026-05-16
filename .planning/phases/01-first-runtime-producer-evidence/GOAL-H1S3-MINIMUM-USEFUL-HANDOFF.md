# Agent Execution Brief — H1.S3 Minimum-Useful Handoff And Checkpoint Packet

Status: proposed  
Date: 2026-05-07  
Audience: AI agent executing the work, and human reviewer auditing the result  
Primary horizon: H1 — True Minimum-Useful CBM  
Current stage: H1.S3  
Goal type: concrete H1 execution, not broad uplift  
Input benchmark: `.planning/benchmarks/2026-05-07-mcp-git-h1s2c-disposition/`  
Expected result: validated H1 minimum-useful handoff packet prepared, non-current-model checkpoint packet prepared, and H1 pass claim left pending reviewer disposition

## One-Sentence Mission

Produce the H1.S3 validated minimum-useful handoff package and prepare the non-current-model checkpoint packet, while preserving H1 boundaries and surfacing all provenance caveats before any pass claim is accepted.

## Non-Negotiable Scope

This goal is **H1.S3 preparation only**.

Do **not** claim H1 complete.  
Do **not** claim minimum-useful CBM complete.  
Do **not** claim Phase B or later.  
Do **not** fill in or fake a non-current-model reviewer disposition.  
Do **not** run a new live Surface Mapper or Skeptic unless the existing H1.S1/H1.S2 packet is proven invalid.  
Do **not** rewrite `VISION.md`.  
Do **not** broadly refactor `cbm/cli.py`.  
Do **not** add unrelated validators or project packs.  
Do **not** reintroduce repo-local main-session `.codex/hooks.json`.

The output of this goal should make the H1 pass claim **reviewable**, not accepted.

## Required Reading

Read these before editing:

- `VISION.md`
- `RUNTIME-CONSTITUTION.md`
- `.planning/HORIZONS.md`
- `.planning/CURRENT-PLAN.md`
- `.planning/STATE.md`
- `.planning/phases/01-first-runtime-producer-evidence/PLAN.md`
- `.planning/phases/01-first-runtime-producer-evidence/VERIFICATION.md`
- `.planning/phases/01-first-runtime-producer-evidence/SUMMARY.md`
- `.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/RESULT.md`
- `.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/RESULT.md`
- `.planning/benchmarks/2026-05-07-mcp-git-h1s2c-disposition/RESULT.md`
- `.planning/benchmarks/2026-05-07-mcp-git-h1s2c-disposition/surface-map.json`
- `.planning/benchmarks/2026-05-07-mcp-git-h1s2c-disposition/handoff.md`
- `.planning/benchmarks/2026-05-07-mcp-git-h1s2c-disposition/evidence-ledger.jsonl`
- `schemas/surface-map.schema.json`
- `schemas/handoff.schema.json`
- `schemas/evidence-ledger.schema.json`
- `schemas/run-manifest.schema.json`

Interpretation order:

1. `VISION.md` defines the destination and the minimum-useful floor.
2. `.planning/HORIZONS.md` defines H1.S3 acceptance.
3. `.planning/CURRENT-PLAN.md` defines current allowed work.
4. `.planning/STATE.md` defines factual project state.
5. Phase 01 docs define the implementation phase record and must be brought up to date.
6. Benchmark artifacts define evidence, not chat history.

## Current Facts To Preserve

H1.S1 is complete narrowly:

- Real `surface-mapper@1.2` output exists on pinned MCP `src/git`.
- H1.S1 does not include a real Skeptic review.

H1.S2a is complete:

- H1.S1 evidence bundle was repaired before live Skeptic review.

H1.S2b is complete:

- Real isolated `skeptic@1.2` review exists.
- The review produced a cited interpretive challenge against `auth-001`.

H1.S2c is complete:

- `auth-001` / `chl-10001` was accepted as an alternative reading.
- Final state:
  - `auth-001.claim_status = contested`
  - `chl-10001.status = accepted_as_alternative`
  - handoff has `open_challenges: 0`
  - handoff has `claims_by_status.contested: 1`
  - H1.S3 is recommended next.

H1 itself is **not** complete until H1.S3 produces the validated minimum-useful handoff packet and a non-current-model checkpoint accepts the H1 pass claim.

## H1.S3 Deliverables

Produce these artifacts:

```text
.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/
  RESULT.md
  HANDOFF.md
  VERIFY.md
  LINEAGE.md
  CHECKPOINT-PACKET.md
  CHECKPOINT-PROMPT.md
  INCLUDED-ARTIFACTS.md
  .research/<run_id-or-preserved-inputs>/
    ...
```

Use this run/packet id unless there is an existing conflict:

```text
run-mcp-git-h1s3-minimum-useful-handoff-1
```

If no command naturally creates a new `.research/<run_id>` tree for H1.S3, preserve the relevant input run trees or exact artifacts in the packet and document the preservation strategy in `INCLUDED-ARTIFACTS.md`.

## H1.S3 Preflight Concerns To Resolve

Resolve or explicitly document these before preparing the pass-claim checkpoint packet.

### Concern 1 — Final Surface Artifact Lineage

Problem:

The H1.S2c `surface-map.json` is materially updated, but it still carries some H1.S1-era fields such as the original Surface Mapper `produced_at` timestamp and H1.S1 inputs. The final H1.S3 packet must make the lineage explicit.

Required H1.S3 statement:

```text
Final H1 surface state = H1.S1 runtime Surface Mapper artifact + H1.S2b runtime Skeptic review + H1.S2c mapper response/disposition.
```

Required action:

- Create `LINEAGE.md`.
- List each source artifact and its role:
  - H1.S1 `surface-map.json`: original runtime Surface Mapper reading.
  - H1.S2b `skeptic-review/surface-map.md`: real isolated Skeptic review.
  - H1.S2c `surface-map.json`: successor/disposition state carrying accepted alternative.
  - H1.S2c `handoff.md`: handoff carrying contestation summary.
  - H1.S2c `evidence-ledger.jsonl`: ledger with `challenge_resolved`.
- Do not let the final H1.S3 handoff imply the H1.S1 surface map alone already contained the H1.S2c disposition.

If the implementation can safely add a `refreshed_from`/lineage-style block to the H1.S3 successor artifact under the existing schema, do so. If not, preserve the explanation in `LINEAGE.md`.

### Concern 2 — Historical Smoke Citation Ledger Entry

Problem:

The H1.S2b rendered Skeptic review no longer contains the smoke citation anchor, but the ledger still includes a historical `citation_introduced` entry for `.gitignore:1@...` tied to the earlier review artifact path.

Required action:

Choose one of these paths:

1. Preferred if existing tooling supports it:
   - append a schema-valid ledger entry explaining that the smoke-anchor citation was a historical pre-cleanup rendered-review artifact entry and is not promoted in the H1.S3 handoff;
   - do not edit existing ledger lines.

2. Acceptable if no safe ledger entry exists:
   - document the issue in `LINEAGE.md` under `Historical ledger caveats`;
   - state that the raw Codex output was preserved, rendered review was cleaned, and the final H1.S3 handoff does not promote the smoke anchor as supporting evidence.

Do **not** hand-edit existing ledger lines.
Do **not** corrupt `.integrity.json` sidecars.

### Concern 3 — Mixed Run-Id On H1.S2b Challenge Ledger Entry

Problem:

The H1.S2b `claim_challenged` ledger entry may contain a `run_id` associated with H1.S1 while pointing to an H1.S2b artifact path. That is provenance ambiguity.

Required action:

Choose one of these paths:

1. Preferred if existing tooling supports it:
   - append a schema-valid clarification entry referencing the challenge id and explaining the lineage:
     - challenge raised during H1.S2b against the imported H1.S1 surface map;
     - artifact path points to the H1.S2b copied/imported surface artifact;
     - durable challenge id is `chl-10001`.

2. Acceptable if no safe ledger entry exists:
   - document this in `LINEAGE.md` under `Historical ledger caveats`.

Do **not** rewrite existing ledger entries unless there is a documented, tested migration command.

### Concern 4 — Local Verification Evidence

Problem:

There is no visible GitHub CI status. The repo relies on committed local verification records.

Required action:

Create `VERIFY.md` containing:

- exact commands run;
- exact exit status/outcome;
- test count and warnings;
- artifact validation commands;
- citation verification commands;
- evidence check commands;
- loop-status command and output summary.

Do not rely on chat history or agent messages.

## H1.S3 Handoff Requirements

Create `HANDOFF.md` as the H1 minimum-useful handoff packet.

It must include:

1. Target:
   - MCP servers `src/git`
   - pinned SHA `4503e2d12b799448cd05f789dd40f9643a8d1a6c`

2. H1 evidence chain:
   - H1.S1 Surface Mapper producer: `surface-mapper@1.2`
   - H1.S2b Skeptic producer: `skeptic@1.2`
   - H1.S2c mapper response: accepted `chl-10001` as alternative

3. Producer honesty:
   - distinguish runtime-produced artifacts from deterministic baseline/dev-fixture artifacts;
   - do not describe deterministic baseline artifacts as runtime-agent evidence.

4. Coverage honesty:
   - use final surface map coverage;
   - preserve limitations.

5. Contestation state:
   - `auth-001` is contested;
   - `chl-10001` is accepted as alternative;
   - `open_challenges: 0`;
   - `contested_claims` includes `auth-001`;
   - explain the original reading and accepted alternative.

6. Unknowns:
   - mention remaining unknown edge if still present;
   - do not imply full codebase understanding.

7. Recommended next action:
   - non-current-model checkpoint review of H1 pass claim;
   - not H2 or Phase B yet.

8. Boundary:
   - H1 pass claim is prepared but not accepted;
   - H1 is not complete until non-current-model checkpoint disposition accepts;
   - Phase B+ is not passed.

## Checkpoint Packet Requirements

Prepare a checkpoint packet for non-current-model review. Use existing `cbm checkpoint` if it is fit for purpose. If not, create static packet files and document why.

Target path:

```text
.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/
```

Required files:

```text
PROMPT.md
CHECKPOINT.md
DISPOSITION.md
```

Optional but recommended:

```text
EVIDENCE-MANIFEST.md
```

### PROMPT.md Requirements

The prompt must ask a non-current-model reviewer to determine whether H1 clears the minimum-useful CBM floor.

It must include:

- pass criterion;
- explicit non-claims;
- artifacts to inspect;
- questions to answer;
- allowed dispositions.

Use this pass criterion:

```text
H1 minimum-useful CBM floor: one pinned external target has a real runtime Surface Mapper output, a real isolated Skeptic review over that output, a structurally carried challenge/no-challenge result, a validated handoff with contestation and coverage honesty, and no deterministic-baseline overclaim.
```

Explicit non-claims:

- not Phase B;
- not standard mode;
- not repeatability;
- not beta readiness;
- not mature CBM;
- not cross-platform parity;
- not broad product maturity.

Reviewer questions:

1. Did H1.S1 use a real runtime Surface Mapper producer?
2. Did H1.S2b use a real isolated Skeptic producer?
3. Was the H1.S2b challenge grounded in citations?
4. Was the H1.S2c disposition structurally carried into the surface/handoff path?
5. Does the final handoff preserve coverage honesty and unknowns?
6. Does the final handoff distinguish runtime evidence from deterministic/dev-fixture evidence?
7. Are artifact lineage and ledger caveats clear enough to audit?
8. Is the H1 pass claim scoped correctly?
9. Should the disposition be `accept`, `accept_with_blockers`, `revise`, or `reject`?

### CHECKPOINT.md Requirements

Create skeleton frontmatter:

```yaml
status: pending
date: 2026-05-07
scope: pass-claim
pass_criterion: H1 minimum-useful CBM floor
reviewer_model_id:
same_model_fallback: false
confidence:
disposition:
```

Body:

```text
Reviewer fills this file. Do not complete from the current dev-agent model.
```

### DISPOSITION.md Requirements

Create skeleton:

```markdown
# H1 Minimum-Useful Checkpoint Disposition

Status: pending
Decision:

## Reviewer Summary

<to be completed by non-current-model reviewer>

## Required Revisions Or Blockers

<to be completed by non-current-model reviewer>

## Final Disposition

Allowed values: accept, accept_with_blockers, revise, reject.
```

Do not fill in a reviewer decision.

## Phase 01 Docs Update Requirements

Update these phase docs during H1.S3.

### `.planning/phases/01-first-runtime-producer-evidence/PLAN.md`

Update status and track summary:

- H1.S1 complete.
- H1.S2a complete.
- H1.S2b complete.
- H1.S2c complete.
- H1.S3 current or completed depending on result.
- Phase 01 remains open until non-current-model checkpoint disposition accepts the H1 pass claim.

Do not rewrite the phase concept.

### `.planning/phases/01-first-runtime-producer-evidence/VERIFICATION.md`

Update remaining close evidence:

- Mark real isolated Skeptic review as complete.
- Mark H1.S2c challenge disposition as complete.
- Add H1.S3 handoff/checkpoint artifacts if produced.
- Keep non-current-model disposition as pending unless actually completed by a non-current reviewer.
- Keep `cbm-loop-status --scope pass-claim` expected to fail until reviewer identity/disposition is filled, unless the checkpoint is actually accepted.

### `.planning/phases/01-first-runtime-producer-evidence/SUMMARY.md`

Update summary:

- no longer say isolated Skeptic review is missing;
- say H1.S1, H1.S2b, and H1.S2c evidence exist;
- say H1.S3 packet is prepared or current;
- say Phase 01 is not closed until non-current-model checkpoint disposition accepts.

## Planning Docs Update Requirements

If H1.S3 packet is prepared successfully:

1. `.planning/CURRENT-PLAN.md`
   - Current stage remains H1.S3 until non-current-model review accepts.
   - Next action is external/non-current-model checkpoint review.
   - Do not move to H2.

2. `.planning/HORIZONS.md`
   - H1.S3 status may become `current; checkpoint pending` or equivalent.
   - Do not mark H1 complete unless checkpoint disposition is accepted.
   - Include H1.S3 packet path under completion evidence only if packet validates.

3. `.planning/STATE.md`
   - Add H1.S3 packet state.
   - State H1 pass claim is prepared but pending non-current-model disposition.
   - State minimum-useful CBM is not complete until accepted disposition.

4. `BUILD-LOG.md`
   - Add exact commands run.
   - Include boundary statement.

## Required Verification

Run focused tests first if code changes are made.

At minimum run:

```bash
python3 -m cbm.cli validate <H1.S3 handoff artifact> --repo <target-repo>
python3 -m cbm.cli verify-citations <H1.S3 handoff artifact> --repo <target-repo>
python3 -m cbm.cli validate <final surface-map if produced> --repo <target-repo>
python3 -m cbm.cli verify-citations <final surface-map if produced> --repo <target-repo>
python3 -m cbm.cli check-evidence <final surface-map if produced> --repo <target-repo>
TMPDIR=/var/tmp pytest -q
git diff --check -- .planning BUILD-LOG.md cbm tests schemas
python3 -m cbm.cli loop-status --repo . --scope broad-goal --work-category runtime-producer --json
python3 -m cbm.cli loop-status --repo . --scope pass-claim --work-category runtime-producer --json
```

Expected pass-claim loop-status behavior:

- If checkpoint reviewer fields are still pending, `pass-claim` should fail or remain blocked.
- That is acceptable and should be recorded.
- Do not force pass-claim success by filling reviewer fields yourself.

## Suggested Tests If Code Changes Are Needed

Only add code tests if the H1.S3 work requires new behavior.

Possible tests:

```text
test_h1s3_handoff_includes_runtime_mapper_skeptic_and_disposition_lineage
test_h1s3_checkpoint_packet_has_pending_reviewer_fields
test_h1s3_checkpoint_prompt_lists_non_claims
test_h1s3_phase_docs_do_not_mark_h1_complete_without_checkpoint_acceptance
```

Do not add tests just to increase test count.

## Completion Criteria

This goal is complete when:

- H1.S3 handoff packet exists.
- H1.S3 checkpoint packet exists with pending reviewer fields.
- Preflight concerns are resolved or explicitly documented.
- Phase 01 docs are updated to current truth.
- Planning docs point to non-current-model checkpoint review, not H2.
- Validation and citation checks pass.
- Full tests pass.
- Broad-goal loop-status passes.
- Pass-claim loop-status behavior is recorded honestly.
- No H1 completion, minimum-useful-CBM completion, or Phase B+ claim is made.

## Stop And Surface Conditions

Stop and surface if:

- ledger correction semantics are ambiguous;
- checkpoint packet generation requires filling reviewer identity or disposition;
- pass-claim loop-status can only be made green by pretending same-model review is non-current;
- the agent thinks H1 should be marked complete before external/non-current review;
- artifact lineage cannot be explained without revising earlier H1 status;
- H1.S3 would require rewriting `VISION.md`;
- full suite fails outside the focused blast radius;
- the agent is tempted to start H2.

## Expected Commit

Suggested commit message:

```text
docs: prepare h1s3 minimum-useful checkpoint packet
```

If code changes are needed:

```text
feat: produce h1s3 minimum-useful handoff packet
```

Do not bundle unrelated cleanup.

## Post-Goal Follow-Up

After this goal completes, the next action is not H2.

The next action is:

```text
Run the non-current-model checkpoint review using the H1.S3 checkpoint packet.
```

Only after the checkpoint disposition accepts the H1 pass claim should the project mark H1 complete and consider H2.
