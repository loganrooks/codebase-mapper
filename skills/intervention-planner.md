# Skill: Intervention Planner

**Skill version**: 1.1
**Loaded by**: Intervention Planner subagent (one per candidate surface).
**Reads**: `AGENTS.md`, `schemas/intervention-card.schema.json`, surface map, synthesis notes/index, this skill.

## Purpose

Produce one intervention card (or findings card, if `research_only: true`) for one candidate surface. Cards are independent; many Planner instances run in parallel.

## Inputs

- `./.research/<run_id>/surface-map.json` (MVP)
- `./.research/<run_id>/intake.json` for `goal` and `mode`
- `./.research/<run_id>/synthesis-notes.md` (MVP) or `goal-binding.json` (standard+)
- A specific candidate surface id passed by the orchestrator
- (When loaded as subagent) the goal pack identifier

## Outputs

- `./.research/<run_id>/interventions/<id>.md` (or `findings/<id>.md`)
- Append entries to `evidence-ledger.jsonl`
- Zero or more append entries to `uncertainty-register.jsonl`

## Method

### Step 1 — Read what you've been given

You have a specific candidate surface and the user goal. Read:
- The candidate surface in the surface map.
- All edges where `from.path` or `to.path` matches the candidate.
- Synthesis notes' entry for this candidate.
- Relevant uncertainty register entries.
- **Crucially**: any `challenges` on the candidate's claim, and the candidate's `claim_status`.

If the candidate has `claim_status: contested` or `claim_status: contradicted`, your card must reflect that. A card built on contested claims cannot be high-confidence.

### Step 2 — Decide card type

`research_only: true` → findings card. Otherwise intervention card. MVP defaults to findings card via the `understand_repo` goal pack.

### Step 3 — Frontmatter: bind the goal

Standard fields. New fields in v1.1:

- `claim_status`: status of *this card's interpretive claims* (leverage classification, surface classification). Defaults to `active`. Will be set to `challenged` if the Skeptic raises an alternative reading.
- `surface_classification_register`: defaults vary by surface_type:
  - `explicit` → typically `factual`.
  - `implicit` → typically `inferential`.
  - `missing` → typically `interpretive`.
  - `virtual` → always `interpretive`.

### Step 4 — primary_files

For each file: `path`, optional `lines`, `role`, `citations` (≥1).

If `surface_type: missing`, primary_files names where the missing surface should live.

### Step 5 — related_dependencies (four-partition rule)

Walk outgoing edges from the candidate up to N hops (N = 1 lightweight, 2 standard, 3+ deep). Partition:

- `certain`: `confidence: high` AND kinds `import | call | public_api | config_contract | schema_contract`.
- `suspected`: `confidence: medium` OR kinds `test_exercises | generated_from`.
- `advisory`: kinds `doc_contract | implicit_social_contract`.
- `unknown`: kind `unknown` OR `confidence: low`.

All four partitions required, even if empty.

### Step 6 — affected_workflows

If workflow traces exist (deep mode) or the surface map identifies workflows touched, list them with citation or trace pointer.

### Step 7 — expected_leverage (interpretive by default)

In v1.1, `expected_leverage` is a structured object:

```yaml
expected_leverage:
  rating: low | medium | high
  rationale: "<≥20 chars; references primary_files or related_dependencies>"
  claim_register: interpretive  # default
  claim_status: active          # may move to challenged
  evidence_kinds: [<from list>]
  challenges: []                # populated if Skeptic raises alternatives
```

**Default `claim_register: interpretive`.** Leverage is a claim about how impactful a change would be — that's an interpretive judgment about significance. Setting to `factual` or `inferential` requires explicit cited grounding (e.g., "this surface is exercised by 15 of 20 workflows per workflow-traces.json, so leverage is high" — that's inferential, not interpretive).

The Skeptic operates in interpretive mode on this field unless you've explicitly downgraded the register.

**Anti-pattern**: high leverage rationale that doesn't cite. "This change has high leverage because it touches many things" — bad. Good: "Adding a method to ToolRegistry at `src/registry.py:14-29@<sha>` exposes new behavior to all 7 callers in `related_dependencies.certain`, including the public API entry at `src/api.py:88@<sha>`."

### Step 8 — blast_radius

Summarize partitioned counts. `unknown_partition_present: true` is the default; setting `false` requires `unknown_partition_rationale`.

### Step 9 — verification_strategy

At least one of `hard_gates` or `manual_review` must be non-empty.

For `hard_gates`, you can optionally set `command_ref: <ci_gate id>` pointing at a declared gate in `verification-map.ci_gates`. In standard+ mode, `cbm-run-gate <id>` will execute it within its declared safety envelope and produce `command_output` evidence.

**Anti-patterns**:
- Soft hard-gates ("tests should pass" — name a test or check).
- `command_ref` pointing at a gate that doesn't exist in verification-map.
- Gates that require capabilities outside the safety envelope (e.g., `requires_network: true` when the user approved `requires_network: false`).

### Step 10 — risks, confidence, confidence_rationale

`confidence_rationale` (≥20 chars) cites maps, open_questions, or **dependent_challenges**.

A card whose dependencies have `claim_status: challenged` or `contested` cannot be `confidence: high`. Examples:

- Card depends on `auth-001` which is `challenged` (centrality contested) → `confidence: medium` at best, with rationale: "depends on auth-001 which is currently challenged (chl-00012); the alternative reading would shift expected_leverage from high to medium."
- Card depends on `edge-0042` which is `contradicted` → card must either remove that dependency or move to `claim_status: superseded`.

### Step 11 — open_questions and dependent_challenges

These are different.

- `open_questions`: things we don't know. Reference `uncertainty-register.jsonl` ids.
- `dependent_challenges`: contested *readings* of things we do know. Reference challenge ids in the surface map.

```yaml
dependent_challenges:
  - claim_artifact: ".research/<run-id>/surface-map.json"
    claim_id: "auth-001"
    challenge_ids: ["chl-00012"]
    impact: "If the alternative reading prevails, this card's surface_kind shifts from plugin_registry to module_boundary, and verification strategy needs revision."
```

A card with non-empty `dependent_challenges` is propagating contestation. That is correct discipline; do not hide it to make the card look stronger.

### Step 12 — recommended_next_slice

Smallest safe next action. For findings cards, this is the next investigation step.

### Step 13 — Body prose

Below frontmatter:

```markdown
# <Card title>

## Why

<One paragraph: why this surface, given the goal. Cites maps and primary_files.>

## How (sketch)

<One paragraph.>

## Contestation

<If claim_status is challenged/contested or dependent_challenges is non-empty: explain in plain prose what readings are live and how the recommended_next_slice would help adjudicate. Omit this section if there's no contestation.>

## What this defers

<Bullet list.>
```

### Step 14 — Append to evidence ledger

Per citation introduced. For interpretive claims (leverage, surface classification), include `claim_register: interpretive` in the ledger entry so the Skeptic applies interpretive-mode protocol.

### Step 15 — Validate and write

Check schema mentally; let the hook validate. Fix the artifact if hooks reject.

## When to refuse a card

- The candidate, on closer reading, doesn't actually serve the goal → write a `findings_card` instead.
- The candidate's `claim_status` is `contradicted` → the card cannot be built on a contradicted foundation; surface to the orchestrator.
- Blast radius can't be partitioned (too many `unknown` edges) → write the card with `confidence: low` and explicit open questions.
- Verification strategy cannot be articulated → write a `draft` card with the verification gap as primary open question.

## Anti-patterns

- **Recommending without grounding.** Every claim about leverage, blast radius, or verification cites maps or source.
- **Leverage labeled factual.** Interpretive by default; downgrade only with explicit cited reasoning.
- **Hiding contestation.** If your candidate's claim_status is challenged, propagate it via `dependent_challenges`.
- **Citing the user goal as evidence for leverage.** Leverage is a property of the surface and dependency closure, not of the goal.
- **Soft hard-gates.** Name the test, check, or command.
- **Card depending on a contradicted claim.** If a dependency was contradicted, you cannot rely on it.

## Output

The card file. Final response (subagent): pointer, status, one-line note on confidence, most significant open question or dependent challenge.
