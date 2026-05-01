# CBM Build State

Status: current operational state
Last updated: 2026-05-01
Supersedes: none
Superseded by: none

## Summary

CBM currently has a real deterministic kernel and a substantial artifact-validation surface. It does not yet have the runtime agent layer required by `VISION.md`.

Current product state:

- deterministic baseline extraction exists;
- artifact schemas and validation gates exist;
- citation, freshness, ledger, registry, contestation, reuse, and refresh scaffolding exist;
- deterministic smoke artifacts exist under `.research/`;
- runtime Surface Mapper/Skeptic/Synthesizer/Planner orchestration does not exist;
- current deterministic artifacts must not be treated as proof of nuanced codebase understanding.

## Authority

- `VISION.md`: destination and maturity target; committed in `e309eaa`; surgically amended during the recovery intervention.
- `RUNTIME-CONSTITUTION.md`: runtime-agent discipline; committed in `e309eaa`.
- `.planning/STATE.md`: factual current state.
- `.planning/CURRENT-PLAN.md`: active recovery plan and allowed next work.
- `BUILD-LOG.md`: chronological audit evidence, not a live plan.
- `docs/roadmap.md`: original phase taxonomy and acceptance context; not current pass/fail status.

## Phase Status

Phase A is partially implemented as a deterministic foundation.

Phases B-F are not passed. Some deterministic substitutes and later-phase scaffolding exist, but the roadmap acceptance criteria name agentic deliverables and benchmark behavior that have not yet been demonstrated.

Important examples:

- deterministic `cbm run` is not an agent orchestrator;
- deterministic trace/refine/skeptic artifacts are not runtime agent output;
- project-type packs exist as scaffolding, not mature Phase E evidence;
- Claude Code portability is not verified;
- no external benchmark run proves mapping adequacy.

## Recent Checkpoints

- `e309eaa` `docs: commit CBM authority documents`
- `3ce5ae7` `docs: add external review comparison artifacts`
- `5742c18` `docs: add independent strategy audit outputs`
- `a086749` `docs: replace biased review with neutral audit plan`
- `5a2ceb5` `docs: add live planning and review surface`
- `692e9ef` `docs: preserve pre-reset reuse refresh work`
- `f98605d` `docs: install recovery governance gate`
- `5d47a7a` `feat: add recovery loop status preflight`
- `ebf43d7` `feat: label deterministic artifacts honestly`
- `5368a33` `feat: add run producer manifest`
- `20af433` `docs: record codex cli isolation spike`
- `9f618b2` `test: add external deterministic benchmark baseline`

## Active Architecture Decision

Accepted default for recovery:

CBM should own the run lifecycle through a producer registry. A producer entry chooses whether an artifact is produced by the deterministic baseline, an external host-agent handoff, or a CLI-launched agent backend. Parent-side CBM validation remains mandatory after each produced artifact.

Codex CLI subprocesses are a candidate backend, not an assumption. The local CLI capability spike shows useful isolation controls exist, but the Skeptic role may use Codex subprocesses only after a live smoke proves model-visible isolation and output-schema behavior.

Hooks remain optional adapter glue. They are not the deployment model and not the correctness mechanism.

## Benchmark State

The tiny fixture in `tests/fixtures/sample_repo/` is useful for tests only.

Default benchmark candidate:

- `https://github.com/modelcontextprotocol/servers`
- SHA `4503e2d12b799448cd05f789dd40f9643a8d1a6c`
- first target subtree to evaluate: `src/git`, if workable.

No Phase B+ pass claim is allowed until a real agent-produced artifact passes existing gates on a pinned external benchmark.

First deterministic external baseline:

- Target: MCP servers `src/git` at `4503e2d12b799448cd05f789dd40f9643a8d1a6c`.
- Result artifact: `.planning/benchmarks/2026-05-01-mcp-git-baseline/RESULT.md`.
- Status: deterministic baseline passed validation, but benchmark scope was polluted by copied CBM schemas because schema loading currently expects `<target-repo>/schemas`.

## Known Risks

- Deterministic artifact provenance was misleading; the recovery slice now labels deterministic baseline and dev-fixture producers explicitly.
- Direct-examination coverage was overreported in deterministic surface, verification, and trace paths; the recovery slice now reports zero direct examination for those baseline artifacts.
- `cbm/cli.py` remains a large monolith; splitting should follow producer-registry work, not precede it as churn.
- Planning docs can become process theater if they are not tied to checkpoint review and concrete verification.

## `/goal` Readiness

Recovery implementation is complete enough for checkpoint review. Broad unattended `/goal` is not yet restored because `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/CHECKPOINT.md` still says `Satisfies resume gate: no`.

The only known readiness blocker is checkpoint disposition plus final broad `cbm-loop-status` success. If the checkpoint accepts the recovery state, the next `/goal` track is the first real agent-produced benchmark artifact, not additional deterministic hardening.

## Verification Status

Last known full suite after the false-provenance recovery slice: `pytest -q` reported `53 passed, 2 warnings`.

Last known full suite after the producer-registry/run-manifest slice: `pytest -q` reported `55 passed, 2 warnings`.

Last known full suite after the benchmark/ledger fix slice: `pytest -q` reported `56 passed, 2 warnings`.

This verifies the test suite, not `VISION.md` maturity.

Required next verification:

- planning reset: `git diff --check -- .planning AGENTS.md VISION.md docs/architecture.md docs/roadmap.md BUILD-LOG.md`;
- provenance/coverage slice: focused regressions passed; full `pytest -q` passed;
- producer-registry/run-manifest slice: focused regressions passed; full `pytest -q` passed;
- Codex isolation spike: local CLI help/version evidence recorded; no live model subprocess was run;
- benchmark baseline: deterministic MCP `src/git` run passed handoff and run-manifest validation; scope pollution by copied schemas recorded as a harness gap;
- benchmark/ledger fix slice: focused regressions passed; full `pytest -q` passed;
- benchmark slice: generated artifacts must validate and show honest producer identity and coverage.
