# Claude review playbook

How to pick a mode and effort level for CBM PRs. Backs the central
agentic-ops mode taxonomy ([ADR-001](https://github.com/loganrooks/agentic-ops/blob/main/docs/adr/ADR-001-mode-taxonomy.md))
and effort dial ([ADR-010](https://github.com/loganrooks/agentic-ops/blob/main/docs/adr/ADR-010-effort-level-input.md))
with CBM-specific guidance learned from PR #1.

## Modes vs. effort

Two orthogonal axes:

- **Mode** picks the prompt SHAPE (diff-focused vs spatial vs whole-repo).
- **Effort** picks the depth of attention (default / high / max).

Pick mode first by PR shape; pick effort second by stakes.

## Mode selection

| PR shape | Mode | Why |
|---|---|---|
| Routine (<10 files, no gate logic) | `quick` | Fast AI-failure-mode scan; cheap. |
| Standard (<60 files) | `review` | Default. Weighted by `review_focus_paths`. |
| Large (>60 files, mixed concerns) | `survey` | Spatial decomposition. Zone map then per-zone reads. |
| Touches gate logic / contract code | `gates` | Narrow surface, deep look at gate scripts + cli.py + loop_status_config + skill_loader/skills. |
| Specific file you suspect | `opus <file>` | ≤3 files, Opus model, designed for "I think there's something subtle here." |
| Deep dive on full diff | `deep` | Uncapped read. Expensive on large PRs. |
| Repo-level question, no PR | `audit:<lens>` | Reads repo against a built-in or free-form lens. |

## Effort selection

| Stakes | Effort | Cost vs default |
|---|---|---|
| Routine, low-stakes | `default` | 1x |
| Pre-merge sanity on substantive change | `high` | ~2-3x (Opus for non-quick modes; ~1.5x budgets) |
| Horizon closeout, post-incident audit, "spend the budget" | `max` | ~4-6x (Opus everywhere; no per-mode file cap) |

## CBM-specific guidance

### Gate-correctness PRs (touch `cli.py`, `loop_status_config.json`, gate scripts)

Recommended sequence:
1. `@claude gates` at `high` or `max` — narrow surface, designed for vocabulary drift and missing-check bugs.
2. `@claude opus cbm/cli.py` at `high` — deep reasoning on the specific gate file.
3. Skip `survey` unless the PR is also large by file count.

PR #1 lesson: a single missing scope-match check in
`checkpoint_pass_claim_issues` was invisible to `survey` (the model
read cli.py at zone-map-budget attention) but would have been caught
by `gates` or `opus`. For gate logic, narrower modes beat broader
modes regardless of PR size.

### Horizon closeout PRs (large diffs, many concerns)

Recommended sequence:
1. `@claude survey` at `max` — get the breadth/architecture picture.
2. `@claude gates` at `max` — verify the gate surface specifically.
3. `@claude opus <load-bearing-file>` at `high` for each file that the
   survey or gates pass surfaced concerns on.
4. After fixes, repeat 1-3 (incremental — CodeRabbit / Codex are
   incremental reviewers).

### Pre-H2 PRs and other "feature work" PRs

Default cadence:
1. `@coderabbitai review` (auto-fires on PR open).
2. `@codex review` (auto-fires; manual re-trigger after fixes).
3. `@claude review` at `default` if the PR is in scope for its budget;
   else `@claude survey` at `high`.

### Audit-only inquiries (no PR)

Common lenses:
- `@claude audit:discipline` — AGENTS.md / ADR commitments vs reality.
- `@claude audit:tech-debt` — refactor candidates.
- `@claude audit:forward-compat` — readiness for the next horizon.
- `@claude audit:agential-dx` — workspace organization for AI contributors.

Free-form is allowed: `@claude audit do we have hidden coupling between the gate code and the producer registry?`

## Knobs in `.github/workflows/claude-review.yml`

The caller stub passes these to the central workflow:

| Input | Purpose |
|---|---|
| `enabled_modes` | Which modes are allowed for this repo. CBM enables all seven. |
| `effort_level` | Global effort dial (default \| high \| max). |
| `timeout_minutes` | Per-job timeout. Bump alongside effort. |
| `review_focus_paths` | Priority paths in `review` mode. |
| `gates_paths` | The ONLY paths reviewed in `gates` mode. |
| `extra_allowed_tools` | Static-analysis tools (ruff, mypy, rg). |
| `agents_md_path` | Where to read AGENTS.md from. |
| `repo_label` | Human-friendly repo name in the prompt header. |

## Experimentation discipline

Changes to the caller stub or the central workflow ref MUST be
committed and pushed. Track each experiment with a descriptive commit
message naming what you're testing.

If pinning to a non-`@v1` ref (e.g., a feature branch SHA), record:
- the branch / PR number on agentic-ops
- the rationale for the temporary pin
- the criterion for reverting to `@v1`

Place this in a comment block near the `uses:` line. See the current
caller stub for the template.

## Cost awareness

`max` on a 354-file PR is expensive. The workflow timeout caps it at
`timeout_minutes` (default 45, raised to 90 in the CBM stub for max
runs), but the API cost scales with files read × Opus rate.

Rule of thumb: use `max` for one final pass before a high-stakes merge,
not for routine reviews. Use `high` as the working default for
substantive PRs.

## Adding a new mode or effort variant

Modes and effort levels live in agentic-ops, not CBM. Adding either
requires:
1. ADR on agentic-ops (mode → addendum to ADR-001; effort tier →
   addendum to ADR-010).
2. Workflow change in agentic-ops/v1 (additive per ADR-003).
3. Optional opt-in via `enabled_modes` or `effort_level` in the
   caller stub.

Do not fork the central workflow into CBM. The substrate model exists
specifically to avoid that.
