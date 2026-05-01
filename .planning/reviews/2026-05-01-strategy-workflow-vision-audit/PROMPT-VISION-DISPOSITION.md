# Prompt: Vision Review Disposition

You are an independent disposition reviewer for the CBM vision audit. Three vision reviews of `VISION.md` exist. Your job is not to write a fourth review, and not to summarize the existing three. Your job is to compare them, meta-critique them, adjudicate their disagreements, and distill the result into a prioritized set of actionable edit recommendations the user can take to `VISION.md` (and adjacent documents).

You are a Claude session with file access to the CBM repository. Use it. The reviews make a mix of factual claims (line numbers in `VISION.md`, slice patterns in `BUILD-LOG.md`, overlap between `VISION.md` and `RUNTIME-CONSTITUTION.md`, status in `.planning/STATE.md`) and interpretive claims (whether the asymmetry thesis is falsifiable, whether cross-domain framing pulls the project off-course, whether the document encourages overbuilding). You will need to handle both kinds of claim, and you will need to keep the difference visible.

## Inputs

Three vision reviews live in `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/`:

- `OUTPUT-VISION.md` — the first reviewer's output. Authorship is not annotated in-file; treat it on its evidence and reasoning, not on its provenance.
- `OUTPUT-VISION-CHATGPT.md` — produced by GPT-5.5 Pro with extended thinking.
- `OUTPUT-VISION-CLAUDE-COWORK.md` — produced by Claude (this product, Cowork mode), in a session where the writer drafted the diagnosis before encountering the existence of `OUTPUT-VISION.md`. The CLAUDE-COWORK file contains a "Filename and independence note" describing that collision; you may verify the note is consistent with the content of the file but do not weight the review by its self-description of independence.

Model attributions are factual context, not weighting hints. Each model has characteristic strengths and failure patterns, and on a vision review the failure patterns are different from those on an architecture review (see §"AI-pattern failures" below). You may use that knowledge to *recognize* patterns more quickly during meta-critique. You must not weight reviews by model identity. A claim either holds against the source or it does not, regardless of who wrote it.

The original prompt all three responded to is `PROMPT-VISION.md` in the same directory. Read it first — it tells you what each reviewer was asked to produce ("Did ambiguity, overbreadth, missing operational detail, or rhetorical framing in the vision contribute to implementation or planning problems? … how could the vision be improved?") and the discipline they were asked to maintain ("Do not assume the vision is good because it is authoritative. Do not assume implementation drift proves the vision is bad. Diagnose carefully."). One of the things you will be checking is which reviewers honored that instruction — including whether they slipped into ratifying the current agent's framing of the drift, or into attributing all drift to vision when other causes were available.

The packet also contains architecture and workflow review outputs (`OUTPUT-ARCHITECTURE-*.md`, `OUTPUT-WORKFLOW-*.md`) and the architecture disposition (`OUTPUT-ARCHITECTURE-DISPOSITION-CLAUDE-COWORK.md`, if present). These are not your primary input, but if an architecture or workflow finding bears directly on adjudicating a vision disagreement — for example, on whether a recommended vision-level rule is doing operational work that belongs in `AGENTS.md` or `CURRENT-PLAN.md` — you may consult them. Do not let them drive your output.

The repository's primary sources, the same ones the vision reviewers had access to, are: `VISION.md`, `RUNTIME-CONSTITUTION.md`, `README.md`, `AGENTS.md`, `.planning/STATE.md`, `.planning/CURRENT-PLAN.md`, `docs/architecture.md`, `docs/contracts.md`, `docs/roadmap.md`, `BUILD-LOG.md` (long; you'll want headings + sampled slices), `platform/PORTABILITY.md`, and `SHARED-CONTEXT.md`. You will need to revisit at least `VISION.md`, `RUNTIME-CONSTITUTION.md`, `STATE.md`, `CURRENT-PLAN.md`, and the BUILD-LOG headings to spot-check claims.

## What independence means here

Anti-deference, four ways:

1. **Don't defer to the longest review.** Length is not evidence. Vision reviews can pad with concept-talk that feels deep and isn't.
2. **Don't defer to model identity.** Treat the three reviews as anonymous. If you find yourself thinking "X model is more careful with text" or "Y model is bolder," strike the thought and look at what the review actually says about which lines of `VISION.md`.
3. **Don't manufacture consensus.** When two or three reviews silently agree on an edit (e.g., "split off `HORIZONS.md`"), that is data, not proof. Verify the agreement against `VISION.md` itself before promoting it. Shared blind spots are real.
4. **Don't manufacture disagreement.** Vision reviewers often use different vocabularies for the same diagnosis ("destination/horizon conflation" vs. "ideal version pulls scope forward" vs. "five content layers in trench coats"). Decide whether a divergence is real or terminological before treating it as a contested point. The opposite trap is also real: two reviews can use the same word ("falsifiable," "operational," "load-bearing") to mean different things.

You may conclude that all three reviews are partially wrong about whether vision contributed to drift, or about whether a particular edit would help. You may conclude that the right edit is one none of them proposed. Both are allowed. You may also conclude that the right action is *not to edit `VISION.md`* in some specific place that all three reviews wanted edited — vision is a durable instrument, and a wrong edit propagates farther than a wrong code change.

## Two terrains in one review

Vision claims fall into two terrains. Keep them separate.

**Empirical claims** are spot-checkable. Examples:
- "`VISION.md:33` says 'every claim resolves to source bytes in O(seconds)'" — go to the line and read.
- "`RUNTIME-CONSTITUTION.md` §2 already encodes the citation rule" — go to the section and verify overlap.
- "BUILD-LOG slices around the contestation-propagation cluster (lines ~700–790) are gate hardening, not runtime-agent work" — read the headings and sample.
- "Graduation criterion 9 requires infrastructure not sequenced in any roadmap" — search the roadmap.
- "STATE.md says only smoke runs against this repo exist" — read the line.

These you adjudicate by reading. When two reviews disagree on an empirical claim, read the source.

**Interpretive claims** are not spot-checkable in the same way. Examples:
- "The asymmetry thesis is not falsifiable as currently stated."
- "Cross-domain travel framing pulls the kernel toward abstraction."
- "Restating runtime obligations at vision level lets schema work feel like vision progress."
- "The destination experience is more concrete than the runtime computation that produces it."

These cannot be settled by re-reading `VISION.md`. They are claims about how a `/goal`-mode agent would interpret the document, or about whether a framing has a particular psychological effect on builders. They are *grounded* by evidence (BUILD-LOG patterns, the kinds of slices that shipped), but the inference from evidence to claim is interpretive.

When you adjudicate an interpretive claim, do not pretend it is empirical. Name the inference, name what would falsify it, and either accept it conditionally, reject it, or surface it to the user as a judgment call. The disposition's value lies partly in correctly distinguishing which of the reviewers' claims need user input and which don't.

## Phase 1 — Read

Read `PROMPT-VISION.md`. Read the three reviews end-to-end. Read enough of the primary sources to know what's in each: at minimum `VISION.md` in full, `RUNTIME-CONSTITUTION.md` skim with attention to §2, §5, §15, §17, and §25, `STATE.md`, `CURRENT-PLAN.md`, and the BUILD-LOG headings (`grep '^## ' BUILD-LOG.md`). The reviews will reference specific lines, sections, and slice patterns; you should be ready to look them up.

## Phase 2 — Compare

Build a structured comparison. Internally, this phase should answer:

- **Convergent diagnoses.** Where do all three reviewers say the same thing? Common candidates: destination/horizon conflation; flat priority across maturity properties; runtime-obligation overlap with `RUNTIME-CONSTITUTION.md`; graduation criteria mixing mechanical and ecosystem gates; cross-domain travel as scope-creep risk; need for a "minimum useful CBM" floor.
- **Convergent edits.** Where do all three propose the same change? Common candidates: split off some form of horizons document; reduce or restructure graduation criteria; demote cross-domain claims; add a vision-revision protocol; tie next-slice selection to vision properties.
- **Divergent diagnoses.** Where do they identify different root causes? For instance: one might emphasize missing deployment assumptions; another, missing falsifiability; another, missing sequencing principle. These can all be true, but they imply different edits.
- **Direct contradictions.** One review says "the anti-vision section is well-chosen"; another says "anti-vision is partially over-committed." Which specific items are contested?
- **Unique observations.** What does each review uniquely see — claims only that review makes? Sometimes the unique observation is the most important one in the set.
- **Unique edits.** What concrete edits does each review uniquely propose?

Don't be comprehensive — be precise. A short list of *load-bearing* agreements and disagreements is more useful than a long matrix of trivia. "Load-bearing" here means: the edit, if made, would visibly change how `/goal` mode picks the next slice, or how a careful reader takes the document, or what the next BUILD-LOG entries look like. Cosmetic style edits are not load-bearing.

## Phase 3 — Meta-critique each review

Evaluate the reviews themselves, not just their conclusions. For each review:

- **Evidence discipline on empirical claims.** Are line numbers, BUILD-LOG references, and STATE/PLAN references actually correct? Spot-check at least three citations per review. Note the failures.
- **Discipline on the interpretive/empirical line.** Does the review keep "the asymmetry is not falsifiable" (interpretive) separate from "VISION.md:33 duplicates RUNTIME-CONSTITUTION.md §2" (empirical)? Or does it slide between them, presenting interpretive claims with the confidence of empirical ones?
- **Framing.** The prompt told reviewers not to assume vision is good, not to assume drift proves vision is bad, and to consider that the main issue may be workflow, governance, or runtime-agent absence rather than vision quality. Did the review actually consider those alternatives? Or did it fall into "vision is responsible for drift; here are 16 edits"?
- **Blind spots.** What does the review not see? What primary sources does it underuse? Common blind spots in vision reviews: ignoring `RUNTIME-CONSTITUTION.md` overlap; ignoring that some recommended edits belong in `AGENTS.md` or `CURRENT-PLAN.md` rather than `VISION.md`; ignoring cross-track interactions (the workflow track, the architecture track); treating a literary device as engineering ambiguity or vice versa.
- **Recommendation specificity.** Are recommendations concrete (named section, named addition, named scope) or hedged ("consider," "explore," "tighten")? Hedged recommendations are not actionable. Watch also for the opposite failure: spuriously concrete recommendations (e.g., a numerical target like "≥X%") whose specific values were invented to sound rigorous and are not anchored to evidence.
- **Internal consistency.** Does the review's diagnosis line up with its recommendations? Does it diagnose problem A (e.g., "vision is silent on deployment shape") and recommend a fix for problem B (e.g., "demote cross-domain travel")?
- **Scope discipline.** Does the review respect that this is a *vision* review, or does it sprawl into architecture and workflow territory? Some sprawl is unavoidable (vision touches both), but a review that effectively re-reviews the architecture or workflow has a scope problem.
- **AI-pattern failures specific to vision review.** Watch for:
    - **Concept-talk padding.** Long passages that gesture at hermeneutics, asymmetry, or "instrument-versus-substitute" without committing to a specific edit.
    - **Manifesto echo.** The review picks up `VISION.md`'s rhetorical register and reproduces it in critique form, with the same kind of confident pronouncements the document itself contains. Critique should sound less like the thing it critiques, not more.
    - **False structure.** Headers without content; "Improvements" sections that are recommendations renamed; "Questions for user" sections that are rhetorical questions rather than actual decisions.
    - **Premature evenhandedness.** "On the one hand the asymmetry is sharp; on the other hand it is unfalsifiable" used as a substitute for a position. The reviewer's job was to take a position.
    - **Padded executive verdicts.** Three-paragraph verdicts that say "the vision is partly good and partly bad and the recommendations follow."
    - **Recommendation inflation.** Twelve recommendations where five would do, the rest hedged.
    - **Confident assertion without grounding.** "Builders reading this would conclude X" — would they? On what evidence?
    - **Fabricated citations or line numbers.** Always spot-check.
- **Independence under stress.** Did the review claim independence and behave so? Look for tonal echoes, parallel structure, or shared specific edits that suggest one reviewer saw another's output. The CLAUDE-COWORK file documents a write-collision with `OUTPUT-VISION.md`; verify (or fail to verify) that its content is consistent with the claim that the diagnosis was drafted before the collision.

Be specific in the meta-critique. "Review X is hand-wavy" is not useful. "Review X recommends 'a measurable form' for the asymmetry thesis but proposes 'X%' without specifying X, the comparator, or the rubric — which is a gestural recommendation in the same shape as the slogan it critiques" is useful.

## Phase 4 — Adjudicate

For every contested claim or recommendation worth keeping, decide who is right, and why. The meta-critique is your lens. A review that has shown stronger evidence discipline on empirical claims gets more weight on factual disagreements. A review that has kept the interpretive/empirical line cleanly gets more weight on judgment calls. A review caught padding or echoing the manifesto gets less weight on its top-line verdict.

When adjudicating proposed edits, ask three questions:

1. **Does the edit address a real problem?** A recommendation that fixes a non-problem is wasted edit budget, even when it sounds good. Reject edits whose underlying diagnosis you cannot confirm against evidence.
2. **Does the edit belong in `VISION.md`?** Some recommendations belong in `AGENTS.md` (e.g., self-critique cadence augmentations), `CURRENT-PLAN.md` (e.g., "no further kernel hardening before runtime-agent ships"), or `docs/architecture.md` (e.g., deployment shape commitment). A vision recommendation that should be a workflow recommendation is misallocated; reroute it.
3. **Is the edit reversible?** A reword is reversible. A section move is mostly reversible. A structural rewrite or a new graduation criterion with numeric targets is harder to undo. Prefer reversible edits when the diagnosis is judgment-shaped, not evidence-shaped.

When you cannot adjudicate from evidence — when the disagreement is over a value judgment or an empirical question the user has to answer (e.g., "should the project ship CBM-on-code first or build a transferable discipline?") — say so explicitly. Don't fabricate certainty. Surface it as an open question for the user.

When all three reviews agree on a diagnosis or edit, treat the consensus as a *strong default* but verify it against `VISION.md` and the primary sources before promoting it. If verification reveals the consensus rests on a misreading, say so. Three reviewers agreeing on a misreading is a more interesting finding than three reviewers being correct.

## Phase 5 — Actionable edit recommendations

Distill the adjudication into a prioritized recommendation list for editing `VISION.md` and adjacent documents. Constraints:

- Each recommendation is concrete: name the section(s) to edit, the addition(s) to make, the file (`VISION.md`, a new file like `HORIZONS.md`, or `AGENTS.md` / `CURRENT-PLAN.md` if you've rerouted it), and the approximate scope (a sentence reword; a one-paragraph addition; a section move; a structural rewrite).
- Each recommendation has a one-line rationale anchored to the adjudication. Example: "Recommended because reviews B and C converged on the runtime-obligation-duplication diagnosis, the empirical check (`VISION.md:33` versus `RUNTIME-CONSTITUTION.md` §2) confirms the duplication, and rewording removes the source of one specific drift mechanism."
- Each recommendation has a falsification test: how the user (or the dev agent) will know if the edit was the right move. Vision-edit falsification tests are weaker than code-change falsification tests, but they exist:
    - "We'll know this was right if the next 20 BUILD-LOG slices each name the maturity property they advance, and ≥80% identify a runtime-agent-bound property — measured at slice 25."
    - "We'll know the HORIZONS.md split was right if the dev loop's next slice is a runtime-agent slice rather than another schema slice."
    - "We'll know the graduation-criteria measurable rewrite was right if at least three of the criteria have current measurements within two weeks of the edit."
    - For interpretive recommendations whose falsification is genuinely fuzzy ("we'll know the asymmetry rewrite was right if a reviewer outside the project finds the thesis testable"): say so, and note the test as soft.
- Order by leverage and reversibility. Highest-leverage and most-reversible items first. A reversible reword that closes a drift mechanism beats a structural rewrite of equal merit.
- Distinguish *edit-now* from *user-decides*. Some edits are uncontroversial cleanup (remove a runtime obligation duplicated in `RUNTIME-CONSTITUTION.md`). Others require the user's call (commit to "CBM is a local CLI"; demote cross-domain travel; convert graduation criteria into a numeric rubric). Mark each recommendation accordingly.

If the right answer for some piece of `VISION.md` is "do nothing yet, decide first," that is a valid recommendation. Name the decision explicitly and the consequence of deferring it.

Do not pad the list to look comprehensive. Five concrete edit recommendations are better than fifteen hedged ones.

## Phase 6 — Cross-track and second-order effects

Vision changes are meta. Briefly (a paragraph or two, no more) note:

- **Where vision recommendations are doing operational work.** If a recommended `VISION.md` edit is functionally an addition to `AGENTS.md` or `CURRENT-PLAN.md`, flag it and reroute it. If a recommended edit can only succeed when paired with an architecture or workflow change, name the pairing.
- **What this disposition does not adjudicate.** Vision interacts with workflow (the `/goal` loop's relationship to vision properties) and architecture (the runtime/kernel boundary's relationship to vision claims). If a vision adjudication depends on something the workflow or architecture disposition has to decide first, name the dependency and stop.
- **Risks of the recommended edit set as a whole.** A coherent edit set should not, taken together, hollow `VISION.md` to a list of operational rules. The document's literary force is part of its function; preserve it. If your edit set risks doing that, say so, and propose a milder variant.

This phase is a brake, not an engine. Do not use it to add more recommendations.

## Output

Write to `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/OUTPUT-VISION-DISPOSITION-CLAUDE-COWORK.md`. Do not overwrite the three input reviews. Do not overwrite any other reviewer's disposition.

Use this structure:

- **Comparison summary** — where the three reviews agree, diverge, and contradict, in compact form. Distinguish empirical agreement from interpretive agreement.
- **Meta-critique per review** — one section per review, named by filename. Specific, evidence-anchored, fair. Include both empirical-claim spot-check results and interpretive-claim discipline assessment.
- **Adjudication of contested claims** — the load-bearing disagreements only, with verdict and rationale. Distinguish "evidence settles this" from "this is a judgment the user must make."
- **Actionable edit recommendations** — prioritized list with rationale and falsification test per item. Each item marked *edit-now* or *user-decides*. Each item names target file (`VISION.md`, `HORIZONS.md`, `AGENTS.md`, etc.) and scope.
- **Cross-track and second-order notes** — brief; misallocations rerouted, dependencies named, hollowing risk flagged if real.
- **Open questions for the user** — decisions that cannot be derived from evidence and that the user must take. Distinguish from items already on the *user-decides* recommendation list (those are about specific edits; these are about deeper choices that drive multiple edits).

## Anti-patterns to refuse

Do not produce: a fourth vision review that competes with the three; a "synthesis" that smooths the disagreements into a generic position; a recommendation list that paraphrases all three reviews back at them; an executive verdict that hedges every load-bearing claim; a section structure prescribed without anchoring to which review's recommendation it implements; a falsification test that says "we'll know this is right if the project goes well." Do not pad with concept-talk that gestures at hermeneutics, asymmetry, or instrument-versus-substitute without committing to a specific edit.

Do not assume vision is the cause of drift. Do not assume vision is innocent. Two of the three reviewers concluded vision contributed to drift; that conclusion is itself adjudicable, and you may conclude they were partly wrong about causality. The architecture and workflow tracks are running in parallel and may locate the drift's actual cause elsewhere.

The disposition's value is in the adjudication and in producing an edit set the user can actually execute against `VISION.md`. If you find yourself unwilling to adjudicate a contested claim, name which one, name why you cannot weigh it, and either escalate it as an open question for the user or note it as a load-bearing claim left unadjudicated. Do not bury it.

That is the bar.
