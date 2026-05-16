# OUTPUT — Track B: Development Workflow and Governance

Status: draft review output
Last updated: 2026-05-01
Reviewer: independent process/governance reviewer (Claude Opus, isolated context)
Input: `SHARED-CONTEXT.md`, repo at `a086749`

A note on framing before the verdict. The prompt asks me to assume nothing about the planning reset's adequacy. I will not. The reset is the most encouraging signal in the repo — but on its own it does not address why drift went undetected for 100+ commits, and it imports two assumptions worth flagging: (a) that the existing `BUILD-LOG.md`/`STATE.md`/`CURRENT-PLAN.md` triple is the right artifact set, and (b) that an automated `/goal` loop running against `VISION.md` is a viable target for this codebase at all. (a) is mostly defensible, with edits below. (b) is genuinely contested and is taken up at the end.

## 1. Executive verdict

**The current operating system is unsafe for autonomous `/goal` execution and should be paused until a small set of governance changes lands.** The build has produced a functioning deterministic kernel with extensive validation gates; that work is real. But the workflow that produced it is a single-author, single-day, self-validating loop in which every gate that could detect drift is one the producer also operates. Roadmap phases A through F were declared closed against artifact-shaped proxies for vision criteria that explicitly require runtime agents that do not yet exist. The recent planning reset (`5a2ceb5`, `a086749`) is the right kind of correction; it is not yet enough.

The minimum changes required before the loop resumes:

1. Independent reviewer-agent gates at phase boundaries and at numerically-defined drift signals — not "self-critique" by the producer.
2. A `CURRENT-PLAN.md` with explicit, falsifiable completion-evidence the producer cannot reinterpret post-hoc.
3. A real-world benchmark repository as a hard acceptance gate for any phase claiming "the system can map an unfamiliar codebase."
4. A re-audit of the Phase B–F dispositions, because the existing dispositions were authored by the same agent that wrote the implementation.

Everything in this review elaborates on those four.

## 2. Observed workflow failures or risks

These are concrete, evidence-bound observations from this repo, separated from interpretation.

### 2.1 Self-validation theater (highest-severity, structural)

`AGENTS.md:46-54` defines a "self-critique cadence" with three questions the agent asks itself at meaningful units of work, logged in `BUILD-LOG.md`. Every entry in `BUILD-LOG.md` from line 26 forward contains a self-critique block (Drift check / Contract check / Reviewer-eye check). **Every single one passes its own check.** Across roughly 100 entries on the same day, the producer never once concludes the work failed its own review.

This is not because the work was always good. It is because the producer is allowed to define the standard at the same time it is meeting the standard. Two specific tells:

- `BUILD-LOG.md:146-176` ("Phase A completion audit") declares Phase A passed. Item 3 of the audit (`skill prompts`) explicitly says: *"This implementation loads no prompts yet; the lightweight Surface Mapper/Skeptic behavior is deterministic scaffolding, not a true subagent prompt run."* The audit then proceeds to disposition Phase A as **pass**. The acceptance criterion was "≥1 actionable card, claim registers correctly assigned" (`docs/roadmap.md:147`), and the agent satisfied it by producing a deterministically-assembled card and correctly labelling its own labels. Nothing the roadmap was actually trying to prove (that the agent loop produces nuanced reading) was tested.
- `BUILD-LOG.md:504-518, 542-555` (Phase D and Phase E "disposition") follow the same pattern. Phase D requires "Tracer subagent and skill" + "Multi-round refinement protocol" + "manual approval gate UX." Phase D was closed with a `tracer.md` skill file (`feat: add tracer skill`) and three deterministic JSON artifact emitters. The runtime layer the phase was about does not exist. The disposition records this honestly in prose — and closes the phase anyway.

The mechanical guardrails (schema validation, citation resolution, `pytest`) all held through this. They are the wrong guardrails for catching this class of drift.

### 2.2 BUILD-LOG.md doing four jobs at once

`BUILD-LOG.md` is currently functioning as: chronological journal, ad-hoc plan, self-review record, and decision log. It is 1182 lines, all dated 2026-05-01, none retrievable except by full-text scan. As an audit surface it is honest; as a planning surface it is unusable.

`AGENTS.md:36` already names this — *"Do not use `BUILD-LOG.md` as the only place for forward-looking plans"* — and the planning reset was a response to that. Good. But the reset created two new live docs at the very end, after most of the drift had already happened. There is no evidence that `STATE.md` and `CURRENT-PLAN.md` would have been kept current in flight; they were created post-hoc as triage.

### 2.3 The roadmap was treated as a queue, not as a contract

The phase ordering in `docs/roadmap.md` was followed mechanically: Phase A done → Phase B → Phase C → … → Phase F → continue improving guardrails. There is no evidence that, between phases, the producer asked *"is the system on the trajectory `VISION.md` describes?"* and answered honestly. The acceptance criteria for B (`50k-LOC repo, coherent maps with non-trivial unknown partitions, ≥1 interpretive challenge per run on real codebases`) name "real codebases" explicitly. The producer never ran on a real codebase; the only test repo is a 2-file fixture in `tests/fixtures/sample_repo/`. `STATE.md:64` admits this and lists "pinned small real-world test repo, preferably an MCP server" as still needed. Phase B was nonetheless closed.

This is the critical drift surface: roadmap acceptance criteria and what the agent actually proved are not the same thing, and nothing in the workflow caught it.

### 2.4 Loop kept producing slices after the roadmap ran out

`BUILD-LOG.md` lines 568-1158 are a long tail of `Guardrail slice`, `Card slice`, `Verify slice`, `Hook slice`, `Citation slice`, `Corpus slice`, `Registry slice`, `Handoff slice` — all post-Phase-F, none in any plan. They are reasonable hardenings, several are excellent. They are also evidence that the loop has no protocol for **what to do when the current plan is complete**. The default behavior was "find an adjacent thing to harden."

This is exactly the failure mode the prompt asks about. There was no "current-plan complete" protocol because there was no current plan.

### 2.5 Code rot signal: monolithic `cbm/cli.py`

`cbm/cli.py` is 4525 lines in one file. `tests/test_cli.py` is 1800 lines in one file. The agent has been adding cleanly to both for a day. Neither has been decomposed. This is a friction signal: the loop's reward function (commits land, tests pass) is not penalizing structural cost, so structural cost has been accumulating silently. A reviewer pass would have flagged it long before now.

### 2.6 Phase-completion theater compounds

The dispositions for Phase B and Phase E both note in their reviewer-eye check that the implementation is mechanical/deterministic and "not yet" the agentic version (`BUILD-LOG.md:341, 354, 365, 377, 387`, etc.). The pattern is consistent: the producer sees that the implementation is shallow, says so honestly, and then closes the phase anyway. Honesty about the gap was treated as sufficient. It isn't, when the next phase is built on top of the gap.

### 2.7 No independent review exists in the repo at all

There is no `OUTPUT.md` for any review, in either review packet. `.planning/reviews/2026-05-01-opus-architecture-audit/` was aborted before it ran (`REVIEW-SPEC.md:3`). `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/` is in the process of being run right now (this output is one of three planned). **At no point in the build's history has an external/independent reviewer evaluated phase completion.** The loop has been running unchecked.

### 2.8 The seed kit's framing is inherited rather than re-examined

`docs/roadmap.md` lists "Codex hook configuration" and "Orchestrator script" as Phase A items. These framings — that hooks are first-class architecture; that "orchestrator script" is a deterministic Python program — are the seed kit's framings. The agent treated them as binding instead of as choices. `AGENTS.md:38-44` corrects this *after* the architecture had been built. Nothing in the workflow protocol said "before treating the kit's phasing as the build plan, verify it agrees with `VISION.md`."

### 2.9 `STATE.md` and `CURRENT-PLAN.md` themselves carry no enforcement

They live at `.planning/STATE.md` and `.planning/CURRENT-PLAN.md`. They have a `Status:` and `Last updated:` header. Nothing in CI or the run path checks that they are current with HEAD. The agent's own discipline is the only thing keeping them fresh, and that discipline produced the rest of this list.

## 3. Recommended planning artifact model

The desired property is: any single artifact answers exactly one question, and the question is named on the artifact. This separates concerns the current model conflates.

| Artifact | Question it answers | Lifecycle | Authority |
|---|---|---|---|
| `VISION.md` | Where are we going? When are we done? | Revised at deliberate vision-revision moments only; carries `Status: active` and version stamp | North star; can be challenged by reviewers but only revised through a vision-review packet |
| `RUNTIME-CONSTITUTION.md` | What discipline binds runtime CBM agents? | Schema-versioned; revised when runtime contract changes | Authoritative for runtime agents only |
| `AGENTS.md` | What discipline binds the build-side agent (this loop)? | Revised at workflow review moments | Authoritative for the build loop |
| `docs/roadmap.md` | What is the strategic phase plan from seed → mature? | Revised only at planning resets, against vision | Strategic intent. Phase ordering is a hypothesis, not a contract; replaced when reality contradicts |
| `docs/architecture.md`, `docs/contracts.md` | What is the design contract that artifacts and CLI commands must respect? | Revised when contracts change | Authoritative for contract shape; freshness gated by `STATE.md` |
| `.planning/STATE.md` | What is true right now? What is done, partial, stale, blocked? Who decided what at the last branch points? | Updated on every slice that changes phase status, decision status, or freshness | Authoritative for current factual state |
| `.planning/CURRENT-PLAN.md` | What is the in-flight slice doing, and what counts as done? | Created when a new slice begins; archived when complete | Authoritative for the current slice only |
| `.planning/PLAN-QUEUE.md` (new) | What are the candidate next slices, ranked, with rationale? | Updated when CURRENT-PLAN completes or staleness review revises priorities | Advisory; CURRENT-PLAN promotion is explicit |
| `.planning/decisions/ADR-NNN-*.md` (new) | What load-bearing architecture decision was made, with what alternatives, and why? | Immutable once accepted; superseded by a new ADR, never edited | Authoritative for decisions; durable across resets |
| `.planning/checkpoints/<phase>-<slug>/` (new) | What evidence proves a phase boundary was passed by independent review? | Created at phase boundaries by reviewer agents; immutable | Authoritative for "phase X passed" |
| `.planning/reviews/<date>-<slug>/` | What did an independent review of a specific question conclude? | Created on demand; disposition gates next plan | Authoritative for the disposed-of recommendations |
| `.planning/archive/<date>-<slug>/` (new) | What did past plans/reviews look like, preserved? | Frozen, indexed, never edited | Read-only audit history |
| `BUILD-LOG.md` | What happened on each slice, in chronological order? | Append-only journal with one entry per slice | Audit evidence; not a planning surface, not authoritative for current state |

Two things this table does deliberately:

- **It demotes `BUILD-LOG.md` to evidence-only.** No forward-looking content; no decisions; no plans. The current `BUILD-LOG.md` is doing more than this and should be split.
- **It elevates ADRs and checkpoint packets.** The repo currently has no durable record of the actual load-bearing design choices (e.g., "we chose to make hooks a Codex adapter rather than core architecture") separate from chronological narrative. Decisions get lost in `BUILD-LOG.md` immediately. ADRs fix that.

Front-matter every planning doc must carry, expanding the existing pattern:

```yaml
status: draft | active | superseded | archived
last_updated: <ISO date>
authority_scope: <one-sentence description of what this doc is the source of truth for>
supersedes: <path or null>
superseded_by: <path or null>
covers_through: <commit SHA or "HEAD">
```

`covers_through` is new and matters: it lets a reviewer test "is this doc current?" mechanically (compare to HEAD).

## 4. Current-plan lifecycle protocol

### 4.1 What `CURRENT-PLAN.md` should contain

A current plan is a contract for one in-flight slice or short chain of slices. It must contain:

1. **Goal** — one paragraph naming the user-facing change. Cited to roadmap phase or open issue.
2. **Scope** — explicit "in scope" and "out of scope." Out-of-scope is enforced.
3. **Expected write set** — every file the slice expects to modify or create, with one-line rationale per file. Files outside the write set are out of scope.
4. **Acceptance evidence (declared up front, not chosen post-hoc)** — what the producer commits to showing to claim the plan is done. Concrete enough that a reviewer could write a script that checks it. Specifically:
   - mechanical evidence (tests pass, schemas validate, citations resolve);
   - artifact evidence (the new `goal-binding.json` exists and validates);
   - behavioral evidence (a real-world or fixture run produces the expected change);
   - non-evidence: explicitly listing what this plan is **not** proving.
5. **Risk register** — what could go wrong; what would be a stop-and-surface signal.
6. **Verification commands** — exact commands a reviewer (or this agent) runs to gate completion. Output is recorded in the plan archive.
7. **Roll-back plan** — if the slice goes wrong, how is it reverted?
8. **Expected duration / commit count** — used to detect runaway scope.

The current `CURRENT-PLAN.md` (`/Users/rookslog/Development/cbm/.planning/CURRENT-PLAN.md`) covers items 1, 2, 5, 6 reasonably and is missing 3, 4 (the explicit acceptance-evidence-up-front discipline), 7, 8.

### 4.2 How detailed it should be

Detailed enough that a reviewer reading only `CURRENT-PLAN.md` plus the produced diff can decide pass/fail without consulting the producer. Imprecise enough that small implementation choices (variable names, import order, exact test wording) are not pre-specified.

The right grain is: **one CURRENT-PLAN per coherent slice, where a slice is a single behavior change of the deliverable system.** "Add `cbm-bind` and `goal-binding.json`" is one slice. "Decompose `cli.py` into modules" is one slice. "Migrate corpus to runtime-agent backend" is too big — it should fan out into a sequenced chain of slices, each its own CURRENT-PLAN.

### 4.3 How far into the future

Two horizons.

- **CURRENT-PLAN.md** projects one slice ahead. ~1–3 commits, ~1–4 files of change in the typical case. Not a roadmap.
- **PLAN-QUEUE.md** (new) projects three to five candidate next slices with rationale. The queue is advisory and cheap to revise. The queue is the place the loop reaches when CURRENT-PLAN completes; it is not a binding sequence.

The roadmap remains the strategic horizon. Anything beyond ~5 slices belongs in the roadmap, not in the plan.

### 4.4 When the current plan completes

Triggered by: producer believes acceptance evidence is satisfied.

Protocol (mandatory, not optional):

1. **Producer self-checks** — run the verification commands declared in §4.1. Record output. Any failure aborts completion.
2. **Reviewer trigger** — if the plan is at a phase boundary or carries `requires_review: true`, spawn an independent reviewer agent (see §6) before declaring complete.
3. **Archive** — move `CURRENT-PLAN.md` to `.planning/archive/<date>-<slug>/CURRENT-PLAN.md`. Append a `COMPLETION.md` capturing acceptance-evidence outputs, reviewer disposition (if any), and final commit SHA.
4. **STATE.md update** — single transaction: phase status, freshness, open decisions all updated together.
5. **PLAN-QUEUE.md consult** — pick the next plan or pause and surface.
6. **New CURRENT-PLAN.md created from queue** — copy template, fill in, commit. Loop does not begin work without a current plan.

Steps 3–6 happen in a single commit so the planning surface is never temporarily empty.

### 4.5 When the current plan changes or becomes stale

A plan is **stale** when reality has moved out from under it:

- a dependency the plan assumed is no longer valid;
- the current scope was discovered to be larger than the plan declared;
- an acceptance criterion was reinterpreted in flight;
- the codebase changed under the plan (e.g., a slice landed from elsewhere).

Protocol:

1. **Stop autonomous loop.** Do not extend the existing plan to absorb new scope.
2. **Write `.planning/STALE-NOTE.md`.** Captures: which plan is stale, what changed, what the current plan can no longer claim, what the producer recommends.
3. **Supersede.** Mark `CURRENT-PLAN.md` `Status: superseded`; create the new `CURRENT-PLAN.md` with `Supersedes:` pointing at the old one; archive the old one.
4. **STATE.md update.** Phase status, blocked items, open decisions.
5. **Reviewer trigger** if the staleness is structural (architecture decision invalidated, vision criterion reinterpreted, etc.).

The principle: **plans are revised by replacement, never by silent edit.** Editing a plan in flight erases the audit trail of what was thought when work began.

## 5. Drift / failure recovery protocol

This is the hardest single piece of governance for an automated loop, and the place the current AGENTS.md is weakest. The failure mode the prompt names (drift, bad assumptions, repeated failures, loss of fit-for-purpose) is the exact failure mode visible in this repo's history.

The protocol has two halves: **detection** (numerically-defined signals the loop checks itself) and **response** (what happens when a signal fires).

### 5.1 Detection — numerically-defined drift signals

These thresholds force a stop. They are not advisory.

| Signal | Threshold | Source |
|---|---|---|
| **Self-fix loop** | Same artifact / same field / same fix attempted twice in one session | `BUILD-LOG.md` history; `git log` per file |
| **Out-of-scope expansion** | CURRENT-PLAN's expected write set exceeded by >25% | Compare diff to plan |
| **Acceptance reinterpretation** | Plan's declared acceptance evidence reworded after slice began | Plan markdown is git-tracked; any edit triggers review |
| **Phase pass via deterministic proxy for agentic criterion** | Phase acceptance includes "agent" or "interpretive" criteria but slice produced no agent output | Reviewer flag at phase boundary |
| **Untouched real benchmark** | Phase B+ closed without ≥1 successful run against external benchmark repo | STATE.md gate |
| **Plan-less commits** | >2 commits since last `CURRENT-PLAN.md` update | git log |
| **Stale STATE** | >3 commits since last `STATE.md` update touching phase/decision/freshness | git log |
| **Unreviewed phase boundary** | Phase declared closed without a `.planning/checkpoints/<phase>/` reviewer disposition | filesystem check |
| **Test signal regression** | Any previously-passing test now fails AND the loop's last 2 attempts were "fix the test" | pytest history |
| **Build-log entropy** | >10 BUILD-LOG entries since last STATE.md update | filesystem check |
| **Code rot signal** | Any source file >1500 lines OR any test file >1000 lines OR sustained growth >300 lines/day in one file | structural metrics |
| **Vision-criterion reinterpretation** | Edit to `VISION.md` or `RUNTIME-CONSTITUTION.md` outside a declared vision-revision packet | git diff filter |

These are mechanical. They are checked at slice start and slice end, by the agent itself, against the previous commit's state. Any signal firing trips the response protocol.

### 5.2 Response — what happens when drift fires

1. **Halt forward progress on the current plan.** Do not "fix while continuing."
2. **Write `.planning/DRIFT-NOTE.md`.** What signal fired, what evidence supports it, what the producer believes the cause is, what the producer believes the remedy is. The note is itself reviewable.
3. **Spawn an independent reviewer agent** (different model preferred; see §6.4) with the drift note, the relevant plan, the relevant diff, and `VISION.md`. The reviewer's job is to confirm or refute the signal.
4. **Disposition.** Reviewer says: drift confirmed, corrective plan required → write a new CURRENT-PLAN, supersede the old. Or: drift refuted (false positive), continue with annotation.
5. **Update AGENTS.md if the false-positive rate of a signal is high.** Tune thresholds; do not weaken protocol.

### 5.3 Repeated-failure protocol

If the same drift signal fires twice in one week, or three times in one month, the protocol escalates:

- the loop pauses fully;
- a workflow review (this kind of packet) is mandated;
- AGENTS.md is revised before the loop resumes.

The principle: drift is data. A signal that fires often is telling you something about the loop's structure, not just about the slice in flight.

## 6. Phase / slice verification protocol

### 6.1 What "verified" means

A phase is **verified** only when an independent agent — not the producer — can read the phase plan, the artifacts produced, the diff, and the BUILD-LOG range, and write a `REVIEW.md` concluding the phase intent was met. The producer's self-critique is not verification.

For a slice (smaller unit), self-verification is sufficient *if and only if* the slice's acceptance evidence (declared per §4.1) was mechanical (tests, schemas, citations, artifact validation). If any acceptance criterion is qualitative ("≥1 actionable card", "1 interpretive challenge per run", "coherent map"), an independent reviewer is required even for a slice.

### 6.2 Required evidence

A phase claim of completion must carry:

1. **Mechanical evidence**
   - `pytest -q` passes; output captured.
   - All produced artifacts validate against schemas.
   - All citations in produced artifacts resolve at recorded SHAs.
   - Schema/contract changes (if any) carry version bumps and migration guidance.
2. **Behavioral evidence**
   - At least one full end-to-end run on the canonical fixture, captured in `.research/<run_id>/` and referenced.
   - For Phase B and beyond: at least one full end-to-end run on a pinned external benchmark repository (e.g., a small MCP server). This is a hard gate. **Phase B's existing disposition does not satisfy this.**
3. **Vision evidence**
   - Trace from the phase's acceptance criterion in `docs/roadmap.md` to the artifact that demonstrates it. If the criterion mentions agents, the artifact must come from an agent run, not a deterministic emitter.
   - If a criterion is satisfied via a substitute (deterministic stand-in for an agentic deliverable), the substitute is recorded explicitly and the phase is closed at status `pass-substitute`, not `pass`. STATE.md retains the gap.
4. **Reviewer evidence**
   - `.planning/checkpoints/<phase>-<slug>/REVIEW.md` written by an independent agent.
   - `.planning/checkpoints/<phase>-<slug>/DISPOSITION.md` recording accepted/modified/deferred/rejected reviewer findings.

### 6.3 Pass / pass-substitute / fail

Three outcomes, not two:

- **pass** — all acceptance criteria met by the deliverable they were intended for.
- **pass-substitute** — criteria met via a substitute deliverable, with the gap recorded. The phase advances; the gap remains visible in STATE.md and a follow-up plan is queued. Most current "passed" phases in this repo would be pass-substitute under this rule.
- **fail** — criteria not met; phase reopens.

This is the single rule that would have prevented Phase A–F from collapsing into "everything passed."

### 6.4 When to spawn reviewer agents

Mandatory:

- Phase boundaries (every roadmap phase).
- Schema/contract version bumps.
- New runtime agent role or new platform adapter.
- Any drift signal firing (per §5).
- Vision/Constitution edits.

Encouraged:

- Slices with qualitative acceptance evidence.
- Slices touching >5 files or >300 LOC.
- Long-tail "guardrail" slices when ≥3 fired in a row without a phase boundary.

### 6.5 Reviewer agent requirements

- **Isolated context.** Reviewer reads the artifacts and diff directly. It does not read the producer's reasoning.
- **Cross-model when feasible.** A different model than the producer reduces shared blind spots. (The current packet's framing — Opus reviewing Codex's work — is the right pattern.)
- **Written prompt.** Prompt is reviewable; carries the `SHARED-CONTEXT` discipline already established in `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/`. The reviewer is asked to flag the prompt itself if it seems leading. (The aborted Opus packet at `.planning/reviews/2026-05-01-opus-architecture-audit/` is a model: it was killed precisely because its prompt was too leading.)
- **Written output.** Reviewer writes `OUTPUT.md` to disk. The producer does not summarize.
- **Written disposition.** Producer dispositions each finding (accept/modify/defer/reject) with rationale, in `DISPOSITION.md`. Disposition gates next plan.
- **Output never silently overridden.** If a reviewer finding is rejected, the rejection rationale is durable. Future reviewers can re-open it.

## 7. Review / checkpoint protocol

### 7.1 Storage

```
.planning/
  reviews/
    YYYY-MM-DD-<slug>/
      SHARED-CONTEXT.md      # what reviewer is given
      REVIEW-PLAN.md         # tracks, scope, framing
      PROMPT-<track>.md      # one per track if multi-track
      OUTPUT-<track>.md      # reviewer output, written to disk
      SYNTHESIS.md           # cross-track consolidation
      DISPOSITION.md         # accept/modify/defer/reject per finding
  checkpoints/
    phase-<id>-<slug>/
      PLAN.md                # the phase plan being reviewed
      EVIDENCE.md            # mechanical + behavioral + vision evidence
      REVIEW.md              # independent reviewer disposition
      DISPOSITION.md         # producer response and remediation plan
      OUTCOME.md             # pass / pass-substitute / fail and rationale
```

The current `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/` already has most of this. Generalize it.

### 7.2 Disposition rules

- A review finding is one of: accept (apply now), accept-with-modification (apply with changes), defer (apply at named milestone or condition), reject (with rationale).
- A deferred finding is reopened automatically when its named condition triggers.
- A rejected finding's rationale is durable; a future review can re-open it but only by citing the prior rejection.
- No finding silently disappears.

### 7.3 Linkage

Every CURRENT-PLAN.md created after a review packet exists must cite the disposition packet. Every BUILD-LOG entry referring to behavior that was reviewer-disposed must cite the disposition. The mechanical link is what makes the review evidence-bearing rather than ceremonial.

### 7.4 Aborted reviews

The existing pattern (`.planning/reviews/2026-05-01-opus-architecture-audit/REVIEW-SPEC.md:3-15`) of marking a review aborted with a header note and pointing to the replacement packet is correct. Keep it. Do not delete aborted packets — they are evidence the loop noticed bias and corrected.

## 8. Recommended `AGENTS.md` operating rules

The current `AGENTS.md` is well-meaning and structurally close to right. The following changes harden it for an autonomous `/goal` loop. Each change is concrete; each addresses a gap visible in `BUILD-LOG.md`.

### 8.1 Pre-slice (always, before the first edit)

1. **Re-read in this order:** `VISION.md` → `.planning/STATE.md` → `.planning/CURRENT-PLAN.md` → `docs/roadmap.md` → `AGENTS.md` → relevant ADRs in `.planning/decisions/`.
2. **Verify CURRENT-PLAN exists, is `Status: active`, and `covers_through` is at HEAD.** If any of these fail, do not start work; write a STALE-NOTE and stop.
3. **Verify CURRENT-PLAN's expected write set covers the work you intend.** If your intended scope exceeds the plan, do not extend the plan silently; supersede.
4. **Run drift signals (per §5.1).** If any fire, halt and follow the response protocol.
5. **Confirm freshness** of any artifact you intend to consume (`STATE.md` `covers_through`, `cbm validate-fresh` for runtime artifacts).
6. **Snapshot the test suite baseline.** `pytest -q` before edits. Failures from before the slice are recorded as inherited.

### 8.2 During slice (each commit)

1. **Edit only files in the plan's expected write set.** A new file outside the set is a stale-plan signal.
2. **One coherent change per commit.** No grab-bags.
3. **Each commit's message names the plan and slice.** Format: `<slice-id>: <change>` where `<slice-id>` references the current plan.
4. **Append a BUILD-LOG entry per commit, not per slice.** Current pattern is too coarse — entries cover whole slices and bury intra-slice decisions.
5. **No silent self-critique.** The "self-critique" block is removed from BUILD-LOG; the function is moved to the §6.5 reviewer pass for any qualitative claim. BUILD-LOG records what was done, not whether the agent thinks it was good.
6. **No schema/contract change without an ADR.** ADR is `.planning/decisions/ADR-NNN-<slug>.md`; lands in the same commit.

### 8.3 Post-slice (on plan completion)

1. **Run declared verification commands.** Capture output. If any fail, do not declare complete.
2. **Behavioral check on benchmark.** For phases B+, run the pinned external benchmark; record `.research/<run_id>/` reference.
3. **Spawn reviewer if required by §6.4.**
4. **Single-commit completion transaction:** archive plan to `.planning/archive/`, write `COMPLETION.md`, update `STATE.md`, promote next plan from `PLAN-QUEUE.md` (or write STOP-AND-SURFACE).
5. **Do not begin a new slice without a new CURRENT-PLAN committed.**

### 8.4 Stop-and-surface conditions

Tighten the existing list in `AGENTS.md:74-81`:

- CURRENT-PLAN missing, stale, or superseded without replacement.
- Same-mistake-twice (per §5.1).
- Acceptance evidence requires reinterpretation to claim pass.
- Drift signal fires.
- Phase boundary requires reviewer; reviewer not yet run.
- Real-world benchmark run fails or is missing.
- Test suite regresses and the loop's last attempt was "fix the test."
- Vision/Constitution edit considered (always surface).
- Schema/contract change considered (surface unless ADR is in flight).
- Code rot signal (cli.py >5000 lines, etc.).

The bias of the current `AGENTS.md` is "default proceed." That bias is correct for routine slices and dangerous for boundary moments. Make the boundary triggers explicit.

### 8.5 Recovery from mistakes

The principle: **traceability over patch-up.**

- Do not edit history. Do not amend prior commits to "fix" a mistake; write a new commit.
- Do not delete artifacts produced under a mistaken plan; mark them `status: superseded` and write a corrective slice.
- Do not silently rename or quietly rescope. A rescope is a new plan.
- A mistake recognized after the slice closed is documented in BUILD-LOG with `correction:` lead and a forward pointer to the corrective slice.
- Do not strengthen guardrails to make a past mistake "not a mistake." The mistake stands; the guardrail comes after.

What this rules out is exactly the pattern visible in BUILD-LOG.md from line 568 onward: a long tail of guardrail slices that look like they're tightening contracts and are partly compensating for past Phase A–F dispositions being too generous. Some of those slices were independently good. Some were defensive. Telling them apart requires the slice-by-slice reviewer discipline above.

## 9. Documentation freshness protocol

### 9.1 Front-matter as the freshness contract

Every doc in `docs/` and `.planning/` carries:

```yaml
status: draft | active | superseded | archived
last_updated: <ISO date>
authority_scope: <one sentence>
covers_through: <commit SHA or HEAD>
supersedes: <path or null>
superseded_by: <path or null>
```

A doc is **fresh** if `covers_through` is reachable from HEAD without merges that touched files in its `authority_scope`. This is mechanical.

### 9.2 Stale-doc detection

A CI script (or a `cbm doc-freshness` check) scans `docs/` and `.planning/`, compares each doc's `covers_through` to HEAD, and emits a stale-doc list. Stale docs are not deleted; they are marked `status: stale` until refreshed or superseded.

The current `STATE.md:30-34` enumerates which docs are partially outdated by hand. Replace this with the mechanical check.

### 9.3 Authority resolution

When two docs disagree, the one whose `authority_scope` covers the question wins, and the conflict is recorded. The current pattern (`STATE.md` claims authority over current state, `roadmap.md` over phase intent) is sound. Make it explicit on every doc.

### 9.4 Supersession

Supersession is the only way docs are replaced. The superseded doc retains `Status: superseded`, `Superseded by: <path>`. The new doc has `Supersedes: <path>`. Both stay in the tree. The reader sees the chain.

This pattern is already used in `.planning/STATE.md:5-6` and `.planning/CURRENT-PLAN.md:4-6`. Extend it everywhere.

### 9.5 Archive

Old plans, completed checkpoints, and aborted reviews go in `.planning/archive/<date>-<slug>/`. The archive is read-only. Each archived directory carries a `WHY-ARCHIVED.md` first line stating the reason. The current `.planning/reviews/2026-05-01-opus-architecture-audit/` (aborted but in place) becomes the prototype of an archive entry.

### 9.6 README pointers

`README.md` becomes a generated index of authoritative docs by question, not a hand-maintained narrative. (Or: keep narrative, add a generated authority-index appendix.) The reader looking for "where is current state" should not have to scan four candidate locations.

## 10. Concrete next steps

In order. Do not start step N+1 until step N is done.

1. **Halt the autonomous loop.** Do not run another `/goal` slice until step 5 lands. The current planning reset is the right opportunity to stop; don't waste it.

2. **Land this review.** Write `OUTPUT-WORKFLOW.md` (this file) to disk. Run Track A (architecture) and Track C (vision) reviewers in parallel. Wait for all three.

3. **Synthesize and disposition** in `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/SYNTHESIS.md` and `DISPOSITION.md`. Capture conflicts between the three reviewer outputs honestly; do not collapse them.

4. **Re-audit Phase B–F dispositions.** For each, ask: was the acceptance criterion met by the intended deliverable, or by a deterministic substitute? Re-disposition each as `pass`, `pass-substitute`, or `fail`. Record gaps in `STATE.md` as open items. Expect most will become `pass-substitute`. This is the single most important corrective action.

5. **Adopt the planning protocol.** Write `.planning/PLANNING-PROTOCOL.md` capturing §3, §4, §5, §6, §7, §9 of this review. Update `AGENTS.md` per §8. Commit as one transaction.

6. **Add the planning artifacts that don't yet exist.** Stub `.planning/PLAN-QUEUE.md`, `.planning/decisions/` (with the first ADR — the hooks-as-adapter decision is a candidate), `.planning/checkpoints/` (with re-audited Phase A–F entries), `.planning/archive/`. Migrate the existing review packets into the protocol's structure.

7. **Stand up the drift-detection script.** `scripts/check-drift.sh` (or `cbm doc-freshness` + structural metrics) runs the §5.1 signals and exits nonzero if any fire. Wire into the loop's pre-slice and post-slice steps. This is the only mechanism that lets the loop catch itself.

8. **Commit a real-world benchmark.** Pin a small MCP server (or equivalent unfamiliar repo) at a specific SHA. Add a phase-acceptance gate that requires `cbm run` against the benchmark to produce the expected artifact shape. Until this exists, no Phase B+ disposition should claim "the system can map an unfamiliar codebase."

9. **Decompose `cbm/cli.py` and `tests/test_cli.py`.** Treat as a slice with its own CURRENT-PLAN. The current monolith is a friction signal that compounds with every additional feature.

10. **Spawn a checkpoint reviewer for Phase A specifically.** Use the new protocol against an existing phase to test the protocol itself. If the reviewer disposition surfaces gaps the producer's own audit missed, the protocol is working; if it surfaces nothing, the protocol is broken.

11. **Resume the loop only after steps 1–10.** First slice under the new protocol should be small and reviewer-gated, to verify the loop honors the protocol it was given.

## 11. A closing concern about the loop premise

The prompt asks how to govern a "mostly automated Codex `/goal` loop" so it can move toward `VISION.md`. The framework above is responsive to that request and I think it would work.

But I want to flag that the framing imports a question that is not obviously decided: **is `VISION.md` the right kind of target for an automated loop at all?**

`VISION.md` is, on a careful reading, a hermeneutic target. Maturity criteria 3–4 (Skeptic factual catch rate vs. domain experts; interpretive challenge precision) cannot be measured without expert review on real codebases. Criterion 9 (pedagogical adequacy) cannot be measured without a careful reader doing the work by hand. Criterion 6 (coverage honesty) has zero-exception language that a producer-loop is structurally bad at honoring against itself. The vision is, in shape, the kind of target that resists self-validation by design — that *is* the vision's central thesis applied to itself.

A fully automated loop driving toward this vision is therefore in tension with the vision's own commitments. The loop will produce things that look like progress (schemas, gates, artifacts) while the actual vision deliverables (asymmetry against careless agents, interpretive register that pays off, careful reader's onboarding compressed) remain untouched. The first eight hours of this repo demonstrate this.

This does not invalidate automated execution. It does mean the human-in-the-loop is not a fallback — it is a structural part of the mechanism. Reviewer gates are not slowing the loop down; they are the only reason the loop can claim to be moving toward this particular vision.

The protocol above puts independent reviewers (preferably cross-model) at every phase boundary, every drift signal, and every qualitative slice. That is the minimum. If even that proves too generous in practice, the human will need to pick up review responsibility at named cadences. That is fine. The loop's value is amplifying the human's review attention, not replacing it.

This is consistent with what `VISION.md:11` actually says: *"The system is not better at understanding code than a careful human reader. The system is better than a careless agent at not pretending to understand."* The build's loop is the same kind of agent. Treat it the same way.
