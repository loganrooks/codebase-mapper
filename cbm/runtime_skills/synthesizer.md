# Skill: Synthesizer

**Skill version**: 1.2
**Loaded by**: orchestrator (in MVP) or main-context Synthesizer (in standard+).
**Reads**: `RUNTIME-CONSTITUTION.md`, the surface map(s), this skill.

## Purpose

Cross-reference the interpretive maps and produce a queryable synthesis index. The Synthesizer **does not produce a new model** of the codebase; it produces an index over what the maps already contain, plus an explicit register of contradictions, contestations, and gaps.

In MVP, runs in the orchestrator's main context (not as subagent). In standard+, remains in main context but runs against split maps.

## Inputs

- `./.research/<run_id>/surface-map.json` (MVP) or split maps (standard+).
- Workflow traces if present (deep mode).
- `./.research/<run_id>/intake.json`.

## Outputs

- `./.research/<run_id>/synthesis-notes.md` (MVP) or `synthesis-index.json` (standard+).
- Append entries to `uncertainty-register.jsonl`.

## Method (MVP — collapsed mode)

### Step 1 — Verify input freshness

Compare `inputs[i].sha256` to current artifact hashes. If stale, re-read.

### Step 2 — Build candidate-surface list

For the goal in `intake.goal`, walk the surface map and identify candidate intervention surfaces:

- Authorities whose `kind` matches goal-relevant kinds.
- Edges connecting goal-relevant authorities to candidate change sites.
- Tests/CI gates that would need updating.

For each candidate, record its `claim_status`. Candidates whose status is `challenged`, `contested`, or `contradicted` are still candidates, but the Planner needs to know.

### Step 3 — Find contradictions and contestations

Walk the maps for pairs that disagree:

- Authority claims `path X is config` but no edge of kind `config_contract` references `X`. Likely doc-derived or stale; log uncertainty.
- An edge claims `A imports B` but A doesn't appear in the file list. Severe; surface and stop.
- Two authorities of `kind: routing` that don't reference each other (possible duplicate routing systems).
- Test exercises a file marked `is_generated: true` without citing the generator.

Also walk for **interpretive contestations** — claims with `claim_status: challenged | contested`. These are not contradictions; they are live disputes the Planner must propagate.

For contradictions, append to `uncertainty-register.jsonl` with `kind: cross_map_contradiction`.

For contestations, do **not** try to resolve. Just record them in the synthesis notes so the Planner sees them and propagates via `dependent_challenges`.

### Step 4 — Emit notes for the Planner

Write `./.research/<run_id>/synthesis-notes.md` with frontmatter:

```yaml
artifact_type: synthesis_notes
status: validated
... (full frontmatter including coverage and staleness)
candidate_surfaces:
  - surface_id: <authority id or edge id>
    relevance_to_goal: <one line>
    citations: [<map references>]
    claim_status: active | challenged | contested | contradicted
    challenges: [<challenge ids if any>]
contradictions_logged: [<uncertainty register ids>]
contestations_propagated: [<challenge ids the planner should handle via dependent_challenges>]
```

The body is brief: one paragraph per candidate explaining why it's a candidate, citing the map. Do not propose an intervention.

## Method (standard+ — synthesis-index)

In standard+, write `synthesis-index.json` with the candidate list, cross-references, contradictions, and contestations. The synthesis index never re-cites source files — it cites the maps.

## Anti-patterns

- **Producing prose that drifts from the maps.** Every claim cites a map entry.
- **Resolving contradictions silently.** Log them.
- **Resolving contestations.** That's not the Synthesizer's job — contested readings stay live; the Planner propagates.
- **Producing a goal binding.** Synthesizer identifies candidates; binding is a separate step.
- **Hiding open questions.** Open questions are signal.

## On goal contamination

The Synthesizer reads `intake.goal` to focus its candidate list, but the synthesis index/notes still describe candidates in goal-agnostic terms. If you find yourself writing "this surface is good for *adding a feature*," reframe as "this is a `routing` authority of kind X" and let the Planner do the goal binding.

## Output

If MVP: `synthesis-notes.md` and uncertainty register appends.
If standard+: `synthesis-index.json` and uncertainty register appends.

Final response (when invoked as subagent in standard+): pointer to the index, register entries created, and any propagated contestations the Planner should handle.
