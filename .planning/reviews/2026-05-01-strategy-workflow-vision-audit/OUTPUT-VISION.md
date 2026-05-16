# OUTPUT-VISION.md

Status: draft, independent review
Reviewer: Track C, vision quality
Last updated: 2026-05-01

## Executive verdict

`VISION.md` is a strong essay and a partly-failing engineering input. As a piece of writing, it sets a real bar, articulates a defensible thesis ("instrument human reading rather than substitute for it"), names anti-patterns, and lists graduation conditions. As a document an autonomous `/goal` agent will consult to choose what to build *next* on a given Tuesday, it under-prioritizes its own thesis, conflates destination with horizon, and lists a long catalog of mature-state features alongside MVP-load-bearing ones with no sequencing pressure. There is plausible evidence — though not proof — that this contributed to the current drift, in which most kernel/scaffold features (`.research/run-phase-b-*`, `cbm-bind`, `cbm-stale`, `cbm-consult`, refresh-delta, project-type-pack annotations, reuse) shipped while the runtime agent layer that the central asymmetry depends on remains unbuilt (`.planning/STATE.md:10-18`, `.planning/STATE.md:32-40`).

Recommendation: **keep the vision, but split it and tighten it**. Pull the "ideal version" and "broader stakes" sections into a `HORIZONS.md`. Reduce the graduation criteria to a smaller load-bearing core. Add an explicit **sequencing principle** that prevents kernel machinery from outpacing agent producers. Add an explicit **minimum-demonstration-run** condition that a kernel feature ships only when it is demonstrably load-bearing for an agent's actual reading work.

## Strengths of the vision

1. **The central thesis is sharp and load-bearing.** `VISION.md:9-13` (Section "The point") states the single asymmetry that justifies the project: not better-than-human at understanding, better than a careless agent at not pretending to understand. This is testable, falsifiable, and explains every other commitment in the kit. Most "destination" docs do not have a thesis this clean.

2. **The anti-vision is well-chosen.** `VISION.md:106-120` (Section "What the system will not become") names six concrete anti-patterns: chatbot, code generator, PR reviewer, confidence-aggregator, marketplace, fluent uncertainty. Most are correct *and* hard to want to violate accidentally.

3. **The graduation criteria are at least partially measurable.** `VISION.md:91-104`. Six of the ten conditions are either numerical (≥80%, ≥75%, ≥99%) or auditable (citation resolution at 100%, coverage honesty as zero-exception audit, contestation propagation as zero-exception audit). That is unusually concrete for a vision document.

4. **Open conjectures are named honestly.** `VISION.md:132-146`. Producer-argues-back, claim-dependency modeling, cross-run synthesis, human-in-the-loop UX, and the hermeneutic-circle problem are all flagged as unsolved rather than glossed. This is exactly the right move for a kit that wants to remain revisable.

5. **The user the system serves is described.** `VISION.md:65-71`. Explicit user persona pushes back on the temptation to make CBM a one-line-summary tool. The "for a user who wants the ground truth they need to form their own answer" framing is clear and load-bearing.

6. **The end-state walkthrough is concrete.** `VISION.md:77-87`. The numerical example (47/18/29 files, 312/228/71/13 claims by register, 4/3/1 challenge counts) gives an implementer something specific to aim a handoff at. That is rare and useful in a destination document.

## Ambiguities or failure modes

These are the places the vision is plausibly contributing to implementation friction.

### A. Destination, ideal, runtime, architecture, and workflow are conflated

`VISION.md` mixes at least five distinct content layers:

- **Destination** — what mature CBM is at v1.0 graduation (`§"What mature looks like"`, lines 24–37).
- **Horizon** — what excellent CBM is far past graduation (`§"The ideal version"`, lines 39–61).
- **Runtime experience** — concrete walkthrough of an actual run (`§"The end-state experience"`, lines 73–87).
- **Architectural commitment** — claims that imply specific implementation shapes ("every claim resolves to source bytes in O(seconds)" at line 33; "the same kernel, schemas, and skills run on at least two orchestration platforms" at line 100).
- **Anti-vision** — `§"What the system will not become"` (lines 106–120).

These are five different documents in trench coats. An agent operating from this vision under `/goal` cannot reliably tell which part of which section is binding for *next-month's work* versus binding for *eventual maturity* versus binding for *late aspiration*. When the destination is a 30-line description and the horizon is a 23-line description on the same page in the same prose register, an agent maximizing toward "make the vision more true" can pick from either pool. That is a recipe for the kind of drift `.planning/STATE.md:10-18` describes.

### B. The vision under-prioritizes its own thesis

The central asymmetry is stated once at lines 9–13 and then *not used as a sequencing rule*. Subsequent sections list properties additively ("It works on first contact. Its claims hold up. It is honest about what it didn't do. It composes with humans. It composes with itself across time. The interpretive discipline pays off."). All six are listed at the same level of priority. Five of them describe runtime-agent behavior; only the second ("its claims hold up") restates the central thesis directly. There is no explicit ordering, no "the asymmetry is the bar; everything else is supporting machinery."

If the vision said something like *"if a feature does not strengthen the asymmetry between fluent fabrication and instrumented honesty, it is deferred until a feature that does is shipped,"* the kernel-vs-agent imbalance documented in `.planning/STATE.md:32-40` would have a counter-pressure that today does not exist in the document.

### C. The graduation criteria are conjunctive, equally weighted, and pull in parallel

`VISION.md:104` says "These ten conditions are conjunctive." That is technically a strong gate, but operationally it tells an agent "all ten are equally load-bearing." Some of these criteria depend on *runtime agent quality* (3, 4, 6, 7) and some on *kernel/operational stability* (1, 2, 5, 8, 9, 10). The agent has no signal that 3 and 4 (factual catch rate, interpretive challenge precision) are *the asymmetry test* and the others are supporting. A `/goal` loop that hill-climbs on conjunctive criteria will hill-climb on whichever is most tractable next, which is *kernel work*: schemas, gates, validators, refresh deltas. This matches what shipped.

### D. The "ideal version" section pulls feature scope forward

`VISION.md:39-61` describes:

- Multi-perspective adversarial review with stance-isolated panels (security, performance, accessibility, maintainability, sustainability skeptics).
- Cross-domain travel to legal, scientific, policy, archival, philological corpora.
- Tens of thousands of indexed runs as queryable empirical material.
- Pedagogical transfer to onboarding and graduate coursework.
- "Reading the artifact replaces reading the codebase, for some classes of question."

These are good aspirations and they belong somewhere. They probably should not be in the same document an agent reads to plan this week's work, because they make every present-day feature feel insufficient and every architectural choice seem under-scoped. An agent reading "the corpus becomes empirical material" while planning next week's work has no defense against asking "should the schemas I'm shipping today already accommodate cross-domain non-code corpora?" — and that is the kind of question that produces overbuilt early kernels.

The same scope-creep risk applies to the "cross-platform parity" graduation criterion at line 100. Including it as a graduation gate (rather than a post-graduation portability concern) means the seed kit has to keep platform abstraction alive from day one, which currently shows up as `platform/codex/`, `platform/claude-code/`, and `platform/PORTABILITY.md` while the actual runtime agent layer the platforms host has not been built yet.

### E. Deployment, interface, and execution model are absent

The vision describes runs, agents, artifacts, and handoffs but does not commit on:

- **Interface model.** Is mature CBM a CLI? A daemon? An IDE plugin? An MCP server? An agent orchestrator? `VISION.md:77` says "the user runs `cbm-init`" but does not say *where* — local terminal? CI? Chat session? Codex `/goal` orchestration?
- **Process model.** Does CBM launch subprocesses (per the candidate direction in `.planning/CURRENT-PLAN.md:33-50`)? Does it run as a single in-process agent? Does it call an SDK? Does it require a host platform's hooks? The vision is silent.
- **Authority over the run.** When the vision says "the Skeptic runs," what process owns "running" it? The current ambiguity around Codex hooks vs. `cbm run` vs. `codex exec` subprocesses vs. parent-side validation (`.planning/CURRENT-PLAN.md:31-50`) is *exactly* the gap the vision did not close.
- **Failure model.** What happens when a runtime agent crashes mid-run? When the Skeptic's review itself is malformed? When two readings exist and the schema has no way to record the second? The runtime constitution gestures at recovery (§22) but vision does not commit to durability properties.

These omissions are load-bearing for current architecture work. The fact that `.planning/CURRENT-PLAN.md` is asking these questions in 2026-05 — Phase A's nominal calendar window was "week 1–2" — suggests the vision left them open longer than was useful.

### F. Anti-vision is partially over-committed

Most anti-vision items are correct. Two are brittle:

- *"CBM will not become a marketplace of community-contributed packs"* (line 118) is engineering policy, not destination. A mature CBM with a curated-by-people-who-can-keep-the-discipline pack ecosystem is plausibly *more useful*, not less. Locking it out here is overreach.
- *"CBM will not become a confidence-aggregator"* (line 116) is correct *as anti-pattern* but the absolute phrasing forecloses possibly-useful aggregations (e.g., "fraction of cards with non-empty `dependent_challenges`" as a per-run signal). The discipline that single-number confidence is forbidden is right; the discipline that no aggregation may exist is too strong.

These don't cause drift today, but they constrain v1.x in ways that may need to be reopened, which is the wrong shape for an anti-vision section.

### G. Aspirational language without engineering handles

A few lines are not actionable:

- *"The discipline transfers."* (line 53). What test would tell an implementer when this has happened? None given. Useful as essay; not useful as a vision pole.
- *"The interpretive register is humanistically serious."* (line 47). True if true, but no implementer can target it.
- *"It attracts the practitioners who can push it."* (line 59). A cultural property, not a software property.
- *"The hermeneutic-circle problem"* in open conjectures (line 144) is correctly acknowledged, but the vision treats it as *both* possibly out-of-scope *and* something the mature design must address. That ambiguity is the document's, not the problem's.

These are fine in a HORIZONS doc; they are noise in an engineering vision.

### H. The vision does not push verification discipline hard enough

`VISION.md:91-104` lists 10 graduation conditions, including "≥80% of runs under 60 min on representative sample of unfamiliar mid-size repositories (5k–50k LOC, multiple languages, mixed project types)." This is the closest the document gets to demanding empirical evidence on real codebases. But:

- There is no *pre-graduation* verification gate. A v0.1 kit can pass nothing on real codebases and still call itself in-progress.
- The current state — running smoke artifacts on the implementation's *own* repo (`.research/run-phase-a-*`, `.research/run-phase-b-*`) and `tests/fixtures/sample_repo/` — is exactly the failure mode this would have prevented. `.planning/STATE.md:60-64` flags it: "the existing fixture is intentionally tiny... A pinned small real-world test repo... is still needed for meaningful mapping evaluation."
- A vision that said *"every claim of capability requires a smoke run on a public repo at a pinned SHA"* would have created earlier pressure to establish that benchmark target.

### I. The vision encourages a long Skeptic taxonomy

`VISION.md:48-49` describes Skeptic as panel-of-stances at maturity (security, performance, accessibility, maintainability, sustainability). The architecture file (`docs/architecture.md:24-34`) caps roles at five templates with "new agent additions require justification." But the vision named six future Skeptic frames. An agent reading both will reasonably infer that adding skeptic frames is a path the project endorses. It probably is — but the vision's enthusiasm here is at odds with the architecture's parsimony, and that gap is unresolved.

## Possible contribution to current drift

The drift is real (`.planning/STATE.md:10-18`, `.planning/STATE.md:32-40`): kernel, schemas, gates, refresh, consult, registry, packs, staleness — all shipped or scaffolded. Runtime Surface Mapper / Skeptic / Synthesizer / Planner agent producers — not built. The implementation has every supporting piece for an asymmetry-demonstrating run *except the pieces that do the demonstrating*.

How much of this is the vision's fault?

**Plausibly contributing:**

- The vision's ten-criteria graduation list with no priority order means an agent picks tractable ones; kernel work is more tractable than agent producers, so kernel ships first (`§§ C, D` above).
- The vision mixes destination and horizon, which inflates the perceived importance of features like reuse-and-refresh trajectory artifacts that arguably should not have shipped before a single real Surface Mapper agent existed (`§ A, D`).
- The vision is silent on deployment/process model, which means architecture decisions get deferred at exactly the moment they would have prevented opportunistic kernel scaling (`§ E`).
- The vision does not establish a "kernel feature ships only with a paired agent demonstration" rule, which would have made the drift visible earlier (`§ B`).

**Plausibly not the vision's fault:**

- An autonomous `/goal` loop building toward a complex destination *should* prefer reversible, schema-validated, atomic-commit-friendly work in absence of an architectural anchor. That's a workflow/governance failure as much as a vision failure.
- The kernel work that shipped is mostly *correct*. The drift is in sequencing, not in quality.
- `AGENTS.md` already names the levels-confusion risk (line 11: "do not confuse the levels"). A stronger vision would not have rescued that if the agent did not internalize it.

The honest reading: the vision contributed to drift by **not pushing back hard enough against tractable-feature-first momentum**, not by being wrong about destination. The destination is right. The sequencing pressure is missing.

## Improvements to guide implementation quality

These are concrete edits to make `VISION.md` produce better code and a better-shaped repo.

### V1. Add a sequencing principle near the top

Insert after `§ "The point"`, line 13:

> **Sequencing principle.** A feature ships only when it strengthens the asymmetry between fluent fabrication and instrumented honesty, *and* a real run on a real codebase demonstrates that strengthening. Kernel machinery built faster than the agent producers that consume it is drift, not progress. When in doubt about what to build next, the next thing is whichever feature will most directly close the gap between current capability and the central asymmetry — usually that is an agent producer, not another schema.

This single paragraph, if it had existed, would have created the counter-pressure missing in `.planning/STATE.md`'s drift narrative.

### V2. Add a minimum-demonstration-run criterion

Add a new criterion to `§ "Graduation criteria"` and a parallel pre-graduation gate:

> **0. Minimum demonstration run (pre-graduation gate).** Before the system claims any version label past v0.1, a single end-to-end run on a public repository at a pinned SHA produces (a) an interpretive surface map with at least three interpretive claims correctly registered, (b) a Skeptic artifact that raises at least one factual defect *and* one interpretive challenge with competing evidence, and (c) a handoff a senior engineer not affiliated with the project can act on. Without this run, the system is not yet alpha. Smoke artifacts on the implementation's own repo do not satisfy this gate.

This would have foreclosed the current pattern of running Phase A and Phase B smoke against this very repo and treating that as evidence of foundation.

### V3. Reduce graduation criteria to load-bearing core

Restructure `§ "Graduation criteria"` from a flat list of ten conjunctive conditions into:

- **Core (the asymmetry test):** items 2, 3, 4, 6, 7 from the current list. These directly test "claims hold up," "honest about what it didn't do," and "the interpretive discipline pays off."
- **Supporting (operational):** items 1, 5 (cold-start time, compaction recovery).
- **Maturity portability (post-1.0 candidates):** items 8, 9, 10 (cross-platform parity, pedagogical adequacy, five project types).

Naming the supporting set as supporting frees the agent from treating cross-platform parity as a Phase A concern.

### V4. Add deployment shape commitment (or commit to deferring it)

The vision should either name the interface model — *"CBM is a local CLI invoked by a developer or by an autonomous agent loop; it produces artifacts on disk; it does not run as a long-lived daemon"* — or explicitly say *"interface model is undetermined and is the first architectural decision after vision is settled."* Either is fine. The current silence is the problem.

### V5. Move "the ideal version" to a separate file

`VISION.md:39-61` should become `HORIZONS.md`. It is excellent as a horizons document. As part of the working vision, it competes with the present-tense destination for an agent's attention. A short pointer in `VISION.md` ("see `HORIZONS.md` for what excellent CBM looks like past graduation") is sufficient.

### V6. Tighten anti-vision

Two specific edits to `§ "What the system will not become"`:

- Replace "CBM will not become a marketplace of community-contributed packs" with "CBM does not ship a community pack ecosystem at v1.0." (Open the door for v2.x without committing to it.)
- Replace "CBM will not become a confidence-aggregator" with "CBM does not produce a single system-level confidence number; structured per-run distributions over registers, statuses, and challenges are encouraged." (Forbid the bad aggregation, allow the useful one.)

### V7. Strengthen verification pressure

Add a sentence to `§ "It is honest about what it didn't do"` (currently `VISION.md:31`):

> Capability claims are evidence-bound the same way artifact claims are: the system does not claim to map a class of codebase until at least one such codebase has been mapped end-to-end with a citation-resolving handoff. Verification is by example, on real repositories, not by self-test against fixtures.

### V8. Add an explicit anti-pattern for kernel-without-agent

In `§ "What the system will not become"`, add:

> CBM will not accumulate kernel artifact machinery that has no agent producer consuming it. Refresh deltas, registries, packs, and lineage trackers are valuable only when they participate in real runs that strengthen the asymmetry. Premature machinery is drift, even when the machinery is correct.

This directly addresses the failure mode `.planning/STATE.md:32-40` documents.

## Improvements to guide workflow and verification

(Note: workflow review is owned by Track B. These are vision-level levers that *would* improve workflow if added.)

### W1. The vision should mandate that drift is detectable

A section on "what drift looks like" — with explicit named symptoms — would let the workflow protocols (the `/goal` loop, `BUILD-LOG.md` self-critique cadence, `.planning/STATE.md`) know what they are checking against. Symptoms to name: kernel features outpacing agent producers; smoke runs only against the implementation's own repo; graduation criteria treated as parallel rather than sequenced; anti-vision items quietly violated in implementation.

### W2. The vision should require the .research/ benchmarks be real

A vision-level rule that *all* `.research/` runs published as evidence of capability must be on external pinned repos would have forced the missing benchmark choice (`.planning/STATE.md:60-64`) months earlier.

### W3. The vision should prescribe a self-critique frequency tied to vision

`AGENTS.md:47-54` already prescribes drift/contract/reviewer-eye self-critique. A vision-level instruction that *the central asymmetry is the only drift question that matters* — not five-Skeptic-frames-vs-one, not cross-platform, not refresh-delta ergonomics — would sharpen the cadence.

## Recommended edits or sections

Concrete diff to `VISION.md`:

1. **Insert sequencing principle** after current line 13 (per V1 above).
2. **Insert "minimum demonstration run" pre-graduation gate** as a new §"Pre-graduation gate" before `§ "Graduation criteria"` (per V2).
3. **Restructure graduation criteria** into Core / Supporting / Post-1.0 portability sections (per V3).
4. **Add deployment shape commitment or explicit deferral** as a new short section near `§ "The thing the system is doing"` (per V4).
5. **Move `§ "The ideal version"` (lines 39–61) to `HORIZONS.md`**, replace in `VISION.md` with a one-paragraph pointer (per V5).
6. **Edit two anti-vision items** for over-commitment (per V6).
7. **Add capability-evidence sentence** to "honest about what it didn't do" (per V7).
8. **Add kernel-without-agent anti-pattern** to "What the system will not become" (per V8).
9. **Add brief drift-symptom subsection** to support workflow surface (per W1).

Optional further edits:

- Replace `§ "The broader stakes"` (lines 122–130) with a single sentence pointer to `HORIZONS.md` or a `MOTIVATION.md`. The cross-domain travel argument is strong but it is not vision; it is positioning.
- Add a line at the end of `§ "Open conjectures"` clarifying which conjectures must be addressed by graduation and which can remain open. Currently all five are equally unresolved; that is itself a sequencing failure.

## Questions requiring user decision

1. **Is the central asymmetry actually the bar, or is it one bar among several?** If the user agrees that "better than a careless agent at not pretending to understand" is *the* test and other properties are supporting, the sequencing principle (V1) is correct. If the user thinks the asymmetry is one of several co-equal goals — for example, the long view that the corpus becomes empirical material is itself the vision, and asymmetry is one means — then the vision needs different surgery, not a sequencing principle.

2. **Is `HORIZONS.md` separation acceptable, or does the user want vision and horizon kept together for rhetorical force?** The current document's compactness is an argument for keeping them together. The drift evidence is an argument against. The user's preference matters here.

3. **Should the "minimum demonstration run" gate be absolute, or should it be soft (i.e., a strong norm but not blocking)?** Absolute is more useful for `/goal` loops; soft preserves user override. The user's tolerance for the loop blocking on this gate determines the answer.

4. **How aggressive should the deployment-shape commitment be?** "CBM is a local CLI" is the most constraining and most useful. "Interface is undetermined and decided next" is the least constraining. The user's confidence about long-run interface model determines what the vision can fairly commit to.

5. **Should the graduation criteria be reduced from ten conjunctive conditions, or should the conjunction stay and the priority order be added separately?** The reduction is cleaner; the priority-order overlay is more conservative.

6. **Are anti-vision items revisable, or are they constitution-level commitments?** The current document treats them as the latter. The brittleness of items #5 (no marketplace) and #6 (no confidence-aggregator) suggests they should be the former. If the user agrees, the anti-vision should say so.

7. **Is the user comfortable with the vision reaching down into workflow ("drift looks like X")?** Some users prefer vision to stay strictly destination-oriented and let workflow protocols handle drift detection. Others prefer the vision to anchor everything. The correct answer depends on whether the user reads `VISION.md` as a constitution or as a target.

8. **How strongly should the vision push real-codebase verification?** Strong push (V7) means the seed kit cannot ship without external benchmark runs; that may be too strong for current state. Soft push means the same drift can recur. The user's risk tolerance for further smoke-on-self runs determines the strength.
