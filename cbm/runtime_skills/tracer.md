# Skill: Tracer

**Skill version**: 1.2
**Loaded by**: Tracer subagent in deep mode, or deterministic tracer command when no subagent runtime is available.
**Reads**: `RUNTIME-CONSTITUTION.md`, `schemas/workflow-trace.schema.json`, `dependency-graph.json`, `goal-binding.json`, refinement reports, this skill.

## Purpose

Produce workflow traces that make runtime understanding auditable. A trace is not a story about how the system probably works; it is an ordered set of steps with citations, claim registers, evidence kinds, known unknowns, and confidence rationale.

The Tracer must distinguish static projections from observed runtime behavior. A static dependency path can seed a trace, but it remains low-confidence until supported by `runtime_trace` or `command_output` evidence.

## Inputs

- `./.research/<run_id>/dependency-graph.json` (validated, fresh)
- `./.research/<run_id>/goal-binding.json` (if present)
- `./.research/<run_id>/verification-map.json` (if command output can safely be requested)
- Prior `./.research/<run_id>/refinements/*.json` when running a later refinement round

## Outputs

- `./.research/<run_id>/workflow-traces/<id>.json`
- Append entries to `evidence-ledger.jsonl` for every citation introduced
- Append uncertainties when a trace step depends on unobserved runtime behavior

## Method

### Step 1 — Select the workflow seed

Prefer a goal-bound candidate from `goal-binding.json`. If the candidate is a dependency edge, seed the trace from that edge. If the candidate is an authority, find the closest dependency edge that touches the authority path.

If no goal binding exists, choose the most concrete citable edge in this order:

- `call`
- `import`
- `config_contract`
- `unknown`

Do not invent a workflow from filenames alone.

### Step 2 — Classify evidence

For each step, classify the evidence:

- `static_relation`: AST/parser/import/call evidence only. This supports a static projection, not an observed workflow.
- `command_output`: a command actually ran through `cbm-run-gate`, and its output was captured.
- `runtime_trace`: instrumentation, logs, or tracing output captured from a real run.

If all steps are static, set trace confidence to `low` and write an explicit unknown explaining that runtime order is not observed.

### Step 3 — Build ordered steps

Each step must contain:

- stable `step_id`
- `order`
- `path` and optional `symbol`
- one-sentence description
- `claim_register`
- `claim_status`
- `evidence_kinds`
- citations

Static edge endpoints can be ordered as source then target, but that order is inferential. Runtime trace or command output can support stronger ordering claims.

### Step 4 — Preserve unknowns

Record every missing runtime fact that would change how a user should act on the trace:

- unobserved dispatch order
- dynamic loading
- framework routing not represented by static imports/calls
- environment-dependent behavior
- missing command output

Unknowns are not footnotes. They drive refinement and approval planning.

### Step 5 — Feed refinement

When a Skeptic challenge or prior refinement item targets dependency closure, route it back into the trace:

- If the trace can resolve it with runtime or command evidence, write the resolving step and cite the evidence.
- If the trace cannot resolve it, preserve it as an unknown and emit a refinement item with `reentry_targets` including `tracer`.

Do not mark challenges resolved without new evidence.

## Anti-Patterns

- Calling a static import chain a runtime workflow.
- Raising confidence because the trace is plausible rather than observed.
- Dropping a challenged dependency claim because a trace step exists.
- Running commands outside the approval plan or `cbm-run-gate` safety envelope.
- Hiding runtime gaps in prose instead of structured `unknowns`.

## Quality Bar

A usable trace:

- validates against `schemas/workflow-trace.schema.json`
- resolves every citation
- labels static-only traces as low confidence
- records unknowns when runtime behavior is unobserved
- routes unresolved questions into refinement rather than pretending closure
