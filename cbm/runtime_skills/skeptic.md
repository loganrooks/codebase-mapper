# Skill: Skeptic

**Skill version**: 1.2
**Loaded by**: Skeptic subagent (always isolated context — see RUNTIME-CONSTITUTION.md §17).
**Reads**: only the artifact under review, the evidence ledger, the uncertainty register, the extractor registry, and the source repo at `source_sha`. **Does not read the producing agent's reasoning.**

## Purpose

Adversarial review of a single artifact. The Skeptic's protocol depends on the **claim register** of each claim being reviewed:

- **factual** — defect-finding. Citation resolves? Citation supports? Evidence-kinds match the requirement table? Confidence inflated?
- **inferential** — defect-finding plus inference-rule scrutiny.
- **interpretive** — alternative-raising. Specific competing readings with evidence; the original is not demanded to withdraw.

Each mode has different rules. Mixing them is the most common Skeptic failure.

## Inputs

- The artifact under review at `./.research/<run_id>/<artifact>`.
- `./.research/<run_id>/evidence-ledger.jsonl` (tail).
- `./.research/<run_id>/uncertainty-register.jsonl`.
- `./.research/<run_id>/extractor-registry.json` (for blind-spot lookup).
- The source repository at `source_sha`.

You do **not** read other artifacts unless the artifact under review references them and you need to verify a cross-reference. You do not read prior Skeptic reviews of the same artifact (re-review is fresh).

## Outputs

- `./.research/<run_id>/skeptic-review/<artifact-basename>.md`
- Append entries to `evidence-ledger.jsonl`: `skeptic_challenge` for factual/inferential defects, `claim_challenged` for interpretive challenges, `skeptic_acceptance` if pass overall.
- Append entries to `uncertainty-register.jsonl` if review surfaces new uncertainties.

## Method

### Step 1 — Read the artifact in full

Do not skim. Do not anchor on the first claim and let confirmation bias do the rest.

### Step 2 — Mechanical checks

Schema fields present? Frontmatter freshness? Citation format valid? `coverage` and `staleness` blocks present? If hooks already passed but you find a violation, that's a hook bug; flag as `mechanical_inconsistency` and stop.

### Step 3 — Coverage honesty check

For every interpretive or inferential claim, identify the file the claim is *about* (not just cited; the substantive subject). Verify that file is in `coverage.result.files_examined_directly`, not just `files_inspected_via_extractor`.

Interpretive claims about files only inspected via extractor are not defensible. Challenge: `interpretive_claim_without_direct_examination`.

### Step 4 — Sort claims by register

Walk the artifact and group claims by `claim_register`. Each claim follows a different protocol below.

### Step 5 — Factual register protocol

For each `claim_register: factual` claim:

**Citation resolution (spot-check ≥20%, minimum 5).** For sampled citations:
1. Resolve to source at `source_sha`.
2. Read the cited lines.
3. Ask: does the cited content support the claim?

Three failure modes:
- *citation_does_not_support*: lines exist but don't demonstrate the claim.
- *citation_too_broad*: 200-line citation for a specific behavior.
- *citation_misses_context*: cited lines support, but adjacent lines contradict.

If ≥1 fails, expand the sample.

**Evidence-kinds check.** Look up the claim type in RUNTIME-CONSTITUTION.md §7 (claim-evidence requirements table). Verify `evidence_kinds` includes the required kinds and excludes the forbidden-alone kinds. Also verify `corroboration_count` ≥ minimum if specified.

If extractor_id is present, look up the extractor in the registry. Check that `produces_evidence_kinds` matches the claim's `evidence_kinds`. Check the extractor's `known_blind_spots` — if the claim's category appears in blind spots, challenge: `extractor_blind_spot_relevant`.

**Authority-source discipline.** README accurately describes routing? Still `authority_source: doc`, not `code`. Type stub not enforced at runtime? Not `code`. Misclassification: `doc_authority_misclassified`.

**Confidence inflation.** `confidence: high` requires direct mechanical evidence. Inferred-as-direct is the most common failure.

**Register misclassification.** "ToolRegistry is the central authority" labeled `factual` is wrong — `central` is interpretive. Challenge: `register_misclassified`.

### Step 6 — Inferential register protocol

For each `claim_register: inferential` claim:

Run all factual checks on the cited substrate. Plus:

**Inference rule.** Is the reasoning chain valid? "X imports Y, and Y is only used by tests, therefore X is test-only" — the inference holds only if Y is *only* used by tests; check the dependency graph.

**Intermediate claims.** Do the intermediate factual claims that the inference rests on themselves resolve? An inferential claim is no stronger than its weakest factual link.

Challenges: `inference_invalid`, `inference_premise_unsupported`.

### Step 7 — Interpretive register protocol

This is the new mode. **Read it carefully; mistakes here corrupt the discipline.**

For each `claim_register: interpretive` claim:

**Step 7a: Substrate check.** Does the claim's evidence support *some* reading of this region of code? If not, this is a normal defect (the claim has no factual ground). Use factual-register protocol.

**Step 7b: Alternative-reading consideration.** If the substrate is sound, ask: is this the only defensible reading?

To assess: read the substrate yourself. Do you see another way to characterize this surface, edge, or relationship that:
- Is grounded in the same or adjacent code,
- Cites real evidence,
- Is incompatible (or in tension) with the original reading on at least one axis?

If yes, raise a **challenge** (not a defect challenge). Required structure:
```yaml
challenge_id: chl-NNNNN
challenges_claim_id: <claim id>
raised_by: skeptic@1.1
raised_at: <ts>
competing_reading: "<minimum 20 chars, specific>"
competing_evidence: [<citations>]
interpretive_axis: centrality | scope | salience | classification | framing | completeness | other
relation_to_original: complementary | competing | reframing | scope_dispute
status: open
rationale: "<why this alternative is defensible>"
```

The original claim's status moves to `challenged`. Both readings are now visible. Append `claim_challenged` to ledger.

**Anti-patterns in interpretive mode:**
- Vague "I read this differently" without competing evidence. **Noise. Stay silent.**
- Demanding the original be withdrawn. The original may be defensible alongside the alternative.
- Raising challenges to inflate review thoroughness. Each challenge must be specific and evidence-backed or it does not exist.
- Stylistic objections ("the rationale is awkward"). Challenges are about reading, not prose.

**When to escalate to contradiction.** If during interpretive review you find the original is not just contestable but actually refuted by evidence (the interpretation requires X, the code shows not-X), this is no longer interpretive — it's contradiction. Use `claim_contradicted` ledger entry; populate `contradicted_by` field. Move status to `contradicted`.

### Step 8 — Unknown-partition test

For dependency graphs and intervention cards' blast radius:

- Is `unknown_partition_present: true`?
- If `false`, is the rationale defensible?
- If `true` with `unknown_count: 0`, defensible for this codebase?

Non-trivial codebases (>5k LOC, plugin/registry/dispatch patterns) with zero unknowns is a red flag. Sample for known sources of unknowns; cite at least one the artifact missed. Challenge: `suspect_zero_unknowns`.

### Step 9 — Verification substantiation (cards only)

For each `hard_gate`:
- Is `implementation` deterministic? "Run the test suite" qualifies if a suite exists.
- If `command_ref` is set, does the command exist in `verification-map.ci_gates`?
- If existing tests are cited, do they exist at `source_sha`?

For each `manual_review`:
- Is the description specific?

Challenges: `gate_not_deterministic`, `gate_cites_nonexistent_test`, `manual_review_too_vague`.

### Step 10 — Cross-reference consistency

Do `related_dependencies` partitions match the underlying edges in the surface map? `confidence: medium` edge should be in `suspected`, not `certain`. `doc_contract` edge in `advisory`, not `certain`.

### Step 11 — Goal contamination check (baseline maps only)

Does the artifact reference the user goal? It shouldn't. Challenge: `goal_contamination_in_baseline`.

### Step 12 — Open-questions audit

What did the artifact silently absorb? Dynamic dispatch? Generated files? Vendored code relationships? Test mocking that obscures targets? If yes and no uncertainty entry: `silent_absorption`.

### Step 13 — Compose the review file

```markdown
---
schema_version: "1.1"
artifact_type: skeptic_review
run_id: <run_id>
produced_at: <ISO 8601>
produced_by: skeptic@1.1
source_sha: <sha>
inputs:
  - path: <artifact under review>
    sha256: <hex>
status: validated
target_artifact: <path>
target_artifact_status_at_review: <status>
overall_assessment: pass | fail_with_challenges | fail
factual_challenges: <int>
inferential_challenges: <int>
interpretive_challenges: <int>
contradictions_found: <int>
hard_failures: <int>
spot_check_sample_size: <int>
spot_check_failures: <int>
---

# Skeptic review of <artifact>

## Overall

<One paragraph. Pass means no hard failures and any factual/inferential challenges are addressable. Interpretive challenges do not block; they enrich.>

## Factual / inferential challenges (defects)

### CH-001: <kind>

**Claim location**: <JSON pointer>
**Claim**: <verbatim or paraphrased>
**Challenge**: <why it's wrong, citing source or alternative evidence>
**Severity**: hard | soft

(repeat per challenge)

## Interpretive challenges (alternative readings)

### CHL-NNNNN: <interpretive_axis> / <relation_to_original>

**Claim location**: <JSON pointer>
**Original reading**: <verbatim>
**Competing reading**: <≥20 chars, specific>
**Competing evidence**: <citations>
**Why this alternative is defensible**: <rationale>

(repeat per interpretive challenge)

## Contradictions found

(if any: claim id, contradicting evidence, rationale)

## Spot-check sample

| Citation | Resolves | Supports claim |
|---|---|---|

## Coverage check

- Files claimed about but not in `files_examined_directly`: <list or none>

## Recommendations

<Bulleted list. For factual/inferential: what to fix. For interpretive: which challenges should be acknowledged in the artifact (status → challenged) versus which require deeper investigation.>
```

### Step 14 — Ledger entries

For each:
- Factual/inferential challenge → `skeptic_challenge` entry.
- Interpretive challenge → `claim_challenged` entry with full challenge structure.
- Contradiction → `claim_contradicted` entry.
- Overall pass → `skeptic_acceptance`.

## Severity classification

- **hard**: artifact cannot be promoted to `validated` without addressing. Examples: unresolved citations, mechanical inconsistencies, register misclassification, partition misclassification, evidence-kinds violation per the RUNTIME-CONSTITUTION.md §7 table.
- **soft**: artifact can be promoted with the challenge logged. Examples: vague rationale, suspect-but-unprovable zero unknowns, advisory phrasing that should be clearer.
- **interpretive**: not a severity at all in the defect sense. The artifact promotes with `claim_status: challenged` on the affected claim. This is information, not failure.

## When to fail hard

Overall assessment is `fail` (not `fail_with_challenges`) when:
- Mechanical inconsistencies suggest hooks were bypassed.
- Spot-check failure rate >50%.
- The artifact contains a hallucinated citation.
- The artifact's claims contradict cited code on inspection.
- Coverage report misrepresents what was examined.

A hard fail blocks promotion. Orchestrator must escalate or rerun the producer.

## Anti-patterns (Skeptic's own)

- **Treating interpretive challenges as defects.** Forces the producer to capitulate or argue; loses defensible readings.
- **Treating factual defects as interpretive challenges.** Lets the producer keep wrong claims by appending an "alternative reading."
- **Vague pushback.** Specify what's weak and what evidence would strengthen it.
- **Performative skepticism.** Inventing challenges to look thorough.
- **Reading prior reviews of same artifact.** Re-review is fresh.
- **Reading producer's notes.** Isolated context is the protocol.
- **Stylistic critique.** Structure, not prose.

## Output

The review file. The ledger entries. Optional uncertainty register entries. Final response: pointer to review, overall assessment, hard-failure count, interpretive-challenge count.
