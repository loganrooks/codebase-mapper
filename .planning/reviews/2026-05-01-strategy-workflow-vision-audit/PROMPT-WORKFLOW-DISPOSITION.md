# Prompt: Workflow Review Disposition

You are an independent disposition reviewer for the CBM workflow and governance audit. Three workflow reviews of this project exist. Your job is not to write a fourth review, and not to summarize the existing three. Your job is to compare them, meta-critique them, adjudicate their disagreements against evidence, and distill the result into a prioritized set of actionable recommendations the user can decide from.

You are a Claude session with file access to the CBM repository. Use it. Workflow reviews make factual claims about git state, branch posture, BUILD-LOG entry counts, planning-file timestamps, the cadence of self-critique entries, what `.planning/` actually contains, what `.research/` actually contains, and whether named protocols are honored in the actual history of the repo. When two reviews disagree on a fact, **read the workflow artifacts** — `git log`, `git status`, the planning directory tree, the BUILD-LOG itself, the timestamps and authorship of planning files. Do not vote-count.

This is not architecture review. The reviewers are not arguing about whether `cbm run` orchestrates agents; they are arguing about whether the *process* that produced `cbm run` is sound, auditable, and survivable for a long-running automated `/goal` loop. The empirical anchors are different. Most workflow claims resolve to one of: a git fact (commit count, branch divergence, untracked files, merge cadence), a planning fact (what artifacts exist, what their statuses are, when they were last updated, whether they reference each other consistently), a BUILD-LOG fact (entry count, self-critique cadence, claim-to-evidence ratio), or a protocol fact (whether a named rule in `AGENTS.md` actually fires in the recorded history).

## Inputs

Three workflow reviews live in `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/`:

- `OUTPUT-WORKFLOW.md` — Opus 4.7 max (1M-token context) via the Claude Code CLI.
- `OUTPUT-WORKFLOW-CHATGPT.md` — GPT-5.5 Pro with extended thinking.
- `OUTPUT-WORKFLOW-CLAUDE-COWORK.md` — Claude (this product, Cowork mode).

The model attributions are factual context, not weighting hints. Each model has characteristic strengths and failure patterns; you may use that knowledge to *recognize* patterns more quickly during meta-critique, but you must not weight reviews by model identity. A factual claim about git state, BUILD-LOG cadence, or planning-file structure either holds against the repository or does not, regardless of who wrote it. One of the reviews shares a model lineage with you; that confers no privilege.

The original prompt all three responded to is `PROMPT-WORKFLOW.md` in that same directory. Read it first — it tells you what each reviewer was asked to produce. Note in particular what it asked about: governance for an automated Codex `/goal` loop, the role of `AGENTS.md`, the division of labor between `docs/roadmap.md` / `.planning/CURRENT-PLAN.md` / `.planning/STATE.md` / `BUILD-LOG.md`, current-plan lifecycle, drift/failure recovery, phase verification, reviewer/checkpoint protocol, escalation thresholds, archival, doc freshness. The prompt also told reviewers not to assume the current planning reset is adequate. One of the things you will be checking is which reviewers honored that instruction and which silently endorsed `STATE.md` / `CURRENT-PLAN.md` as their starting position.

The packet also contains architecture and vision reviews (`OUTPUT-ARCHITECTURE-*.md`, `OUTPUT-VISION-*.md`) and an existing architecture disposition (`OUTPUT-ARCHITECTURE-DISPOSITION-CLAUDE-COWORK.md`). These are not your primary input, but if a recommendation in one bears directly on adjudicating a workflow disagreement — e.g., the architecture disposition has already settled what counts as a "phase" — you may consult it. Do not let it drive your output, and do not adopt its adjudication style without evaluating whether it fits the workflow domain.

The repository's primary workflow sources — the same ones the reviewers had access to — are: `AGENTS.md`, `.planning/STATE.md`, `.planning/CURRENT-PLAN.md`, `.planning/reviews/` (entire tree), `BUILD-LOG.md`, `docs/roadmap.md`, `RUNTIME-CONSTITUTION.md` (for the dev/runtime asymmetry questions), `VISION.md` (for the destination/discipline questions), `README.md`, the `.codex/` adapter files, `platform/PORTABILITY.md`, and the `.research/` directory (as evidence of how runs and smoke tests have actually been used). You will also need git: `git status`, `git log --oneline`, `git branch -a`, `git diff --stat`, and the like. You will need to revisit these to spot-check claims.

## What independence means here

Anti-deference, four ways:

1. **Don't defer to the longest review.** Length is not evidence. Workflow reviews can pad easily by enumerating ten more thresholds or ten more frontmatter fields; precision beats coverage.
2. **Don't defer to model identity.** Treat the three reviews as anonymous. If you find yourself thinking "Claude is more likely to be right on planning ergonomics" or "ChatGPT is more rigorous on protocol design," strike the thought and look at the citations and the artifacts they cite.
3. **Don't manufacture consensus.** When two reviews silently agree on something, that is data, not proof. When all three reviews fail to mention a thing, that is *not* consensus on its absence — it may be a shared blind spot. Workflow reviews are particularly prone to converging on familiar tropes (frontmatter fields, archive directories, escalation thresholds) without checking whether the tropes solve the actual observed friction.
4. **Don't manufacture disagreement.** Sometimes reviews use different vocabularies for the same diagnosis — "checkpoint reviewer," "second-party Skeptic," "phase-boundary auditor." Decide whether a divergence is real or terminological before treating it as a contested point.

You may conclude that all three reviews are partially wrong. You may conclude that the right recommendation is one none of them made. You may conclude that the load-bearing problem is one none of the reviewers named. All are allowed.

## Phase 1 — Read

Read this prompt. Read `PROMPT-WORKFLOW.md` and `SHARED-CONTEXT.md`. Read the three reviews end-to-end. Read enough of the primary sources to know roughly what's in each: at minimum `AGENTS.md`, `.planning/STATE.md`, `.planning/CURRENT-PLAN.md`, the structure (not full text) of `BUILD-LOG.md`, and `docs/roadmap.md`. Run `git status`, `git log --oneline | head -60`, `git branch -a`, and `git diff --stat` against the repo to ground yourself in the *actual current state* the reviews are arguing about — several factual claims in the reviews are about git state and you should know it from the source before adjudicating. The reviews will reference specific BUILD-LOG entries, planning files, and protocol gaps; you should be ready to look those up.

## Phase 2 — Compare

Build a structured comparison. The output of this phase, internally, should answer:

- What workflow diagnoses do all three converge on? (List them — e.g., is "BUILD-LOG is unreviewable" a shared finding, or only one reviewer's?)
- Where do they diverge in *prescription* while agreeing on diagnosis? (E.g., all three see drift; do they prescribe different recovery protocols?)
- Where do they directly contradict on diagnosis? (One says X is the load-bearing problem; another says X is fine, the real problem is Y.)
- What does each review uniquely observe — claims only that review makes? (Single-source claims are high-signal: either the reviewer saw something the others missed, or the reviewer invented something.)
- What recommendations do they agree on? Disagree on? At what level of specificity (protocol vs. principle)?

Don't be comprehensive — be precise. A short list of *load-bearing* agreements and disagreements is more useful than a long matrix of trivia. Workflow reviews tend to converge on principles ("more discipline," "more review," "better archival") and diverge on protocol ("how exactly do plans transition to archived"). The protocol-level disagreements are usually the load-bearing ones.

## Phase 3 — Meta-critique each review

Evaluate the reviews themselves, not just their conclusions. For each review:

- **Evidence discipline.** Are factual claims about workflow state anchored to git output, BUILD-LOG line numbers, planning-file timestamps, or quoted text? Or are they assertions? When you spot-check the citations, do they hold up? Did the reviewer actually count BUILD-LOG entries, or did they estimate? Did they actually look at `git status`, or did they describe a hypothetical dirty tree?
- **Framing.** The prompt told reviewers not to assume the current planning reset is adequate. Did the review actually push back, or did it echo `STATE.md` / `CURRENT-PLAN.md` and call that diagnosis? A review that recommends what `CURRENT-PLAN.md` already says is mostly recommending compliance, not change.
- **Blind spots.** What does the review not see? What primary sources does it underuse? Common workflow blind spots to check for: untracked governance files; the per-slice self-critique cadence problem; the verification-on-self circular evidence problem; the dev-vs-runtime discipline asymmetry; the missing checkpoint reviewer; the `.research/` smoke run direct-examination ratio; the absence of a benchmark fixture; the unreviewable BUILD-LOG; the lack of escalation thresholds tied to actually-exhibited drift modes.
- **Recommendation specificity.** Are recommendations concrete (with files, protocols, named commands, threshold numbers) or hedged ("consider," "explore," "more discipline")? Vague workflow recommendations are not actionable. "Add escalation thresholds" is vague; "halt the loop when uncommitted constitution-class files are older than one session" is concrete.
- **Internal consistency.** Does the review's diagnosis line up with its recommendations? A review that diagnoses "BUILD-LOG self-critique is noise" and then recommends adding more frontmatter to BUILD-LOG entries has not connected its own dots.
- **AI-pattern failures.** Watch for: hedging without commitment, false structure (headers without content), padded executive verdicts, "let me know if you'd like me to elaborate" tails, premature evenhandedness ("on the one hand … on the other hand …" as a substitute for taking a position), confident assertion without grounding, fabricated citations, pretending observed facts are recommendations ("the project should commit untracked files" presented as new advice when the reviewer is just describing a current violation).
- **Workflow-domain hazards.** Workflow reviews have characteristic failure modes architecture reviews do not: process-mongering (recommending so much protocol that the loop spends more cycles on governance than on building); imported-from-elsewhere templates (escalation matrices that look corporate-borrowed and don't match a single-developer/single-agent reality); recommending tools (frontmatter fields, status manifests, doc-stale checkers) without recommending the discipline that would make humans actually use them.
- **Independence under stress.** Did the review claim independence and actually behave so? Did it read other reviewers' outputs (you may not be able to verify directly, but tonal echoes, shared specific phrasings, or shared lists of failure modes in the same order are tells)?

Be specific in the meta-critique. "Review X is a bit hand-wavy" is not useful. "Review X claims `BUILD-LOG.md` has 'about 100 entries' but a `grep -c '^## ' BUILD-LOG.md` returns N, and the review uses the inflated count to justify its rotation threshold" is useful.

## Phase 4 — Adjudicate

For every contested claim or recommendation worth keeping, decide who is right, and why. The meta-critique is your lens: a review that has shown stronger evidence discipline gets more weight on factual disagreements (e.g., "is the working tree dirty in a way that's load-bearing?"); a review that has shown stronger protocol design gets more weight on lifecycle disagreements (e.g., "how should plans transition to archived?"); a review caught padding or process-mongering gets less weight on its top-line verdict.

Some workflow disagreements *cannot* be adjudicated from current evidence — they are forward-looking ("will this escalation threshold prove well-tuned?") and only settle over operating time. When you cannot adjudicate from the evidence alone, say so explicitly. Don't fabricate certainty. Surface the unresolvable question for the user as part of Phase 5 ("Open questions").

When all three reviews agree, treat the consensus as a *strong default* but verify it against primary sources before promoting it to the recommendations. Shared blind spots are real, especially in workflow review — three reviewers can all import the same template (frontmatter, archive directories, status fields) without any of them checking whether the template solves the observed friction. The acid test is: "does this recommendation, if implemented, actually prevent the specific failures the reviewers documented?" If not, the consensus is a trope.

## Phase 5 — Actionable recommendations

Distill the adjudication into a prioritized recommendation list. Constraints:

- **Each recommendation is concrete.** Name the files, the protocols, the threshold numbers, the commit hooks, the planning artifacts, the named commands. "Add a stale-doc detector" is half a recommendation; "Add `cbm-docs-status` that flags governance docs whose `last_verified` precedes the most recent commit touching their referenced subject area; require it to pass on session start" is a recommendation.
- **Each recommendation has a one-line rationale anchored to the adjudication** ("recommended because reviews B and C converged on observation X, the meta-critique sustained their evidence — specifically the git log shows N commits without a merge — and review A's objection was rejected because it conflated phase boundaries with slice boundaries").
- **Each recommendation has a falsification test.** Workflow recommendations are harder to falsify in the moment than architecture recommendations — most can only be observed over operating time. State the test in operational terms: "We'll know this was right if, over the next 30 days of `/goal` execution, the loop surfaces to the user no more than N times for non-substantive reasons and no fewer than M times for substantive reasons" beats "this should improve auditability." For recommendations that *can* be checked immediately ("commit the untracked files"), the falsification test is the immediate check.
- **Order by leverage and reversibility.** Highest-leverage and most-reversible items first. A recommendation to commit untracked files is high-leverage and fully reversible; a recommendation to restructure the planning directory is high-leverage but only reversible at cost; a recommendation to redefine what counts as a "phase" is high-leverage but irreversible-ish (subsequent BUILD-LOG entries will use the new vocabulary). Order accordingly.
- **Distinguish protocol from tooling.** Some recommendations are pure protocol (a rule in `AGENTS.md`); others require tooling (a `cbm-loop-status` command, a checkpoint-reviewer agent definition, a CI hook). Mark which is which. A protocol the loop won't follow without tooling is not a protocol — it's a wish.

If the right answer is "do nothing yet, decide first," that is a valid recommendation. Name the decision explicitly and the consequence of deferring it. Workflow questions like "should the dev agent use Codex CLI subprocess invocation as its escalation channel" may be answered by the architecture disposition; if so, defer to it and say so.

Do not pad the list to look comprehensive. Five concrete recommendations are better than fifteen hedged ones. Workflow reviews tend to produce long lists; the disposition's value is in pruning to the load-bearing few.

## Output

Write to `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/OUTPUT-WORKFLOW-DISPOSITION-CLAUDE-COWORK.md`. Do not overwrite the three input reviews.

Use this structure:

- **Comparison summary** — where the three reviews agree, diverge, and contradict, in compact form. Distinguish diagnosis-level convergence from prescription-level convergence; they often differ.
- **Meta-critique per review** — one section per review, named by filename. Specific, evidence-anchored, fair. Note workflow-specific failure modes (process-mongering, template-importing, tooling-without-discipline) where you see them.
- **Adjudication of contested claims** — the load-bearing disagreements only, with verdict and rationale. Skip terminological-only disputes.
- **Actionable recommendations** — prioritized list with rationale, protocol-vs-tooling tag, and falsification test per item.
- **Open questions for the user** — decisions that cannot be derived from evidence and that the user must take. Include forward-looking workflow questions whose answers depend on operating experience.

## Anti-patterns to refuse

Do not produce: a fourth workflow review that competes with the three; a "synthesis" that smooths the disagreements into a generic position about "more discipline"; a recommendation list that paraphrases all three reviews back at them; an executive verdict that hedges every load-bearing claim; a meta-policy document that prescribes process about process. Do not import a generic governance template (escalation matrices, RACI charts, board-style reviews) and pretend the reviewers recommended it. Do not turn the disposition into a wish list of tooling without naming the discipline that would make humans use it.

The disposition's value is in the adjudication. If you find yourself unwilling to adjudicate, say which review you cannot weigh against the others, and why. If you find yourself recommending more process than the project's actual operating tempo can absorb, you are recommending bureaucracy, not workflow. The bar is: a `/goal` loop, run unattended for a week, would be measurably more aligned with `VISION.md` if these recommendations were in force — and a human reviewer, returning after that week, could verify the alignment in under an hour.

That is the bar.
