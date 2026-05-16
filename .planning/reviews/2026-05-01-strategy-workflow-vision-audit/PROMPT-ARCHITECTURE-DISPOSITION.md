# Prompt: Architecture Review Disposition

You are an independent disposition reviewer for the CBM architecture audit. Three architecture reviews of this project exist. Your job is not to write a fourth review, and not to summarize the existing three. Your job is to compare them, meta-critique them, adjudicate their disagreements against evidence, and distill the result into a prioritized set of actionable recommendations the user can decide from.

You are a Claude session with file access to the CBM repository. Use it. Reviews make factual claims about file paths, line numbers, function behavior, and counts. When two reviews disagree on a fact, **read the code**. Do not vote-count.

## Inputs

Three architecture reviews live in `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/`:

- `OUTPUT-ARCHITECTURE.md` — Opus 4.7 max (1M-token context) via the Claude Code CLI.
- `OUTPUT-ARCHITECTURE-CHATGPT.md` — GPT-5.5 Pro with extended thinking.
- `OUTPUT-ARCHITECTURE-CLAUDE-COWORK.md` — Claude (this product, Cowork mode).

The model attributions are factual context, not weighting hints. Each model has characteristic strengths and failure patterns; you may use that knowledge to *recognize* patterns more quickly during meta-critique, but you must not weight reviews by model identity. A factual claim either holds against the code or does not, regardless of who wrote it.

The original prompt all three responded to is `PROMPT-ARCHITECTURE.md` in that same directory. Read it first — it tells you what each reviewer was asked to produce, and what discipline they were asked to maintain (notably: "Do not assume the current agent's diagnosis is correct. … Diagnose from evidence."). One of the things you will be checking is which reviewers honored that instruction.

The packet also contains workflow and vision reviews (`OUTPUT-WORKFLOW-*.md`, `OUTPUT-VISION-*.md`). These are not your primary input, but if a workflow or vision finding bears directly on adjudicating an architecture disagreement, you may consult them. Do not let them drive your output.

The repository's primary sources — the same ones the reviewers had access to — are: `VISION.md`, `RUNTIME-CONSTITUTION.md`, `README.md`, `AGENTS.md`, `.planning/STATE.md`, `.planning/CURRENT-PLAN.md`, `docs/architecture.md`, `docs/contracts.md`, `docs/roadmap.md`, `docs/reuse-and-refresh.md`, `cbm/cli.py`, `pyproject.toml`, `schemas/*.json`, `skills/*.md`, `platform/*`, `.codex/*`, and `BUILD-LOG.md`. You will need to revisit these to spot-check claims.

## What independence means here

Anti-deference, four ways:

1. **Don't defer to the longest review.** Length is not evidence.
2. **Don't defer to model identity.** Treat the three reviews as anonymous. If you find yourself thinking "Claude is more likely to be right" or "ChatGPT is more rigorous," strike the thought and look at the citations.
3. **Don't manufacture consensus.** When two reviews silently agree on something, that is data, not proof. When all three reviews fail to mention a thing, that is *not* consensus on its absence — it may be a shared blind spot.
4. **Don't manufacture disagreement.** Sometimes reviews use different vocabularies for the same diagnosis. Decide whether a divergence is real or terminological before treating it as a contested point.

You may conclude that all three reviews are partially wrong. You may conclude that the right recommendation is one none of them made. Both are allowed.

## Phase 1 — Read

Read the prompt. Read the three reviews end-to-end. Read enough of the primary sources to know roughly what's in each: at minimum `VISION.md`, `AGENTS.md`, `.planning/STATE.md`, `.planning/CURRENT-PLAN.md`, `docs/architecture.md`, `pyproject.toml`, and the structure (not full text) of `cbm/cli.py`. The reviews will reference specific lines and functions; you should be ready to look those up.

## Phase 2 — Compare

Build a structured comparison. The output of this phase, internally, should answer:

- What diagnoses do all three converge on? (List them.)
- Where do they diverge? (Note the specific point of divergence and which reviews fall on which side.)
- Where do they directly contradict? (One says X, another says ¬X.)
- What does each review uniquely observe — claims only that review makes?
- What recommendations do they agree on? Disagree on?

Don't be comprehensive — be precise. A short list of *load-bearing* agreements and disagreements is more useful than a long matrix of trivia.

## Phase 3 — Meta-critique each review

Evaluate the reviews themselves, not just their conclusions. For each review:

- **Evidence discipline.** Are factual claims anchored to file paths, line numbers, or quoted text? Or are they assertions? When you spot-check the citations, do they hold up?
- **Framing.** The prompt told reviewers not to ratify the current agent's framing. Did the review actually push back, or did it echo `STATE.md` / `CURRENT-PLAN.md` and call that diagnosis?
- **Blind spots.** What does the review not see? What primary sources does it underuse? What architectural option does it dismiss too quickly?
- **Recommendation specificity.** Are recommendations concrete (with files, schemas, or sequences) or hedged ("consider," "explore")? Vague recommendations are not actionable.
- **Internal consistency.** Does the review's diagnosis line up with its recommendations, or does it diagnose problem A and recommend a fix for problem B?
- **AI-pattern failures.** Watch for: hedging without commitment, false structure (headers without content), padded executive verdicts, "let me know if you'd like me to elaborate" tails, premature evenhandedness ("on the one hand … on the other hand …" as a substitute for taking a position), confident assertion without grounding, fabricated citations.
- **Independence under stress.** Did the review claim independence and actually behave so? Did it read other reviewers' outputs (you may not be able to verify directly, but tonal echoes are a tell)?

Be specific in the meta-critique. "Review X is a bit hand-wavy" is not useful. "Review X claims `cbm run` 'orchestrates agents' but cites no spawn site, and the function it describes — at line N — is in-process Python" is useful.

## Phase 4 — Adjudicate

For every contested claim or recommendation worth keeping, decide who is right, and why. The meta-critique is your lens: a review that has shown stronger evidence discipline gets more weight on factual disagreements; a review that has shown stronger architectural imagination gets more weight on alternative-options disagreements; a review caught manufacturing structure gets less weight on its top-line verdict.

When you cannot adjudicate from the evidence alone — when the disagreement is over a value judgment or an empirical question the user has to answer — say so explicitly. Don't fabricate certainty. Surface it as an open question for the user.

When all three reviews agree, treat the consensus as a *strong default* but verify it against primary sources before promoting it to the recommendations. Shared blind spots are real.

## Phase 5 — Actionable recommendations

Distill the adjudication into a prioritized recommendation list. Constraints:

- Each recommendation is concrete: name the files, the commands, or the contracts that change.
- Each recommendation has a one-line rationale anchored to the adjudication ("recommended because reviews B and C converged on X, the meta-critique sustained their evidence, and the code at file:line confirms").
- Each recommendation has a falsification test: how the user (or the dev agent) will know if it was the right move. "We'll know this was right if a real Surface Mapper produces a schema-valid surface-map.json against the benchmark repo within two weeks" beats "this should improve architecture clarity."
- Order by leverage and reversibility. Highest-leverage and most-reversible items first.

If the right answer is "do nothing yet, decide first," that is a valid recommendation. Name the decision explicitly and the consequence of deferring it.

Do not pad the list to look comprehensive. Five concrete recommendations are better than fifteen hedged ones.

## Output

Write to `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/OUTPUT-ARCHITECTURE-DISPOSITION-CLAUDE-COWORK.md`. Do not overwrite the three input reviews.

Use this structure:

- **Comparison summary** — where the three reviews agree, diverge, and contradict, in compact form.
- **Meta-critique per review** — one section per review, named by filename. Specific, evidence-anchored, fair.
- **Adjudication of contested claims** — the load-bearing disagreements only, with verdict and rationale.
- **Actionable recommendations** — prioritized list with rationale and falsification test per item.
- **Open questions for the user** — decisions that cannot be derived from evidence and that the user must take.

## Anti-patterns to refuse

Do not produce: a review of your own that competes with the three; a "synthesis" that smooths the disagreements into a generic position; a recommendation list that paraphrases all three reviews back at them; an executive verdict that hedges every load-bearing claim. The disposition's value is in the adjudication. If you find yourself unwilling to adjudicate, say which review you cannot weigh against the others, and why.

That is the bar.
