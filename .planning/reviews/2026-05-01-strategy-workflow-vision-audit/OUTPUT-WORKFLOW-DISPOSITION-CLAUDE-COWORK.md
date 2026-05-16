---
name: Workflow disposition (independent)
status: draft
last_updated: 2026-05-01
reviewer: Claude Cowork (disposition role; not the workflow reviewer)
adjudicates:
  - OUTPUT-WORKFLOW.md (Opus 4.7 max, 1M context, Claude Code CLI)
  - OUTPUT-WORKFLOW-CHATGPT.md (GPT-5.5 Pro, extended thinking)
  - OUTPUT-WORKFLOW-CLAUDE-COWORK.md (Claude Cowork)
inputs_consulted:
  - PROMPT-WORKFLOW.md, PROMPT-WORKFLOW-DISPOSITION.md, SHARED-CONTEXT.md, REVIEW-PLAN.md
  - the three OUTPUT-WORKFLOW-*.md files in full
  - AGENTS.md, .planning/STATE.md, .planning/CURRENT-PLAN.md, BUILD-LOG.md (full),
    docs/roadmap.md, RUNTIME-CONSTITUTION.md (skim), VISION.md (skim),
    .codex/, .research/run-phase-a-final-audit/handoff.md, OUTPUT-ARCHITECTURE-CLAUDE-COWORK.md (head)
  - git status / log --oneline / branch -a / diff --stat / ls-files for VISION/RUNTIME-CONSTITUTION
---

# Workflow Disposition

This document compares, meta-critiques, and adjudicates the three workflow
reviews. It is not a fourth review. Where I cite the reviews I use short
labels: **OPUS** = `OUTPUT-WORKFLOW.md`, **CHATGPT** = `OUTPUT-WORKFLOW-CHATGPT.md`,
**COWORK** = `OUTPUT-WORKFLOW-CLAUDE-COWORK.md`.

## 1. Comparison summary

### 1.1 Diagnosis-level convergence

All three diagnose the same five things, in slightly different vocabularies:

- **Self-validation theater.** OPUS §2.1, CHATGPT §5, COWORK F3/F4. The
  build's only review gate is the producer reviewing itself, on the same day,
  via a self-critique block in `BUILD-LOG.md`. The runtime CBM agents have a
  Skeptic with isolated context; the dev agent does not.
- **`BUILD-LOG.md` is doing too many jobs.** OPUS §2.2, CHATGPT §4, COWORK F7.
  It is journal + plan + review record + decision log; at 1182 lines and 100
  H2 sections it is no longer reviewable.
- **Phase boundaries are nominal / "passed" claims overreach.** OPUS §2.3 and
  §2.6, CHATGPT §6, COWORK F6. The roadmap acceptance criteria for B–F name
  agentic deliverables; the slices that closed those phases produced
  deterministic stand-ins.
- **No real-world benchmark.** OPUS §2.3, CHATGPT §6, COWORK F5. Smoke runs
  on the project's own repo are circular evidence; no pinned external
  benchmark exists.
- **No independent reviewer / no escalation thresholds.** OPUS §2.7 and §5.1,
  CHATGPT §5 and "Escalation thresholds", COWORK F11 and §D. The current
  AGENTS.md "stop and surface" list fires on catastrophic failure, not on the
  slow-accumulation drift the project actually exhibited.

These five are the **load-bearing** convergent diagnoses. Verified against
primary sources in §3 below.

### 1.2 Diagnosis-level divergence

- **Untracked governance files** (`VISION.md`, `RUNTIME-CONSTITUTION.md`,
  `docs/reuse-and-refresh.md`, `schemas/refresh-delta.schema.json`,
  `skills/consult.md`). COWORK F1 names this precisely. CHATGPT §1 raises it
  but mis-frames it as "those files were not available at the referenced root
  paths" — actually they exist on disk and are uncommitted. OPUS does not
  mention it. **Verified:** `git ls-files VISION.md RUNTIME-CONSTITUTION.md`
  returns empty; both files exist in the working tree dated the same as the
  initial seed commit, never committed.
- **Branch discipline.** COWORK F2 names that the entire 103-commit history
  sits on one branch (`phase-a-mvp-foundation`) with zero merges to main, in
  direct violation of `AGENTS.md:24`. OPUS notes the long uninterrupted
  cadence implicitly but never names branch hygiene as a problem. CHATGPT
  does not raise it. **Verified:** `git log --merges` returns nothing;
  `git branch -a` shows local main untouched since the seed commit.
- **Self-critique cadence is wrong.** COWORK F4 uniquely observes that
  AGENTS.md says "at meaningful units of work" but the actual cadence is
  per-slice (98 critiques across 100 entries). OPUS argues the right fix is
  to remove self-critique entirely and replace with reviewer agent. CHATGPT
  keeps self-critique advisory. The three diagnoses are compatible but the
  prescriptions differ.
- **Code rot.** OPUS §2.5 uniquely raises `cbm/cli.py` 4525 lines /
  `tests/test_cli.py` 1800 lines as a structural cost the loop's reward
  function is not penalizing. CHATGPT does not. COWORK does not in the
  workflow review (the same reviewer's architecture review catches it).
  **Verified:** `wc -l` confirms both numbers exactly.
- **Direct-examination ratio.** COWORK V3 uniquely cites the latest
  final-audit smoke run reporting `files_examined_directly: 1` of
  `files_in_scope: 35` — 3% on the system's own codebase. **Verified:**
  `.research/run-phase-a-final-audit/handoff.md:30-31`. This single number
  is the most damning verified fact in any of the reviews and OPUS/CHATGPT
  both miss it.
- **STATE.md normalizes the dirty working tree.** COWORK F8 uniquely flags
  `STATE.md:52`'s "Treat them as intentional working-tree context unless
  reviewed otherwise" as the language pattern of normalization-of-deviance.
  OPUS §2.9 catches the same surface fact (no enforcement) but does not
  diagnose the language move. CHATGPT does not.
- **VISION.md is hermeneutic and resists self-validation.** OPUS §11
  uniquely raises that the loop premise itself ("a fully automated `/goal`
  loop pointed at this vision") is in tension with the vision's commitments.
  Neither CHATGPT nor COWORK frame it this way (COWORK's closing observation
  is adjacent but lower-stakes). This is the most strategic single point in
  any of the three reviews.

### 1.3 Prescription-level divergence

The three reviews agree on diagnosis more than on protocol. The
disagreements that matter:

- **Plan-amendment-in-flight.** OPUS §4.5 and COWORK lifecycle "Hard rules"
  both forbid in-flight plan edits — a plan changes only by archive +
  successor. CHATGPT explicitly allows "minor amendments in place" if
  objective/risk/acceptance criteria are unchanged. **Real disagreement.**
- **Self-critique disposition.** OPUS §8.2.5 removes self-critique from
  `BUILD-LOG.md` entirely and reassigns the function to reviewer agents.
  COWORK §AGENTS.md "Self-critique cadence" keeps it but reduces frequency
  and adds register-tagging. CHATGPT keeps self-critique mandatory but
  advisory. **Real disagreement.**
- **How many incident-class artifacts.** OPUS proposes `STALE-NOTE.md` and
  `DRIFT-NOTE.md` (two). CHATGPT proposes `.planning/incidents/<slug>.md`
  with full L0-L5 taxonomy. COWORK proposes per-condition entries inside
  `BUILD-LOG.md` (`discovered_falsified_assumption`, `repeated_failure`,
  `plan_stale`). **Real disagreement, partly terminological.**
- **Phase-completion vocabulary.** OPUS proposes a three-state outcome —
  `pass / pass-substitute / fail` — and recommends re-auditing Phase B–F
  under this rule (§10.4). CHATGPT proposes `pass / pass-with-limitations /
  fail / superseded`. COWORK rejects "partial pass" outright as oxymoron and
  prefers `in-progress, blocked on [Y]`. **Real disagreement, load-bearing.**
- **Frontmatter scope.** All three propose more structured frontmatter on
  governance docs. OPUS proposes a 6-field set with `covers_through`.
  CHATGPT proposes a 9-field set including `applies_to_branch`,
  `applies_to_commit`, `owner_mode`, `review_status`. COWORK proposes a
  similar 7-field set with `last_verified` separate from `last_updated` and
  a `cbm-docs-status` CLI tool that consumes it. **Mostly convergent;
  divergence is in scope, not direction.**

### 1.4 Where the three reviews quietly agree without checking

These are the convergences I am most suspicious of:

- All three propose a templates directory and a frontmatter schema. None of
  them ask whether the dev agent's actual failures (uncommitted
  constitution-class files, self-grading, no benchmark) would have been
  prevented by frontmatter or templates. **Frontmatter does not enforce
  branch hygiene.** Templates do not run benchmarks. The convergent
  recommendation imports a familiar trope.
- All three propose more directories under `.planning/` (archive, decisions,
  checkpoints, incidents, phase-reviews, critiques, templates,
  verification). The repo currently has a working planning surface in three
  files. Adding nine subdirectories without first proving the discipline
  exists to keep them filled is, on its face, the kind of process the
  `/goal` loop will perform mechanically and never load-bearing-ly.
- All three treat the existing review packet (this packet) as roughly the
  right shape — and on this I agree, with a single caveat: none of the
  three reviewers tested whether `DISPOSITION.md` and `SYNTHESIS.md` would
  actually be filled in. Those files exist as 19-line stubs; this
  disposition is the first thing actually filling that slot.

## 2. Meta-critique per review

### 2.1 OUTPUT-WORKFLOW.md (OPUS)

**Evidence discipline: strong.** Cites BUILD-LOG by line range
(`BUILD-LOG.md:146-176`, `BUILD-LOG.md:504-518, 542-555`); cites AGENTS.md
by line; cites roadmap.md by line for the Phase B benchmark criterion. Spot
check: line 504 ("Phase D disposition") and line 542 ("Phase E disposition")
hold; the substantive quotes are accurate. The 1182-line BUILD-LOG count is
exact. The 4525-line `cli.py` and 1800-line `test_cli.py` are exact.

**Framing: pushed back, partly.** OPUS opens by explicitly refusing to
ratify the planning reset's adequacy and flags two assumptions in the
prompt — (a) the artifact triple is right, (b) the loop premise itself is
viable. (b) is the strongest single move in any of the reviews. But OPUS
then quietly accepts that `STATE.md`/`CURRENT-PLAN.md` should remain
authoritative for current state, when the more aggressive read (which
COWORK partly takes via F8) is that those two files have already absorbed
the unhealthy state into the new baseline. OPUS does not push that hard.

**Blind spots:**

- *Untracked governance files.* OPUS never runs or considers
  `git status` / `git ls-files` against `VISION.md`,
  `RUNTIME-CONSTITUTION.md`. Given OPUS cites both files as authority
  ("Re-read in this order: VISION.md → STATE.md → ...", §8.1), this is a
  significant miss — the entire authority chain rests on uncommitted files
  and OPUS does not detect it.
- *Branch discipline.* OPUS counts 100+ commits on the same day but does
  not check whether they sit on a feature branch unmerged to main; if it
  had, AGENTS.md:24 would be the obvious rule violation.
- *Direct-examination ratio.* OPUS gestures at "no real-world benchmark"
  but never reads the existing smoke run's coverage block, so it misses
  that the system's own self-evaluation reports 3% direct examination on
  its own repo.

**Recommendation specificity: high.** §5.1's table of 12 numerically-defined
drift signals is the most operational artifact in any of the three reviews.
"Same artifact / same field / same fix attempted twice in one session,"
"out-of-scope expansion >25%," "any source file >1500 lines OR sustained
growth >300 lines/day in one file" are all checkable mechanically. §6.3's
`pass / pass-substitute / fail` is concrete and load-bearing.

**Internal consistency: mixed.** OPUS diagnoses the BUILD-LOG self-critique
as theater (§2.1) and then in §8.3 prescribes adding a `COMPLETION.md`,
`STATE.md` update, and PLAN-QUEUE consult to *every* plan completion. This
risks recreating the same ceremony at the planning level that BUILD-LOG
became at the journal level. The §10 "concrete next steps" is 11 sequential
items each gated on the prior — a long-running pause that the prompt
partly justifies but should be checked for tractability.

**AI-pattern failures: minor.** OPUS uses some hedge language ("genuinely
contested," "the closest match") and the §11 closing concern, while
substantively the strongest part, is structured as a "but I want to flag"
that softens the punch. Otherwise the prose is direct.

**Workflow-domain hazards:**

- *Process-mongering risk: medium.* OPUS proposes 12 drift signals, ADRs, a
  `PLAN-QUEUE.md`, `.planning/checkpoints/`, `.planning/archive/`,
  `.planning/decisions/`, three completion-transaction files
  (`COMPLETION.md`, `STATE.md` update, plan promotion), and a
  `cbm doc-freshness` script. The 12 signals would land cleanly as one
  script; the rest are folders that may stay empty for weeks.
- *Imported-template risk: low.* OPUS's recommendations are anchored in the
  observed failures, not in an imported governance template. The 12-signal
  table is the cleanest example: each signal corresponds to a specific
  observed drift mode.

**Independence under stress: yes.** OPUS reads as written without other
review outputs in view. No tonal echoes of CHATGPT or COWORK; the §11
closing concern is genuinely original.

**Top-line verdict on OPUS:** the most rigorous review of the three on
*signal design and lifecycle protocol*, and the only review that pushes back
on the loop premise itself. Misses the two most obvious git-state friction
signals (untracked governance files, no merges) and one specific benchmark
fact (direct-examination ratio). Process-mongering risk in the §10
implementation list is the main thing to filter.

### 2.2 OUTPUT-WORKFLOW-CHATGPT.md (CHATGPT)

**Evidence discipline: weakest of the three.** CHATGPT references concrete
files (AGENTS.md, STATE.md, CURRENT-PLAN.md, docs/roadmap.md) but cites
none of them by line. The headline empirical claim — that `VISION.md` and
`RUNTIME-CONSTITUTION.md` "were not available at the referenced root paths
on the inspected branch" — is **half right and load-bearing-wrong**: the
files exist on disk; they are not committed. Calling that "absent" leads
the reader toward "files are missing" rather than "branch hygiene
collapsed." COWORK gets this exactly right (F1).

The "five passing tests" / "51 passing" framing is correct but
unattributed — `STATE.md:70` is the source.

**Framing: weakest pushback of the three.** CHATGPT's executive verdict
("the planning reset is directionally right but not sufficient") echoes the
language of `STATE.md` and `CURRENT-PLAN.md` themselves and proceeds to
recommend largely what those documents say should happen next. The prompt
explicitly told reviewers not to assume the planning reset is adequate.
CHATGPT does not visibly stress-test that assumption beyond noting "not
sufficient."

**Blind spots:**

- *Branch discipline.* CHATGPT does not raise the 103-unmerged-commits
  problem. AGENTS.md:24's rule (`Main only via merged, validated branches`)
  is mentioned only obliquely.
- *BUILD-LOG specifics.* CHATGPT recognizes that BUILD-LOG is "too long and
  chronological" but never gives line counts or H2 counts; the prescription
  ("keep it append-only and chronological, but add a separate state
  structure") is the same as `STATE.md` already says.
- *Direct-examination ratio.* Same miss as OPUS.
- *Self-critique cadence.* CHATGPT keeps self-critique "mandatory but
  advisory," missing COWORK's observation that 98-of-100 cadence is itself
  the failure mode.

**Recommendation specificity: medium-low.** The L0-L5 failure-level
taxonomy (§Drift/failure recovery) is well-shaped but uncalibrated against
the actual repo — the prompt asked which thresholds would have caught the
*observed* drift, and CHATGPT's L0-L5 is generic. The CURRENT-PLAN.md
section template is exhaustive (16 named sections) but no test of whether
the existing CURRENT-PLAN.md (which has 9 of those sections in different
form) would actually fail freshness against this template.

The `.planning/incidents/<slug>.md` template is concrete (12 named fields).
The "prompt preflight checklist" is concrete (7 questions). These are
useful.

**Internal consistency: mixed.** CHATGPT identifies that "self-critique can
catch obvious drift, but it cannot be the only gate" (§5) and then
prescribes an 11-item "before each slice" checklist, an 8-item "during
each slice" checklist, and a 6-item "after each slice" checklist — 25
items total — for the dev agent to run unattended. The prescription
treats the dev agent's compliance as solving the problem the diagnosis
already attributed to self-validation.

**AI-pattern failures: noticeable.** Three patterns recur: (a) "Required
correction:" as a formal closer to every section regardless of whether the
correction is actually different from the diagnosis; (b) very long bulleted
lists where each bullet is a near-paraphrase of the next; (c) hedged
recommendations ("may be a reasonable transitional state, but it is not
yet governed") that decline to take a position. The 14-item "concrete next
steps" list contains substantial overlap (steps 5, 6, 7 are largely
restatements of step 3) and treats the act of producing artifacts as the
governance change itself.

**Workflow-domain hazards:**

- *Process-mongering risk: high.* CHATGPT proposes seven new template
  files, six new directory structures, a frontmatter with 9 fields, a
  governance validation script, three before/during/after slice
  checklists, a phase-status correction artifact, an L0-L5 incident
  taxonomy, a prompt preflight checklist, and a `docs/governance.md`. This
  is more process than the project's daily commit volume can absorb without
  becoming theater.
- *Imported-template risk: high.* The L0-L5 severity taxonomy reads as
  borrowed from operational incident management (SRE / oncall culture) and
  is not calibrated against the kinds of failures this repo has actually
  exhibited — none of the observed drift was an "L5 irreversible/external
  action."
- *Tooling-without-discipline.* CHATGPT recommends `cbm-docs-status`,
  `governance validation`, `prompt preflight`, but does not name the human
  rule that would make the loop run them. The default-proceed-but-honor-X
  posture is harder than CHATGPT acknowledges.

**Independence under stress:** plausible. No direct echoes of OPUS or
COWORK phrasings; the L0-L5 taxonomy and the "incidents" framing are
distinct.

**Top-line verdict on CHATGPT:** the most comprehensive in coverage and
the weakest in evidence; the most likely to over-process the loop.
Specific items worth keeping: the prompt preflight checklist, the
incident artifact template (consolidated to one file), the
"phase-status correction" idea (which OPUS makes more concrete via Phase
B–F re-audit). Most of the rest restates what `STATE.md` and
`CURRENT-PLAN.md` already say.

### 2.3 OUTPUT-WORKFLOW-CLAUDE-COWORK.md (COWORK)

**Evidence discipline: strongest of the three.** Cites by line throughout
(AGENTS.md:46-54, AGENTS.md:24, STATE.md:23, STATE.md:52, BUILD-LOG.md
line counts, RUNTIME-CONSTITUTION.md:222-242, etc.). Spot check: F1's
"VISION.md, RUNTIME-CONSTITUTION.md, docs/reuse-and-refresh.md, ...
untracked" is exactly right against `git status`. F2's 103 commits, no
merges to main, is exact. F4's "98 self-critique passes across 100
entries" is verified: `grep -c "Reviewer-eye check" BUILD-LOG.md` = 98;
`grep -c '^## ' BUILD-LOG.md` = 100. F5's 3% direct-examination ratio
verifies against `.research/run-phase-a-final-audit/handoff.md:30-31`
(`files_examined_directly: 1`, `files_in_scope: 35`).

**Framing: pushed back firmly.** F8 explicitly identifies that
`STATE.md:52`'s "Treat them as intentional working-tree context unless
reviewed otherwise" is normalization-of-deviance language — i.e., the
planning reset itself folded the prior unhealthy state into the new
baseline. This is the strongest single push-back on the prompt's "do not
assume the reset is adequate" instruction in any review.

**Blind spots:**

- *Code rot.* Same miss as CHATGPT — COWORK does not flag the cli.py
  monolith here. (The same reviewer's architecture review catches it; the
  workflow review does not coordinate.)
- *Loop premise.* COWORK does not raise OPUS's §11 concern about whether
  `VISION.md` is the right kind of target for an automated loop. The
  closing observation ("the project's own diagnostic vocabulary applies to
  itself with terrifying precision") is adjacent but operates one register
  lower — about the build process, not about the loop's compatibility
  with the vision.
- *Re-audit of past phases.* OPUS's strongest single recommendation —
  re-grading Phase B–F with `pass / pass-substitute / fail` — is missing
  from COWORK. COWORK proposes "in-progress, blocked on [Y]" prospectively
  but does not address what to do about phases already declared closed.

**Recommendation specificity: high.** F1–F13 are evidence-anchored. The
escalation thresholds (§D "Hard escalation thresholds") are concrete and
calibrated against observed drift modes ("more than 20 commits since the
last merge to main," "any constitution-class file modified for more than
one session without commit"). The §V3 direct-examination-ratio gate is
directly checkable from the handoff coverage block.

The "Concrete next steps" §1-§10 are unusually small-grained: each step
closes a specifically-numbered observation. Step 1 (`git add ...`) is a
single command. Step 9 (rotate the BUILD-LOG) is a one-time move plus a
threshold rule. This is the most tractable next-step list of the three.

**Internal consistency: high.** Diagnosis "BUILD-LOG self-critique is
noise" → prescription "move self-critique out of BUILD-LOG, change cadence
to per-completed-plan." Diagnosis "no checkpoint reviewer" →
prescription "define one with isolated context, narrow read list, fixed
output location, blocking authority." The dots connect.

**AI-pattern failures: minor.** Some Claudean tics — the closing
observation reaches for a strong rhetorical close ("terrifying
precision"); the F-numbered list is slightly long (13 items, some
overlapping). The overall prose is direct; the recommendations match the
diagnoses.

**Workflow-domain hazards:**

- *Process-mongering risk: low.* COWORK proposes one new directory
  (`.planning/critiques/`), one rotation rule for `BUILD-LOG.md`, one
  archive convention, one `cbm-docs-status` CLI, and one
  `cbm-loop-status` CLI. Compare to CHATGPT's seven templates + six
  directories.
- *Imported-template risk: low.* The escalation-threshold list is
  observation-derived; no SRE templates imported.
- *Tooling-without-discipline:* moderate. COWORK proposes `cbm-loop-status`
  and `cbm-docs-status` as CLI commands but, like the others, doesn't say
  *what mechanism makes the loop actually run them* beyond "the loop runs
  this on session start." This is the same hand-wave the other two reviews
  perform; just less of it.

**Independence under stress:** explicit and verifiable. The frontmatter
declares which inputs were deliberately skipped (other OUTPUT files,
SYNTHESIS, DISPOSITION). The reviewer noted in F2 that "the user has had
to manually re-issue this current prompt with explicit isolation
instructions" — meta-aware of the operating constraint and treats it as a
finding.

**Top-line verdict on COWORK:** the strongest evidence discipline, the
sharpest framing push-back, the most tractable next-step list. Misses code
rot and the loop-premise question. The closing observation is rhetorical
but lands. Of the three, this is the review whose recommendations I would
adopt most aggressively.

### 2.4 Anonymity-of-model check

I read the three reviews on three reading passes. The first pass I left
the file labels visible. The second pass I covered them and re-read the
diagnoses. The third pass I checked the citations against the repo. The
ranking on evidence discipline (COWORK > OPUS > CHATGPT) was the same on
all three passes. The ranking on prescription concreteness (OPUS ≈ COWORK
> CHATGPT) was also stable. I do not believe my model lineage with COWORK
biased the ranking in any direction the citations can't carry.

## 3. Adjudication of contested claims

These are the load-bearing disagreements where the reviews actually
contradict (not just use different vocabularies). I name the verdict and
the rationale; small terminological disputes are skipped.

### 3.1 Are `VISION.md` / `RUNTIME-CONSTITUTION.md` "missing"?

**Verdict: COWORK right; CHATGPT wrong; OPUS silent.**

Evidence: `git ls-files VISION.md RUNTIME-CONSTITUTION.md` returns empty;
`ls -la` confirms both files exist on disk dated 2026-05-01 09:20.
CHATGPT's "not available at the referenced root paths on the inspected
branch" reads as "files are missing." That framing is wrong and load-
bearing — the failure mode is *uncommitted load-bearing context*, not
absence. The fix in CHATGPT's framing ("add or restore them") would be
done by `git add` + commit; the fix the actual situation requires is
identical mechanically but comes with a different governance lesson:
*constitution-class files have been edited in the working tree for hours
or days while being cited as authority in committed planning files*. That
is a branch-hygiene failure, not a missing-files failure. COWORK names it
correctly.

This adjudication promotes the diagnosis from "minor reference fix" to
"load-bearing rule violation."

### 3.2 Should plans be amendable in flight?

**Verdict: OPUS / COWORK right; CHATGPT wrong.**

OPUS §4.5 and COWORK lifecycle "Hard rules" both forbid in-flight plan
edits — supersede + new plan, never edit. CHATGPT allows minor amendments
when objective/risk class/acceptance criteria are unchanged.

The repo's actual history shows the failure mode: phase boundaries that
were "closed honestly" with a written acknowledgment of a gap and then
closed anyway (`BUILD-LOG.md:176`, `:518`, `:555`). Honesty about the gap
in the same surface that closed the slice is the failure mode. CHATGPT's
"minor amendment in place" rule is a softer version of the same move:
the producer reweights the criteria silently and the audit trail of what
was thought when the slice began is lost.

The cost of strict supersession is verbosity (more archived files). The
cost of soft amendment is invisible to the producer (which is the whole
problem). Pay the verbosity cost.

### 3.3 What outcome vocabulary should phase completion use?

**Verdict: OPUS framework, COWORK constraint.**

OPUS proposes `pass / pass-substitute / fail`. CHATGPT proposes
`pass / pass-with-limitations / fail / superseded`. COWORK rejects "partial
pass" outright as oxymoron and prefers `in-progress, blocked on [Y]`.

These are reconcilable. COWORK is right that "partial pass" is an
oxymoron *for a phase whose acceptance criteria are conjunctive* — a
phase doesn't half-graduate. OPUS is right that the project needs a way to
acknowledge that a real, useful slice landed against a roadmap criterion
*without* claiming the agentic deliverable the criterion actually named.

Resolution: a phase has only two outcomes — `passed` or `not passed`.
"Partial pass" as a *phase* outcome is forbidden. A *slice* whose
acceptance was a deterministic substitute for an agentic deliverable
records that fact in its slice-completion entry as
`evidence_kind: deterministic-substitute` and the *phase* stays
`not passed` until the agentic deliverable lands. This combines OPUS's
honesty-vocabulary and COWORK's conjunctive-rigor.

The Phase B–F re-audit (OPUS §10.4) follows: every closed phase between
B and F is re-graded `not passed` if it relied on a deterministic
substitute. Most will. The slices remain real and shipped; only the
phase-pass claim is retracted. `STATE.md` records the gaps as open.

### 3.4 What is the right cadence for self-critique?

**Verdict: COWORK closer, OPUS more aggressive than necessary.**

OPUS §8.2.5 removes self-critique from `BUILD-LOG.md` entirely and moves
the function to reviewer agents. COWORK §AGENTS.md "Self-critique cadence"
keeps self-critique but reduces frequency to "completed plans / phase
boundaries / before merge / kit deviation, no more than once per slice."
CHATGPT keeps self-critique mandatory but advisory.

The 98-of-100 cadence is the failure mode. OPUS's removal would prevent
that mode. COWORK's reduction would prevent it more cheaply. Test:
imagine the most recent five slices on the kit's current cadence (per-
slice critique). Under OPUS, those five slices have zero critique entries
and one reviewer-agent invocation if any was warranted. Under COWORK, the
five slices have at most one critique entry total and possibly zero.
Under CHATGPT, the five slices probably each have a critique entry.
COWORK and OPUS both prevent the noise; COWORK preserves the
introspective discipline at meaningful boundaries.

Adopt COWORK on cadence; adopt OPUS's reviewer-agent rule for *any
qualitative claim*. They are not in conflict.

### 3.5 How many incident-class artifacts?

**Verdict: One file, three triggers.**

OPUS proposes `STALE-NOTE.md` and `DRIFT-NOTE.md`. CHATGPT proposes
`.planning/incidents/<slug>.md` with L0-L5. COWORK puts the events inside
`BUILD-LOG.md` as typed entries.

The right answer is one file, named for what triggers it, not for the
governance category. Call it `.planning/STOP-NOTE.md` (singular, mutable
during the stop, archived to `.planning/archive/<date>-<slug>/STOP-NOTE.md`
when the stop ends). Triggers: drift signal fires, plan stale,
discovered-bad-assumption, repeated failure, escalation threshold crossed.
Content: which trigger, what evidence, what plan was active, what the
producer recommends, who must decide.

This avoids three problems: CHATGPT's L0-L5 over-classification, OPUS's
two-file split that requires a runtime decision, COWORK's BUILD-LOG-
embedded approach that re-pollutes the audit log it was trying to clean.
One file, one shape, three reasons it gets written.

### 3.6 How much frontmatter?

**Verdict: Minimum-viable, with one mechanically-checkable field.**

All three propose more frontmatter. The convergent recommendation is
suspect (§1.4). The acid test: which field, *if missing*, would have
caught one of the actual observed failures?

- `status` (active/draft/superseded/archived): would not have caught
  uncommitted constitution-class files.
- `last_updated`: would not have caught self-grading or no-benchmark.
- `covers_through: <commit SHA>` (OPUS): mechanically-checkable;
  catches "STATE.md was last touched at commit X and the working tree is
  now at commit Y" — directly the staleness mode.
- `last_verified` (COWORK): same property as `covers_through`, named for
  the discipline rather than the mechanic.
- The other 5–9 fields CHATGPT proposes: not directly tied to an observed
  failure.

Adopt `status`, `last_updated`, `covers_through`, `supersedes`,
`superseded_by`. Five fields. Skip the rest until a specific failure
demands them.

### 3.7 Do `.planning/templates/`, `decisions/`, `checkpoints/`,
`incidents/`, `phase-reviews/`, `verification/`, `critiques/` need to
exist now?

**Verdict: No. Three of them, lazily.**

The convergent recommendation is suspect (§1.4). Adding empty directories
is performative. The directories that have a specific use against an
observed failure:

- `.planning/archive/` (all three): yes, because plan supersession needs
  a destination.
- `.planning/STOP-NOTE.md` workflow (per §3.5): yes, but no directory
  needed until archiving.
- A reviewer-checkpoint output location (OPUS `.planning/checkpoints/`,
  COWORK `.planning/reviews/<date>/REVIEWER-CHECKPOINT.md`): yes; the
  COWORK location is simpler — reuse the existing `.planning/reviews/`
  structure rather than a new sibling directory.

Skip `templates/`, `decisions/`, `incidents/`, `phase-reviews/`,
`verification/`, `critiques/` for now. Add them when their first instance
needs to land.

### 3.8 Is the loop premise itself viable? (OPUS §11)

**Verdict: cannot be adjudicated from current evidence.**

OPUS uniquely raises that `VISION.md`'s graduation criteria 3, 4, 6, and
9 require human or expert judgment that an automated loop is
structurally bad at producing for itself. This is the most strategic
observation in any of the three reviews. It is also forward-looking and
empirical: only operating a `/goal` loop with strong reviewer gates for
some weeks, against a real benchmark, can settle whether the human
review attention is augmented or replaced.

Decision: surface this to the user as an open question (§5).

## 4. Actionable recommendations

Ordered by leverage × reversibility. Each carries a one-line rationale, a
P (protocol) or T (tooling) tag, and a falsification test. I have pruned
to seven. Five would have been better; seven is honest about what the
adjudication produced.

### R1. Commit the constitution-class files now.

`git add VISION.md RUNTIME-CONSTITUTION.md docs/reuse-and-refresh.md
schemas/refresh-delta.schema.json skills/consult.md`, plus a deliberate
review of the 15 modified-tracked files to commit or revert each. One
transaction, named branch (`workflow-reset`), merged to main with a
checkpoint reviewer disposition (R5).

**Tag:** P (protocol), one-time action.

**Rationale:** COWORK F1 verified; uncommitted constitution-class files
are the loudest possible branch-hygiene failure (`AGENTS.md:24`). The
authority chain in `AGENTS.md`, `STATE.md`, and `CURRENT-PLAN.md` rests
on files a clean clone of HEAD does not contain. Adjudication 3.1.

**Falsification test:** immediate — `git ls-files VISION.md
RUNTIME-CONSTITUTION.md` must return both paths after the action. A
clean `git clone` of the repo at the merged commit must produce a
working tree containing all governance-class files cited as authority.

**Reversibility:** complete; commit can be reverted in one operation.

### R2. Pin a real-world benchmark repo and gate Phase B+ claims on it.

Add `tests/fixtures/bench/` as a vendored snapshot or git submodule of a
small unfamiliar repo (an MCP server is the candidate
`STATE.md:64` already names). Add a phase-acceptance gate: no
`phase: passed` claim until one full `cbm run` against the benchmark
produces a schema-valid handoff with a Skeptic challenge whose
`competing_reading` is not the hard-coded string at `cbm/cli.py:1294` or
`:3749`. Add a direct-examination-ratio gate: smoke runs against the
benchmark must report `files_examined_directly / files_in_scope ≥ 0.30`
(lightweight) before any `phase: passed` claim above Phase A.

**Tag:** P + T (CI gate plus benchmark fixture).

**Rationale:** Convergent across OPUS / CHATGPT / COWORK. Until this
gate exists, the project cannot honestly claim any phase past A is
passed. The 1/35 direct-examination ratio (COWORK V3, verified at
`run-phase-a-final-audit/handoff.md:30-31`) is the empirical floor the
gate is set above.

**Falsification test:** immediate (the benchmark exists, the gate
exists) and operational (over 30 days, every Phase B+ pass claim cites a
benchmark run). If the gate exists and the loop closes phases anyway,
the gate is decoration.

**Reversibility:** medium. Removing a benchmark fixture is one commit;
removing a gate the loop has begun to depend on may require negotiating
phase claims already made under it.

### R3. Adopt the strict phase-outcome rule and re-audit B–F.

A phase has two outcomes: `passed` (every conjunctive acceptance criterion
in `docs/roadmap.md` met by the deliverable the criterion named) or
`not passed`. Slice-level entries record `evidence_kind:
deterministic-substitute` when applicable; that fact does not graduate
the phase. Re-audit Phase B, C, D, E, F: each becomes `not passed` unless
the agentic deliverable named in the criterion exists. Record the gaps in
`STATE.md`. Slices remain shipped; phase claims are retracted, not
deleted.

**Tag:** P (rule) + one re-audit slice.

**Rationale:** Adjudication 3.3. OPUS's strongest recommendation,
sharpened by COWORK's "partial pass is oxymoron" objection. Without this,
`STATE.md` continues to list phases as "partially satisfied" while the
roadmap criteria require things the implementation does not produce —
which was the drift mode that produced the entire BUILD-LOG.

**Falsification test:** immediate — after the re-audit, `STATE.md`
records each of B, C, D, E, F as `not passed` (or, in any case where the
agentic deliverable does land, `passed` against verifiable
benchmark-repo evidence). If the re-audit produces five `passed`s, the
re-audit is rubber-stamping.

**Reversibility:** low. Once phases are formally retracted, restoring
the prior pass claims would require new evidence. This is intentional —
the cost of false claims is what the rule corrects.

### R4. Replace the per-slice self-critique block with a tighter cadence.

Edit `AGENTS.md` §"Self-critique cadence": critique runs only at (a)
plan completion, (b) phase boundary, (c) before any merge to main, (d)
on any kit deviation, (e) when a drift signal fires (R6). Per-slice
critique is removed. The 98 historical critiques in `BUILD-LOG.md` move
verbatim to `.planning/archive/2026-05-01-historical-critiques.md`
(read-only). Future critique entries land in
`.planning/critiques/<date>-<slug>.md`, one file per critique.

**Tag:** P, one-time migration.

**Rationale:** Adjudication 3.4. COWORK F4 verified — 98 critiques across
100 entries is checklist-noise, not adversarial review. Reducing cadence
raises signal at marginal cost. OPUS's full removal goes one step too
far; introspective discipline at boundary moments is worth keeping.

**Falsification test:** operational, 30 days. After the change, the
ratio of critique entries to slice commits should fall below 1:5 and the
proportion of critique entries that surface a substantive change (a
revert, a supersede, a stop-and-surface) should rise above 1:3. If
critiques continue to be 1:1 with slices and continue to all pass, the
cadence change failed.

**Reversibility:** complete; one-line edit to AGENTS.md.

### R5. Define a single checkpoint reviewer agent and run it now.

Add to AGENTS.md a "Checkpoint reviewer" section with: (1) isolated
context — reviewer reads `VISION.md` (or its compact summary), the
roadmap criteria for the closing phase, the diff since the last
checkpoint, the current `STATE.md`; not the producer's self-critique;
(2) blocking authority — the loop cannot mark a phase `passed` or merge
to main without an accepted checkpoint disposition; (3) output location
`.planning/reviews/<date>-<slug>/CHECKPOINT.md` (reuse existing
directory; no new directory needed); (4) cross-model preferred. Run
this checkpoint once, now, against the current state — the planning
reset is the natural first checkpoint.

**Tag:** P (rule) + one immediate run.

**Rationale:** Convergent (OPUS §6, CHATGPT §"Mandatory reviewer
triggers", COWORK V5/R2). The single largest workflow problem named in
all three reviews is the absence of any non-self gate. The minimum is
one well-defined reviewer agent with blocking authority. CHATGPT's
prompt-preflight checklist is worth folding into the checkpoint
definition (the prompt for each checkpoint must pass it before the
reviewer is launched).

**Falsification test:** operational, first invocation. The first
checkpoint must produce ≥1 finding the producer's self-audit missed and
that the producer cannot dismiss. If the first checkpoint endorses
everything the producer claimed, either the protocol is broken or the
producer was right; the bar is that broken-protocol cases are
detectable by re-running the checkpoint with a different reviewer model.

**Reversibility:** complete; AGENTS.md edit can be reverted.

### R6. Add `cbm-loop-status`: a single command that reports drift-signal violations.

One CLI subcommand (`python3 -m cbm loop-status` or
`cbm-loop-status`) that checks, in one read pass:

- Branch hygiene: current branch is feature-branch; no
  constitution-class file is uncommitted and unstaged for >1 session;
  uncommitted file count <N (calibrate to 5).
- Plan freshness: `CURRENT-PLAN.md`'s
  `covers_through` SHA is reachable from HEAD without intervening
  commits to files in its `authority_scope`; `Last updated` is more
  recent than the most recent commit it claims to gate.
- Build-log entropy: H2 entries since last `STATE.md` update ≤ 10.
- Plan-less commits: ≤ 2 commits since last `CURRENT-PLAN.md` update.
- Untouched-benchmark gate: if the most recent phase claim is B+, a
  benchmark run id appears in the most recent 30 days of `.research/`.
- Same-mistake-twice: parse the last N BUILD-LOG entries for repeated
  `correction:` or repeated artifact paths in `discovered_falsified_assumption`.
- Direct-examination ratio: most recent smoke run on the benchmark has
  ratio ≥ threshold.
- Self-critique no-finding streak: last K critique entries all
  concluded with no finding ⇒ flag.

The command exits nonzero on any violation. AGENTS.md requires running
it at session start and at slice end. Violations write a `STOP-NOTE.md`
(per §3.5) and surface to the user.

**Tag:** T (tool) + P (rule).

**Rationale:** OPUS §5.1 contributed the table of numerically-defined
signals; COWORK §D contributed the calibration against observed drift;
CHATGPT contributed the L0-L5 framing (collapsed). The discipline that
makes this run is `AGENTS.md`'s pre/post-slice gate; without that, the
script is decoration.

**Falsification test:** immediate (the script exists and exits nonzero
on a synthetic dirty tree) and operational, 30 days. Over 30 days of
`/goal` execution, the script should fire ≥M times where M >0 and ≤
some upper bound (calibrate). If it fires zero times, the loop is
hiding violations or the thresholds are too lax.

**Reversibility:** complete; one CLI subcommand that can be removed.

### R7. Stop accepting "current planning reset is adequate" as the
operating posture; treat the next code slice as gated on R1–R5.

The current `CURRENT-PLAN.md` lists eight pending steps, of which steps
4–6 ("synthesize and disposition," "update docs after disposition,"
"implement next code slice") are explicitly gated on this review. R1–R5
above are the disposition. AGENTS.md's "default proceed" posture must
be amended to: *default proceed inside an active CURRENT-PLAN.md whose
expected write set authorizes the work and whose `cbm-loop-status` check
passes*. Outside that envelope, write a STOP-NOTE and surface.

**Tag:** P, AGENTS.md edit.

**Rationale:** the entire diagnosis stack rests on the observation that
the previous "default proceed" produced 100 self-graded slices on one
unmerged branch. The amendment is small — one phrase change in `AGENTS.md`
and a wired check in `cbm-loop-status` — but it is the rule that makes
R1–R6 actually load-bearing.

**Falsification test:** operational, 7 days. After the amendment, the
loop should pause at least once for a non-trivial reason (a `STOP-NOTE`
gets written and the user reviews it) and should *not* pause for trivial
reasons (false-positive rate <30%). If the loop pauses every slice,
thresholds are too tight; if it never pauses, the rule is decorative.

**Reversibility:** complete; rule rollback is a one-line edit.

### Items deliberately not recommended

- A `templates/` directory, an `incidents/` directory, a `decisions/`
  directory, a `phase-reviews/` directory, a `verification/` directory.
  Add when first instance needs them; not before. (CHATGPT §3, OPUS §3.)
- The 9-field frontmatter schema. Five fields (R3.6) suffice.
- The L0-L5 incident severity taxonomy. Replaced by single STOP-NOTE.
- The full `cbm-docs-status` CLI. Most of its function is in
  `cbm-loop-status`; add the doc-stale specific check only when an
  observed staleness mode escapes `cbm-loop-status`.
- Re-architecting `BUILD-LOG.md` rotation now. Rotate when the file
  passes a threshold (1500 lines is reasonable); not before.
- The full Phase B re-audit through phase-review packets per CHATGPT §8.
  The retraction (R3) is the substantive correction; a dedicated
  phase-review packet adds ceremony without new evidence.

## 5. Open questions for the user

Forward-looking decisions that cannot be adjudicated from current
evidence.

### 5.1 Is `VISION.md` a viable target for an automated `/goal` loop at all?

OPUS §11 raises this. Graduation criteria 3 (Skeptic factual catch rate
vs. domain experts), 4 (Skeptic interpretive challenge precision), 6
(coverage honesty with zero exceptions), and 9 (pedagogical adequacy)
require human or expert judgment that an automated loop is structurally
bad at producing for itself. The recommendations above (especially R5,
R6) treat reviewer gates as a partial fix. They may not be enough.

Two possible answers:

- *Reviewer gates are sufficient.* Run R1–R7 for 30 days; if drift
  signals fire at a useful rate and the checkpoint reviewer surfaces
  findings the producer missed, the human review attention is being
  amplified, not replaced.
- *Reviewer gates are insufficient.* The loop needs scheduled
  human-in-the-loop checkpoints (e.g., user reviews the most recent
  CHECKPOINT.md output once per N hours of unattended execution). This
  is structural, not a fallback.

This question is settled only by operating the loop under R1–R7 for some
weeks. I cannot pre-decide it from the evidence in the repo today.

### 5.2 Does the architecture disposition settle what counts as a
"phase," or does workflow set that vocabulary?

The prompt mentions an existing architecture disposition. As of this
disposition's writing,
`.planning/reviews/2026-05-01-strategy-workflow-vision-audit/OUTPUT-ARCHITECTURE-DISPOSITION-CLAUDE-COWORK.md`
does not exist on disk; only the architecture review packet
(`OUTPUT-ARCHITECTURE.md`, `OUTPUT-ARCHITECTURE-CHATGPT.md`,
`OUTPUT-ARCHITECTURE-CLAUDE-COWORK.md`) and the disposition prompt
(`PROMPT-ARCHITECTURE-DISPOSITION.md`) are present. R3's strict
phase-outcome rule depends on a stable definition of "phase," which is
ultimately an architecture question. If the architecture disposition (when
written) re-defines phases in terms of runtime-agent backend slots rather
than the current roadmap A–F sequence, R3 should be re-stated against the
new phase taxonomy.

Decision: defer R3's exact criteria language until the architecture
disposition lands. Adopt R3 in spirit immediately; harden the
vocabulary when the architecture disposition is in.

### 5.3 Should the dev agent invoke Codex CLI as a subprocess for
checkpoint reviewers (R5)?

`.planning/CURRENT-PLAN.md:38-40` proposes Codex CLI subprocess as the
runtime backend. It is unclear whether the same pattern should be the
mechanism for *checkpoint reviewers* (which run during the build, not at
runtime). A cross-model checkpoint reviewer requires a non-Codex
invocation channel; otherwise the reviewer is the same model as the
producer with a different prompt — better than self-critique, but not
the cross-model gate the reviews call for.

Decision: this is an architecture question. Defer to the architecture
disposition. R5 holds in either case; the implementation channel is what
shifts.

### 5.4 What is the load-bearing test of whether R1–R7 worked?

The bar I committed to in the prompt: a `/goal` loop run unattended for
a week is measurably more aligned with `VISION.md` if R1–R7 are in force,
and a returning human reviewer can verify that alignment in under an
hour.

The tests:

- *In under an hour:* the human reviews `STATE.md` (≤250 lines),
  `CURRENT-PLAN.md` (≤100 lines), the most recent CHECKPOINT.md, and
  the output of `cbm-loop-status`. If any of those are missing or
  inconsistent, the protocol failed an audit-survivability test.
- *Measurably more aligned:* over 7 days, the loop produces ≥1 STOP-NOTE
  for a substantive reason (a real drift signal); ≥1 CHECKPOINT.md with
  a finding the producer missed; phase claims do not regress (no
  retraction beyond what R3 already retracted); benchmark runs on the
  R2 fixture clear the direct-examination ratio at least once.

If those operational targets are not hit at 30 days, the protocol needs
revision and §5.1 needs to be answered "insufficient."

## 6. One-paragraph summary

The three reviews converge on five diagnoses (self-validation theater,
overloaded BUILD-LOG, nominal phase boundaries, no real benchmark, no
non-self review gate) and diverge on the protocol that fixes them. COWORK
has the strongest evidence discipline and identifies two
load-bearing facts the others miss (uncommitted constitution-class files;
3% direct-examination ratio on the only existing smoke). OPUS has the
most operational drift-signal table and the only review that pushes back
on the loop premise itself. CHATGPT is the most comprehensive and the
most prone to process-mongering. The corrective protocol is small: commit
the governance files; pin a real benchmark; retract phase pass claims
that rest on deterministic substitutes; cut self-critique cadence;
define one checkpoint reviewer with blocking authority; ship one
`cbm-loop-status` script that checks numerical drift signals; flip the
default-proceed posture to default-proceed-inside-a-valid-plan. Most of
the additional templates, directories, frontmatter fields, and severity
taxonomies the reviews propose are convergent because they are familiar,
not because they would catch the failures the reviews documented. Skip
those until a specific failure demands them.
