# VISION

This document describes the end-state. What CBM is when it is no longer a seed kit and no longer a beta — when it is a fully-fledged epistemic instrument for working with unfamiliar code.

It is intentionally separate from `roadmap.md`, which is about phases and what gets built next. The roadmap answers *how*. This document answers *what for*, and *when do we know we got there*.

## The point

CBM exists because the work of understanding a codebase well enough to change it is mostly hermeneutic, not structural. Structure can be extracted by tools. Understanding cannot. But the moment you ask an agent to do the understanding part, the agent fluently produces text that *looks* like understanding while quietly fabricating citations, smuggling interpretive claims in as facts, and erasing the genuine disputes that careful readers have to carry.

CBM's contribution is to make the *form* of understanding legible: every claim labeled by register, every claim citing real bytes, every interpretive disagreement carried in the artifact rather than collapsed. The system is not better at understanding code than a careful human reader. The system is better than a careless agent at *not pretending to understand*. The asymmetry is what makes it useful.

That asymmetry is the thesis, not yet a finished measurement protocol. A mature CBM must eventually name the comparator, rubric, and evaluation procedure that make "not pretending to understand" measurable rather than merely persuasive.

The mature version of CBM is the version where this asymmetry is reliable enough that humans treat the system as a colleague whose work needs review, not as a black box whose output needs forensics.

## The thing the system is doing

A user has a repository they did not write and a goal they care about. They want, at the end of an hour or a day, to know: which surfaces in this codebase matter for this goal? What's connected to what? What claims about this code are settled, what claims are reasoned-from, what claims are interpretive? Where is the dispute live?

CBM's deliverable is not a chatbot transcript. It is a directory of artifacts on disk: a deterministic baseline of what the codebase *is*, interpretive maps of what the codebase *does*, intervention or findings cards bound to the user's goal, an evidence ledger of every citation introduced, an uncertainty register of every known unknown, and a handoff that summarizes what the system found and — equally — what it didn't find, couldn't determine, and currently disputes.

A mature CBM run produces a handoff that a senior engineer who has never used the system can read and act on without further explanation.

## What mature looks like

Six properties distinguish the mature system from the seed.

**It works on first contact.** A user clones a repository they have never seen, runs `cbm-init` with a goal, and gets a usable handoff in a predictable time window. No project-type pack required for basic adequacy; the universal heuristics produce a defensible map of any reasonably idiomatic codebase. Project-type packs make runs better, not feasible.

**Its claims hold up.** When the system reports a factual claim with `confidence: high`, a domain expert agrees on inspection. When the system reports an interpretive claim with a challenge, the challenge is one the expert recognizes as worth raising. False-high-confidence rate is below the rate at which a careful human reviewer would make the same mistake. The Skeptic catches non-trivial defects in non-trivial runs.

**It is honest about what it didn't do.** Coverage reports distinguish files examined directly from files inspected via extractor only. Uncertainty registers carry real unknowns, not perfunctory disclaimers. Handoffs name the things the run could not look at and why. The system never reports a 100% coverage figure because the figure would be either trivial or false.

**It composes with humans.** Every claim resolves to source bytes in O(seconds). Reviewers can challenge any claim and the system records the challenge structurally — competing reading, competing evidence, interpretive axis, relation to original. A reviewer's challenges become first-class artifacts that participate in the system the same way the Skeptic's do. The handoff bundle drops cleanly into PR descriptions, RFCs, or knowledge bases without translation.

**It composes with itself across time.** A repository accumulates a `.research/` directory. Runs from six months ago are valid inputs to runs today, with staleness automatically detected. The corpus of completed runs across many repositories becomes a reference: how does this team handle plugin systems, where does that codebase put authority, what kinds of unknowns recur. The system is one whose value increases with use.

**The interpretive discipline pays off.** Cards labeled `claim_register: interpretive` are challenged at higher rates than cards labeled `factual` — and the challenges are mostly substantive, not pedantic. Cards with non-empty `dependent_challenges` correlate with downstream surprise: when a card hides contestation, things go wrong; when a card carries contestation, the human is prepared. The three-register model is not just a labeling exercise; it changes outcomes measurably.

## Minimum useful CBM

Before the system can claim it is more than a deterministic mapping kernel, it must complete one runtime-agent-produced run on a pinned external codebase. The minimum useful demonstration is a surface map produced by a real Surface Mapper, reviewed by a real isolated Skeptic, with at least one non-trivial interpretive claim or challenge grounded in citations, and a handoff that passes CBM validation without templated patches. Deterministic baselines are necessary evidence, but they do not by themselves satisfy this floor.

## The ideal version

Maturity is the floor. The ideal version is the ceiling: what CBM is when every design choice pays off, the discipline holds, and the work attracts practitioners who push it furthest.

**Reading the artifact replaces reading the codebase, for some classes of question.** Not because the system has substituted for understanding. Because the system's reading, on a particular question, is more careful than the user's would have been in the same time. The artifact earns the right to be read as a primary source for that question. An engineer onboarding to a 200kLOC codebase reads the CBM corpus on it for two days and is functional, where reading the code itself would have taken six weeks. A maintainer making a refactor decision reads the cards rather than re-traversing the dependency graph by hand. A postmortem starts by pulling the run from before the breaking change and finds, in retrospect, that the surface that broke was already marked `contested`. The artifact has earned the right to be a primary source. This is the strongest claim a tool of this shape can make and the only one worth aiming at.

**The Skeptic's interpretive challenges become contributions.** On serious codebases, the challenges raised in interpretive mode are themselves readings worth circulating. People cite specific challenge ids the way they cite blog posts or RFCs — `chl-00482 on commit X of project Y` becomes a coherent reference in design discussions. The Skeptic gets good enough that its readings, where they survive review, are insights rather than defect-catches. Some interpretive challenges become the entry points to design discussions the team would not have had otherwise.

**The interpretive register is humanistically serious.** A card on a serious codebase contains interpretive claims that people who know the code learn from. The hermeneutic discipline is not just careful labeling — it is genuine reading work. A senior engineer reading a CBM card on their own codebase encounters readings of their own code that they had not considered, grounded in citations they recognize. The interpretive register, taken seriously, makes room for the kind of reading that close-reading-as-a-practice has always been about: not summary, not paraphrase, but a defended claim about what the text is doing.

**Multi-perspective adversarial review.** The Skeptic is no longer a single role; it is a panel with documented frames. Security skeptic, performance skeptic, accessibility skeptic, maintainability skeptic, sustainability skeptic — each with isolated context and a stated stance. Interpretive challenges come from articulated positions; the producer engages the position, not anonymous skepticism. The challenge graph becomes structurally rich enough to be its own object of study: which positions tend to challenge which kinds of claim, where positions converge, where they remain irreducibly different.

**The corpus becomes empirical material.** Tens of thousands of runs across thousands of repositories, indexed and queryable. When someone asks "how do plugin systems usually work in Python servers," or "what are the common identity-distortion failure modes in agent runtimes," the answer comes from indexed evidence rather than impressionistic priors. Cross-project synthesis is a first-class feature, with the same citation discipline at the meta level: "23 of 28 sampled MCP servers had a single registry surface; 5 had parallel registration paths" cites the runs that found it. The corpus is itself a piece of evidence about how software is actually built, and it can be reasoned from.

**The discipline transfers.** People who work extensively with CBM read code better afterward — outside the system, with no tool running. The three-register claim model, the citation discipline, the unknown-as-first-class instinct become habits of mind. The system is teachable, and practitioners teach it. CBM artifacts get used as teaching material in onboarding, in review training, and in graduate-level coursework on software engineering and on hermeneutics applied to artifacts beyond code.

**Cross-domain travel.** The schemas and discipline ship successfully to legal corpora, scientific literature reviews, policy analyses, archival research, philological work. CBM-on-code is the original instance; CBM-the-framework handles "Section 1031 grants the IRS authority X," "this paper's central claim depends on assumption Y," and "this code's primary workflow runs through path Z" with the same three-register/contestation machinery. Each domain has its own extractors and packs; the kernel and the discipline are shared. The kernel becomes a small but distinctive contribution to the broader question of how AI systems should mediate between humans and large bodies of evidence.

**It is understated.** The mature CBM is, in personality, an editor — careful, exacting, quiet, indispensable. It does not perform helpfulness. It does not push features, suggest follow-ups, pad output, or close every artifact with a "let me know if you'd like me to elaborate." It produces what it produces, lets the artifacts speak, and stays out of the way. Users come to trust it precisely because it does not push. The work is the work; the artifacts are the artifacts; the user knows what to ask for next, or asks no more.

**It attracts the practitioners who can push it.** Mature CBM is shaped by — and shapes — projects whose own methodologies share its commitments: vision-first-class and revisable, evidence-discipline as load-bearing, interpretive moves kept visible, premature closure refused. Projects of this kind use CBM well, push it on the things that matter, and contribute back the patterns that the kernel and discipline incorporate. The system grows by being used by people who would not tolerate it doing less than what it claims to do.

The single line: CBM, ideal, is the system you reach for when the question is hard enough that you would otherwise reach for a senior reviewer with a free week and the patience to actually read.

## The user the system serves

The mature CBM is for a person who:
- Reads code carefully, knows that careful reading is hermeneutic, and is unwilling to outsource judgment.
- Wants a tool that does the mechanical work reliably and labels its interpretive work honestly, so they can spend their attention where attention matters.
- Is comfortable with uncertainty being reported as content, not as a disclaimer footer.
- Can read a handoff bundle as a piece of writing, not as a debug log.

The system is not for a user who wants a one-line answer to "is this codebase good." It is for a user who wants the ground truth they need to form their own answer, with the system's own reading of the ground truth marked clearly enough that they can disagree.

## The end-state experience

A mature run feels like this.

The user runs `cbm-init` against a repository at a specific commit, with a goal in plain language and a mode appropriate to scope. The system's first artifact is the codebase map — purely deterministic, no judgment, the kind of thing they could have produced themselves with `find` and `grep` and patience. Reading it confirms the system has the same view of the structure they do.

The next artifact is a surface map. They see authorities classified by kind, dependency edges with extractor ids, and — because the codebase has the usual dynamic patterns — an `unknowns` block that names specific things the static extractors miss. Each authority has a register: most factual, some interpretive. Reading the interpretive ones, they recognize the moves the system is making. They might disagree with the centrality assignment for one authority; they raise a challenge; the artifact updates to carry both readings.

The Skeptic runs. Two factual defects flagged — a citation in the verification subsection points at a deleted file, a confidence inflation on an inferred edge. The mapper fixes both. One interpretive challenge raised — the Skeptic argues that what the mapper called the "primary" workflow is one of two co-equal workflows in this codebase. The mapper accepts the challenge as alternative; the artifact carries `claim_status: contested` on the centrality claim.

Cards are produced for the goal. The card depending on the contested centrality claim has it in `dependent_challenges`, and `confidence: medium` rather than high. The card's `recommended_next_slice` is exactly the experiment that would adjudicate the dispute. The user reads the card, looks at the recommended slice, sees that it would resolve the question in twenty minutes of reading, and does it. The challenge resolves; the card moves to high confidence; they proceed.

At handoff, the bundle reports: 47 files in scope, 18 examined directly, 29 inspected via extractor only; 312 claims by register (228 factual, 71 inferential, 13 interpretive); 4 challenges raised, 3 resolved, 1 left open and adjudicated by the user; 2 contradicted claims now superseded; 8 unknowns on file. The handoff prose summarizes what changed, what the system could not determine, and where the live disputes are. They forward it to a colleague. The colleague reads it without further explanation.

That is the experience. Specific, evidence-bound, honest about its limits, useful as a piece of writing.

## Deployment shape

The near-term CBM product is a local CLI that produces artifacts on disk for a repository at a pinned commit. The CLI owns run setup, producer dispatch, artifact locations, and validation. Platform hooks and Codex/Claude session adapters may improve ergonomics inside specific agent runtimes, but they are not the source of correctness and not the deployment model.

## Graduation criteria

CBM exits beta when, on a representative sample of unfamiliar mid-size repositories (5k–50k LOC, multiple languages, mixed project types):

1. **Cold-start time-to-handoff** is under 60 minutes in standard mode for ≥80% of runs.
2. **Citation resolution** is at 100% on every artifact promoted to `validated` (anything else is a hook bug, not a quality issue).
3. **Skeptic factual-defect catch rate** matches a domain expert's catch rate within a small constant — measured against ≥30 runs reviewed by experts blind to the Skeptic's findings.
4. **Skeptic interpretive-challenge precision** is high enough that experts agree the challenges are worth raising in ≥75% of cases. (Recall is harder to measure and not a graduation criterion.)
5. **Compaction recovery** succeeds without human intervention in ≥99% of session restarts.
6. **Coverage honesty** holds: every claim about a file's role can be traced to that file being in `files_examined_directly`, with zero exceptions in audit.
7. **Contestation propagation** holds: every card whose dependencies have non-active claim status carries the contestation in `dependent_challenges`, with zero exceptions in audit.
8. **Cross-platform parity**: the same kernel, schemas, and skills run on at least two orchestration platforms (Codex and Claude Code, or Codex and a custom runner), producing equivalent artifacts on the same input.
9. **Pedagogical adequacy**: a careful reader new to the system can produce a valid surface map and intervention card by hand from `RUNTIME-CONSTITUTION.md` alone, on a small repository, within a working day. The discipline is teachable, not just executable.
10. **Productive use across project types**: the system has been used to produce non-trivial value on at least five distinct project types (e.g., web framework app, MCP server, CLI tool, library, monorepo subsystem) without project-type packs being required for basic adequacy.

These ten conditions are conjunctive. Failing any of them means the system is still a beta — it might be useful, but it is not yet what it should be.

## What the system will not become

Naming the anti-vision is part of the vision.

CBM will not become a chatbot. It will not converse about codebases. The deliverable is artifacts, not dialogue. The agents speak to each other through artifacts on disk; the user reads the artifacts. If a user wants conversation, they bring the artifacts to a different system.

CBM will not become a code generator. It does not edit source files. Cards recommend changes; humans (or other systems) make them. The boundary is not a limitation; it is a commitment. Systems that map and systems that mutate have different epistemic shapes, and combining them in one agent is how false confidence gets manufactured.

CBM will not become a code reviewer in the PR sense. It is a research instrument, not a gatekeeper. PR review involves social judgment — whether this change is *good*, given the team's priorities, the timeline, the politics. CBM stays out of all of that. It produces material that informs review; it does not perform review.

CBM will not become a confidence-aggregator. It will not produce a single "code health" number. Every claim has its own confidence, its own register, its own status. There is no system-level confidence because there is no system-level claim. Aggregating to a single number throws away the structure that makes the system useful.

CBM will not become a marketplace of community-contributed packs. Goal packs and project-type packs are part of the design. Their composition is not a community process; it's a curated extension of the kernel by people who can keep the discipline.

CBM will not perform fluent uncertainty. Confidence is not adjusted to sound humble; it is calibrated to evidence. The system would rather be flatly wrong and corrected than ambient-hedged and unfalsifiable. If the artifact says high confidence, it means high confidence. If it says low, it means low. The vocabulary is small and is used as small.

## The broader stakes

The reason this matters beyond the immediate utility: agentic systems are becoming the default mediator between humans and large knowledge bodies. Most of those systems are designed to *replace* the cognitive work — to give the human a confident summary they can act on without reading the source. This is a design choice, and it is the wrong one for any domain where being wrong has consequences.

CBM is a small argument that there is a different design shape: agentic systems that *instrument* human reading rather than substitute for it. That make their work auditable rather than fluent. That carry dispute rather than collapse it. That are, in the technical sense, hermeneutic — concerned with the conditions under which a reading can be defended.

If CBM matures, it is one example of that shape working in one domain. Other domains — legal research, scientific literature review, policy analysis — have the same problem. The schemas and discipline travel.

That is not a promise the kit makes. It is a horizon the kit is working toward.

## Open conjectures

Things that the mature design must address, but the seed kit does not yet.

The first two questions are v1-blocking for the runtime agent layer: the system must choose explicit behavior before it ships real producer/Skeptic interaction. The remaining questions shape later maturity and 2.0 work.

**Producer-argues-back protocol.** When the Skeptic raises an interpretive challenge, the producer can accept-as-alternative or accept-as-replacement. There is currently no protocol for the producer defending the original with new evidence. Whether such a protocol is worth implementing depends on whether real runs produce challenges where the producer plausibly has more evidence than the Skeptic. If they do, the protocol is necessary; if they don't, it's overhead.

**Claim-dependency modeling.** Interpretive claims often depend on each other. The schemas track claim *evidence*, not claim *dependencies*. When one interpretive claim is contradicted, the cascade behavior is unmodeled. The mature design needs a way to express claim dependencies and propagate status changes.

The remaining conjectures are not allowed to block the first runtime-agent benchmark, but they stay visible because they shape what a mature corpus becomes.

**Cross-run synthesis.** A mature CBM running on the same repository over months should accumulate something more than a directory of dated artifacts. The form of that accumulation — a knowledge graph, a longitudinal claim corpus, a periodic synthesis — is unspecified. Whatever shape it takes must preserve the discipline (every claim cites, registers are honored, contestation is carried).

**Human-in-the-loop challenge UX.** The schema supports human-raised challenges (`raised_by` is a free string), but the user-facing interface for raising one is not designed. A mature CBM has a clean way for a reviewer to challenge a claim and see the system's response; this is more than a CLI flag.

**The hermeneutic-circle problem.** Some interpretive claims are genuinely circular — A only makes sense given B, B only makes sense given A. Whether the schema and protocol can carry such pairs without forcing premature resolution is an open empirical question. The mature design either solves it or marks it cleanly as out-of-scope.

These are real questions. Some must be settled before the first runtime agent backend ships; the rest shape what 2.0 looks like. They go on the wall and stay visible.

## Coda

A line for the wall: CBM is mature when a careful reader can use it for an hour and come away knowing more about a codebase than they would have known after an hour of reading the codebase alone. Not because the system did the reading for them — but because it instrumented their reading well enough that they read more carefully than they would have otherwise.

This vision can change, but not silently. Revisions require a review or checkpoint artifact that names the pressure for change, the rejected alternatives, and the downstream planning docs that must be updated.

That is the bar. Everything else is implementation.
