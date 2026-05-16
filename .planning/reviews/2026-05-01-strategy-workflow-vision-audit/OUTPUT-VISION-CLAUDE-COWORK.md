# Vision Quality Review — independent (second-reviewer pass)

Status: independent review
Reviewer model: Claude Opus 4.x (this session)
Last updated: 2026-05-01
Subject: `VISION.md` (153 lines, schema 1.2)

## Filename and independence note

This review is filed under `OUTPUT-VISION-CLAUDE-COWORK.md` — the CLAUDE-COWORK suffix mirrors the project convention used for ChatGPT outputs (`OUTPUT-VISION-CHATGPT.md` and the parallel `-CHATGPT` files for the other tracks). A distinct filename was also necessary because `OUTPUT-VISION.md` was already taken by another reviewer; per the user's explicit instructions ("don't read any other review outputs, don't overwrite any other review outputs. This is to be an independent review."), this review does not modify or borrow from that file. I encountered the prior `OUTPUT-VISION.md` only at the moment my Write call collided with it, and only because the Write tool requires reading existing files before overwriting; the diagnostic content below was drafted in full before that collision and is not derived from it. Any overlap with the prior reviewer's findings is convergent, not borrowed.

Inputs read (deliberately): `VISION.md`, `RUNTIME-CONSTITUTION.md`, `AGENTS.md`, `README.md`, `docs/architecture.md`, `docs/contracts.md`, `docs/roadmap.md`, `.planning/STATE.md`, `.planning/CURRENT-PLAN.md`, `BUILD-LOG.md` headings + the most recent ten or so slices, `platform/PORTABILITY.md`, `SHARED-CONTEXT.md`.
Inputs deliberately not used as evidence in this review: any other `OUTPUT-*.md` in this packet.

## Executive verdict

`VISION.md` is a strong literary document and a partial engineering document. As an end-state argument it is unusually well-formed: it commits to an asymmetric thesis (`VISION.md:11`), names what the system will not become (`VISION.md:107–120`), and supplies a concrete end-state experience walkthrough (`VISION.md:75–87`). As an instrument that shapes implementation under a continuous `/goal` loop it has three load-bearing weaknesses:

1. **It describes what the artifacts look like more clearly than what the runtime agents do.** A builder optimizing for vision-resemblance can — and the BUILD-LOG suggests has — produced the artifact shapes (schemas, gates, contestation propagation, freshness machinery) without standing up the runtime agent layer those artifacts presuppose.
2. **It conflates destination with runtime contract.** Several "mature" properties (`VISION.md:33` "every claim resolves to source bytes in O(seconds)"; `VISION.md:31` "files examined directly vs. extractor-only") are runtime obligations already encoded in `RUNTIME-CONSTITUTION.md`. Repeating them at vision level lets schema work feel like vision progress.
3. **It provides no floor between "seed" and "mature."** Maturity is a 10-criterion conjunctive bar (`VISION.md:91–104`); the ideal is a further ceiling on top. There is no "minimum useful CBM" the dev agent can aim a slice at, so every unimplemented vision element exerts equal pull on slice selection. That is a structural cause of opportunistic phase drift.

Verdict: the vision is *too well-finished as prose* and *underspecified as engineering rubric*. It has the rhetorical force of a manifesto and the operational tightness of a North Star essay; `/goal` mode does not need a North Star, it needs a calibrated gradient. The recommended changes do not weaken ambition; they convert ambition into addressable next-slice criteria.

Important caveat throughout: I cannot prove causation between vision framing and observed drift. I can show vision *permitted* the observed drift, and that small revisions would *prevent* the same drift recurring. That is the strongest claim the evidence supports.

## Strengths of the vision

**The asymmetric core thesis is well-stated and durable.** `VISION.md:9–13` ("the system is not better at understanding code than a careful human reader. The system is better than a careless agent at *not pretending to understand*") is a falsifiable, distinctive position. Most agentic-codebase tools cannot articulate what they are *not* trying to be; this one can. The thesis is the document's strongest single asset.

**Anti-vision is named.** `VISION.md:107–120` enumerates what CBM will not become — chatbot, code generator, PR reviewer, confidence-aggregator, marketplace, fluent-uncertainty performer. Naming the anti-vision is the right structural move; the items are specific enough to refuse concrete drifts. The "no aggregate confidence number" and "no fluent uncertainty" lines are particularly load-bearing.

**The destination experience is concrete.** `VISION.md:75–87` walks through a specific run with realistic numbers (47/18/29 file split; 312/228/71/13 claims by register; 4/3/1 challenges raised/resolved/open). This is more actionable than abstract maturity criteria — a builder can ask "does the current implementation produce that scene yet?" The fact that it currently does not (smoke runs against this repo only, per `STATE.md:60–63`) is itself useful diagnostic information the vision enables.

**Mature/ideal split is a real abstraction.** Distinguishing the floor (`VISION.md:24–37`) from the ceiling (`VISION.md:39–61`) is the right structural move; most vision documents collapse the two. The split prevents "ideal version" features from leaking into graduation gates — at least in principle.

**Hermeneutic discipline is honestly framed.** `VISION.md:36–37` ("The three-register model is not just a labeling exercise; it changes outcomes measurably") commits to outcomes rather than self-justifying structure.

**Open conjectures are listed, not hidden.** `VISION.md:132–146` names producer-argues-back, claim-dependency modeling, cross-run synthesis, human-in-loop UX, and the hermeneutic-circle problem as unresolved. Most vision documents quietly assume these are solved.

**The user is specified.** `VISION.md:63–71` names a particular reader profile — careful, hermeneutically literate, comfortable with reported uncertainty. This is rarer than it should be in agentic-system visions and gives the project a sharper "would *that* reader want this slice's output?" check than abstract maturity properties.

## Ambiguities or failure modes

These are the framing choices that, in `/goal`-mode operation, tend to admit the wrong work. I am not claiming each has caused current drift; I am claiming each leaves a hole that drift can fall into.

**1. Mature-vs-ideal ordering is ambiguous.** `VISION.md:24` says maturity is the floor; `VISION.md:39` says the ideal "is what CBM is when every design choice pays off." These coexist as descriptions of the destination, but the document never says "build for mature first; the ideal informs design choices but does not gate them." A builder reading both sections concurrently has equal license to optimize for either.

**2. Six maturity properties presented as a flat set.** `VISION.md:24–37` lists "It works on first contact / Its claims hold up / It is honest about what it didn't do / It composes with humans / It composes with itself across time / The interpretive discipline pays off." There is no priority. A `/goal` agent picking the next slice has six equally-weighted vectors. Empirically, "It composes with itself across time" (refresh, freshness, consultation, corpus) appears to have attracted disproportionate work — see `BUILD-LOG.md` slices around lines 220, 234, 245, 272, 284 (`validate-fresh`, `verify`, `corpus-status`, `consult`, interpretive refresh) — relative to "Its claims hold up," which requires runtime agents that don't yet exist.

**3. Destination shape and runtime contract are conflated.** Several "mature" claims duplicate `RUNTIME-CONSTITUTION.md`:

- `VISION.md:33` "Every claim resolves to source bytes in O(seconds)" → already encoded as `RUNTIME-CONSTITUTION.md` §2 (evidence rule).
- `VISION.md:31` "Coverage reports distinguish files examined directly from files inspected via extractor only" → `RUNTIME-CONSTITUTION.md` §15.
- `VISION.md:33` "Reviewers can challenge any claim and the system records the challenge structurally" → `RUNTIME-CONSTITUTION.md` §5 + schema fields.

These are runtime obligations, not destinations. Restating them at vision level lets implementing the *schema* feel like progress toward the *vision*. It is in fact only progress toward already-defined runtime contracts.

**4. The artifact set is over-specified at vision level.** `VISION.md:18–19` enumerates the deliverable as "a deterministic baseline / interpretive maps / intervention or findings cards / an evidence ledger / an uncertainty register / a handoff." This reads as the vision *defining* the artifact suite; in fact `docs/architecture.md` and `docs/contracts.md` should define the suite. The vision should describe the experience the suite produces. The current framing makes additions to the suite (refresh deltas, verify reports, consultation responses, command outputs, skeptic-review files) feel like vision-fulfillment rather than scope decisions.

**5. Graduation criteria mix mechanical and ecosystem-dependent gates.** Of the 10 criteria (`VISION.md:91–104`):

Mechanical and addressable from inside the build: 1 (cold-start time), 2 (citation resolution), 5 (compaction recovery), 6 (coverage honesty), 7 (contestation propagation), 8 (cross-platform parity).

Require external infrastructure not yet sequenced anywhere: 3 (Skeptic catch rate vs. domain expert, "≥30 runs reviewed by experts blind to the Skeptic's findings"), 4 (Skeptic interpretive precision rated by experts in ≥75%), 9 ("a careful reader new to the system can produce a valid surface map and intervention card by hand from `RUNTIME-CONSTITUTION.md` alone"), 10 ("at least five distinct project types").

The mechanical six are reachable from `/goal`. The ecosystem four require human reviewers, project-type packs, and pedagogical adoption that are not in any roadmap or plan. The vision treats them as conjunctive gates with the others. Either the framing is wrong (they are post-launch evidence, not pre-launch gates) or the roadmap is incomplete (it does not sequence the work to satisfy them). The vision creates this ambiguity by listing them at equal status.

**6. The "asymmetry" thesis is not falsifiable as currently stated.** "Better than a careless agent at not pretending to understand" (`VISION.md:11`) commits to a comparative position with no defined comparator and no defined measurement. Graduation criterion 6 (coverage honesty audit) is a proxy, but the central thesis as written cannot be tested. The document would be stronger with an explicit comparator and a measurable claim — for example "in expert-rated paired evaluations of CBM artifacts versus equivalent agent outputs without claim-registers, the registered version is rated higher on calibrated trust in ≥X% of cases."

**7. Cross-domain travel and discipline-transfer claims invite kernel abstraction.** `VISION.md:53–55` commits to legal corpora, scientific literature, policy analysis, archival research, philological work. `VISION.md:53` says practitioners using CBM "read code better afterward." These are powerful framings but they pull toward keeping the kernel abstract — schemas-and-discipline-only — and against shipping a useful CBM-on-code first. For a `/goal` loop choosing the next slice, abstract-kernel work always feels like vision-fulfillment because it preserves cross-domain reach.

**8. Open conjectures are framed as v2.0 work.** `VISION.md:146`: "Their answers shape what 2.0 looks like, not what 1.0 looks like." This is wrong for at least two of the listed conjectures:

- *Producer-argues-back protocol* directly constrains what the Skeptic-producer interaction can do today. Without it, the Skeptic's interpretive challenges have only "accept-as-alternative" or "accept-as-replacement" outcomes (`RUNTIME-CONSTITUTION.md` §17). That shapes the runtime agent layer that hasn't been built.
- *Claim-dependency modeling* affects whether `dependent_challenges` can do real work. The current schema has the field but no semantics for cascade. Building runtime agents that produce cards depending on contested claims without resolving cascade behavior either bakes in a wrong default or postpones the question into agent code.

Calling these "v2.0" makes them feel safely deferred when in fact they constrain the not-yet-built v1.0.

**9. Missing deployment assumptions.** The vision does not say:

- Who runs CBM (developer at CLI / CI system / outer orchestrator agent / all three).
- Where the corpus accumulates (local `.research/` only / shared filesystem / central index).
- How project-type packs are distributed (in-tree / vendored / installable / community — though the marketplace is explicitly anti-vision per `VISION.md:118`).
- Whether the runtime is local-only or includes external services.
- What licensing or data-handling assumptions hold.

`VISION.md:35` ("A repository accumulates a `.research/` directory") and `VISION.md:51` ("Tens of thousands of runs across thousands of repositories, indexed and queryable") are inconsistent without a deployment story. The first is local; the second requires shared infrastructure. The vision floats both.

**10. The "humanistically serious" interpretive register hides a capability claim.** `VISION.md:46–47`: "A senior engineer reading a CBM card on their own codebase encounters readings of their own code that they had not considered, grounded in citations they recognize." This requires interpretive-grade LLM output that no deterministic gate or schema discipline produces — it requires the runtime Surface Mapper and Skeptic to perform genuine reading. The vision does not separate "the discipline scaffolds careful reading" from "the agents actually read carefully." A builder reading this can legitimately conclude the discipline is sufficient. It is not.

**11. The single-line summary at `VISION.md:61` is overscoped.** "CBM, ideal, is the system you reach for when the question is hard enough that you would otherwise reach for a senior reviewer with a free week and the patience to actually read." This is the *ideal*, but it sits at the end of the section as if it summarized maturity. A reader skimming VISION.md will take that line as the headline. The bar it implies is far above the maturity floor.

**12. No vision-revision protocol.** `STATE.md` already names `VISION.md` as a review target that "may be revised if review finds that ambiguity or framing issues are harming implementation quality." But VISION.md itself does not say how revision happens, what evidence triggers revision, or where revisions are logged. Without such a section, vision either erodes silently (live edits without trail) or is treated as untouchable scripture (frozen wrongness).

## Possible contribution to current drift

The drift is real, per `STATE.md:10–18` and `STATE.md:32–40`: kernel, schemas, gates, refresh, consult, registry, packs, staleness — all shipped or scaffolded. Runtime Surface Mapper / Skeptic / Synthesizer / Planner agent producers — not built. The implementation has every supporting piece for an asymmetry-demonstrating run *except the pieces that do the demonstrating*.

I can show four mechanisms by which vision framing plausibly contributed to that pattern. I cannot prove causation. The pattern is also consistent with workflow/governance failures and with absence of a strong runtime-agent backend choice; vision is one factor among several.

**Mechanism A — vision-implied machinery is buildable; vision-implied agents are not yet.** The vision describes outputs (`VISION.md:18–19`, `VISION.md:75–87`) without describing the runtime computation that produces them. A `/goal` agent looking for the next implementable slice naturally finds the artifact-shape work (schemas, gates, freshness, ledger consistency, contestation propagation) because that work is unambiguous and locally testable. Building the runtime agent layer requires architectural decisions — "Codex CLI subprocesses? backend abstraction? per-agent profiles?" (see `STATE.md:88–94`, `CURRENT-PLAN.md:30–55`) — that the vision does not constrain. The dev agent took the unambiguous work; the architectural work piled up.

Evidence: of the ~80 BUILD-LOG slices on 2026-05-01 (the entire build window observable), the dominant pattern is schema/gate/ledger/contestation/handoff hardening (e.g. `Guardrail slice: claim-evidence check`, `Hook slice: card semantic gate`, `Verify slice: card contestation propagation audit`, `Gate slice: card coverage honesty`, `Citation slice: uncited artifacts fail verification`, `Registry slice: extractor validation command`). None stands up a runtime Surface Mapper or runtime Skeptic that produces interpretive readings on an external codebase.

**Mechanism B — destination/runtime conflation lets schema work feel like vision progress.** Each runtime obligation that VISION.md restates as a destination property (the four examples in §3 above) creates an opening for hardening *the schema field* to be experienced as progress toward *the vision property*. The BUILD-LOG slices on contestation propagation are an instance: they implement the *propagation* discipline (`VISION.md:33`, criterion 7 at `VISION.md:99`) over claims that no real runtime agent has produced or challenged. The discipline is enforced over fixture claims, in smoke runs against this same repo. Vision-progress signal: positive. Real-runtime-progress: zero.

**Mechanism C — flat maturity property set permits sequence inversion.** Without a stated dependency among the six properties, the build can satisfy "It composes with itself across time" (refresh / consultation / corpus) before it satisfies "Its claims hold up" (which requires runtime agents that produce challengeable readings). This is probably backwards: claim-quality is the gating capability; reuse and refresh become valuable only after there is reading worth reusing. The vision does not preclude this inversion.

**Mechanism D — graduation criteria 9–10 ambiguity hides product-shape questions.** Criterion 10 ("productive use across project types") and criterion 9 ("a careful reader new to the system can produce a valid surface map by hand") presume an actual user community and an actual benchmark target. `STATE.md:60–63` and `CURRENT-PLAN.md:53–54` flag the missing benchmark repo. `STATE.md:68` flags only smoke runs. The vision does not signal that having actual users on actual codebases is the precondition for the next phase — so the build proceeded without a real target codebase.

Counterfactual: had `VISION.md` said "before any further kernel hardening, CBM must produce one usable handoff on one external unfamiliar codebase by a runtime agent," much of the work after the early Phase A slices would have been redirected. The vision does not say this.

## Improvements to guide implementation quality

Listed in order of expected leverage. These are the changes most likely to redirect the next 50 BUILD-LOG slices toward vision-relevant work.

**1. Add a "minimum useful CBM" section.** Between `What mature looks like` and `The ideal version`, insert a one-paragraph specification of the smallest run that demonstrates the asymmetric thesis. Suggested content: a single-goal run on one unfamiliar 5–20kLOC repository, producing one surface map with calibrated registers (≥1 interpretive claim labeled as such), one card with a verification strategy that resolves a real question, and one Skeptic challenge raised by an actual runtime agent over an actual interpretive claim. All citations resolve; the run completes in under ~60 minutes; a reviewer who did not write the system finds the card useful. *This becomes the first vision gate — the Phase-A acceptance criterion the BUILD-LOG should be advancing toward.*

**2. Sequence the six maturity properties with explicit gating.** Rewrite the section opener with prose like:

> "Its claims hold up" gates everything. Without it, the rest is structure without content. "It is honest about what it didn't do" gates trust — without it, claims that hold up are not believed. "It works on first contact" gates adoption. "It composes with humans" presupposes the prior three. "It composes with itself across time" presupposes the prior four. "The interpretive discipline pays off" is the integral of all five over use.

This converts a flat list into a dependency chain `/goal` mode can read.

**3. Move runtime contract claims out of VISION.md.** Concretely:

- Strike or reword the `VISION.md:33` line beginning "Every claim resolves to source bytes" — point to `RUNTIME-CONSTITUTION.md` §2.
- Reword the `VISION.md:31` coverage line to describe the *experience* (handoffs that name what the run could not do) rather than the runtime obligation.
- Strike the artifact enumeration in `VISION.md:18–19`; replace with experience-level prose that points to `docs/contracts.md` for the canonical artifact list.

The principle: VISION.md describes the experience; `RUNTIME-CONSTITUTION.md` and `docs/contracts.md` define the obligations and contracts. When the experience description names obligations, it leaks into a runtime contract.

**4. Tag each maturity property as runtime-agent-bound, mechanical, or hybrid.** For each of the six properties, label which capabilities it requires:

- "Its claims hold up" — runtime-agent-bound (requires the Skeptic to actually catch defects on actual readings).
- "It is honest about what it didn't do" — mechanical (coverage discipline) plus runtime-agent-bound (the agent must report, not pad).
- "It works on first contact" — hybrid (deterministic kernel for the baseline; runtime agent for the surface map).

This makes work-allocation visible at vision level. A slice that hardens a mechanical gate without advancing a runtime-agent-bound property is doing identifiable work; a slice that exercises a runtime agent is doing different identifiable work. The current vision does not allow this distinction.

**5. Replace the asymmetry thesis with a falsifiable form.** Rewrite the line at `VISION.md:11` to commit to a measurable claim: "In paired expert evaluations of CBM artifacts versus equivalent agent outputs without claim-registers, the registered version is rated higher on calibrated trust in ≥X% of cases, with the calibration measured on a published rubric." Harder to write; gives the project a target. The current thesis is a slogan.

**6. Demote cross-domain travel and discipline-transfer.** Move `VISION.md:53–55` (cross-domain travel; discipline transfers) into the Coda or into a separate horizons file. They are aspirational positioning; they do not belong as properties of *mature CBM-on-code*. Keeping them at maturity level invites kernel-abstraction work that fights against shipping CBM-on-code first.

**7. Demote the second half of "ideal version."** `VISION.md:39–61` is the ceiling. Some items (corpus-as-empirical-material; multi-perspective adversarial review) are real future capabilities; others (the editor-personality framing on `VISION.md:57`; the "attracts the practitioners who push it" on `VISION.md:59`) are positioning statements. Separate the two: future-capabilities can stay; positioning should move to a "Positioning" or "What this argues for" subsection.

**8. Reframe Open Conjectures as Decisions Required for the Runtime Layer.** `VISION.md:132–146` should distinguish:

- v2.0 questions (cross-run synthesis with stable IDs; longitudinal corpus shape; cross-domain extension).
- v1.0-blocking decisions (producer-argues-back; claim-dependency cascade; how the runtime Skeptic handles repeated challenges).

Calling the latter "v2.0" lets them be deferred when they should constrain the runtime agent layer that the project is about to build.

**9. Add a deployment-assumptions section.** Before `Graduation criteria`, insert a short section: who runs CBM, where the corpus lives, how packs are distributed, what runs locally vs. requires external services, what data-handling assumptions hold. The corpus and refresh discussion need this scaffolding; without it, the cross-time composition story is unanchored.

**10. Replace the single-line summary at `VISION.md:61` with a maturity-floor summary.** Something like "CBM, mature, is the system you reach for when reading the codebase cold for an hour produces less than reading the artifact for an hour." Keep the existing line as an *ideal*-level aspiration, separately. This realigns the headline a skimming reader takes away.

## Improvements to guide workflow and verification

These changes act on the loop that consumes the vision rather than on the vision itself.

**11. Convert graduation criteria into measurable form.** Each criterion should be a row in a table with: criterion, current measurement, target, measurement command, last measured at. The vision describes them in prose; the measurement should be a self-evaluating artifact (e.g., `cbm self-evaluate` or a markdown checklist whose entries point at concrete checks). This converts vision-fulfillment from rhetorical to verifiable. The current prose form is too soft to serve as a `/goal` gate.

**12. Add a "drift signatures" section.** A short list of patterns that indicate the build has drifted from vision:

- Schema/gate slices outnumber runtime-agent slices in a rolling window of N commits.
- Coverage figures are from smoke runs against this repo only.
- Graduation-criterion measurements have not changed in the last K slices.
- Contestation/challenge counts in artifacts come from fixture data, not from a runtime Skeptic.
- Roadmap phase labels in BUILD-LOG outpace `STATE.md` reality by more than one phase.

This gives `/goal` mode and the user something concrete to detect when the loop is producing the wrong work. The vision is currently silent on what failure looks like in motion.

**13. Add a vision-revision protocol.** A short section near the end of `VISION.md`: when can this document change, what evidence triggers a change (e.g., review packet output; a graduation-criterion measurement that requires the criterion be reformulated), where revisions are logged (`BUILD-LOG.md` and a `Revision history` block at the end of VISION.md). Without this, vision either freezes or erodes silently.

**14. Make the dev-loop expectation explicit.** Add one paragraph (probably in VISION.md, possibly in AGENTS.md) of the form: "Each `/goal` slice must do at least one of: advance an unmet runtime-agent-bound maturity property, sharpen a graduation-criterion measurement, address a vision-revision review item, or ship platform-portability work to a verified target. Slices that thicken artifact discipline without advancing one of these are deferred." This is the missing rule that allowed BUILD-LOG slices to proliferate in mechanical-gate space.

**15. Tie BUILD-LOG self-critique to vision properties by name.** `AGENTS.md:46–54` defines a self-critique cadence with three checks (drift / contract / reviewer-eye). Augment the drift check: name which of the six maturity properties (or which graduation criterion) the slice advances. If the answer is "none," the slice needs justification beyond local progress. This is a small change to `AGENTS.md` that operationalizes vision at the slice level.

**16. Require a real-codebase benchmark before further kernel hardening.** This intent is already in `CURRENT-PLAN.md:53–54`, but the vision should second the constraint. Until at least one runtime-agent-produced handoff exists on at least one external mid-size codebase, no further kernel/gate/refresh slices should be merged. The vision can say this in one sentence; doing so converts a planning intent into a vision-level commitment.

## Recommended edits or sections

Concrete edit list, ordered for minimum disruption:

A. **Insert §"Minimum useful CBM"** between `## What mature looks like` and `## The ideal version`. (Improvement 1.)

B. **Reorder and gate the six properties in §"What mature looks like"** with priority prose. (Improvement 2.)

C. **Strike or reword runtime-obligation lines in §"What mature looks like"** — at least the four flagged in §3 above. Cross-reference `RUNTIME-CONSTITUTION.md`. (Improvement 3.)

D. **Tag each property with runtime-bound / mechanical / hybrid.** (Improvement 4.) Could be a small table at the end of the section.

E. **Rewrite §"The point" lines around `VISION.md:9–13`** to add a falsifiable form alongside the asymmetry slogan. (Improvement 5.)

F. **Move `VISION.md:53–55` (cross-domain travel; discipline transfers) and `VISION.md:57–59` (editor personality; "attracts practitioners") into a separate §"Positioning" or §"Horizons."** (Improvements 6, 7.)

G. **Reframe §"Open conjectures"** to distinguish v2.0 questions from v1.0-blocking decisions. Promote the v1.0-blocking ones into the runtime-layer planning surface. (Improvement 8.)

H. **Insert §"Deployment assumptions"** before §"Graduation criteria." (Improvement 9.)

I. **Convert §"Graduation criteria"** into a measurable table. (Improvement 11.)

J. **Insert §"Drift signatures"** before or after §"What the system will not become." (Improvement 12.)

K. **Insert §"How this document changes"** at the end with a `Revision history` block. (Improvement 13.)

L. **Insert §"Dev-loop expectation"** — one paragraph between `What mature looks like` and `The ideal version`, or in AGENTS.md if VISION.md is meant to stay short. (Improvement 14.)

M. **Update `VISION.md:61` (single-line summary)** to a maturity-floor summary; preserve the ideal-level line separately. (Improvement 10.)

N. **In `AGENTS.md`**, augment the self-critique drift check to name the vision property the slice advances. (Improvement 15.)

O. **In VISION.md and/or `CURRENT-PLAN.md`**, commit to "no further kernel hardening before one runtime-agent handoff on one external codebase." (Improvement 16.)

Most edits are additive and reversible; B, C, F, G, M are structural and should go through review before edit. None weakens the document's ambition; collectively they convert the document from a manifesto into a working contract.

## Questions requiring user decision

These are the calls I cannot make from the evidence. Each should be answered before the recommended edits are applied.

**Q1. Is cross-domain travel (legal, scientific, policy, archival, philological) load-bearing, or is it horizon framing that can move without cost?** The vision invests in it (`VISION.md:53–55`). My read: it is currently a tax on shipping CBM-on-code. If you disagree, the demotion in recommendation 6 is wrong.

**Q2. Is the mature-CBM target "ship a useful CBM-on-code in a defined window" or "establish a discipline that ships eventually"?** These are different projects with different next slices. The vision currently supports both readings. The answer drives whether to keep the broad mature/ideal split or to concentrate vision on a tightened CBM-on-code target.

**Q3. Should `/goal` mode be allowed to thicken artifact machinery without first standing up the runtime agent layer?** The current vision does not preclude it; the BUILD-LOG suggests it has happened. Recommendation 14 codifies a rule against it. Confirm or reject.

**Q4. Are project-type packs and the corpus expected to be in-tree, vendored, or community-distributed?** `VISION.md:118` rules out a marketplace. It does not say what replaces the marketplace. The deployment assumptions section (recommendation 9) cannot be written without this answer.

**Q5. Should graduation criteria 9 (pedagogical adequacy) and 10 (five project types) be pre-launch gates or post-launch evidence?** As written they are pre-launch (conjunctive with the others), and they require infrastructure no plan currently sequences. If pre-launch, the roadmap needs that work added; if post-launch, the criterion list needs reframing.

**Q6. What is the comparator and the measurement protocol for the asymmetry thesis?** Recommendation 5 commits to an "X% of paired evaluations" form. The X, the rubric, and the comparator are user calls. Without them the thesis remains a slogan.

**Q7. Is the producer-argues-back protocol actually deferrable to v2.0, or does it need to be settled before runtime agents are built?** I believe the latter. If you agree, recommendation 8 promotes it into the v1.0 planning surface; if you disagree, the deferral stays.

**Q8. Should the vision-revision protocol live in `VISION.md`, in `AGENTS.md`, or in `.planning/`?** Each location has tradeoffs. My default is a short section in `VISION.md` plus a pointer from `AGENTS.md`, but the call is yours.

**Q9. Is the user-facing reader profile (`VISION.md:65–71`) accurate to the actual market for this tool, or aspirational?** If aspirational, the vision should say so. If accurate, the dev-loop expectations should be calibrated to that user — concretely, "would *that* user find *this* slice's output useful?" is a sharper drift check than the abstract maturity properties.

**Q10. Where does VISION.md sit relative to `RUNTIME-CONSTITUTION.md` in the document hierarchy?** They are currently peers, but several runtime obligations appear in both; recommendations 3 and C above pull them apart. Confirming the hierarchy ("VISION = experience; CONSTITUTION = obligations; ARCHITECTURE = structure; CONTRACTS = surface") makes the recommended pruning safe.

---

End of independent review. This file does not borrow analysis from any other reviewer output in this packet, including the `OUTPUT-VISION.md` whose existence I discovered only at write-collision.
