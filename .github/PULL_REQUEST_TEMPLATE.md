<!--
PR template for codebase-mapper. Sections below are read by AI reviewers
(notably @claude opus, which uses the Focus section for targeting per
agentic-ops review.yml). Keep Summary tight; spend space in Focus.
-->

## Summary

<!-- 1-3 bullets on what changed and why. The "why" matters more than the "what" — the diff shows what. -->

## Focus

<!--
Optional but recommended. Naming specific files, functions, or invariants
here directs @claude opus to those surfaces (per agentic-ops review.yml
mode prompt). Skip this section if there's nothing specific to scrutinize.

Example:
- cbm/cli.py:5640 — checkpoint_pass_claim_issues, verifying scope match
- cbm/loop_status_config.json — new _documentation field shape
- ADR-005 invariant: pass-claim must require cross-model reviewer
-->

## Test plan

<!-- Bulleted checklist. Reviewers read this without running it; specificity helps. -->

- [ ] `TMPDIR=/var/tmp pytest -q` passes.
- [ ] `python3 -m cbm.cli loop-status --scope pass-claim --work-category runtime-producer --json` returns `status: ok`.
- [ ] `git diff --check` is clean.

## Boundary

<!-- What this PR does NOT claim. Especially important for horizon-adjacent work. -->

- Does not claim Phase B+ / repeatability / beta readiness.
- Does not advance the current horizon stage unless explicitly stated.

## Review hints

<!--
Pick a mode + effort if you have a strong preference. Default is for
the reviewer to pick. See docs/review-playbook.md.

Suggested for this PR: @claude <mode> at effort_level <level>
-->
