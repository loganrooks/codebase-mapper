# Vision Review Disposition

Reviewer: Claude (Cowork mode), independent disposition pass
Date: 2026-05-01
Inputs: `OUTPUT-VISION.md`, `OUTPUT-VISION-CHATGPT.md`, `OUTPUT-VISION-CLAUDE-COWORK.md`, `PROMPT-VISION.md`, primary sources (`VISION.md`, `RUNTIME-CONSTITUTION.md`, `.planning/STATE.md`, `.planning/CURRENT-PLAN.md`, `BUILD-LOG.md` headings).

The disposition is shorter than any single review and is meant to be. Three reviewers said most of what needed saying; the value here is in deciding which of their claims hold against the evidence and producing an edit set the user can act on.

## Comparison summary

### Empirical agreement (verifiable against the sources, all three reviews concur)

- **Five-layer conflation in `VISION.md`.** Destination (mature, lines 23–37), horizon (ideal, 39–61), runtime experience walkthrough (73–87), runtime/architectural commitments embedded in destination prose (line 31, line 33, line 100), and anti-vision (106–120) coexist in one document in one register. Verified against the document. All three reviewers identify this. (`OUTPUT-VISION.md` §A; `OUTPUT-VISION-CHATGPT.md` "blur five distinct things"; `OUTPUT-VISION-CLAUDE-COWORK.md` §3.)
- **Graduation criteria are conjunctive and equally weighted.** `VISION.md:104` says "These ten conditions are conjunctive." Verified. Three reviewers agree this fails to differentiate kernel-mechanical from runtime-agent-bound from ecosystem-dependent gates.
- **Deployment / interface / process model is absent.** `VISION.md` does not commit on whether mature CBM is a CLI, daemon, MCP server, outer-orchestrator client, or hybrid. Verified. Three reviewers agree.
- **Smoke runs are against the implementation's own repo.** `STATE.md:60–64` confirms. The vision provides no pre-graduation gate forcing external benchmark runs.

### Interpretive agreement (cannot be settled by re-reading; convergent inferences from evidence)

- **Vision permitted (did not necessarily cause) the kernel-vs-runtime-agent drift.** `OUTPUT-VISION.md` ("plausibly contributing"), `OUTPUT-VISION-CLAUDE-COWORK.md` ("vision permitted; cannot prove caused"), `OUTPUT-VISION-CHATGPT.md` ("indirectly, not because the core ambition is wrong"). All three are appropriately hedged about causation. The user should treat this as a strong but unproven default, not a verdict.
- **Some form of "minimum useful CBM" / "minimum demonstration run" floor is missing.** `OUTPUT-VISION.md` V2; `OUTPUT-VISION-CLAUDE-COWORK.md` improvement 1; `OUTPUT-VISION-CHATGPT.md` "benchmark requirement." Same diagnosis in three vocabularies.
- **"Ideal version" pulls scope forward.** `OUTPUT-VISION.md` §D; `OUTPUT-VISION-CLAUDE-COWORK.md` §7. (`OUTPUT-VISION-CHATGPT.md` does not engage VISION.md's actual ideal section because it never read the file; see meta-critique below.)

### Convergent edits (ranked by how often they appear and how anchored they are)

- Split `§ "The ideal version"` (39–61) off into `HORIZONS.md` or equivalent. `OUTPUT-VISION.md` V5 + `OUTPUT-VISION-CLAUDE-COWORK.md` recommendations F/L. `OUTPUT-VISION-CHATGPT.md` has a weaker scoped-maturity-levels variant.
- Reform graduation criteria: `OUTPUT-VISION.md` V3 wants Core / Supporting / Post-1.0 split; `OUTPUT-VISION-CLAUDE-COWORK.md` improvement 11 wants a measurable table; `OUTPUT-VISION-CHATGPT.md` wants benchmark + rubric. Same impulse, different shapes.
- Add deployment-shape commitment (or explicit deferral). All three.
- Add a sequencing / "kernel without agent producer is drift" rule. `OUTPUT-VISION.md` V1 + V8; `OUTPUT-VISION-CLAUDE-COWORK.md` improvement 14 + 16. (`OUTPUT-VISION-CHATGPT.md` has a weaker "artifact economy rule.")

### Direct contradictions

- **Is the asymmetry thesis falsifiable as currently stated?** `OUTPUT-VISION.md` strength #1 ("testable, falsifiable"). `OUTPUT-VISION-CLAUDE-COWORK.md` §6 ("not falsifiable as currently stated"). They disagree about the same single sentence at `VISION.md:11`. Adjudicated below.
- **Is anti-vision over-committed?** `OUTPUT-VISION.md` §F flags marketplace and confidence-aggregator items as overreach. `OUTPUT-VISION-CLAUDE-COWORK.md` and `OUTPUT-VISION-CHATGPT.md` do not engage. Not strictly a contradiction; an asymmetric finding.

### Unique observations worth preserving

- `OUTPUT-VISION.md`: the explicit "kernel-without-agent" anti-pattern as a vision-level addition (V8). Sharp, anchored.
- `OUTPUT-VISION-CLAUDE-COWORK.md`: tagging each maturity property as runtime-bound / mechanical / hybrid (improvement 4); reframing the *producer-argues-back* conjecture as v1.0-blocking rather than v2.0 (improvement 8). The producer-argues-back observation is the disposition's most interesting unique finding.
- `OUTPUT-VISION-CHATGPT.md`: the "negative examples" idea (show what bad CBM output looks like). Generic but transferable.

## Meta-critique per review

### `OUTPUT-VISION.md` — first reviewer

**Evidence discipline (empirical):** Strong. Spot-checked five citations: `VISION.md:9-13` (thesis — correct), `VISION.md:91-104` (graduation criteria — correct), `VISION.md:106-120` (anti-vision — correct, with one-line off-by-one on the section header), `VISION.md:33` ("every claim resolves to source bytes" — correct), `STATE.md:32-40` (drift narrative — correct). No fabricated line numbers detected.

**Discipline on the interpretive/empirical line:** Mostly held. The review is honest that "plausibly contributing" is the strongest claim it can make, and it explicitly enumerates "plausibly not the vision's fault" alongside (§"Possible contribution"). That is the prompt's discipline ("do not assume drift proves vision is bad") visibly honored.

**Framing and scope:** The review took the prompt seriously and considered alternative causes. The conclusion that "the destination is right; the sequencing pressure is missing" is well-located. Slightly over-confident in places (e.g., "this single paragraph would have created the counter-pressure" — would it? unproven counterfactual).

**Internal consistency:** High. V1–V8 follow from §A–§I.

**Specific failure 1: the asymmetry-falsifiable claim.** Strength #1 says the thesis is "testable, falsifiable." The thesis as written ("better than a careless agent at not pretending to understand") names no comparator and no measurement protocol. Calling it "falsifiable" without grounding *which test* would settle it is the kind of premature confidence the prompt warned about. Adjudicated against this review on this specific point.

**Specific failure 2: anti-vision overreach.** §F's argument that "no marketplace" is overreach is reasonable but undersells the *function* of an anti-vision: a commitment device. The proposed reword ("CBM does not ship a community pack ecosystem at v1.0") opens a door the original chose to close. Worth keeping the door closed unless the user has a current reason to crack it.

**AI-pattern check:** Some manifesto-echo ("five different documents in trench coats" — clever, but the document is being critiqued for prose performance, not asking for matching prose). Eight numbered improvements + nine recommended edits + eight user-decision questions slightly tips into recommendation inflation. The recommendations are concrete and anchored, so the inflation is mild rather than fatal.

**Verdict:** The strongest of the three on evidence discipline and on edit specificity. Take its top recommendations seriously, push back on its strength claim about falsifiability and on its anti-vision-overreach diagnosis.

### `OUTPUT-VISION-CHATGPT.md` — second reviewer

**Evidence discipline (empirical):** Broken. The review opens by asserting that `VISION.md` "could not be located or inspected from the current branch paths available to this review." The file exists at the repository root and is 153 lines long. Verified by direct read. This is not a minor sourcing issue: it is the review's headline finding ("That is itself the most important finding") and it is empirically false. The reviewer then elects to write a vision review based on inferred-from-secondary-docs reasoning (`README.md`, `docs/architecture.md`, `docs/contracts.md`, `docs/roadmap.md`).

The downstream consequence is that essentially every recommendation the review makes about specific `VISION.md` content is uncalibrated — the reviewer cannot critique what the document does or does not say because the reviewer never read it. Recommendations like "add a vision contract at the top," "add a product-in-one-paragraph section," "replace 'Skeptic catches ≥1 weak claim per run on average'" are about a document the reviewer reconstructed, not the one on disk. Some of those reconstructions are wrong (e.g., the cited "≥1 weak claim per run on average" criterion is not present in `VISION.md`'s actual graduation list).

**Discipline on the interpretive/empirical line:** Cannot be assessed independently because the empirical foundation is absent.

**Framing and scope:** Sprawls into architecture and workflow territory. Recommendations 1, 3, 4, 8, 9, 10 are arguably workflow or architecture concerns; the review does not acknowledge the boundary.

**Internal consistency:** Reasonable in the abstract — the recommendations align with each other and with the diagnosed (inferred) failure modes — but the diagnosis itself is built on a missing foundation.

**AI-pattern check:** Severe recommendation inflation (ten section-level edits + twelve user-decision questions). Heavy hedging language ("should," "ought," "could be useful"). Several "add a section that does X" recommendations are gestural — they describe the function but not the wording. The numerical form "Skeptic catches ≥X% weak claims" critique attacks a phrasing the document does not contain.

**One genuinely useful contribution:** the "negative examples" idea (a list of what bad CBM output looks like) is portable and was not raised by either other reviewer.

**Independence:** Independent in the strict sense (no echo of the other two), but its independence is purchased at the cost of empirical grounding.

**Verdict:** Heavily discounted on specific claims. Useful for a few generic instincts (negative examples; document-integrity policy), but its contribution to adjudication is small relative to the other two. Where its convergent recommendations align with the others, the convergence is real but is not three-source confirmation — it is two-source confirmation plus a guess.

### `OUTPUT-VISION-CLAUDE-COWORK.md` — third reviewer

**Evidence discipline (empirical):** Strong. Spot-checked seven citations: `VISION.md:11` (thesis — correct), `VISION.md:33` ("every claim resolves to source bytes" — correct), `VISION.md:31` (coverage discipline — correct), `VISION.md:75–87` (end-state walkthrough — correct), `VISION.md:53-55` (cross-domain travel and discipline transfer — correct), `VISION.md:146` ("Their answers shape what 2.0 looks like" — correct), `RUNTIME-CONSTITUTION.md` §2/§5/§15/§17 cross-references (verified — overlap is real). One minor: `VISION.md:107-120` for anti-vision should be `106-120`. No fabricated citations.

**Discipline on the interpretive/empirical line:** Visibly honored. The review explicitly distinguishes "vision permitted the drift" from "vision caused the drift" and refuses to claim causation. The four mechanisms (A–D) are presented as plausibility arguments rooted in BUILD-LOG patterns, not as proofs.

**Framing and scope:** Generally respects vision-review boundaries. A few recommendations spill into AGENTS.md / CURRENT-PLAN.md territory; the review acknowledges this and routes them appropriately ("In `AGENTS.md`, augment...", "In VISION.md and/or `CURRENT-PLAN.md`...").

**Internal consistency:** High. The diagnoses (§§1–12) and the improvements (1–16) line up.

**Specific failure 1: recommendation inflation.** Sixteen recommendations is too many. Items 11 (graduation criteria as table), 13 (vision-revision protocol), 15 (BUILD-LOG self-critique tied to vision), and 16 (no-kernel-hardening commitment) are each defensible, but presented as a flat list they signal "everything is high-priority." The review's own ordering ("listed in order of expected leverage") is not enforced by the structure.

**Specific failure 2: gestural numeric in improvement 5.** The proposed falsifiable form ("≥X% of cases, with calibration measured on a published rubric") inserts an unspecified X. The review does flag this as a user-decides item (Q6), so the failure is partial — but the recommendation is in the same prose as the slogan it is replacing, which is the AI-pattern signature the prompt warned about.

**Specific failure 3: improvement 4 (tag properties as runtime-bound / mechanical / hybrid) and improvement 12 (drift signatures section) belong in AGENTS.md or `.planning/`, not VISION.md.** The review correctly senses this for #14 and #16; less so for #4 and #12.

**Independence:** The "filename and independence note" is consistent with the file's content. The review did not borrow specific claims from `OUTPUT-VISION.md` despite the write-collision; convergent findings (HORIZONS split, graduation reform, sequencing principle) use different vocabulary and different anchoring evidence than the prior review. The independence claim is verifiable.

**AI-pattern check:** Some manifesto-echo ("the document is too well-finished as prose"). One gestural numeric (above). Acceptable for a vision review of this length.

**Verdict:** The strongest on discipline, on the interpretive/empirical distinction, and on producer-argues-back as v1.0-blocking (a unique and sharp finding). Loses points for recommendation inflation and for one or two recommendations that should have been rerouted.

## Adjudication of contested claims

### Is the asymmetry thesis falsifiable as currently stated?

**Verdict: not as currently stated.** `OUTPUT-VISION-CLAUDE-COWORK.md` is correct; `OUTPUT-VISION.md` is wrong on this specific point.

**Evidence:** `VISION.md:11` reads "The system is better than a careless agent at *not pretending to understand*. The asymmetry is what makes it useful." The sentence names no comparator (which careless agent, with what prompt, on what task?), no measurement (what counts as "not pretending"?), and no protocol (who measures, blind to what?). The thesis is *gesturally* falsifiable — one can imagine a paired-evaluation rubric — but it is not falsifiable as written.

This adjudication does *not* automatically endorse `OUTPUT-VISION-CLAUDE-COWORK.md`'s recommendation 5, which proposes a specific replacement form with an unspecified `≥X%`. That replacement is itself a gesture without the X. The right move is to separate two questions: (a) acknowledge the thesis is not directly testable (settled by evidence; edit-now eligible to add a one-line note), and (b) decide whether to commit to a measurement protocol (user-decides; the protocol is non-trivial).

### Is anti-vision over-committed?

**Verdict: judgment call leaning against the proposed edit.**

`OUTPUT-VISION.md` §F argues that "no marketplace" and "no confidence-aggregator" are over-committed. The arguments are reasonable but the function of anti-vision is precommitment: it forecloses futures the project has decided not to pursue, *and the foreclosure is part of what makes the discipline credible.* Loosening "no marketplace" to "no marketplace at v1.0" trades a strong commitment for a weak one and gives back the rhetorical force the document buys with the closure. The argument for opening the door is hypothetical ("a curated pack ecosystem could be useful"); the argument for keeping it closed is operational (the project's discipline depends on its precommitments holding).

Recommend: keep both anti-vision items as-is unless the user has a specific reason to reopen one. If the confidence-aggregator language genuinely rules out *useful* aggregations (e.g., per-run distributions across registers, which the document's own end-state walkthrough describes), the right edit is to add a clarifying sentence — not to weaken the absolute. The other reviewers' silence on this is a soft signal that the existing wording isn't actually causing observed drift.

### Is "minimum useful CBM" the right floor?

**Verdict: yes, conditionally.** Two reviewers converge on this; the diagnosis (no floor between seed and mature) is verifiable against `VISION.md`'s structure (the document offers a floor named "mature" and a ceiling named "ideal" with nothing between them). The conditional: the floor must commit to *one external codebase, runtime-agent-produced, end-to-end* to do the work the diagnosis says it should do. A weaker floor that allows continued smoke-on-self runs would not address the drift mechanism either review identified. Edit eligible; concrete content is *user-decides* on aggressiveness (blocking gate vs. strong norm).

### Is the producer-argues-back conjecture v2.0 work or v1.0-blocking?

**Verdict: judgment call leaning toward v1.0-blocking.** Unique to `OUTPUT-VISION-CLAUDE-COWORK.md`. The argument is: `RUNTIME-CONSTITUTION.md` §17 currently gives the producer two options on an interpretive challenge (accept-as-alternative or accept-as-replacement) plus a footnote allowing argue-back with new evidence. The "argue back" path is named but not protocolized. When the runtime Skeptic is built, *something* will happen on argue-back — either the design will include it (which means the conjecture should be settled now) or the design will exclude it (which is a v1.0 decision, not a v2.0 deferral). Calling it v2.0 lets the question float into agent code without an explicit choice.

This is interpretively right but operationally tractable: the user can decide before the runtime layer is built whether argue-back is supported. The vision can mark the conjecture as "decision required before runtime agents ship" without committing to an answer. *User-decides* eligible.

### Should `HORIZONS.md` be split off?

**Verdict: judgment call; reversible if attempted.** Two reviewers converge. The diagnosis (ideal section pulls scope forward) is plausible and partially supported by BUILD-LOG patterns (work on cross-time composition outpaced work on the asymmetry-grounding criteria). Counterargument: the document's literary force comes partly from carrying floor and ceiling in one place; the rhetorical move "this is the bar; this is what excellent looks like above the bar" is a reading experience, not just a structural one. Splitting reduces drift exposure but also reduces the document's argumentative density.

The split is reversible (re-merging is cheap if the split was wrong; the split itself is mostly cut-and-paste). Recommend: try the split, and revert if the user finds the truncated `VISION.md` thinner than they want. *User-decides* with low cost to either choice.

### Did the vision contribute to drift?

**Verdict: undecidable from the evidence available; the strongest claim supported is "the vision permitted the drift, the workflow loop did not push back, and a clearer vision would have created counter-pressure."** All three reviewers reach approximately this conclusion; their convergence is a real signal, but it is also a signal worth examining for shared blind spots. The architecture and workflow tracks may locate the drift's actual cause in (a) the absence of a runtime-agent backend choice, or (b) the `/goal` loop's bias toward locally tractable work, or (c) both. The disposition cannot adjudicate causation; it can only report the convergent finding and refuse to overclaim.

This is the load-bearing claim that goes unadjudicated and is surfaced to the user as an open question (Q1 below).

## Actionable edit recommendations

Ten recommendations, ordered by leverage and reversibility. Each names target file, scope, rationale, and a falsification test. Where the test is necessarily soft, that is noted.

### 1. Strike or reword runtime-obligation lines in `VISION.md` "What mature looks like"

**Target:** `VISION.md`, lines 31 and 33 (and the artifact enumeration at lines 18–19).
**Scope:** sentence-level edits. Replace duplications of `RUNTIME-CONSTITUTION.md` §2/§5/§15 with experience-level prose pointing to the constitution.
**Rationale:** The duplication is verifiable (`VISION.md:33` ≈ `RUNTIME-CONSTITUTION.md:13–25`; `VISION.md:31` ≈ `RUNTIME-CONSTITUTION.md:207–211`). When destination prose names runtime obligations, it lets schema/gate work register as vision progress; the BUILD-LOG pattern is consistent with this mechanism.
**Falsification test (soft):** of the next 20 BUILD-LOG slices, none should be a contestation-propagation or coverage-honesty slice that is *only* over fixture data. If they continue to be, this edit didn't address the mechanism.
**Status:** *edit-now*. The duplication is a verifiable cleanup; no judgment call is needed about whether to commit.

### 2. Move `§ "The ideal version"` (lines 39–61) to `HORIZONS.md`; replace in `VISION.md` with a one-paragraph pointer

**Target:** new file `HORIZONS.md` (root); `VISION.md` lines 39–61 replaced with a pointer.
**Scope:** structural move (mostly cut-and-paste).
**Rationale:** Two reviewers converge; verified that VISION.md mixes mature and ideal in one prose register without a structural break. Reversible.
**Falsification test:** of the next 30 BUILD-LOG slices following the split, the ratio of slices advancing maturity-floor properties (`Its claims hold up`, `It is honest about what it didn't do`, `It works on first contact`) to slices advancing horizon-shaped properties (`It composes with itself across time` — refresh/consult/corpus) should rise above its current value. If it does not, the split did not redirect implementation choice.
**Status:** *user-decides*. The literary-force-vs-drift-prevention tradeoff is real; only the user can weigh it.

### 3. Add a "Minimum useful CBM" floor between current `§ "What mature looks like"` and `§ "The ideal version"` (or wherever ideal moves)

**Target:** `VISION.md`, new section after current line 37.
**Scope:** one paragraph (~80–120 words). Specifies the smallest run that demonstrates the asymmetric thesis: one runtime-agent-produced surface map and one Skeptic challenge over an actual interpretive claim, on one external 5–20kLOC codebase, with citations resolving.
**Rationale:** Two reviewers converge; the diagnosis (no floor between seed and mature) is verifiable; `STATE.md:60–64` confirms the missing benchmark.
**Falsification test:** within four weeks of the edit, `CURRENT-PLAN.md` either names a specific external benchmark repository or explicitly justifies why none has been chosen. If neither, the edit added language without changing planning behavior.
**Status:** *user-decides*. The floor's aggressiveness (blocking gate vs. strong norm) is a user call. A weak version is worse than no edit.

### 4. Add a sequencing-principle paragraph to `VISION.md`, OR augment `AGENTS.md`'s self-critique drift check, with the same content

**Target:** *either* `VISION.md` (after line 13, ~one paragraph), *or* `AGENTS.md` (augment self-critique cadence: "name which maturity property or graduation criterion this slice advances; if none, justify").
**Scope:** one paragraph either place.
**Rationale:** Two reviewers converge on the underlying diagnosis (kernel work outpaced agent producers because no rule pushed back). The choice of *which file* is a real one: in `VISION.md` it has more rhetorical weight but blurs the vision/workflow boundary; in `AGENTS.md` it operationalizes cleanly but loses vision-level force.
**Falsification test:** of the next 20 BUILD-LOG slices, ≥80% should name a specific maturity property or graduation criterion they advance, and the named property should be runtime-agent-bound at least 50% of the time. (The percentages are illustrative; the user should pick the values they will actually hold the loop to.)
**Status:** *user-decides*. The choice is between two locations; either is a real edit.

### 5. Add a one-sentence acknowledgment that the asymmetry thesis is not directly testable, and either commit to a measurement protocol or note the protocol is open

**Target:** `VISION.md` near line 11.
**Scope:** one sentence acknowledging the gesturalness; optionally, a second sentence committing to a measurement direction.
**Rationale:** Adjudicated above. The thesis as written names no comparator and no measurement. Acknowledging this strengthens the document by making its central claim honest about its own status.
**Falsification test (soft):** if the user later proposes a measurement protocol, the protocol should refer back to this sentence as the open question it answers. If no protocol ever materializes, the sentence still does work as an honesty marker.
**Status:** *edit-now* for the acknowledgment sentence. *User-decides* for whether to commit to the measurement protocol (because committing without a real X, comparator, and rubric is the AI-pattern failure the prompt warned about).

### 6. Reframe `§ "Open conjectures"` to distinguish v1.0-blocking decisions from v2.0 questions

**Target:** `VISION.md`, lines 132–146.
**Scope:** small structural edit; partition the existing five conjectures into two sub-lists, with explicit prose that says producer-argues-back and claim-dependency cascade are decisions required before the runtime agent layer is designed.
**Rationale:** Unique to `OUTPUT-VISION-CLAUDE-COWORK.md`; verified against `RUNTIME-CONSTITUTION.md` §17, where argue-back is named but not protocolized. Calling these "v2.0" lets them float into agent code without a decision.
**Falsification test:** when the runtime Skeptic is implemented (a future slice), its design either implements producer-argues-back semantics or explicitly defers it with reasoning attached. If it implements neither and silently defaults, this edit didn't do its work.
**Status:** *user-decides* for the v1.0-blocking classification (the user may believe the conjecture is genuinely deferrable). The structural separation is *edit-now*; the v1.0-blocking label is the part that needs user signoff.

### 7. Commit on deployment shape (or commit to deferring it)

**Target:** `VISION.md`, new short section before `§ "Graduation criteria"`, OR `docs/architecture.md` if the user prefers to keep `VISION.md` thin.
**Scope:** one or two sentences. Either "CBM is a local CLI invoked by a developer or autonomous loop, producing artifacts on disk" or "Deployment shape is undetermined and is the next architectural decision."
**Rationale:** All three reviewers converge. The current silence is the problem; either commitment is fine.
**Falsification test:** after commitment, `CURRENT-PLAN.md`'s candidate-architecture-direction section should not churn for at least four weeks. If it does, the commitment was not specific enough.
**Status:** *user-decides*. The user's confidence about long-run interface model determines what the document can fairly commit to.

### 8. Restructure graduation criteria

**Target:** `VISION.md`, lines 89–104.
**Scope:** moderate structural rewrite. Three candidate forms:
- (a) Core / Supporting / Post-1.0 split (`OUTPUT-VISION.md` V3).
- (b) Tag-each-criterion-as-mechanical/runtime-bound/ecosystem (`OUTPUT-VISION-CLAUDE-COWORK.md` improvement 4 + 11).
- (c) Measurable-table form with current measurement column (`OUTPUT-VISION-CLAUDE-COWORK.md` improvement 11).
**Rationale:** All three reviewers want this. Verified that criteria 9 and 10 require ecosystem infrastructure not sequenced anywhere, while 1, 2, 5, 6, 7 are mechanically reachable.
**Falsification test:** within two weeks of the edit, at least three criteria should have a current measurement attached (even if the measurement is "not yet measured because the runtime agent layer doesn't exist"). If none get measured, the criteria are still gesture rather than gate.
**Status:** *user-decides*. Form (a) is the most conservative; form (c) is the most operationally rigorous. Pick one; don't blend.

### 9. Add a "Coda" or one-line at the end of `VISION.md` that names the document's revision protocol

**Target:** `VISION.md`, near the existing Coda (lines 148–152).
**Scope:** one short paragraph naming when the document changes, what evidence triggers a change, and where revisions are logged.
**Rationale:** Unique to `OUTPUT-VISION-CLAUDE-COWORK.md` improvement 13. The diagnosis (vision either freezes or erodes silently) is plausible; `STATE.md:22` already names VISION.md as a revision target without saying how revision happens.
**Falsification test:** the next time `VISION.md` changes, the change is logged in the place this paragraph names. If `VISION.md` is edited silently, the paragraph wasn't enough.
**Status:** *edit-now*. Low risk; high mild value.

### 10. Add a single-line VISION.md commitment that no further kernel-hardening work merges before one runtime-agent-produced handoff on one external codebase exists

**Target:** *primarily* `CURRENT-PLAN.md`'s "Non-Goals Right Now" section (it already partially covers this at lines 96–97); *secondarily* `VISION.md` as one supporting line if the user wants vision-level force.
**Scope:** one line in CURRENT-PLAN.md; optionally one line in VISION.md.
**Rationale:** This is fundamentally a planning commitment, not a vision claim. It should live in CURRENT-PLAN.md. A vision-level reflection of it is supportive but not essential.
**Falsification test:** of the next 10 BUILD-LOG slices, at least one is either a runtime-agent-architecture slice (a decision artifact, a backend choice, a scaffolding commit), or an explicit deferral with reasoning. If all 10 are kernel-hardening, the commitment is rhetorical.
**Status:** *edit-now* for CURRENT-PLAN.md. *User-decides* for whether to mirror at vision level.

### Recommendations the disposition does NOT promote

- `OUTPUT-VISION.md` V6 (loosen anti-vision items #5 and #6). Adjudicated against above; the function of anti-vision is precommitment. If the user disagrees, this can be revisited as user-decides.
- `OUTPUT-VISION-CLAUDE-COWORK.md` improvement 12 (drift signatures section). Belongs in `AGENTS.md`, not `VISION.md`. If the user wants drift signatures, write them where they will be read by the loop.
- `OUTPUT-VISION-CHATGPT.md` recommendations 1, 3, 4, 5, 8, 9, 10. Each is uncalibrated against `VISION.md`'s actual content (the reviewer never read it). Several are workflow concerns dressed as vision concerns.
- `OUTPUT-VISION-CHATGPT.md` recommendation 7 ("negative examples") — interesting but bloats the document and does not address the drift mechanism. Consider for `RUNTIME-CONSTITUTION.md` if anywhere.

## Cross-track and second-order notes

Several recommendations are doing operational work — they tell `/goal` mode what to do — and that work mostly belongs in `AGENTS.md` (drift detection, slice-naming requirement, self-critique augmentation) or `CURRENT-PLAN.md` (no-kernel-without-runtime-agent commitment), not `VISION.md`. The disposition reroutes recommendation 4 (sequencing) and 10 (kernel-hardening pause) accordingly. If the user wants the rule visible at vision level for rhetorical force, a single-sentence cross-reference is cheaper than duplicating the rule.

This disposition does not adjudicate whether the drift's *primary* cause is vision permissiveness, workflow opportunism, or absence of a runtime-agent backend choice. The architecture and workflow tracks are running in parallel and may locate the cause elsewhere. If the architecture disposition concludes that the runtime-agent backend choice was the binding constraint, several vision-level recommendations here may become less load-bearing (because the right fix would be architectural, not rhetorical). The user should read the dispositions together rather than treating this one as authoritative on causation.

The recommended edit set as a whole is moderate. It adds: a minimum-useful-CBM floor, a sequencing principle (probably in AGENTS.md), an honesty marker on the asymmetry thesis, a v1.0-blocking re-classification of two open conjectures, a deployment commitment, a graduation-criteria restructure, a revision protocol, and a runtime-obligation cleanup. It removes: the ideal-version section to a separate file. The literary force of `VISION.md` survives this set if the runtime-obligation cleanup is done lightly (replacing line 31/33 *experience* prose, not stripping the prose entirely) and if the ideal-version split is done with a strong pointer paragraph at the seam. If the user wants a milder variant, recommendations 1, 5, 6, 7, 9 alone would address the load-bearing diagnoses; 2, 3, 4, 8 are the ambitious half.

## Open questions for the user

These cannot be derived from the reviews or the source documents. Each drives multiple edits.

1. **Did vision permissiveness, workflow opportunism, or absence of a runtime-agent backend choice contribute most to the kernel-vs-runtime-agent drift?** All three vision reviewers concluded vision contributed; that conclusion is itself adjudicable, and the architecture and workflow dispositions may relocate the cause. If the user reads architecture's disposition as locating the cause elsewhere, several vision-level recommendations here become less urgent.

2. **Is the central asymmetry the test, or one test among several?** If the user agrees it is *the* test, the sequencing rule (recommendation 4) is correct. If the user reads the cross-domain travel and corpus-as-empirical-material claims as themselves load-bearing — i.e., the discipline traveling is the project's central contribution, not CBM-on-code — then the recommendations to demote ideal-version content and to commit on deployment shape need a different framing. This drives recommendations 2, 3, 4, 7.

3. **Is the project's primary near-term target "ship a useful CBM-on-code in a defined window" or "establish a discipline that ships eventually"?** Different next slices follow from different answers. The vision currently supports both readings.

4. **What is the comparator and the measurement protocol for the asymmetry thesis?** Recommendation 5 acknowledges the gesturalness without committing to a protocol. A real protocol requires a comparator (which agent baseline, on which task), a rubric, and an evaluator pool. This is non-trivial design work; it should not be invented to satisfy a vision edit.

5. **Should the producer-argues-back protocol be settled before runtime agents are built, or deferred to v2.0?** Drives recommendation 6. The disposition's reading is "settle now"; the user may read otherwise.

6. **Should the `HORIZONS.md` split be tried, or is the document's literary unity worth more than the drift-prevention?** Drives recommendation 2.

7. **How aggressive should the deployment-shape commitment be?** "CBM is a local CLI" is the most constraining; "deployment is undecided" is the least. Drives recommendation 7.

8. **Are project-type packs and the corpus expected to be in-tree, vendored, or community-distributed?** The marketplace is anti-vision; what fills the gap is unspecified. Drives recommendation 7 and the deployment commitment.

The disposition treats every other contested point as either evidence-settled (and labelled *edit-now*) or as a reversible attempt the user can revert if it fails. The eight questions above are the ones where the wrong answer propagates.

---

End of disposition. The edit set is intentionally smaller than any single review's recommendation list. The value is in the adjudication, not in the comprehensiveness.
