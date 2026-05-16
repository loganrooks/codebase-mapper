# Reuse and Refresh

Mapping a codebase is work. The mature workflow does not re-do that work for every new question or every codebase change. This document describes how reuse and staleness handling actually operate in CBM v1.2.

## The principle

Staleness is information, not failure. A stale artifact is not useless — it is a pinned reading of a past state. A surface map of a project at SHA `abc123` is forever a valid reading of *that project at that SHA*, even when HEAD has moved far ahead. The citations still resolve at that SHA. The reading is preserved.

The workflow is therefore not "regenerate when things change" but "use what you have when you can; refresh when you should; re-run when nothing else fits." The choice is per-question and per-artifact, not per-run.

## Five forms of reuse

### Form 1 — Goal-agnostic cache

The codebase map and surface map contain no reference to a goal. They describe the codebase's structure and surfaces in goal-agnostic terms. So if you've mapped a repository at `source_sha: abc123` for goal A, you can run a different goal B against the same baseline without re-running `cbm-map` or the Surface Mapper. Only goal-binding and intervention cards are goal-specific; everything upstream is reusable.

**Workflow**: a second `cbm-init` against the same SHA accepts existing baseline artifacts as inputs (via `inputs[]`); `cbm-bind` produces a new goal-binding; the Intervention Planner produces new cards. No re-mapping.

### Form 2 — Incremental update

Three months later, the codebase has moved. Most files unchanged. The staleness block on each artifact (`depends_on_paths` + `scope_signature` + input hashes) tells you which artifacts are stale and which are not.

**Workflow**: `cbm-corpus-status` reports per-artifact freshness. For artifacts whose `depends_on_paths` haven't changed, no work needed. For artifacts whose depends-on-paths have changed but only in non-substantive ways (whitespace, comments), you may carry forward unchanged. For substantive changes, escalate to refresh.

### Form 3 — Historical consultation

Citations pin to SHAs. A surface map of `project@abc123` is forever a valid reading of `project@abc123`, even when HEAD is at `def789`. For questions about "what was the architecture in March," the old artifact *is* the answer. For questions about "is this still true now," staleness detection tells you whether to trust the old answer.

**Workflow**: pass the old artifact's `source_sha` to your tools; check out that SHA in a worktree if needed; consult the artifact as a primary source about that point in time.

### Form 4 — Consultation mode

You have a `.research/` directory. A new well-scoped question arrives. Often, well-scoped questions about authorities, edges, surfaces, or dependencies are already answered in the existing surface map.

**Workflow**: `cbm-consult <question>` invokes the Reader skill. The Reader runs validate-fresh on relevant artifacts, identifies which contain the answer, surfaces grounded citations and current claim status, or refuses if the answer isn't in the corpus or freshness is too poor to trust.

### Form 5 — Cross-run synthesis (deferred)

Stable cross-run surface IDs, project-level claim register, persistent contestation across many runs. Currently unimplemented; flagged in `VISION.md` as v2.0 work. Until then, cross-run synthesis is manual.

## Five staleness modes

Each mode answers a different freshness question. Order is by escalating cost and decreasing interpretive continuity preserved.

### Mode 1 — Validate

`cbm-validate-fresh <artifact>` re-hashes the cited files at current HEAD and compares to the SHAs recorded in the artifact. Output: a freshness report — claims still grounded in unchanged bytes versus claims whose evidence has shifted.

No new artifacts. Cheapest mode. Runs on session start (via `compaction-recovery`), as a precondition for `cbm-consult`, and as a hook on any pre-existing artifact you're about to read.

### Mode 2 — Verify

`cbm-verify <artifact>` re-resolves every citation at current HEAD. For each: bytes unchanged → still grounded; bytes changed → "needs review"; file or lines gone → "broken." This is a per-citation pass that *annotates* the artifact's freshness without rewriting claims.

Useful when you want to know "what in this artifact still holds at HEAD" without committing to a refresh. Output is a verify-report, not a new map.

### Mode 3 — Refresh structural

`cbm-refresh --mode structural` re-runs the deterministic kernel at current HEAD. Diffs against the cached codebase map; emits a refresh delta documenting added/removed/changed files. Updates the codebase map to HEAD; marks downstream interpretive maps as needing review with specific files flagged.

Cheap because the kernel is deterministic. Necessary precondition for any deeper refresh. Does not touch interpretive content.

### Mode 4 — Refresh interpretive

`cbm-refresh --mode interpretive` re-runs the Surface Mapper in differential mode. The Mapper takes the prior surface map as input and addresses what the codebase delta broke:
- Claims with all citations resolving to unchanged bytes → carried forward verbatim.
- Claims with shifted evidence → producer addresses each: update, retract, supersede, or mark needs-review.
- New surfaces, edges, authorities introduced by the delta → added.
- Challenges from the prior → carried forward, classified as still-active, resolved-by-refresh, obsolete-target-retracted, or now-contradicted.

Output: a successor surface map plus a refresh delta. The delta records the trajectory: what carried, what changed, what was retracted, what is new, what is newly contested.

This is the mode that preserves the most interpretive continuity. The previous reading is honored where it survives the codebase change; only what actually broke gets re-examined.

### Mode 5 — Re-run

`cbm-init` again. Full pipeline. The previous run is preserved at `.research/runs/<old-run-id>/` for historical reference; the new run starts fresh.

Use when the codebase has moved enough that the previous reading is no longer a useful starting point: major refactor, framework migration, new lead reader who wants their own first contact.

## When to use which mode

| Situation | Mode |
|---|---|
| Session resume; check before any read | 1 (validate) |
| User wants to know "what still holds in this artifact" | 2 (verify) |
| Codebase moved; baseline needs updating | 3 (structural) |
| Codebase moved; want to preserve interpretive readings where possible | 4 (interpretive) |
| Codebase moved enough to warrant first-contact again | 5 (re-run) |
| Question is well-scoped and corpus is fresh | Form 4 (consult) |
| Different goal, same SHA | Form 1 (goal-agnostic cache) |
| Asking about historical state | Form 3 (historical consultation) |

## Refresh delta as trajectory artifact

The refresh delta is what makes the corpus accumulate something more than dated artifacts. Without it, refresh is just overwrite, and the history of how the reading evolved is lost.

The delta records:
- **carried_forward**: claims that survived as-is.
- **updated**: claims whose evidence shifted but interpretive content survives.
- **retracted**: claims no longer defensible.
- **superseded**: claims replaced by a different but related successor.
- **newly_added**: claims introduced by the codebase delta.
- **newly_contested**: claims that survived but where the change surfaced a competing reading.
- **challenges_carried_forward**: per-challenge status post-refresh.
- **open_questions_reconciled**: per-uncertainty status post-refresh.
- **downstream_invalidation**: artifacts downstream of this one that are now stale.

Six months from now, "how did our understanding of this codebase change between Run 1 and Run 5?" is answerable from the deltas alone. The corpus accumulates not just artifacts but the trajectory of revision.

## The migration protocol (Mode 4 detail)

The subtle part of interpretive refresh. The simplest correct rule:

For any claim whose citations *all* resolve to unchanged bytes at HEAD: carry forward verbatim.

For any claim with at least one affected citation: the producer addresses it explicitly — re-examine and choose update / retract / supersede / mark-needs-review.

The mechanical pass identifies which claims need attention; the producer addresses only those. This converts refresh from "re-do everything" to "address the delta." Cost scales with change, not with codebase size.

**The interpretive wrinkle.** A claim like "ToolRegistry is the central authority" might survive bytes-level change to its citations even if the bytes changed — if the change was a comment fix or an internal refactor that doesn't shift centrality. The producer's job in Mode 4 is to ask, per affected interpretive claim: does the change in evidence affect the *reading*?

Often the answer is no. The claim survives with updated `evidence_kinds` and a refreshed citation, but the interpretive content is unchanged. Sometimes the answer is yes, and the claim needs re-examination. The discipline is to make this judgment per-claim rather than nuking everything.

## What stable IDs would let you do (deferred)

Currently each run uses run-local IDs. `auth-001` in one surface map; `auth-001` in the next surface map might or might not be the same surface. For refresh-mode workflows, this is fine — the refresh is a single Mapper invocation that knows how to map input-map IDs to output-map IDs via lineage links recorded in the delta.

For *project-level* persistent contestation across many independent runs (Form 5 reuse), you need stable IDs that survive arbitrary re-runs. That's v2.0 territory.

Until then: a `.research/` directory with many runs has trajectories within each run-pair (via deltas) but not stable identity across runs. This is sufficient for most reuse needs and falls short for a few. The shortfall is named here so it's not a surprise later.

## A note on `.research/` directory shape

Recommended layout for v1.2:

```
.research/
  runs/
    <run_id_1>/                   # individual runs
      intake.json
      state.json
      codebase-map.json
      surface-map.json
      interventions/...
      handoff.md
      ...
    <run_id_2>/
      ...
  refreshes/                      # refresh deltas indexed cross-run
    <delta_id>.json
  consultations/                  # consultation responses, optional
    <consultation_id>.md
```

Refresh deltas live cross-run because they connect runs. Consultations live cross-run because they may consult artifacts from any run. Individual runs stay self-contained.

This shape is recommendation, not enforcement. Implementations may flatten or reorganize as long as artifact paths in `inputs[]` and `refreshed_from` remain resolvable.

## How this serves a long-arc project

For a project that maps a codebase repeatedly over months or years (e.g., an uplift project working against an evolving substrate codebase), the v1.2 workflow is:

1. Map the codebase once, thoroughly.
2. For new well-scoped questions: `cbm-consult` (Form 4). No new run.
3. For questions that need a different goal but same SHA: a thin `cbm-bind` + Intervention Planner (Form 1). No re-mapping.
4. When the codebase has moved: `cbm-corpus-status` to see what's stale; `cbm-refresh --mode structural` to update the baseline; `cbm-refresh --mode interpretive` if substantive changes touched mapped surfaces. The refresh delta records what changed in your understanding.
5. Re-run only when the change is large enough that the prior reading is no longer a useful starting point.

The escalation matches the actual epistemic situation. You do the cheap thing first; you escalate only when escalation is warranted; the corpus accumulates trajectory rather than just snapshots.
