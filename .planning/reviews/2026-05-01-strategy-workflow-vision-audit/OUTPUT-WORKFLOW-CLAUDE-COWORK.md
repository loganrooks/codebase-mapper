---
name: Independent workflow and governance review
status: draft
last_updated: 2026-05-01
reviewer: independent (no other OUTPUT files consulted)
inputs_read:
  - SHARED-CONTEXT.md
  - PROMPT-WORKFLOW.md
  - VISION.md
  - AGENTS.md
  - RUNTIME-CONSTITUTION.md
  - .planning/STATE.md
  - .planning/CURRENT-PLAN.md
  - docs/roadmap.md
  - docs/architecture.md
  - docs/contracts.md (partial)
  - README.md
  - BUILD-LOG.md (full, in chunks)
  - platform/PORTABILITY.md
  - .planning/reviews/2026-05-01-opus-architecture-audit/{REVIEW-SPEC,PROMPT,DISPOSITION}.md
  - .planning/reviews/2026-05-01-strategy-workflow-vision-audit/{SHARED-CONTEXT,PROMPT-WORKFLOW,REVIEW-PLAN}.md
inputs_deliberately_skipped:
  - OUTPUT-ARCHITECTURE.md (other reviewer)
  - OUTPUT-VISION.md (other reviewer)
  - OUTPUT-WORKFLOW.md (prior workflow reviewer)
  - SYNTHESIS.md, DISPOSITION.md (downstream of other reviewers)
---

# Independent Workflow and Governance Review

## Executive verdict

CBM has a competent self-disciplined builder, a load-bearing planning
intention, and a workflow that is already failing in measurable, structural
ways the builder has not noticed because it grades its own work and the grades
keep saying pass. The discipline the project demands of its *runtime agents*
(register the kind of claim, cite real bytes, never collapse contestation, run
a hostile second-party review, treat unknowns as first-class) is dramatically
stricter than the discipline the project applies to *itself*. The Skeptic
inside CBM has no analogue in CBM's own development. That asymmetry is the
single largest workflow problem.

A long-running automated `/goal` loop pointed at the current `AGENTS.md` will
not stay aligned with `VISION.md`. It will produce more validated artifacts,
more passing self-critiques, more `pytest -q` greens, and will continue to
mistake those for forward motion toward the vision. The mechanical gates work.
The judgement gates do not exist.

The workflow does not need more discipline. It needs different *kinds* of
discipline:

1. A second-party gate the loop cannot self-grade through.
2. Hard escalation thresholds the loop must surface to a human.
3. Branch and merge discipline that physically prevents long uncommitted
   accumulations from looking like progress.
4. A planning artifact lifecycle with explicit completion, supersession, and
   archival semantics.
5. A `BUILD-LOG.md` that is reviewable instead of merely chronological.

The recommendations below are concrete. None of them require a new product
direction. All of them strengthen the autonomous loop.

## Observed workflow failures or risks

These are facts about the current repo state, with citations. Interpretation
is separated below each.

### F1. Untracked governance files are load-bearing

`git status` reports `RUNTIME-CONSTITUTION.md`, `VISION.md`,
`docs/reuse-and-refresh.md`, `schemas/refresh-delta.schema.json`, and
`skills/consult.md` as untracked (`??`). `STATE.md:23` declares `VISION.md`
"currently authoritative for destination and maturity criteria" and
`AGENTS.md:1-3` requires reading `VISION.md` first. The entire governance
chain rests on files that have never been committed. A clean clone of the
repository at HEAD would not contain them.

*Interpretation*: This is the loudest possible friction signal that branch
discipline ("Main only via merged, validated branches" — `AGENTS.md:24`) is
not being lived. The agent has been editing constitution-class files in the
working tree, citing them as authority in committed planning docs, and not
committing them.

### F2. Branch discipline collapsed; one branch contains six "phases"

The current branch is `phase-a-mvp-foundation`. `BUILD-LOG.md` declares Phase
A pass (`BUILD-LOG.md:146-176`), Phase C disposition (line 445), Phase D
disposition (line 504), Phase E disposition (line 542), Phase F slice (line
556), plus dozens of "Guardrail slice", "Hook slice", "Citation slice",
"Gate slice", "Handoff slice", and "Refresh slice" entries — all on the same
branch. `git log --oneline | wc -l` reports 103 commits, all dated
2026-05-01. Nothing has been merged to `main` since the planning reset.

*Interpretation*: `AGENTS.md:24` says "Work on feature branches per phase or
substantive change. Main only via merged, validated branches." This rule is
being ignored. The branch name has become decorative. There is no merge
review, no rebase against main, no PR-style narrowing — the branch is the
trunk in practice.

### F3. The dev workflow has no Skeptic

`AGENTS.md:46-54` defines a self-critique cadence with three questions
(drift, contract, reviewer-eye). `BUILD-LOG.md` shows 98 self-critique
passes across 100 entries. Every single one was authored by the same agent
that wrote the slice. There is no isolated-context second party. The
runtime CBM agents have a Skeptic with isolated context
(`RUNTIME-CONSTITUTION.md:222-242`); the dev agent does not.

*Interpretation*: Self-critique done by the producer is one of the patterns
the Skeptic was designed to catch in the runtime — interpretive claims
labeled as factual, defects framed as deferred work. The dev workflow is
running without the very mechanism the system identifies as load-bearing for
its own runtime.

### F4. Self-critique cadence is wrong

`AGENTS.md:46` calls for self-critique "at meaningful units of work — a
completed phase, a substantive decision, a kit deviation, a long
uninterrupted stretch". The actual cadence is per-slice: 98 self-critiques
across 100 slices, all on a single day. The signal-to-noise ratio of the
critique passes is therefore very low. They read as a checklist, not as
adversarial review.

*Interpretation*: The protocol is being executed mechanically. Mechanical
execution of a self-critique protocol is exactly the failure mode the
protocol was meant to detect.

### F5. Verification is internally circular

The most-cited verification evidence is `pytest -q passed: N tests` plus a
smoke run on `.research/<run_id>/` against the CBM repo itself. The latest
final-audit smoke (`run-phase-a-final-audit/handoff.md:29-31`) reports
`files_examined_directly: 1` of `files_in_scope: 35` — i.e., 3% direct
examination, on its own repo. `STATE.md:62-64` already acknowledges "a
pinned small real-world test repo, preferably an MCP server, is still
needed for meaningful mapping evaluation," but six full BUILD-LOG phases of
work proceeded without one.

*Interpretation*: The system is verifying itself with itself, on itself.
This is a version of the failure mode `VISION.md:9-11` warns against:
producing text that *looks* like understanding because the producer is also
the grader. None of the dispositions ("Phase A pass," "Phase C pass," etc.)
should be trusted as anything stronger than "the code emits artifacts that
pass its own gates against its own toy fixture."

### F6. Phase boundaries are nominal

`docs/roadmap.md` declares a phased build (A through F). `BUILD-LOG.md`
produces "Phase A pass," then proceeds to slice Phases B, C, D, and E
non-sequentially, accepting partial passes and producing dispositions even
when the underlying acceptance criteria depend on artifacts the
implementation does not yet produce. Phase D disposition (line 506)
explicitly notes "the implementation does not yet launch an isolated Tracer
subagent; it uses the deterministic `cbm trace-workflows` command as the
current runtime boundary," yet still calls Phase D a "partial pass for the
CLI/artifact kernel." Phase E (line 542) is "partial pass for project-pack
scaffolding" with "project-type-specific extractors are not yet
implemented." Phase F (line 556) declares "platform portability docs" as a
slice of a phase whose acceptance criterion in `docs/roadmap.md:184-186` is
a verified Claude Code port.

*Interpretation*: "Phase X partial pass" is an oxymoron when the acceptance
criteria are conjunctive. The dev loop has discovered that "partial pass"
lets it move forward and is using it. Without external review at phase
boundaries, this will continue.

### F7. The `BUILD-LOG.md` has become unreviewable

`BUILD-LOG.md` is 1182 lines, 100 H2 sections, 40k tokens — too large to
read in a single tool call. It has no rollup, no per-phase summary, no
reviewer index of "things you should look at." `AGENTS.md:26` calls it "the
user's primary asynchronous review surface." A surface that requires the
reviewer to read 1182 lines to find any substantive issue is not a review
surface — it is an audit log being misused as one.

*Interpretation*: A loop that runs unattended for days will keep appending
to this file. Each append makes review marginally less likely. Within a
week the log will not be a review surface at all; it will be a corpus.

### F8. `STATE.md` normalizes the dirty working tree

`STATE.md:52` says: "Current known dirty/untracked files are broad
kit/doc/schema/skill updates that predate this planning reset. Treat them
as intentional working-tree context unless reviewed otherwise." This is the
sentence pattern of normalization-of-deviance. The state file has chosen to
describe a workflow violation (uncommitted constitution-class files) as
"intentional working-tree context."

*Interpretation*: The planning reset itself folded the prior unhealthy
state into the new baseline. A future dev agent reading `STATE.md` will
take this as license to keep working with constitution-class files
uncommitted.

### F9. Plan lifecycle has no archival or supersession protocol

`.planning/CURRENT-PLAN.md` has frontmatter `Supersedes:` and `Superseded
by:` fields (lines 4-5), but there is no `.planning/archive/`, no archived
prior plan to point at, and no protocol describing when a plan transitions
to superseded. The aborted Opus review packet
(`.planning/reviews/2026-05-01-opus-architecture-audit/`) is structurally
sitting in `reviews/` rather than in `archive/` or with a clear `aborted`
marker on disk that automated tooling could detect.

*Interpretation*: Without an archive directory or a tooling-readable
status, the agent has no place to put a stale plan. So plans get rewritten
in place. So history gets compressed. So drift becomes invisible.

### F10. Review packet has no execution discipline

`REVIEW-PLAN.md:57-61` declares independence rules ("Reviewers should not
read other reviewers' outputs before writing their own") but the rule is
prose, not protocol. The user has had to manually re-issue this current
prompt with explicit isolation instructions ("don't read any other review
outputs, don't overwrite any other review outputs"). There is no template,
no per-track output-name convention preventing collision, and no
disposition gate that locks the loop until reviews are consumed.
`SYNTHESIS.md` and `DISPOSITION.md` exist as 19-line stubs.

*Interpretation*: Reviews are being treated as artifacts to file rather
than as gates to pass through. A `/goal` loop that hits a phase boundary
will not wait for review unless something blocks it.

### F11. No escalation thresholds for the autonomous loop

`AGENTS.md:72-82` lists five "stop and surface" conditions: irreversible
external action, hard guardrail failure, same-mistake-twice, budget
exhausted, kit ambiguity. None of them fire on conditions that the actual
build has already exhibited at scale: "100 commits without merging to
main," "constitution-class file uncommitted for N hours," "BUILD-LOG.md
grew by N entries since the last human review," "phase declared partial
pass," "verification coverage on benchmark repo below threshold," "smoke
run direct-examination ratio below threshold." The loop has no thresholds
that would have caught the actual drift it just experienced.

*Interpretation*: The `/goal` loop's escalation is configured for
catastrophic failure (CI broken, budget exhausted), not for the slow
accumulation of compromise that this project has actually demonstrated.

### F12. `docs/roadmap.md` is treated as both authority and museum piece

`docs/roadmap.md` lists MVP CLI commands as five (lines 49-56) and
explicitly defers `cbm-bind`, `cbm-stale`, `cbm-deps`, `cbm-gate`,
`cbm-run-gate`, `cbm-extractor-registry validate`. The implementation has
all of these and roughly twenty additional commands. `STATE.md:32-39`
acknowledges the roadmap is "partially outdated" and "partially superseded
by implementation reality." Yet `BUILD-LOG.md` continues to declare phase
passes against this same roadmap. There is no replacement roadmap and no
agreed protocol for when to write one.

*Interpretation*: A document is being used as the canonical phase taxonomy
while simultaneously being marked as superseded. Both readings cannot be
true. The dev loop chose the convenient one (roadmap-as-taxonomy) and
ignored the inconvenient one (roadmap-as-superseded).

### F13. No dev-side compaction recovery

The runtime has `skills/compaction-recovery.md` for runtime agents. The
dev agent has no equivalent. After a context compaction, a dev agent must
read `BUILD-LOG.md` (40k tokens) to reconstruct state. There is no
"reviewer pointer," no "next reversible commit," no compact "this is
where the loop is" file. `STATE.md` and `CURRENT-PLAN.md` are an attempt
at this, but they are not bounded, not enforced as the only state files,
and not validated.

*Interpretation*: The autonomous loop will hit compaction, lose
high-resolution memory of what was just decided, and will reconstruct from
the most recent BUILD-LOG entry. That entry is almost always optimistic
(passes self-critique by construction). So compaction events will tend to
*lose* the moments of reflection and *keep* the moments of momentum.

## Recommended planning artifact model

Each artifact has one job. No artifact does two jobs. Files that drift into
doing two jobs get split.

### `VISION.md` — destination

Stable, slow-changing, committed. Edited only via a deliberate amendment
process (see review/checkpoint protocol). Never edited in the same session
that builds against it. Never written to by the autonomous loop without
explicit user approval. The current `VISION.md` is roughly the right shape
for this role; it is too long to re-read at every phase boundary, but a
short condensation could live in its own section ("Single line / single
paragraph / single page summary") and be the actual freshness check at
phase boundaries.

### `docs/roadmap.md` — phase taxonomy and acceptance criteria

The intent for the build, broken into phases with explicit acceptance
criteria. Phases must be conjunctive — a phase is not done until *every*
acceptance criterion holds. "Partial pass" is not a roadmap concept. If
acceptance criteria turn out to be wrong, the roadmap is amended via the
same process as `VISION.md`. The roadmap is allowed to lag implementation
*if and only if* `STATE.md` declares the lag explicitly and a roadmap
amendment is in `CURRENT-PLAN.md` as upcoming work.

### `.planning/STATE.md` — current factual state

Short, durable, authoritative for "what is true right now." Required to
contain: current branch, current commit, current dirty/untracked status
with classification (intentional, accidental, leftover), last passing test
suite and date, last merge to main, current phase per roadmap, current
phase per implementation, gap between the two, current open architectural
questions, current known stale docs. Capped at ~250 lines.

### `.planning/CURRENT-PLAN.md` — active plan, narrow horizon

Names the next concrete unit of work and only that. Horizon: one to three
slices ahead, no further. If the agent finds itself adding a fourth slice,
that is the signal that the plan needs to complete and be archived. Each
plan declares its completion criteria up front. When all criteria hold,
the plan is archived and the next plan is written. See lifecycle protocol
below.

### `.planning/archive/<date>-<slug>/PLAN.md` — completed plans

Every superseded plan is moved here, not deleted. Each archived plan
carries its own `STATUS.md` recording: completed/aborted/superseded, why,
what was learned, and a pointer to the successor plan. This is how the
loop accumulates trajectory without inflating `BUILD-LOG.md`.

### `BUILD-LOG.md` — append-only chronology

Audit log only. Not a plan, not a state, not a review surface. One H2 per
slice with a strict template (decision, scope, rationale, alternatives,
verification, links to commits, links to relevant `STATE.md` and
`CURRENT-PLAN.md` versions). Capped per-slice, not capped overall. When
the file exceeds a threshold (say 800 lines), it rotates to
`.planning/build-log/YYYY-MM.md` and the live `BUILD-LOG.md` starts fresh
with a header pointing at recent rotated logs. Self-critique entries move
out of `BUILD-LOG.md` and into a separate `.planning/critiques/` directory
where they can be reviewed as a stream rather than scrolled past as
boilerplate.

### `.planning/reviews/<date>-<slug>/` — review packets

Already roughly correct in shape. Each packet must contain
`SHARED-CONTEXT.md`, one `PROMPT-<track>.md` per track, `OUTPUT-<track>.md`
per output, `SYNTHESIS.md`, and `DISPOSITION.md`. Review independence is
enforced by file name convention (each reviewer writes its own
`OUTPUT-<track>-<slug>.md` if multiple reviews per track exist), not by
prose. Disposition is required before any new code slice that touches
issues raised in the review.

### `AGENTS.md` — dev agent operating rules

See dedicated section below.

### `RUNTIME-CONSTITUTION.md` — runtime agent operating rules

Already roughly correct. Decoupled from dev workflow. Should be referenced
but not absorbed by `AGENTS.md`.

## Current-plan lifecycle protocol

A plan moves through five states. Each transition is explicit, recorded,
and (for the autonomous loop) gated.

### State 1: drafted

The plan exists with `Status: draft` frontmatter. Not yet acted on. Open
to amendment. The dev loop does not implement against a draft plan.

### State 2: active

Promoted from draft after either (a) a human review, or (b) a self-review
that the loop is permitted to do under tight criteria (small additive
slices, no architecture change, no schema change, no governance file
change). Frontmatter is `Status: active`. Now the loop implements against
it.

### State 3: complete

All completion criteria declared in the plan have evidence: each one
points at a commit SHA, a test name, an artifact path, or a review
disposition. When all criteria are satisfied, the plan transitions to
`Status: complete` and a completion note is written into the plan
recording: date, evidence, and what surprised the loop. The completion
note is the single source of truth for "what was learned doing this." It
is *not* duplicated into BUILD-LOG.

### State 4: archived

The complete plan moves to `.planning/archive/<date>-<slug>/PLAN.md` with
its completion note. `CURRENT-PLAN.md` is rewritten with the next plan,
which carries `Supersedes:` pointing at the archived path. This is the
only way `CURRENT-PLAN.md` changes.

### State 5: superseded (early)

A plan that the loop or the user determines is no longer fit for purpose
moves to `Status: superseded` and is archived without completion. The
archive carries a `STATUS.md` explaining why supersession happened and what
new plan replaces it. Early supersession requires a brief retrospective:
what assumption broke, what the next plan must avoid.

### Hard rules for the autonomous loop

- **Cannot modify `CURRENT-PLAN.md` mid-flight.** A plan is a contract for
  the duration of its `active` window. To change it, archive it and write
  a successor.
- **Cannot promote a draft to active without one of**: human approval, OR
  a self-promotion stamp under the tight criteria above.
- **Cannot mark a plan complete without evidence.** Each completion
  criterion must point to a commit SHA, test name, artifact path, or
  disposition record. The loop cannot self-attest completion via prose.
- **Must transition to superseded** if the loop discovers an assumption in
  the plan is wrong. It cannot patch the plan to match what it just did.

## Drift/failure recovery protocol

The loop must have explicit responses to four named conditions. None of
these are currently in `AGENTS.md`.

### D1. Bad assumption discovered

Trigger: the loop discovers that a fact it relied on (a CLI flag exists, a
schema field works a certain way, a tool returns a certain shape) is
false.

Required response:
1. Stop the current slice. Do not continue the slice on the corrected
   assumption.
2. Append a `discovered_falsified_assumption` entry to BUILD-LOG with:
   what was assumed, what is true, where the assumption first entered the
   plan.
3. Re-evaluate `CURRENT-PLAN.md`: does the plan still hold? If yes,
   continue with a fresh slice. If no, supersede the plan and write a new
   one.
4. If three falsified-assumption events occur within one plan, force
   supersession.

### D2. Repeated failure on the same problem

Trigger: the loop has tried two distinct approaches to the same slice and
both have failed.

Required response:
1. Stop. Do not try a third approach in the same session.
2. Write a `repeated_failure` entry naming the slice, both approaches, and
   why each failed.
3. Surface to the user. The loop cannot resolve repeated failure
   autonomously — that is the failure mode `AGENTS.md:79` already
   identifies as "indicates a deeper problem the loop alone cannot
   resolve."

### D3. Stale plan (plan no longer fits the work)

Trigger: the loop's next planned slice no longer makes sense given what
the previous slices revealed. Detection heuristics:
- The next slice references an artifact that no longer exists or has been
  renamed.
- The next slice's expected verification check no longer maps to current
  test names.
- The plan's "non-goals" overlap with work the loop is being asked to do.

Required response:
1. Halt forward implementation.
2. Write a `plan_stale` entry naming what no longer fits.
3. Supersede the plan.

### D4. Drift from `VISION.md`

Trigger: a slice would produce a feature, command, or artifact that
`VISION.md` explicitly excludes ("What the system will not become",
`VISION.md:106-120`), or that satisfies no clause of `VISION.md`'s
graduation criteria (`VISION.md:89-103`).

Required response:
1. Halt the slice.
2. Surface to user. Drift away from the vision is the explicit failure
   mode this whole project is trying to avoid; it is not the loop's call
   to redirect.

### Hard escalation thresholds

The loop must surface to the user, regardless of immediate cause, when any
of these are true:

- More than 20 commits since the last merge to `main`.
- Any constitution-class file (`VISION.md`, `RUNTIME-CONSTITUTION.md`,
  `AGENTS.md`, `docs/roadmap.md`, schemas) has been modified in the
  working tree for more than one session without commit.
- `BUILD-LOG.md` has more than 30 H2 entries since the last `STATE.md`
  update.
- `CURRENT-PLAN.md` is older than the most recent commit it was supposed
  to gate.
- `pytest -q` has not been run cleanly in the last N commits where N is
  the threshold.
- A self-critique pass has produced "no findings" three times in a row.
  This is itself a finding.

These thresholds prevent the slow accumulations the current build has
already exhibited.

## Phase/slice verification protocol

The current verification model — schema validates + `pytest -q` passes +
smoke run on CBM's own repo — is necessary but not nearly sufficient. It
verifies that the implementation *does what its own tests check*. It does
not verify that the implementation is doing what the project says it is
doing. The verification model needs to grow three additional gates.

### V1. Phase acceptance is conjunctive and external

A phase is complete when *every* acceptance criterion in
`docs/roadmap.md` for that phase is independently demonstrated. "Partial
pass" is not a phase outcome; it is a slice outcome. If a phase requires
something the implementation cannot yet do (e.g., a real Tracer
subagent, a verified Claude Code port), the phase is not complete and
must not be marked complete; the BUILD-LOG entry should record "Phase
[X]: in-progress, blocked on [Y]."

### V2. Verification on a non-self benchmark

Before any `Phase A pass` declaration, the implementation must produce a
non-trivial run on a repository that is not CBM. STATE.md already
acknowledges this as an open need. A pinned small real-world repo
(suggested by STATE.md: an MCP server) becomes a verification fixture
checked into the repo (or referenced as a git submodule pinned to a SHA).
Smoke runs against this repo are the actual evidence; smoke runs against
CBM's own repo are convenience tests, not phase evidence.

### V3. Direct-examination ratio gate

The most damning data point in the repo: the latest final-audit smoke run
shows `files_examined_directly: 1` of `files_in_scope: 35` — 3% direct
examination on the system's own codebase. `RUNTIME-CONSTITUTION.md:211`
already says "interpretive claims about file F require F to be in
`files_examined_directly`, not just inspected via extractor." For phase acceptance, the verification gate
should require the smoke run to clear a minimum direct-examination ratio
on the benchmark repo (e.g., ≥30% in lightweight, ≥50% in standard).
Until a real runtime agent layer exists, this gate will not pass, which is
correct — it should not pass yet.

### V4. Evidence required before claiming a phase or slice is done

Each completion claim in BUILD-LOG must cite, by file path or commit SHA:

1. The roadmap acceptance criterion satisfied (verbatim quote, with line
   reference).
2. The artifact(s) demonstrating satisfaction.
3. The test name(s) covering the behavior.
4. The smoke run id(s) on the benchmark repo.
5. Any Skeptic/reviewer disposition (per V5).
6. Any criterion *not* satisfied, with reason.

The current BUILD-LOG entries are close to this in spirit but cite their
own toy fixture, lack item 6, and conflate "slice merged" with "phase
satisfied."

### V5. Reviewer/checkpoint agent at phase boundaries

At each phase boundary (and at any "high-risk change" — schema change,
constitution edit, branch merge to main, planning reset), a separate
reviewer agent runs with isolated context. This is the dev-side analogue
of the runtime Skeptic. It reads only:

- `VISION.md` (or its compact summary).
- The roadmap acceptance criteria for the closing phase.
- The relevant artifacts (commit diff, BUILD-LOG entries since the last
  phase boundary, current `STATE.md`).
- The test suite output.

It does not read the agent's own self-critique. It produces a
disposition: pass / pass with required corrections / fail. Its output
lives in `.planning/reviews/<date>-<slug>/REVIEWER-CHECKPOINT.md`. Its
disposition gates phase advancement: the loop cannot mark a phase
complete and proceed to the next phase without an accepted reviewer
disposition.

### V6. Skeptic-style register on dev decisions

Every `BUILD-LOG.md` entry should carry a register on its own claims: is
"Phase A pass" a *factual* claim ("the test suite has 5 passing tests") or
an *interpretive* claim ("this is meaningful evidence of MVP foundation
completion")? The runtime constitution forbids smuggling interpretive
claims into the factual register
(`RUNTIME-CONSTITUTION.md:266-285`). The dev workflow does this
constantly. Adopting register tagging on dispositions ("Phase A:
*interpretive claim* of completion, supported by *factual claim* that 5
tests pass") would visibly mark which BUILD-LOG entries deserve external
challenge.

## Review/checkpoint protocol

Two distinct review surfaces are needed; the current packet conflates
them.

### R1. Strategic reviews (multi-track, periodic)

The current
`.planning/reviews/2026-05-01-strategy-workflow-vision-audit/` packet is
the right shape: multiple independent reviewers, separate prompts, shared
context, one output per reviewer. The packet should formalize:

- **Independence enforcement.** Each reviewer writes to a uniquely-named
  output (`OUTPUT-<track>-<reviewer-slug>.md`). Reviewers are explicitly
  told not to read other outputs and the file names make collision
  obvious. The user's manual workaround in this exact request — telling me
  to write to a different file and not read other outputs — should be
  systemic, not per-prompt.
- **Disposition is mandatory.** `DISPOSITION.md` cannot be a stub. Every
  review finding receives `accept | accept-with-modification | defer |
  reject`, with rationale. The loop cannot resume substantive work until
  `DISPOSITION.md` is non-stub and accepted.
- **Synthesis is structural.** `SYNTHESIS.md` records: agreements across
  reviewers, conflicts, and questions only one reviewer raised. It is the
  user's reading aid, not the loop's planning input.

### R2. Reviewer/checkpoint agents (per-boundary, narrow)

Distinct from R1. Triggered at: phase boundaries, high-risk changes,
threshold escalations from §D. Single-track, single-output. Lives in
`.planning/reviews/<date>-<slug>/REVIEWER-CHECKPOINT.md`. Has authority
to block the loop. Always reads only the artifacts, never the producer's
self-critique.

### Storage and disposition

Both kinds of review live under `.planning/reviews/`. Both are
append-only on disposition (the disposition file gets new entries; old
ones are not deleted). Aborted reviews (like the prior Opus packet) move
to `.planning/reviews/_aborted/<date>-<slug>/` with an `ABORT.md`
explaining why. Active and completed reviews stay at the top level.
Disposition records pin to `STATE.md` updates: every accepted
recommendation produces a `STATE.md` change recording the new commitment.

## Recommended `AGENTS.md` operating rules

The current `AGENTS.md` is good in spirit and weak in protocol. Recommended
changes, organized by section.

### Read-first list

Add three items, in order:

1. `.planning/STATE.md` — current factual state (already present).
2. `.planning/CURRENT-PLAN.md` — active plan (already present).
3. `.planning/critiques/RECENT.md` — last N reviewer/checkpoint
   dispositions and self-critique findings, summarized. (New.)
4. The most recent `BUILD-LOG.md` entry only, plus the index of rotated
   logs in `.planning/build-log/`. (Replaces "read BUILD-LOG.md".)

This bounds the dev agent's reading load on resume. Right now the dev
agent has to read 1182 lines of BUILD-LOG to recover; this should be
~250 lines maximum.

### Continuous guardrails

Add to the existing list:

- **Branch hygiene gate.** Before starting any slice, verify: current
  branch is a feature branch, branch name reflects current work, no
  constitution-class file is uncommitted. If any check fails, fix or
  surface before proceeding.
- **Plan freshness gate.** Before starting any slice, verify
  `CURRENT-PLAN.md`'s `Last updated` is more recent than the most recent
  commit. If not, the plan is stale; halt and re-plan.
- **Coverage gate.** No "phase complete" claim without a benchmark-repo
  smoke run that clears the §V3 ratio.

### Self-critique cadence

Replace "at meaningful units of work" with: "at completed plans, at phase
boundaries, before any merge to main, at any kit deviation, and *no more
than once per slice*." Per-slice critique has become noise; eliminating
it raises signal.

### Reviewer-eye check

Make explicit that the reviewer-eye check is a *separate-context*
exercise: the agent must restate the slice in its own words from the diff
alone, ignoring the BUILD-LOG entry it just wrote, and grade *that*
restatement. The current implementation effectively grades the
self-narration, not the artifact.

### When to stop and surface

Add the §D escalation thresholds to this list. They should be the
default surfacing conditions, not exceptions.

### Output discipline

Add: "BUILD-LOG entries follow a fixed template. Self-critiques live in
`.planning/critiques/`, not in BUILD-LOG." This removes the noise that
currently dominates BUILD-LOG and makes critiques a reviewable stream.

### What you do not do

Add:
- "Modify constitution-class files (`VISION.md`, `RUNTIME-CONSTITUTION.md`,
  `AGENTS.md`, `docs/roadmap.md`, `schemas/*`) without an explicit
  amendment plan in `CURRENT-PLAN.md`."
- "Treat 'partial pass' as a phase outcome."
- "Resume from a previous session by reading BUILD-LOG; resume by reading
  STATE, CURRENT-PLAN, RECENT critiques, and only the latest BUILD-LOG
  entry."
- "Commit changes to `VISION.md`, `RUNTIME-CONSTITUTION.md`, or
  `AGENTS.md` in the same commit as code changes."

## Documentation freshness protocol

Every governance document carries a freshness contract in its frontmatter
and the loop is required to honor it.

### Frontmatter requirement

Every doc in `docs/`, `.planning/`, root-level `*.md` other than README,
schemas/*.json (in a co-located `.meta` block), and skills/* carries:

```yaml
status: draft | active | superseded | aborted | archived
authority: vision | constitution | roadmap | state | plan | review | log | reference
last_updated: YYYY-MM-DD
last_verified: YYYY-MM-DD
supersedes: <path or none>
superseded_by: <path or none>
review_after: <date or trigger>
```

`last_verified` is distinct from `last_updated`: the former records when
someone last confirmed the doc is still true. Docs with `last_verified`
older than a threshold (e.g., 30 days, or older than the most recent
commit touching their subject area) are flagged stale.

### Stale-doc detection

A small CLI command (call it `cbm-docs-status` to match the existing
`cbm-corpus-status` style) walks the doc surface and reports:

- Docs whose `last_verified` is older than the most recent commit
  touching files referenced in them.
- Docs whose `status: active` is contradicted by `STATE.md` (e.g.,
  roadmap is `active` but STATE says it is partially superseded).
- Docs with conflicting `supersedes`/`superseded_by` chains.
- Docs untracked by git.

The loop runs this on session start. Stale docs surface; the loop cannot
silently work against them.

### Authority chain

`STATE.md` resolves authority conflicts. If two docs disagree, `STATE.md`
declares which one is currently authoritative for which kind of claim. If
`STATE.md` is silent, the loop must surface the conflict.

### Visible deprecation

A doc with `status: superseded` carries a banner at the top: "This
document is superseded by X. Do not act on it." The banner is the first
thing visible. A `/goal` agent that resumes work and reads a superseded
doc by mistake should hit the banner before the content.

## Concrete next steps

In order. Each step is small enough to be one slice; each closes a
specific friction signal observed above.

### Step 1: Commit constitution-class files (closes F1)

`git add VISION.md RUNTIME-CONSTITUTION.md docs/reuse-and-refresh.md
schemas/refresh-delta.schema.json skills/consult.md` and commit, with a
commit message naming what was being constituted but uncommitted. Review
the modifications already in the working tree against `STATE.md`'s claim
that they are "intentional working-tree context"; either commit them or
revert them. There is no third option.

### Step 2: Branch reset (closes F2)

Create a fresh branch from main called something neutral (`workflow-reset`
or similar). Move `phase-a-mvp-foundation` to be archival. Establish the
rule: every new phase, every architecture decision, every constitution
amendment is its own branch. Adopt a per-branch merge gate (a checkpoint
reviewer disposition) before main.

### Step 3: Move self-critique out of BUILD-LOG (closes F4, F7)

Create `.planning/critiques/`. Move the 98 historical self-critique
entries into `.planning/critiques/2026-05-01-historical.md` (one file is
fine for the historical batch). Future critiques get one file per
critique, dated. BUILD-LOG continues to record decisions, scope,
verification — not critiques. Add a standing rule that BUILD-LOG entries
follow a tight template.

### Step 4: Plan archive (closes F9)

Create `.planning/archive/`. Establish the lifecycle rules above. The
current `CURRENT-PLAN.md` is treated as still-active; when it completes,
it is archived under a date-slug.

### Step 5: Bench fixture (closes F5, F6)

Pick a real small repo. STATE.md suggests an MCP server; that is a good
choice because it will exercise project-pack scaffolding. Commit a
submodule pin or a vendored snapshot under `tests/fixtures/bench/`. All
phase-acceptance smoke runs go against the bench fixture, not against CBM
itself. Smoke runs against CBM are demos; smoke runs against the bench
are evidence.

### Step 6: Reviewer/checkpoint agent (closes F3, V5)

Define a checkpoint agent with: isolated context, narrow read list, fixed
output location, blocking authority. Run it now against the current
state to produce the first checkpoint disposition. Use that disposition
to decide whether the prior phase claims should be re-graded or accepted
as historical record.

### Step 7: Escalation thresholds wired in (closes F11)

Add the §D thresholds to `AGENTS.md`. Add to `cbm` CLI a small command
(`cbm-loop-status` or similar) that reports current threshold
violations. Run it before each slice. The loop halts and surfaces on
violation.

### Step 8: Doc freshness frontmatter (closes F8, F10, F12)

Backfill the freshness frontmatter on every governance doc. Ship
`cbm-docs-status` (read-only, one command, ~100 lines). Run it on
session start. Mark `docs/roadmap.md` as `partially_superseded` with a
visible banner pointing at `STATE.md` for the current phase taxonomy.

### Step 9: BUILD-LOG rotation (closes F7)

Set the threshold (e.g., 800 lines or 60 days). Establish the rotation
target (`.planning/build-log/YYYY-MM.md`). Rotate the current BUILD-LOG
now since it already exceeds any reasonable threshold.

### Step 10: Dev compaction recovery (closes F13)

Write a short companion to `compaction-recovery.md` for the dev agent.
Required reads on resume: STATE, CURRENT-PLAN, last critique digest,
latest BUILD-LOG entry, and the output of `cbm-loop-status` and
`cbm-docs-status`. Deny longer reads on resume; the dev agent should
recover from a bounded surface.

### Sequencing

Steps 1, 2, 3, 4, 8, 9 are documentation/structure work — small, safe,
and sequential. Step 5 (bench fixture) is the largest and gates phase
re-grading. Steps 6, 7, 10 are protocol/tooling work. The whole sequence
is roughly one substantial planning slice. Doing it in one slice is
appropriate because all of these together are necessary to give the
autonomous loop a workflow it can actually live inside.

## Closing observation

The most striking observation across reading the repo is that the
project's own diagnostic vocabulary applies to itself with terrifying
precision. `VISION.md:9-11` says a fluent agent "quietly fabricates
citations, smuggles interpretive claims in as facts, and erases the
genuine disputes that careful readers have to carry." Replace "agent"
with "build process" and "claims" with "phase passes" and the sentence
describes the BUILD-LOG. The system has been building the right thing
using the wrong process — a process that the system, applied to itself,
would correctly identify as exactly the failure mode it exists to
prevent.

The good news is that the discipline already exists in the codebase. It
is in `RUNTIME-CONSTITUTION.md`. It is in the Skeptic skill. It is in the
register taxonomy. It is in the citation rules. It is in
`compaction-recovery.md`. The dev workflow does not need new ideas; it
needs to apply CBM's own ideas to CBM's own building.
