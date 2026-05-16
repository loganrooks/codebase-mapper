# OUTPUT-WORKFLOW.md

Reviewer: independent process/governance review
Review date: 2026-05-01
Scope inspected: `phase-a-mvp-foundation` branch and current review packet
Primary review packet: `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/`

## Executive verdict

The current planning reset is directionally right but not sufficient to govern a mostly automated Codex `/goal` loop. It has created a better review surface, acknowledged biased review framing, and separated architecture/workflow/vision questions. However, it still lacks the operating protocols that would make autonomous implementation safe: current-plan lifecycle rules, stale-plan detection, old-plan archival, phase-gate evidence standards, escalation thresholds, and reviewer disposition mechanics.

The project should pause feature implementation until a governance operating system is installed. The core risk is not that the code has no tests. The core risk is that a long autonomous loop can keep producing plausible, tested, artifact-shaped work while silently drifting away from the intended product boundary. Passing tests currently prove parts of the deterministic kernel and artifact gates; they do not prove that CBM has achieved nuanced codebase understanding, runtime-agent orchestration, or the maturity implied by the project vision.

I found one immediate auditability problem: the prompt asks reviewers to read `SHARED-CONTEXT.md`, but the file is not at the repository root. It exists under `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/SHARED-CONTEXT.md`. More seriously, multiple live governance docs refer to `VISION.md` and `RUNTIME-CONSTITUTION.md`, but those files were not available at the referenced root paths on the inspected branch. If those files exist only in a local dirty tree, the automated loop is being governed by non-auditable context. If they are absent, the project is missing its claimed destination and runtime-agent constitution. Either case should block further phase-completion claims until resolved.

The recommended operating model is: one authoritative destination, one durable roadmap, one factual state file, one active current plan, append-only build evidence, archived old plans, explicit incident reports, and mandatory review/disposition at phase boundaries or high-risk changes. Autonomous work should default to proceed only inside an active, fresh, scoped plan. Outside that plan, the loop should pause implementation, create a plan-change or incident artifact, and only resume after the plan/state/review surface has been updated.

## Observed workflow failures or risks

### 1. Authority references are not reliably resolvable

`AGENTS.md` tells future agents to read `VISION.md` first, then `.planning/STATE.md`, `.planning/CURRENT-PLAN.md`, `docs/roadmap.md`, and `README.md`. The shared context also says the project destination lives in `VISION.md` and runtime-agent discipline lives in `RUNTIME-CONSTITUTION.md`. On the inspected branch, `VISION.md` and `RUNTIME-CONSTITUTION.md` were not available at the referenced root paths.

This is not a cosmetic issue. In an autonomous loop, missing authority documents turn “alignment to vision” into a slogan. Agents cannot consistently apply a destination or runtime constitution that is absent, uncommitted, misplaced, or known only through prior context.

Required correction: governance must fail closed when an authoritative document reference does not resolve. Future agents should not continue implementation by reconstructing the missing document from memory or nearby docs.

### 2. The project has already outgrown the roadmap’s phase labels

`docs/roadmap.md` defines an MVP with five CLI commands and explicitly defers commands such as `cbm-bind`, `cbm-stale`, `cbm-run-gate`, project-type packs, per-artifact Skeptic spawning, and richer standard/deep-mode surfaces. The current `pyproject.toml` declares many of those commands and features already. `.planning/STATE.md` correctly acknowledges that the implementation is a mixed kernel build beyond Phase A and that the roadmap is partially outdated.

This is not necessarily bad engineering. Opportunistic kernel work can be useful. The failure is that phase labels and acceptance claims became unreliable. A future `/goal` agent cannot safely “continue Phase B” or “start Phase C” from `docs/roadmap.md` alone because implementation reality and roadmap sequencing have diverged.

Required correction: `docs/roadmap.md` should remain a durable intent/phase taxonomy, while `.planning/STATE.md` is the only source of current phase status. Phase labels should be assigned only through a phase-review artifact, not inferred from command availability or build-log narrative.

### 3. The current plan has status fields but not a lifecycle

`.planning/CURRENT-PLAN.md` has useful metadata: status, last updated, supersession, objective, candidate architecture direction, next actions, verification, open questions, and non-goals. What it does not yet define is when the plan is complete, stale, superseded, archived, or invalid.

That gap matters because autonomous loops need operational transitions, not just prose. Without lifecycle rules, an agent can complete the listed actions and then continue improvising. Or it can discover that the candidate architecture is wrong and patch around it without a visible replan.

Required correction: `CURRENT-PLAN.md` should carry explicit closure criteria, stale triggers, amendment rules, and review triggers. Completion of the plan should force a plan-close protocol before more implementation occurs.

### 4. `BUILD-LOG.md` is doing too much governance work

The build log is valuable: it records decisions, verification runs, self-critiques, and phase assessments. But it is too long and chronological to serve as the active governance surface. It should be evidence, not the place where future state, phase status, and pending decisions are discovered.

A long build log also creates review fatigue. The longer it gets, the easier it becomes for important reversals, caveats, and known gaps to be buried beneath successful test output.

Required correction: keep `BUILD-LOG.md` append-only and chronological, but add a separate state/decision/review structure that summarizes current facts and points to build-log ranges as evidence. Do not require future agents to mine the whole log to know what to do next.

### 5. Self-critique is useful but too weak as a gate

`AGENTS.md` requires drift checks, contract checks, and reviewer-eye checks at meaningful units of work. That is a good practice, but it is not enough for phase boundaries or high-risk changes. A self-critique can catch obvious drift, but it cannot be the only gate that authorizes phase completion, architecture shifts, or claims that the product is closer to the vision.

The repo already shows why. A previous review prompt was aborted because it overdetermined the diagnosis. That is a governance success in one sense, but it also reveals that review-packet quality itself needs a preflight check.

Required correction: self-critique should remain mandatory but advisory. Independent checkpoint review and explicit disposition should be mandatory for phase completion, architectural redirection, schema/contract changes, platform-adapter changes, and repeated failure recovery.

### 6. Verification currently proves artifact mechanics more than product maturity

The tests and smoke runs appear to exercise schema validation, citation resolution, ledger integrity, extractor registry checks, goal binding, challenge propagation, and handoff gates. That is good mechanical coverage. But roadmap-level product claims require more: a real benchmark repo, direct-examination coverage, runtime-agent behavior, meaningful interpretive claims, and reviewer assessment of card usefulness.

The current docs also recognize this gap. The shared context and state file say the tiny fixture is insufficient and that a pinned small real-world repo is still needed. Therefore, the project should not claim vision progress or mapping adequacy from tests alone.

Required correction: each slice and phase needs a verification matrix separating mechanical correctness, artifact contract correctness, product-quality evidence, and review evidence.

### 7. Hook architecture and correctness authority are still ambiguous

The architecture and contracts docs describe hooks as enforcement points, while `.planning/STATE.md` and `.planning/CURRENT-PLAN.md` now argue that hooks should be demoted to optional platform-adapter glue and that explicit CBM validation should be the source of truth. The current `.codex/` files enable SessionStart and Stop hooks that call CBM hook commands.

This may be a reasonable transitional state, but it is not yet governed. Hooks can be useful dogfooding; they can also create false confidence if treated as the product’s correctness mechanism.

Required correction: until architecture review is dispositioned, `STATE.md` should mark hook role as unsettled. Agents should not add more hook behavior or claim hooks enforce CBM correctness beyond the exact checks demonstrated.

### 8. Review independence was recognized only after a biased prompt existed

The aborted Opus review packet is a good trace artifact: it preserves the biased prompt and explains why it should not be used. But a better operating system would have caught the problem earlier with a review-prompt preflight checklist.

Required correction: every review packet should have a `REVIEW-SPEC.md` or `REVIEW-PLAN.md` that explicitly checks for anchoring, presumed conclusions, missing counter-hypotheses, and scope leakage before the reviewer is launched.

### 9. Dirty or local-only context is a recurring audit hazard

`.planning/STATE.md` says some broad dirty/untracked files predated the planning reset and should be treated as intentional working-tree context unless reviewed otherwise. That may be true locally, but it is not auditable from the committed branch. A mostly automated loop cannot safely depend on uncommitted context to make governance decisions.

Required correction: before plan activation, the agent must inventory dirty/untracked files. Pre-existing dirty files must either be committed, stashed, explicitly excluded from the slice, or documented in `STATE.md` with path-level detail and a reason they are safe to ignore.

## Recommended planning artifact model

The project needs a layered authority model. Each artifact should have one job.

| Artifact | Role | What belongs there | What does not belong there |
|---|---|---|---|
| `VISION.md` | Destination and maturity criteria | Product ambition, anti-goals, graduation criteria, non-negotiable epistemic standards | Current implementation status, next tasks, build history |
| `RUNTIME-CONSTITUTION.md` | Runtime CBM-agent discipline | Rules for Surface Mapper, Skeptic, Synthesizer, Planner, Tracer once runtime agents exist | Rules for the development agent building CBM |
| `docs/roadmap.md` | Durable phase taxonomy | Phase sequence, phase acceptance criteria, mode definitions, deferred work | Current phase status, active plan, ad hoc recovery actions |
| `docs/architecture.md` | Accepted architecture | Durable product/execution architecture after disposition | Candidate architecture under review, unaccepted options |
| `docs/contracts.md` | Durable external/internal contracts | CLI/artifact/schema/hook contract commitments | Implementation wish list or transitional behavior |
| `.planning/STATE.md` | Current factual state | Current branch/head, phase status, implemented/partial/stale/blocking facts, last verification, active incidents, authority index | Detailed work plan, speculative architecture argument, long history |
| `.planning/CURRENT-PLAN.md` | One active execution plan | Current slice objective, scope, expected write set, risks, acceptance criteria, verification matrix, review triggers, stale triggers | Multi-phase roadmap, historical logs, completed old plans |
| `BUILD-LOG.md` | Append-only chronological evidence | Decisions made, alternatives considered, verification outputs, self-critiques, commit/slice notes | Source of current truth, active to-do list, hidden plan |
| `.planning/reviews/<date-slug>/` | Review evidence and disposition | Specs, prompts, input list, reviewer outputs, synthesis, disposition | Unreviewed implementation decisions disguised as accepted findings |
| `.planning/archive/` | Historical plans/states | Closed or superseded plans with metadata and outcome | Active plan |
| `.planning/incidents/` | Drift/failure recovery | Bad assumptions, repeated failures, evidence-integrity problems, corrective actions | Routine build log notes |

Recommended additions:

1. `docs/governance.md`: the durable operating system for autonomous development.
2. `.planning/templates/`: templates for current plan, state update, build-log entry, review packet, disposition, incident report, and phase gate.
3. `.planning/decisions/`: accepted architectural/product decisions, similar to lightweight ADRs.
4. `.planning/phase-reviews/`: phase-completion evidence bundles.
5. `.planning/verification/`: optional slice-level command-output summaries when verification is too detailed for `BUILD-LOG.md`.

The key rule: `docs/*` should represent accepted durable knowledge; `.planning/*` should represent live operational state, candidate plans, review evidence, and historical trace.

## Current-plan lifecycle protocol

### Required shape of `CURRENT-PLAN.md`

`CURRENT-PLAN.md` should be detailed enough to constrain autonomous work, but not so detailed that it becomes a second roadmap. It should project one implementation slice ahead, with at most one or two candidate next slices named as non-binding context.

Recommended sections:

```md
# Current Plan

Status: draft | active | blocked | stale | complete-pending-review | completed | superseded | archived
Plan ID:
Created:
Activated:
Last updated:
Applies to branch:
Applies to head:
Supersedes:
Superseded by:
Risk class: low | medium | high | critical
Owner/mode: autonomous | supervised | review-only

## Objective

## Why this plan now

## Inputs and authority checked

## Scope

## Non-goals

## Expected write set

## Assumptions

## Work items

## Acceptance criteria

## Verification matrix

## Review triggers

## Staleness triggers

## Completion protocol

## Candidate next plans
```

The expected write set should name directories and files likely to change. This creates a tripwire for scope drift. If implementation needs to touch materially different files, the agent must amend or replace the plan before continuing.

The verification matrix should separate:

- focused tests;
- full tests;
- schema/artifact validation;
- citation/ledger/freshness checks;
- benchmark or product-quality evidence;
- docs/governance checks;
- reviewer/checkpoint requirements.

### How far into the future it should project

`CURRENT-PLAN.md` should project one coherent slice, not a phase and not a multi-week backlog. It may include a short “candidate next plans” section to preserve continuity, but those candidates are not authorization to implement.

A good slice is small enough that a reviewer can answer: “Did this plan finish, and did it finish without scope drift?” For code work, that usually means one behavior, one contract change, one artifact change, or one governance correction. For architecture/workflow work, it can be one review/disposition loop.

### Protocol when the current plan is complete

When all work items are completed, the agent must stop feature implementation and run a plan-close protocol:

1. Mark `CURRENT-PLAN.md` as `complete-pending-review`.
2. Run the verification matrix and capture command outputs or summaries.
3. Append a `BUILD-LOG.md` entry with:
   - plan ID;
   - commit range;
   - files changed;
   - acceptance criteria result;
   - verification commands and outcomes;
   - known gaps;
   - reviewer requirement status.
4. Update `.planning/STATE.md` with factual changes only.
5. If thresholds require review, create or update a review/checkpoint packet and wait for disposition before further implementation.
6. Archive the completed plan under `.planning/archive/current-plans/`.
7. Create the next `CURRENT-PLAN.md` as `draft`, derived from `STATE.md`, accepted roadmap/decision docs, and any review dispositions.
8. Activate the next plan only after required authority docs resolve and no blocking incident remains.

No agent should continue from a completed plan by appending extra work under the same plan. Completion forces either a new plan or a deliberate plan amendment.

### Protocol when the current plan changes or becomes stale

Distinguish minor amendments from major replans.

A minor amendment is allowed in place when all are true:

- objective is unchanged;
- risk class is unchanged;
- acceptance criteria are unchanged or only clarified;
- expected write set changes narrowly;
- no architecture/product-contract decision is introduced.

A major replan is required when any are true:

- objective changes;
- risk class increases;
- expected write set changes materially;
- a roadmap/architecture/contract assumption changes;
- a required authority doc is missing or contradicted;
- implementation has moved beyond the plan;
- user direction changes the target;
- repeated failures suggest the plan is no longer fit.

Major replan protocol:

1. Mark current plan `stale` or `superseded`.
2. Add a “Closure without completion” section explaining the cause.
3. Archive the old plan with metadata.
4. Update `STATE.md` with the new factual status and open decision.
5. If caused by error/drift/failure, create an incident artifact.
6. Draft a replacement plan.
7. Do not resume implementation until the replacement plan is active.

### Old-plan archival

Yes, old plans should be archived. Use:

```text
.planning/archive/current-plans/YYYY-MM-DD-<plan-id>-<slug>.md
```

Each archived plan should preserve or add:

- original activation date;
- closure date;
- activation commit;
- closure commit;
- status at closure: completed, superseded, stale, aborted;
- superseded-by plan ID;
- reason closed;
- acceptance criteria result;
- verification summary;
- review packet links;
- incident links;
- build-log range;
- final disposition.

Do not delete old plans. Superseded plans are evidence of how the autonomous loop reasoned.

## Drift/failure recovery protocol

The project needs an explicit incident protocol. Drift and repeated failures should not be handled by defensive patching.

### Failure levels

| Level | Trigger | Required response |
|---|---|---|
| L0: local defect | A focused test or obvious bug fails once with a clear fix | Fix inside current plan; log if meaningful |
| L1: plan drift | Work exceeds expected write set, changes objective, or discovers stale assumption | Stop feature work; amend or supersede plan |
| L2: repeated failure | Same gate/test/assumption fails twice after attempted fixes | Create incident; run checkpoint review before continuing |
| L3: architecture/contract uncertainty | Multiple plausible product shapes or contract semantics would lead to different systems | Pause implementation; create decision/review packet |
| L4: evidence integrity risk | Citations, ledger, phase claims, or docs may have misled reviewers/users | Freeze claims; mark artifacts stale/suspect; create incident and disposition |
| L5: irreversible/external action | Publishing, external side effects, production changes, paid services | Require explicit user approval |

### Incident artifact

Create:

```text
.planning/incidents/YYYY-MM-DD-<slug>.md
```

Template:

```md
# Incident: <slug>

Status: open | mitigated | resolved | superseded
Opened:
Closed:
Detected by:
Related plan:
Related commits:
Severity: L1-L5

## Summary

## Trigger

## Evidence

## Impact

## Bad assumption or failure mode

## Affected artifacts/docs/claims

## Immediate containment

## Options considered

## Chosen recovery path

## Verification required

## Preventive governance change

## Disposition
```

### Recovery rules

1. Preserve traceability before fixing. Record the failure, bad assumption, and affected artifacts.
2. Prefer rollback when the bad change is isolated and recent.
3. Prefer forward fix when rollback would destroy useful, well-evidenced work.
4. Invalidate or supersede affected artifacts rather than silently editing them to look clean.
5. Add a regression test or governance check for every repeated failure.
6. Avoid defensive patching: do not add narrow code or doc patches merely to quiet the latest reviewer/test without addressing the underlying assumption.
7. After recovery, update `STATE.md`, `CURRENT-PLAN.md`, `BUILD-LOG.md`, and any affected review disposition.

### Escalation thresholds that force pause/review

Autonomous implementation should pause when any threshold is met:

- `VISION.md`, `RUNTIME-CONSTITUTION.md`, `STATE.md`, or `CURRENT-PLAN.md` is missing or unresolved.
- `CURRENT-PLAN.md` is absent, stale, completed, superseded, or does not authorize the intended work.
- The same test, gate, or review objection fails twice after attempted fixes.
- The same category of mistake recurs twice, even if individual failures differ.
- The implementation touches schema, contract, architecture, roadmap, runtime-agent orchestration, hook behavior, or artifact semantics without a plan that named that risk.
- The expected write set is exceeded by more than a narrow incidental change.
- A phase-completion claim would rely only on self-critique, tests, or smoke runs without independent checkpoint evidence.
- A roadmap phase is declared done while its acceptance criteria have not been mapped to evidence.
- A real benchmark or product-quality criterion is required but unavailable.
- A citation/ledger/freshness issue may affect previously claimed evidence.
- A review prompt is found to be biased, leading, or missing obvious alternative hypotheses.
- Local dirty/untracked files affect the work but are not inventoried.

## Phase/slice verification protocol

### Slice verification

A slice is not done when code is written. A slice is done when the plan’s acceptance criteria are met and evidence is recorded.

Required slice evidence:

1. Active plan ID and objective.
2. Commit range or working-tree diff summary.
3. Files changed versus expected write set.
4. Acceptance criteria checklist.
5. Verification commands with pass/fail outcomes.
6. Focused regression test for changed behavior when code changes.
7. Full `pytest -q` before commit or before claiming done.
8. Schema validation for changed/generated artifacts.
9. Citation resolution for artifacts with citations.
10. Ledger/freshness/staleness checks when artifact lifecycle is affected.
11. Documentation updates when behavior, authority, status, or protocol changes.
12. Known gaps and whether they are acceptable for this slice.
13. Review/checkpoint requirement and disposition, if triggered.

### Phase verification

A phase is not done because a build-log entry says it passed. A phase is done only after a phase gate.

Create:

```text
.planning/phase-reviews/phase-<letter-or-number>-<slug>/
```

Required files:

- `PHASE-SPEC.md`: phase acceptance criteria copied from the accepted roadmap, plus any accepted amendments.
- `EVIDENCE.md`: mapping from each criterion to commands, artifacts, tests, commits, and reviewer findings.
- `CHECKPOINT-PROMPT.md`: prompt used for independent review.
- `CHECKPOINT-OUTPUT.md`: reviewer/checkpoint output.
- `DISPOSITION.md`: accepted/deferred/rejected reviewer findings.
- `PHASE-DECISION.md`: final decision: pass, pass-with-limitations, fail, or superseded.

A phase-completion claim requires:

- all hard acceptance criteria either passed or explicitly superseded by an accepted roadmap amendment;
- full automated test suite passing;
- relevant artifact gates passing;
- benchmark evidence where the roadmap requires product-quality proof;
- known limitations listed;
- independent checkpoint review dispositioned;
- `STATE.md` updated after the decision.

Phase labels should use conservative language:

- “Phase A mechanical foundation passed” is acceptable if that is what evidence proves.
- “CBM can map arbitrary codebases” is not acceptable unless real benchmark and runtime-agent evidence support it.
- “Standard mode implemented” is not acceptable if commands exist but runtime-agent behavior remains deterministic scaffolding.

### Evidence required before claiming phase or slice done

Claims should follow this grammar:

```text
Claim: <slice/phase/status>
Evidence:
- Commit(s):
- Tests:
- Artifact validations:
- Citation/ledger/freshness checks:
- Benchmark/product-quality evidence:
- Review/checkpoint:
- Known limitations:
Disposition:
```

The evidence must be in files, not just chat. The chat may summarize, but the repo should remain auditable after compaction or session loss.

## Review/checkpoint protocol

Reviewer/checkpoint agents should be launched at phase boundaries and high-risk changes. They should not run on every tiny code change; that would create noise and review fatigue. Use risk-based triggers.

### Mandatory reviewer triggers

Launch a checkpoint reviewer for:

- phase completion;
- architecture/product-boundary decisions;
- schema or contract changes;
- changes to `AGENTS.md`, `VISION.md`, `RUNTIME-CONSTITUTION.md`, `docs/roadmap.md`, `docs/architecture.md`, or `docs/contracts.md`;
- hook/platform adapter changes that affect enforcement or deployment assumptions;
- repeated failures or incidents at L2+;
- plan supersession caused by bad assumptions;
- claims of benchmark readiness, standard mode, deep mode, or mature runtime-agent behavior;
- review-prompt rewrites after bias is detected.

### Reviewer packet structure

Use:

```text
.planning/reviews/YYYY-MM-DD-<slug>/
```

Required files:

- `REVIEW-SPEC.md` or `REVIEW-PLAN.md`;
- `INPUTS.md` listing files, commits, artifacts, and known limitations supplied to the reviewer;
- `PROMPT.md` or `PROMPT-<TRACK>.md`;
- `OUTPUT.md` or `OUTPUT-<TRACK>.md`;
- `SYNTHESIS.md` when there are multiple tracks;
- `DISPOSITION.md`;
- optional `CHECKPOINT.md` for quick reviews.

Each reviewer output should be treated as evidence, not as an automatic command. `DISPOSITION.md` decides what to do.

### Prompt preflight

Before launching a reviewer, run a prompt preflight checklist:

- Does the prompt presume the diagnosis?
- Does it name at least two plausible alternative explanations?
- Does it separate observed facts from candidate interpretations?
- Does it ask the reviewer to critique the prompt framing?
- Does it avoid asking for confirmation of the current agent’s plan?
- Does it identify required inputs and known missing inputs?
- Does it specify output format and disposition path?

If the prompt fails preflight, archive it as draft or aborted rather than launching it.

### Disposition rules

Every recommendation must be dispositioned as:

- accept;
- accept with modification;
- defer;
- reject;
- needs user decision.

Each disposition entry must include:

- recommendation summary;
- source reviewer;
- rationale;
- required changes;
- target files;
- verification required;
- owner/mode;
- target plan or commit;
- completion status.

No implementation should proceed from a review output until accepted recommendations are dispositioned.

## Recommended `AGENTS.md` operating rules

`AGENTS.md` should be revised from “default proceed” to “default proceed inside a valid plan.” That distinction preserves autonomy without allowing silent drift.

### Before each slice

Future agents must:

1. Verify required authority docs exist:
   - `VISION.md`;
   - `RUNTIME-CONSTITUTION.md`, if runtime-agent behavior is relevant;
   - `.planning/STATE.md`;
   - `.planning/CURRENT-PLAN.md`;
   - `docs/roadmap.md`.
2. Read `STATE.md` and `CURRENT-PLAN.md`; do not infer current status from `docs/roadmap.md` alone.
3. Check whether `CURRENT-PLAN.md` is active, fresh, and authorizes the intended work.
4. Inventory dirty/untracked files and determine whether they are in scope.
5. Identify risk class and expected write set.
6. Confirm no open incidents or blocking reviews apply.
7. If the plan is absent/stale/completed/superseded, run the plan lifecycle protocol instead of implementing.
8. If an authority doc is missing, create or update an incident and pause implementation.

### During each slice

Future agents must:

1. Keep changes inside the expected write set unless the plan is amended.
2. Make atomic commits or at least preserve coherent diff chunks.
3. Log material decisions and alternatives in `BUILD-LOG.md`.
4. Run focused tests as soon as behavior changes.
5. Update docs when behavior, authority, or workflow changes.
6. Treat schema/contract/architecture changes as high risk.
7. Avoid mixing pre-existing dirty changes into slice commits without explicit inventory.
8. Preserve failed attempts when they affect governance, assumptions, or artifact validity.
9. Escalate instead of repeatedly patching around failures.

### After each slice

Future agents must:

1. Run the plan’s verification matrix.
2. Record verification outcomes in `BUILD-LOG.md` or `.planning/verification/`.
3. Update `STATE.md` for factual status changes.
4. Mark plan work items complete or explain why not.
5. Create review/checkpoint packets when thresholds require them.
6. Archive completed or superseded plans.
7. Draft the next plan rather than continuing beyond the current one.

### Stop/pause rules

`AGENTS.md` should require pause/review for the escalation thresholds listed above. It should also add:

- Do not claim phase completion from tests alone.
- Do not claim mapping quality without benchmark evidence.
- Do not treat deterministic artifacts as runtime-agent understanding.
- Do not let hooks substitute for explicit CBM validation.
- Do not modify authoritative docs to match implementation drift without review/disposition.
- Do not use uncommitted local-only context as governing context unless it is inventoried and committed or explicitly excluded.

### Recovery rule

When an agent discovers a mistake, it should write the mistake down before fixing it if the mistake affected plan scope, evidence, docs, or claims. The expected posture is blameless traceability, not defensiveness.

A good recovery entry says:

- what was wrong;
- how it was detected;
- what artifacts/claims were affected;
- whether rollback or forward fix was chosen;
- what verification now prevents recurrence.

## Documentation freshness protocol

Every governance document should carry a standard header:

```md
Status: active | draft | candidate | stale | superseded | archived | aborted
Authority: destination | runtime-constitution | roadmap | architecture | contract | state | plan | review | evidence
Last updated:
Applies to branch:
Applies to commit:
Supersedes:
Superseded by:
Owner/mode:
Review status:
```

### Authority labels

Use clear labels:

- `active`: current and authoritative for its scope.
- `candidate`: under review; not implementation authority.
- `stale`: known to be out of date; do not rely on it without `STATE.md`.
- `superseded`: replaced by another doc.
- `archived`: historical evidence.
- `aborted`: preserved as trace, not valid guidance.

### Supersession rules

1. A superseded document must link to its successor.
2. An active document must not point to missing authority files.
3. There should be exactly one active `CURRENT-PLAN.md`.
4. Candidate architecture should not be merged into `docs/architecture.md` until disposition accepts it.
5. Roadmap amendments should be explicit; do not silently rewrite history to fit implementation.
6. Review prompts found biased should be marked aborted and preserved.

### Freshness checks

Add a lightweight governance check, either as a script or test, that verifies:

- required authority files exist;
- active docs have status headers;
- superseded docs point to successors;
- no active doc is marked superseded elsewhere;
- `CURRENT-PLAN.md` is active or intentionally blocked;
- `STATE.md` references the active plan;
- review packets with outputs have `DISPOSITION.md`;
- root or prompt references to `SHARED-CONTEXT.md` use the actual path;
- roadmap phase status in `STATE.md` does not contradict phase-review decisions.

### README/file-map freshness

The README file map should be updated whenever governance docs become part of the project’s operating model. If `VISION.md`, `RUNTIME-CONSTITUTION.md`, `.planning/`, review packets, or governance templates are required for operation, they should appear in the file map with their authority roles.

## Concrete next steps

1. Resolve the authority-doc gap. Add or restore `VISION.md` and `RUNTIME-CONSTITUTION.md` at the referenced paths, or update every reference to their actual paths. Until this is fixed, no agent should claim alignment to the vision.

2. Move or clarify `SHARED-CONTEXT.md` references. Review prompts should say `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/SHARED-CONTEXT.md`, or the file should be duplicated/linked at the expected root path for reviewer convenience.

3. Create `docs/governance.md` containing the operating protocols in this review:
   - planning artifact model;
   - current-plan lifecycle;
   - stale-plan protocol;
   - incident protocol;
   - phase/slice verification;
   - review/checkpoint rules;
   - docs freshness rules.

4. Update `AGENTS.md` so autonomous agents proceed only inside an active, fresh plan. Add before/during/after slice rules and hard escalation thresholds.

5. Add templates under `.planning/templates/`:
   - `CURRENT-PLAN.template.md`;
   - `STATE.template.md`;
   - `BUILD-LOG-entry.template.md`;
   - `REVIEW-PACKET.template.md`;
   - `DISPOSITION.template.md`;
   - `INCIDENT.template.md`;
   - `PHASE-GATE.template.md`.

6. Add `.planning/archive/current-plans/`, `.planning/incidents/`, `.planning/phase-reviews/`, and `.planning/decisions/`. Archive the current plan only after this review packet is synthesized and dispositioned.

7. Add a governance validation check. Start simple: a test or script that validates required docs exist, status headers are present, the active plan is not superseded, review packets with outputs have dispositions, and active docs do not point to missing files.

8. Create a phase-status correction artifact. Under `.planning/phase-reviews/`, produce a retrospective “current phase reality” review that maps roadmap criteria to actual evidence and clearly distinguishes:
   - deterministic kernel implemented;
   - artifact gates implemented;
   - runtime-agent layer missing or unsettled;
   - real benchmark not yet established;
   - phase labels that should be retired, retained, or amended.

9. Require independent checkpoint review before further architecture or implementation work. This Track B output should be stored as `OUTPUT-WORKFLOW.md`, then synthesized with architecture and vision outputs. Only accepted recommendations should update docs or code.

10. Establish the benchmark gate before future maturity claims. Add or document a pinned small real-world repo fixture, ideally matching the MCP-server target mentioned in the docs, and define what CBM must demonstrate on it beyond schema-valid artifact generation.

11. Reconcile hook language across docs. Until architecture review is accepted, mark hook role as candidate/unsettled. Keep explicit CBM validation as the correctness source of truth.

12. Split durable decisions from live plan prose. Candidate architecture should live in review/decision artifacts until accepted. Once accepted, update `docs/architecture.md` and `docs/contracts.md`; until then, `STATE.md` should only say the decision is open and point to the review packet.

13. Add a “no defensive patching” rule to `AGENTS.md`. Repeated failures should generate incidents, assumptions should be corrected explicitly, and artifacts should be superseded rather than silently massaged.

14. After all review tracks are complete, write `SYNTHESIS.md` and `DISPOSITION.md`. Then update `.planning/STATE.md`, create the next active `CURRENT-PLAN.md`, and only then resume implementation.
