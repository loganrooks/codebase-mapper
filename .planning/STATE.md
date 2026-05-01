# CBM Build State

Status: current operational state
Last updated: 2026-05-01
Supersedes: none
Superseded by: none

## Summary

CBM is no longer in a clean Phase A-only state. The implementation has a working deterministic kernel and has opportunistically implemented many Phase B-E style kernel features, but it does not yet have the runtime agent layer that `VISION.md` requires for nuanced codebase understanding.

The current product should be described as:

- deterministic baseline extraction;
- artifact schemas and validation gates;
- citation, freshness, ledger, registry, contestation, coverage, reuse, and refresh scaffolding;
- preliminary smoke artifacts in `.research/`;
- no production-grade agentic Surface Mapper/Skeptic/Synthesizer/Planner orchestration yet.

## Document Authority

- `VISION.md`: still authoritative for destination and maturity criteria.
- `RUNTIME-CONSTITUTION.md`: authoritative for runtime CBM agent discipline once real runtime agents exist.
- `.planning/STATE.md`: authoritative for current factual status.
- `.planning/CURRENT-PLAN.md`: authoritative for next work and open decisions.
- `BUILD-LOG.md`: chronological audit evidence, not a live plan.
- `docs/roadmap.md`: baseline seed roadmap and phase taxonomy. Partially superseded by implementation reality; do not use as current status without checking this file.
- `docs/architecture.md` and `docs/contracts.md`: design/contract references, but may need updates after the architecture correction around hooks and agent orchestration.

## Roadmap Status

`docs/roadmap.md` is partially outdated:

- Phase A core CLI/artifact foundation exists and has been repeatedly smoke-tested.
- Several items that roadmap listed as deferred are now implemented as deterministic kernel features, including `cbm-bind`, `cbm-stale`, `cbm-run-gate`, reuse/refresh commands, `cbm-consult`, corpus status, project-type packs, and deterministic trace/refinement/approval artifacts.
- Some later-phase labels are only partially satisfied. For example, `trace-workflows` exists as deterministic projection, but a true Tracer subagent does not.
- Platform portability docs exist, but a verified Claude Code port does not.
- The runtime agent orchestration layer remains the major architectural gap.

Current phase label: mixed kernel build beyond Phase A, pre-runtime-agent architecture correction.

## Implementation State

Committed recent checkpoints include:

- `504fbba` `feat: verify claim evidence and registry health`
- `f08722e` `feat: validate registry in evidence gates`
- `b480b0b` `feat: reject duplicate pack annotations`
- `108ab3a` `feat: reject duplicate extractor ids`
- `7963479` `feat: fail handoff on listed schema errors`

Current known dirty/untracked files are broad kit/doc/schema/skill updates that predate this planning reset. Treat them as intentional working-tree context unless reviewed otherwise.

## Artifact State

Preliminary CBM artifacts exist under `.research/`, mostly smoke runs against this repo. They are useful to inspect artifact shape and gate behavior, not evidence that CBM can yet produce nuanced understanding of arbitrary unfamiliar codebases.

Known sample fixture:

- `tests/fixtures/sample_repo/pyproject.toml`
- `tests/fixtures/sample_repo/src/app.py`
- `tests/fixtures/sample_repo/tests/test_app.py`

This fixture is intentionally tiny. A pinned small real-world test repo, preferably an MCP server, is still needed for meaningful mapping evaluation.

## Verification Status

Last known full suite result before this planning reset:

- `pytest -q`: `51 passed, 2 warnings`
- Warnings: existing `jsonschema.RefResolver` deprecation warnings.

This verifies the current automated test suite, not the full `VISION.md` maturity criteria.

Expected verification checks for future substantive work:

- focused regression test for the changed behavior;
- full `pytest -q` before commit when code changes;
- schema/citation/gate smoke checks for generated artifacts when artifact contracts change;
- update `BUILD-LOG.md` and `.planning/STATE.md` or `.planning/CURRENT-PLAN.md` when status or plan changes;
- for architecture/planning changes, run at least `git diff --check` and create/update review artifacts.

## Current Architectural Correction

The current live Codex hooks are dogfooding/platform adapter glue. They should not be treated as the core CBM deployment or correctness mechanism.

Corrected direction:

- `cbm run` should own run setup, output location, producer execution, and explicit validation.
- Deterministic commands produce baseline artifacts.
- Real nuanced understanding requires runtime agent producers.
- A likely runtime backend is launching Codex CLI subprocesses, for example `codex exec`, with CBM-specific prompts/config/output contracts.
- Parent-side CBM validation remains the source of truth after every produced artifact.
- Hooks may still be useful inside CBM-launched Codex agent sessions, but not as ambient user/global hooks.

## Open Decisions

- Output directory policy for target repositories: default `.research/<run_id>/` under `--repo`, with an optional explicit output root?
- Runtime backend shape: Codex CLI subprocesses first, Claude Code subprocesses later, or a backend abstraction from the start?
- Whether CBM should generate temporary per-agent Codex config/profile files for launched agents.
- Whether the current `.codex/hooks.json` should remain live in this implementation repo or move to template-only dogfood opt-in.
- How to represent true agent-produced direct examination coverage versus deterministic extractor-only coverage.
- Which small real-world repository should become the first meaningful mapping benchmark.

## Next Review

Prepare and run a cross-vendor architecture audit under `.planning/reviews/2026-05-01-opus-architecture-audit/`.

The auditor should review:

- whether the hook work was overbuilt or misplaced;
- whether the deterministic kernel work is still useful;
- whether the corrected Codex CLI backend plan is coherent;
- whether roadmap/plan/state tracking is adequate;
- what should be changed before further implementation.
