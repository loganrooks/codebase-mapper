# Review-response playbook

How to triage and respond to CodeRabbit, Codex, and other AI/human review findings on CBM PRs. Companion to [`review-playbook.md`](review-playbook.md) (which covers how to *launch* reviews).

The principle: **a review finding is a signal, not a script.** The reviewer flagged one site; the fix is rarely just that site. Before committing a narrow patch, audit three axes — generalization, second-order effects, wider horizon. If the patch passes all three, land it. If not, negotiate.

## When to use this playbook

- A CodeRabbit / Codex / human review posts findings on an open PR.
- You are about to push a "fix the comments" commit.
- Especially: when the PR is review-discovery-heavy (multiple rounds, many findings), where narrow patches accumulate technical debt fast.

Skip this playbook only for purely cosmetic findings with no semantic content (typo fixes, formatter noise) — even then, run a quick grep for the same typo elsewhere.

## Disposition vocabulary

Each finding gets one of:

| Disposition | When to use | Reply shape |
|---|---|---|
| **accept** | The finding is right. You will implement exactly what was suggested (or equivalent). | Confirm + name the commit + note any audit findings beyond the spot fix. |
| **accept-with-revisions** | The finding identifies a real problem, but the suggested fix is wrong-shaped. You will implement a different fix that addresses the underlying issue. | Explain the underlying problem, name your fix, justify why it's the right shape. |
| **pushback** | The finding is wrong — based on misreading code, conflicting with a load-bearing constraint, or recommending something against the active horizon's allowed work. | Cite the constraint or code that contradicts the finding. Don't just say "no" — show the evidence. |
| **defer** | The finding is right but out-of-scope for this PR. | Name where it goes (separate cleanup PR, future horizon, follow-up task), with the audit note that captures the deferred work. |
| **clarify** | The finding is ambiguous; you need the reviewer to specify before acting. | Ask the specific question. Don't guess. |

**Never silently accept by pushing a fix without replying.** Even an "accept" finding deserves a reply that names the commit, so the audit trail is legible to humans reading the thread later.

## The three audit axes

For every non-trivial finding, run all three audits before committing a fix.

### Axis 1 — Generalization sweep

> Is this finding a particular instance of a broader class that exists elsewhere in the codebase, where the reviewer just happened to read the first occurrence?

Reviewers — especially AI reviewers reading PR diffs — see only the changed surface. The class-of-bug they spotted often has untouched siblings.

**For code findings**:

- `grep -rn` (or `rg`) for the pattern across the whole repo, not just the PR diff.
- For typed languages: `ast-grep` or the language's symbol-tooling to find structural siblings.
- For symbols or flags: search by name (`grep -n 'symbol_name'`) — finds aliases the reviewer may not have known to look for.

**For doc findings** (harder — semantic relations aren't statically searchable):

- Grep for the exact phrase the reviewer flagged. Stale framings tend to be copy-pasted across authority docs.
- Grep for synonyms ("produce X" vs "create X" vs "generate X"; "deprecated" vs "stale" vs "obsolete").
- Read sibling docs (CURRENT-PLAN.md ↔ STATE.md ↔ HORIZONS.md ↔ BUILD-LOG.md) for the same fact-claim; mismatches indicate the class.

**When the sweep finds siblings**: sweep them in the same commit, unless they're explicitly out of the PR's scope. Then **flag the out-of-scope ones in the reply and in BUILD-LOG.md** so the audit trail captures the deferred work — don't let them silently rot.

### Axis 2 — Second-order audit

> Does the proposed fix break anything that referenced the changed surface? References can be static (callers, imports) or semantic (a sibling doc that asserts the changed claim is still true).

**For code fixes**:

- `grep` for callers of the changed function/symbol.
- Run the test suite to catch unexpected breakage.
- For renames or signature changes: check downstream consumers, especially those outside the PR's blast radius.
- For deletions: check for `# noqa` / `# type: ignore` / commented-out callers that the static checker won't flag.

**For doc fixes**:

- Re-read sibling authority docs for cross-references to the changed claim (CURRENT-PLAN.md ↔ STATE.md ↔ HORIZONS.md cross-reference each other constantly).
- Check BUILD-LOG.md entries that quote the old wording — if the old wording is now wrong, the BUILD-LOG entry needs a follow-up note (don't rewrite history; append).
- Check the VERIFICATION.md / SUMMARY.md / phase PLAN.md trio for any spot that asserted the old shape.
- Check `.codex/skills/*/SKILL.md` and `docs/*.md` for instructions that depended on the old shape.

**Anti-pattern**: a narrow fix that "passes the reviewer's check" but leaves the codebase inconsistent across files. Future iterations of the reviewer (or a different reviewer) flag the next instance — the same class-of-bug just keeps cycling through the PR queue. Sweeping at fix time stops the cycle.

### Axis 3 — Wider-horizon / vision negotiation

> Does the suggested fix conflict with VISION.md, an ADR, RUNTIME-CONSTITUTION.md, the active horizon's allowed work, or a prior load-bearing design decision?

The reviewer typically sees only the PR diff and the immediate file context. They cannot see:

- VISION.md / RUNTIME-CONSTITUTION.md as load-bearing constraints.
- `.planning/decisions/ADR-*.md` decisions that scope a behavior.
- The active horizon's "allowed work" list in CURRENT-PLAN.md.
- Prior commit messages or BUILD-LOG entries that named a constraint.

When a reviewer recommends something that would violate one of these, the right disposition is usually **accept-with-revisions** (the underlying issue is real; the proposed fix is shaped wrong) or **pushback** (the reviewer misread something load-bearing). Almost never silent rejection — if the reviewer flagged it, there's usually a real issue at the bottom, even if the fix is wrong-shaped.

**Reply expectation**: when invoking axis 3, *cite the constraint*. "This conflicts with ADR-005's `SCOPES_REQUIRING_CROSS_MODEL` scope" is a real reply. "We don't do that here" is not.

## Reply shape

Inline-comment replies should be self-contained — a human reading the thread three months from now should understand the disposition without re-reading the whole PR.

Template:

```markdown
**Disposition: <accept | accept-with-revisions | pushback | defer | clarify>.** [Landed in <commit-sha> | No-op (already in <commit-sha>) | Deferred to <where>.]

<one-paragraph: what the finding is, why it's right or wrong, what the fix shape is>

**Class-of-bug audit (axis 1)**: <what you grep'd for, what you found, how many sites swept>.

**Second-order effects (axis 2)**: <what you cross-checked, what you found, why no downstream break>.

**Wider context (axis 3)**: <which constraint you checked (ADR, VISION, horizon, etc.), whether the fix conflicts, the resolution>.
```

You can collapse audit sections that found nothing noteworthy ("Class-of-bug audit: grep returned only the flagged site; no others"). Don't omit them — the explicit "I checked and found nothing" is the audit evidence.

For findings already addressed in a prior commit on the same PR, the reply can be much shorter — just point at the commit and the BUILD-LOG entry. Still mention any class-of-bug findings the prior audit produced.

## Worked example — PR #14 (H2.S1 brief)

Two CodeRabbit rounds + two Codex rounds posted 11 findings. Triage produced:

- 3 no-ops (already addressed in prior commit; reply only).
- 7 accepts (fix landed in same response commit).
- 1 accept-with-revisions (verification-sequence ordering — the suggested fix would have worked but a clearer split made the load-bearing `AUTHORITY_DOC_PATHS` interaction explicit, which solved both this finding and the latent ambiguity in older H1 briefs).
- 0 pushbacks.

Class-of-bug sweeps (axis 1) found that **3 of the 7 accepted findings had sibling instances the reviewers had not flagged**:

| Reviewer flagged | Sweep found | Total fixed in commit |
|---|---|---|
| 1 stale "produce skeletons" wording | 4 instances across HORIZONS / STATE / CURRENT-PLAN | 4 |
| 1 ADR-005 per-slice conflation | 3 instances across CURRENT-PLAN / STATE | 3 |
| 1 broken/empty markdown anchor | 2 instances across STATE / BUILD-LOG | 2 |

Without the axis-1 sweep, the next review round would have re-flagged the siblings. Each unflagged sibling fixed at first-touch saves a full review-round cycle.

## Anti-patterns

- **Spot-fix-then-push**: applying exactly the textual change the reviewer suggested without grepping for siblings or checking sibling docs. The same class re-surfaces in the next review round.
- **Silent rejection**: not replying to a finding you disagree with. The reviewer (and humans reading the thread later) cannot tell whether you saw it. Reply with at least "pushback: <reason>" or "defer: <where>".
- **Reply without commit**: writing "yes, will fix" and then forgetting. Either reply with the landed-in commit, or open a tracked follow-up task and name it in the reply.
- **Disposition-by-effort**: deciding "this is minor so I'll just fix it without audit." Minor findings still have class-of-bug siblings; the cost of a grep is lower than the cost of the next review cycle.
- **Treating CodeRabbit + Codex as one voice**: they apply different lenses. When they agree, that's a stronger signal (raises confidence the contract reading matters). When they disagree, look at what each is anchored to (CR is more rule-based; Codex is more code-and-prose-pattern). Pushback on one does not imply pushback on the other.

## Out-of-scope flagging

When a class-of-bug sweep finds instances outside the PR's scope (e.g., already-merged H1 evidence files that have the same metadata gap as an H2 finding), the rule is:

1. Note in the inline reply that the class extends to those files.
2. Add a BUILD-LOG entry on the response commit recording the deferred work.
3. Add a tracked follow-up task (or file a GitHub issue) — don't rely on memory.
4. Do **not** secretly include the out-of-scope fix in the PR. Scope drift makes review hard and breaks the contract with the reviewer about what's in this PR.

## Related guidance

- [`docs/review-playbook.md`](review-playbook.md) — how to *launch* a review.
- [`AGENTS.md`](../AGENTS.md) — the broader agent guardrails (commit protocol, planning surface).
- [`.codex/skills/cross-vendor-review/SKILL.md`](../.codex/skills/cross-vendor-review/SKILL.md) — how to run a non-current-model checkpoint review.
- [`.planning/decisions/ADR-005-cross-model-checkpoint-mandatory-for-pass-claims.md`](../.planning/decisions/ADR-005-cross-model-checkpoint-mandatory-for-pass-claims.md) — what makes a pass-claim review load-bearing.
