# Agent Execution Brief — H1.S2c Challenge Disposition And Mapper Response

Status: proposed  
Date: 2026-05-07  
Audience: AI agent executing the work, and human reviewer auditing the result  
Primary horizon: H1 — True Minimum-Useful CBM  
Current stage: H1.S2c  
Goal type: concrete H1 execution, not broad uplift  
Input benchmark: `.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/`  
Input run id: `run-mcp-git-h1s2b-skeptic-1`  
Input challenge: `auth-001` / durable id `chl-10001`  
Expected result: H1.S2c complete, verified, and ready for H1.S3

## One-Sentence Mission

Disposition the real `skeptic@1.2` challenge from H1.S2b, record the mapper response structurally, and carry the resulting contestation state into a validated handoff path.

## Non-Negotiable Scope

This goal is **H1.S2c only**.

Do **not** run another live Skeptic unless verification proves the existing H1.S2b packet invalid.  
Do **not** claim H1 complete.  
Do **not** claim minimum-useful CBM complete.  
Do **not** claim Phase B or later.  
Do **not** start H1.S3 pass-claim work.  
Do **not** rewrite `VISION.md`.  
Do **not** broadly refactor `cbm/cli.py`.  
Do **not** reintroduce repo-local main-session `.codex/hooks.json`.

## Required Reading

Read these before editing:

- `.planning/HORIZONS.md`
- `.planning/CURRENT-PLAN.md`
- `.planning/STATE.md`
- `.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/RESULT.md`
- `.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/skeptic-review-surface-map.md`
- `.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/surface-map.json`
- `.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/handoff.md`
- `schemas/surface-map.schema.json`
- `schemas/handoff.schema.json`
- `schemas/evidence-ledger.schema.json`
- `RUNTIME-CONSTITUTION.md`

Interpretation order:

1. `.planning/CURRENT-PLAN.md` defines the current stage and allowed work.
2. `.planning/HORIZONS.md` defines H1.S2c acceptance.
3. The H1.S2b benchmark defines the exact input artifacts.
4. The schemas define allowed status values and required artifact shape.
5. `RUNTIME-CONSTITUTION.md` defines the interpretive challenge semantics.

## Current Facts To Preserve

H1.S2b is complete. Do not redo it.

The input Skeptic review is real runtime output:

```yaml
artifact_type: skeptic_review
produced_by: skeptic@1.2
run_id: run-mcp-git-h1s2b-skeptic-1
findings_logged: 1
```

The input challenge is:

```yaml
claim_id: auth-001
durable_challenge_id: chl-10001
raised_by: skeptic@1.2
interpretive_axis: centrality
relation_to_original: scope_dispute
current_status: open
```

The current challenged claim is:

```yaml
auth-001.kind: routing
auth-001.path: src/mcp_server_git/__init__.py
auth-001.claim_register: interpretive
auth-001.claim_status: challenged
```

The competing reading is:

```text
Routing authority is distributed across `pyproject.toml` and `__main__.py`; `__init__.py` is the shared command implementation rather than the central authority.
```

Competing evidence:

```text
pyproject.toml:25-26@4503e2d12b79
src/mcp_server_git/__main__.py:1-5@4503e2d12b79
src/mcp_server_git/__init__.py:7-24@4503e2d12b79
```

## Required Preflight Cleanup

Do this before or as part of the H1.S2c implementation.

### Cleanup 1 — Normalize Challenge ID In Rendered Review

Problem:

- The raw model output uses `chl-00001`.
- The durable structured id is `chl-10001`.
- The rendered Skeptic review body currently says `CHL-00001`, while frontmatter and the surface map use `chl-10001`.

Required behavior:

- Do **not** edit raw model output in `codex_outputs/`; raw output should remain raw.
- Update generated/rendered Skeptic review artifacts so the body uses the durable id `chl-10001`.
- Apply this to both preserved and convenience rendered review files when updating benchmark artifacts:
  - `.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/skeptic-review-surface-map.md`
  - `.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/.research/run-mcp-git-h1s2b-skeptic-1/skeptic-review/surface-map.md`

Suggested test:

```text
test_skeptic_review_render_uses_durable_challenge_id_in_body
```

Expected assertion:

- Rendered body contains `chl-10001` or `CHL-10001`.
- Rendered body does not contain `CHL-00001`.

### Cleanup 2 — Remove Smoke Citation Anchor From Real Skeptic Review

Problem:

The real `skeptic@1.2` rendered review still ends with:

```text
Smoke citation anchor: .gitignore:1@4503e2d12b79
```

Required behavior:

- Do **not** edit raw model output in `codex_outputs/`.
- Real `skeptic@...` rendered review artifacts must not include the smoke citation anchor.
- Smoke producers may keep smoke anchors if existing tests require them; runtime `skeptic@...` reviews must not.

Suggested test:

```text
test_runtime_skeptic_review_omits_smoke_anchor
```

Expected assertion:

- A rendered `skeptic@1.2` review body does not contain `Smoke citation anchor`.

### Cleanup 3 — Fix H1.S2b Handoff Next Action

Problem:

The H1.S2b handoff currently recommends running a real isolated Skeptic review, but H1.S2b already did that.

Required behavior for the H1.S2b handoff:

```text
recommended_next_action: Disposition the H1.S2b Skeptic challenge as accepted, revised, or unresolved contestation and carry the response into the handoff path.
```

Required behavior for the H1.S2c handoff after disposition:

```text
recommended_next_action: Prepare H1.S3 validated minimum-useful handoff and non-current-model checkpoint packet.
```

Suggested test:

```text
test_handoff_next_action_after_runtime_skeptic_points_to_challenge_disposition
test_handoff_next_action_after_challenge_disposition_points_to_h1s3
```

### Cleanup 4 — Update `HORIZONS.md` Metadata

Problem:

`.planning/HORIZONS.md` has H1.S2b/H1.S2c content but still says:

```text
Last updated: 2026-05-02
```

Required behavior:

- Update `Last updated` to `2026-05-07`.

### Cleanup 5 — Sharpen H1.S2c Acceptance Language

Problem:

H1.S2 currently mixes already-completed H1.S2b production requirements with H1.S2c disposition requirements.

Required behavior:

- Keep H1.S2b marked complete.
- Make H1.S2c acceptance focus on:
  - challenge disposition;
  - mapper response;
  - `surface-map.json` claim/challenge status update;
  - handoff contestation summary;
  - evidence-ledger disposition entry if supported;
  - validation/citation/evidence checks.
- Do not weaken H1.S2b or H1.S3 requirements.

## Main H1.S2c Disposition Decision

Use this disposition unless source inspection proves it wrong:

```yaml
decision: accepted_as_alternative
parent_claim_status: contested
```

Rationale:

- The original reading is not false: `__init__.py` is the shared command implementation.
- The Skeptic’s alternative is also valid: launch/routing authority is distributed across `pyproject.toml`, `__main__.py`, and `__init__.py`.
- This is interpretive disagreement, not factual contradiction.
- Preserve both readings.

Do **not** mark the claim `contradicted`.
Do **not** replace the original reading unless source inspection proves the original is misleading.
Do **not** collapse the alternative into a factual correction.

## Required Artifact State After H1.S2c

Update or produce a surface-map artifact with this state:

```yaml
authorities:
  - id: auth-001
    claim_status: contested
    challenges:
      - challenge_id: chl-10001
        status: accepted_as_alternative
        raised_by: skeptic@1.2
        relation_to_original: scope_dispute
        interpretive_axis: centrality
```

Also update `auth-001.rationale` or equivalent mapper-response field so it explicitly acknowledges both readings. Use wording like:

```text
Mapper response: accept `chl-10001` as an alternative reading. `__init__.py` remains the shared command implementation, while launch/routing authority is also distributed across `pyproject.toml` and `__main__.py`.
```

If the schema has no dedicated mapper-response field, append this sentence to `auth-001.rationale`.

## Required Handoff State After H1.S2c

The H1.S2c handoff must report:

```yaml
contestation_summary:
  claims_by_status:
    challenged: 0
    contested: 1
  open_challenges: 0
  contested_claims:
    - claim_artifact: .research/<run_id>/surface-map.json
      claim_id: auth-001
      challenge_count: 1
      summary: auth-001 has accepted alternative reading chl-10001 about routing authority centrality/scope.
```

Notes:

- `open_challenges` should count only challenges with `status: open`.
- `accepted_as_alternative` is not open; it is live contestation.
- Live contestation must appear in `contested_claims`.

If existing code has a constant like:

```python
LIVE_CHALLENGE_STATUSES = {"open", "accepted_as_alternative", "accepted_as_replacement"}
```

do not use it to compute `open_challenges`. Split the concepts if needed:

```python
OPEN_CHALLENGE_STATUSES = {"open"}
LIVE_CONTESTATION_STATUSES = {"open", "accepted_as_alternative", "accepted_as_replacement"}
```

Suggested test:

```text
test_handoff_counts_accepted_alternative_as_contested_not_open
```

Expected assertions:

- `claims_by_status.contested == 1`
- `claims_by_status.challenged == 0`
- `open_challenges == 0`
- `contested_claims[0].claim_id == "auth-001"`

## Evidence Ledger Requirement

If the implementation supports appending evidence-ledger entries during challenge disposition, append a `challenge_resolved` entry.

Required fields from the schema:

```json
{
  "schema_version": "1.2",
  "entry_kind": "challenge_resolved",
  "challenge_id": "chl-10001",
  "resolution": "accepted_as_alternative: preserved original auth-001 reading and accepted distributed-routing reading as a live alternative"
}
```

Also include the required common ledger fields:

```json
entry_id
ts
agent
skill_version
run_id
source_sha
```

Do not hand-edit ledger line hashes incorrectly. Use existing append/integrity helpers.

Suggested test:

```text
test_challenge_disposition_appends_challenge_resolved_ledger_entry
```

If the current code has no safe ledger append helper available for this path, stop and surface rather than manually corrupting ledger integrity.

## Preferred Narrow Implementation

Use an existing command/helper if one already exists. If no existing path can disposition a challenge, add a minimal command:

```bash
python3 -m cbm.cli respond-challenge <surface-map> \
  --repo <repo> \
  --challenge-id chl-10001 \
  --decision accepted_as_alternative \
  --response-note "Accept as alternative: __init__.py is the shared command implementation; launch/routing authority is also distributed across pyproject.toml and __main__.py." \
  --output <updated-surface-map>
```

Minimal behavior:

1. Load the target surface map.
2. Find the authority or edge containing `challenge_id == "chl-10001"`.
3. Set the challenge status to `accepted_as_alternative`.
4. Set the parent claim status to `contested`.
5. Append/record mapper response text.
6. Write the updated surface map.
7. Append a `challenge_resolved` ledger entry if a run directory and ledger are available.
8. Preserve input and output artifacts in the benchmark packet.

Do not implement a broad challenge-management subsystem. This is a narrow H1.S2c command/helper.

## Suggested Test Matrix

Add or update focused tests for these behaviors:

```text
test_skeptic_review_render_uses_durable_challenge_id_in_body
test_runtime_skeptic_review_omits_smoke_anchor
test_handoff_next_action_after_runtime_skeptic_points_to_challenge_disposition
test_respond_challenge_accepts_alternative_marks_claim_contested
test_handoff_counts_accepted_alternative_as_contested_not_open
test_challenge_disposition_appends_challenge_resolved_ledger_entry
test_handoff_next_action_after_challenge_disposition_points_to_h1s3
```

Use existing naming style if names differ, but keep the same assertions.

## Benchmark Packet To Produce

Create a new H1.S2c benchmark packet:

```text
.planning/benchmarks/2026-05-07-mcp-git-h1s2c-disposition/
  RESULT.md
  surface-map.json
  handoff.md
  evidence-ledger.jsonl
  .research/<run_id>/
    surface-map.json
    skeptic-review/surface-map.md
    handoff.md
    evidence-ledger.jsonl
    evidence-ledger.jsonl.integrity.json
    run-manifest.json if produced
    producer-registry.json if produced
```

Recommended run id:

```text
run-mcp-git-h1s2c-disposition-1
```

The packet must include enough preserved artifacts to audit the disposition without depending on `/var/tmp`.

## Required `RESULT.md` Content

The H1.S2c `RESULT.md` must include:

- status: passed for H1.S2c challenge disposition, or failed/blocked with reason;
- input benchmark path;
- input challenge id `chl-10001`;
- decision `accepted_as_alternative`;
- final `auth-001.claim_status`;
- final `challenge.status`;
- citation support summary;
- validation commands run;
- boundary statement:
  - H1.S2c only;
  - no H1 completion claim;
  - no minimum-useful-CBM claim;
  - no Phase B+ claim;
  - H1.S3 remains next.

## Required Planning Updates

If H1.S2c completes:

1. `.planning/CURRENT-PLAN.md`
   - Current stage becomes `H1.S3`.
   - Next `/goal` track becomes H1.S3 validated minimum-useful handoff.
   - State that H1.S2a/b/c are complete.
   - State that H1 is still not complete until H1.S3 and non-current-model checkpoint pass.

2. `.planning/HORIZONS.md`
   - `Last updated: 2026-05-07`.
   - H1.S2c status becomes complete.
   - H1.S3 status becomes current.
   - Add completion evidence for H1.S2c benchmark.

3. `.planning/STATE.md`
   - Add H1.S2c benchmark state.
   - State that the `auth-001` challenge was accepted as an alternative and carried into handoff.
   - State that H1.S3 remains pending.
   - Do not claim minimum-useful CBM complete.

4. `BUILD-LOG.md`
   - Add one slice entry with exact commands run.

## Required Verification Commands

Run focused tests first.

Then run at minimum:

```bash
python3 -m cbm.cli validate <updated-surface-map> --repo <target-repo>
python3 -m cbm.cli verify-citations <updated-surface-map> --repo <target-repo>
python3 -m cbm.cli check-evidence <updated-surface-map> --repo <target-repo>
python3 -m cbm.cli validate <updated-handoff> --repo <target-repo>
python3 -m cbm.cli verify-citations <updated-handoff> --repo <target-repo>
TMPDIR=/var/tmp pytest -q
git diff --check -- cbm tests .planning BUILD-LOG.md schemas
python3 -m cbm.cli loop-status --repo . --scope broad-goal --work-category runtime-producer --json
```

If no updated handoff contains citations beyond frontmatter, still run the validation command.

## Completion Criteria

H1.S2c is complete only when:

- rendered Skeptic review id mismatch is fixed or explicitly documented without corrupting raw output;
- smoke citation anchor is removed from real runtime Skeptic rendered review;
- H1.S2b handoff next action no longer asks for another Skeptic run;
- `auth-001` challenge `chl-10001` is dispositioned;
- parent claim status is `contested` unless source inspection justifies a different schema-valid status;
- challenge status is `accepted_as_alternative` unless source inspection justifies a different schema-valid status;
- handoff contestation summary reflects the disposition;
- evidence ledger records the disposition if supported by existing helpers;
- all validations and tests pass;
- planning docs point to H1.S3;
- no H1 completion, minimum-useful-CBM, or Phase B+ claim is made.

## Stop And Surface Conditions

Stop and surface if:

- schema semantics for `contested`, `accepted_as_alternative`, or `challenge_resolved` are ambiguous after reading schemas;
- the existing ledger append helpers cannot safely preserve integrity;
- the agent thinks another live model run is needed;
- accepting the challenge would require weakening H1 evidence standards;
- the implementation would require a broad challenge-management subsystem;
- a fix requires changing `VISION.md`;
- H1.S2c would imply H1 completion before H1.S3.

## Expected Commit

Suggested commit message:

```text
feat: disposition h1s2b skeptic challenge
```

Acceptable alternative if mostly artifact/planning:

```text
docs: record h1s2c challenge disposition
```

Do not bundle unrelated cleanup.

## Post-Goal Follow-Up

After this goal completes, the next candidate goal is:

```text
H1.S3 — produce the validated minimum-useful handoff and prepare the non-current-model pass-claim checkpoint.
```

Do not start H1.S3 until this goal’s completion criteria are met.
