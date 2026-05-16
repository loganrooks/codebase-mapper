# Skill: Consult

**Skill version**: 1.2
**Loaded by**: Reader subagent or main-context consultation.
**Reads**: existing `.research/<run_id>/` artifacts at validated/reviewed status, plus the source repo at the artifacts' `source_sha`.

## Purpose

Answer a well-scoped question from existing artifacts without re-running the pipeline. The cheapest form of reuse: someone already mapped this codebase; the artifacts likely contain the answer; pull it out, ground it, deliver — or refuse honestly if the answer is not in the corpus.

This is **not** the Surface Mapper. The Mapper produces; the Reader consults. The Reader does not produce new claims about the codebase; it surfaces existing claims with their citations and current status.

## When to load

- A user asks a question about a codebase that has been previously mapped.
- The question is well-scoped: it names a specific authority, surface, edge, file, or workflow.
- A `.research/` directory exists with at least one validated artifact.
- The user has not asked for a fresh run.

When **not** to load: if the question is broad ("how does this codebase work overall"), if no artifacts exist, if the user's question would require interpretive claims beyond what the existing artifacts contain, or if the corpus is too stale to consult.

## Inputs

- The user's question (plain language).
- The `.research/` directory.
- The source repository at the artifacts' `source_sha` (for citation resolution).

## Outputs

- A consultation response (text or markdown), grounded in citations from existing artifacts.
- Optionally: an `evidence-ledger.jsonl` append (`citation_reused`) recording which artifact citations were surfaced.
- Optionally: an `uncertainty-register.jsonl` append if the consultation surfaces a question the corpus cannot answer.

## Method

### Step 1 — Run validate-fresh

Before reading anything, run `cbm-validate-fresh` against the artifacts you intend to consult. This re-hashes the cited files at current HEAD and reports per-claim freshness. Three outcomes:

- **All cited bytes unchanged**: the artifacts are pinned readings still valid at HEAD. Consult freely.
- **Some cited bytes changed**: the artifact's claims may or may not still hold. Consult with care; flag affected claims as "needs review" in the response.
- **Many cited bytes changed (>30% threshold)**: the corpus is stale enough that consultation is unsafe. Refuse and recommend `cbm-refresh`.

The threshold is heuristic; err on the side of refusing rather than silently consulting stale material.

### Step 2 — Identify relevant artifacts

For the question, identify which artifacts likely contain the answer:

- Question about authorities, surfaces, edges → `surface-map.json`.
- Question about file structure, languages, build → `codebase-map.json`.
- Question about a specific intervention or finding → `interventions/` or `findings/`.
- Question about disputes or contested claims → look for `claim_status: challenged | contested` across artifacts plus `evidence-ledger.jsonl` for `claim_challenged` entries.
- Question about uncertainty → `uncertainty-register.jsonl`.

If multiple runs exist (multi-SHA history), pick the most recent validated/reviewed run unless the question is explicitly historical ("what did we know in March").

### Step 3 — Read the relevant frontmatter and bodies

Frontmatter for orientation; bodies (or specific JSON sections) for the actual content. Note:
- Each claim's `claim_register` and `claim_status`. Surface this in the response.
- Each claim's citations. These ground the answer.
- Any `dependent_challenges` or `challenges` arrays. These are the live disputes; surface them.

### Step 4 — Compose the response

Structure:

```markdown
## <Question, restated>

<Direct answer, grounded in citations from existing artifacts.>

**Evidence**: <citations, copied from the artifact, resolving to source_sha>.

**Status**: <claim_status of the underlying claims — active / challenged / contested>.

**Caveats**: <if validate-fresh flagged some bytes changed, name the affected claims; if claims are challenged, name the challenges and their status>.

**Source artifacts**: <paths to the artifacts consulted, with their status and source_sha>.
```

Key disciplines:

- **Cite from the artifacts, not from the source.** The Reader is consulting prior reading, not doing fresh reading. If the artifact's surface map says "ToolRegistry is the central authority [src/registry.py:14-87@a3f2c91]" then the response cites the artifact's claim and (transitively) the source. Do not introduce new citations not already in the corpus.
- **Preserve register and status.** If the artifact's claim is interpretive and challenged, the response says so. Do not flatten an interpretive-and-challenged claim into a confident factual answer.
- **Refuse when ungrounded.** If the question's answer is not in the artifacts, say so. Do not fall back to fresh reading; that's the Surface Mapper's job, and consulting and reading are different roles.

### Step 5 — Decide between answer, caveat, and refuse

Three response shapes:

- **Answer**: the corpus contains a grounded, fresh answer to the question. Deliver with citations and status.
- **Answer with caveat**: the corpus contains an answer but freshness is partial, or the underlying claims are challenged. Deliver with caveats made structural (not just disclaiming).
- **Refuse**: the corpus does not contain the answer, or the corpus is too stale, or the question requires interpretive claims beyond what the corpus contains. Refuse explicitly and recommend a path: `cbm-refresh`, full re-run, or different framing of the question.

Refusal is a first-class outcome. A Reader that always answers is a Reader that fabricates.

### Step 6 — Append to ledger

For each citation surfaced, append a `citation_reused` entry to `evidence-ledger.jsonl`. This makes consultation auditable: you can see which artifact citations have been consumed by readers and which are dormant.

For refusal, optionally append to `uncertainty-register.jsonl` an entry recording that this question was asked and could not be answered from the corpus. Over time, accumulated unanswerable-questions guide what new runs to perform.

## Anti-patterns

- **Consulting without validate-fresh.** Stale answers delivered without warning. Always check first.
- **Substituting fresh reading for consultation.** If you start opening source files to answer the question rather than citing the artifacts, you've stepped into the Mapper's role. Stop and either delegate or admit the corpus doesn't have the answer.
- **Confidently asserting a challenged claim's interpretation.** If the artifact has the claim at `claim_status: contested`, the response carries the contestation. Two readings are live.
- **Falling back when the corpus is stale.** Refusing to consult is correct when freshness is bad. "Let me read the source instead" is the Mapper, not the Reader.
- **Producing new interpretive content.** The Reader does not generate new readings. If the question demands a reading the corpus does not contain, refuse and suggest a fresh run with that goal.
- **Citing source files directly without citing the artifact that contains the claim.** The Reader's grounding is the corpus; the corpus's grounding is the source. Both layers should be visible.

## When to escalate

- The corpus is stale (>30% citations changed): recommend `cbm-refresh`.
- The question requires a fresh interpretive claim: recommend a new run with that goal as a `cbm-bind`.
- The corpus is contradictory or contested in ways the user needs adjudicated: surface the contestation and let the user decide.
- The question is itself unclear: ask the user for clarification before consulting.

## Output

The consultation response, plus optional ledger and register appends. The Reader's response is conversational and useful; the structural augmentation (ledger, register) is silent unless the user asks.
