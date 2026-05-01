# Skill: Compaction Recovery

**Skill version**: 1.1
**Loaded by**: every agent on every invocation that is not the first in a run.
**Reads**: `state.json`, validated artifacts, ledger and register tails.

## Purpose

Re-establish run state from disk after compaction, crash, or session change.

The rule: before any agent does anything else on a non-first invocation, it runs this skill. The orchestrator can wrap subagent spawns to ensure subagents recover before acting.

## When to load

- First action of any session that is not run-creation.
- After any tool result suggesting context loss.
- When uncertain about run state.
- Before responding to the user when given a `run_id` but no recent context.

If unsure: load. Cost is small; cost of acting on a stale mental model is large.

## Method

### Step 1 — Read `state.json`

Records `run_id`, `source_sha`, `mode`, `goal_class`, `phase`, `artifacts` (with `status`), `subagents_spawned`, `last_action`.

If missing or malformed, surface to the user.

### Step 2 — Read every `validated` or `reviewed` artifact's frontmatter

Frontmatter only, not full content (context-prohibitive). Note `artifact_type`, `status`, `produced_at`, `inputs`, **`coverage`** (so you know what was examined), and **any contestation in the artifact** (look for the contestation summary in the handoff if present, or scan claim_status fields in maps).

### Step 3 — Tail ledger and register

Last ~50 entries of:
- `evidence-ledger.jsonl`
- `uncertainty-register.jsonl`

Look for:
- Recent `skeptic_challenge`, `claim_challenged`, `claim_contradicted` not yet resolved.
- Recent `claim_retracted` that may have invalidated downstream artifacts.
- Recent `uncertainty_logged` with `blocking: true`.

A blocking uncertainty halts the phase. Surface; do not proceed.

### Step 4 — Determine next action

Match your role against `state.phase` and `state.artifacts`:

- Surface Mapper, surface map exists with `status: validated` → done.
- Surface Mapper, prior Skeptic review failed → read review, re-run addressing failures.
- Intervention Planner, candidate has `claim_status: contradicted` → cannot proceed; surface to orchestrator.
- Intervention Planner, candidate has `claim_status: challenged` or `contested` → proceed but propagate via `dependent_challenges`.
- Skeptic, spawned for a specific artifact → review fresh.
- Orchestrator → walk `state.phase`, resume next phase action.

### Step 5 — Verify input freshness

For your next-action artifact, confirm inputs are still fresh. If any differs, **stop** and re-read.

### Step 6 — Verify source SHA

Compare `state.source_sha` to current HEAD. If they differ:
- Research-only runs: continue at recorded SHA via worktree if available.
- File-system-dependent runs: surface to user.

### Step 7 — Resume

Act with disk-rebuilt context. Do not rely on inherited compaction summary; rely on artifacts.

## Anti-patterns

- Trusting compaction summary over artifacts.
- Skipping recovery because "I remember enough."
- Reading every artifact in full (frontmatter first).
- Re-doing completed work.
- Acting on `draft` as if `validated`.
- Ignoring contestation status — a candidate with active challenges may need a different intervention path.

## Output

No artifact of its own. Output is your readiness to act with correct grounding:
- `state.phase` known.
- Next action determined.
- Input freshness verified.
- Blocking uncertainties surfaced or absent.
- Active contestations understood.
