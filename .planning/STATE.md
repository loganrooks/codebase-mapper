# CBM Build State

Status: current operational state
Last updated: 2026-05-02
Supersedes: none
Superseded by: none

## Summary

CBM currently has a real deterministic kernel and a substantial artifact-validation surface. It does not yet have the runtime agent layer required by `VISION.md`.

Current product state:

- deterministic baseline extraction exists;
- artifact schemas and validation gates exist;
- citation, freshness, ledger, registry, contestation, reuse, and refresh scaffolding exist;
- deterministic smoke artifacts exist under `.research/`;
- a guarded `codex-cli` smoke backend exists and can be tested with a fake executable;
- the `codex-cli` smoke backend defaults to `gpt-5.4-mini` with medium reasoning for harness tests;
- the first live Codex CLI smoke artifact has passed on the pinned MCP `src/git` benchmark;
- `cbm-loop-status` now checks review-session completion for broad `/goal`;
- `cbm run` rejects unsafe run IDs before constructing `.research/<run_id>` paths;
- Codex CLI subprocess calls now have a configurable timeout and interrupted manifest status;
- a live Codex CLI isolation probe reported no access to parent-only session context under current backend flags;
- CBM schemas are packaged under `cbm/schemas/` so installed validation does not depend on a repo checkout or target-local schema copies;
- runtime Surface Mapper/Skeptic/Synthesizer/Planner orchestration does not exist;
- no full runtime Surface Mapper or full isolated Skeptic pass has been run through CBM yet;
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
- `bd66d14` `feat: harden goal readiness after audit`
- pending next evidence slice: skill-loaded real Skeptic artifact

## Active Architecture Decision

Accepted default for recovery:

CBM should own the run lifecycle through a producer registry. A producer entry chooses whether an artifact is produced by the deterministic baseline, an external host-agent handoff, or a CLI-launched agent backend. Parent-side CBM validation remains mandatory after each produced artifact.

Codex CLI subprocesses are now a proven smoke backend for one bounded artifact. The local CLI capability spike showed useful isolation controls, the live MCP `src/git` smoke proved cheap-model selection, output-schema use, read-only subprocess dispatch, manifest recording, parent-side validation, and ledger integration, and the live isolation probe reported no access to parent-only session context. This does not yet prove full Skeptic quality or Surface Mapper adequacy.

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
- Status: deterministic baseline passed validation, but benchmark scope was polluted by copied CBM schemas at the time because schema loading expected `<target-repo>/schemas`. The harness gap is now fixed for future runs: validation can use CBM's own schema source without copying schemas into the target checkout.

First live runtime-producer smoke:

- Target: MCP servers `src/git` at `4503e2d12b799448cd05f789dd40f9643a8d1a6c`.
- Result artifact: `.planning/benchmarks/2026-05-02-mcp-git-codex-smoke/RESULT.md`.
- Status: live Codex CLI smoke review passed validation and handoff gates with honest producer identity. This is runtime-producer dispatch evidence for one bounded smoke artifact.

Minimum-useful CBM status:

- Not met.
- Required next: a skill-loaded runtime agent artifact on a pinned external benchmark with at least one non-trivial interpretive claim or challenge grounded in citations.

## Known Risks

- Deterministic artifact provenance was misleading; the recovery slice now labels deterministic baseline and dev-fixture producers explicitly.
- Direct-examination coverage was overreported in deterministic surface, verification, and trace paths; the recovery slice now reports zero direct examination for those baseline artifacts.
- `cbm/cli.py` remains a large monolith; splitting should follow producer-registry work, not precede it as churn.
- Planning docs can become process theater if they are not tied to checkpoint review and concrete verification.
- Review packets can become orphaned artifacts if prompt/output/disposition completion is not mechanically gated; the current `loop-status` slice addresses this for broad `/goal`.

## `/goal` Readiness

Recovery readiness is restored for the next narrow runtime-producer evidence track. The checkpoint gate is accepted, cross-vendor audit blockers have been dispositioned, and final `cbm-loop-status` passed.

Broad unattended `/goal` is restored only for the next narrow runtime-producer evidence track: the first real agent-produced benchmark artifact. It is not restored for Phase B+ pass claims, unrelated kernel hardening, or treating deterministic baseline artifacts as runtime-agent output.

## Verification Status

Last known full suite after the false-provenance recovery slice: `pytest -q` reported `53 passed, 2 warnings`.

Last known full suite after the producer-registry/run-manifest slice: `pytest -q` reported `55 passed, 2 warnings`.

Last known full suite after the benchmark/ledger fix slice: `pytest -q` reported `56 passed, 2 warnings`.

Last known full suite after the guarded Codex CLI backend slice: `pytest -q` reported `58 passed, 2 warnings`.

Last known full suite after the schema-source benchmark-harness slice: `pytest -q` reported `59 passed, 2 warnings`.

Last known full suite after the Codex CLI smoke model-control slice: `pytest -q` reported `59 passed, 2 warnings`.

Last known full suite after the schema packaging slice: `pytest -q` reported `60 passed, 2 warnings`.

Last known packaging verification: `python3 -m pip wheel . --no-deps -w /tmp/cbm-wheel-check` built `cbm-0.1.0-py3-none-any.whl`; wheel inspection found 19 `cbm/schemas/*.schema.json` entries and no unintended top-level packages beyond `cbm` and dist-info. Installed-package smoke also passed from `/tmp` with `PYTHONPATH` pointing only at the wheel target; import came from `/tmp/.../pkg/cbm/cli.py`, `cbm run` completed, and `cbm validate handoff.md` passed without target-local schemas.

Last known live benchmark smoke: `python3 -m cbm.cli run --repo /tmp/cbm-live-mcp-servers-4503e2d/src/git --goal "understand MCP git server surfaces" --backend codex-cli --allow-live-codex --codex-model gpt-5.4-mini --codex-reasoning-effort medium --mode lightweight --run-id run-mcp-git-codex-smoke-4` exited 0.

Last known full suite after the live Codex CLI smoke remediation slice: `pytest -q` reported `61 passed, 2 warnings`.

Last known focused suite after the cross-vendor audit readiness blockers: `pytest -q tests/test_cli.py::test_loop_status_blocks_incomplete_review_sessions_for_broad_goal tests/test_cli.py::test_run_rejects_unsafe_run_id_before_writing_outside_research tests/test_cli.py::test_run_backend_codex_cli_timeout_marks_manifest_interrupted tests/test_cli.py::test_run_backend_codex_cli_fake_producer_writes_agent_review tests/test_cli.py::test_package_schema_resources_match_root_schemas` reported `5 passed, 2 warnings`.

Last known full suite after the cross-vendor audit readiness blockers: `pytest -q` reported `64 passed, 2 warnings`.

Last known broad-goal preflight after committing readiness blockers: `python3 -m cbm.cli loop-status --repo . --scope broad-goal --work-category loop-status --json` reported `status: ok`, no issues, and no warnings.

Last known live isolation probe: `codex exec -m gpt-5.4-mini -c model_reasoning_effort="medium" -c approval_policy="never" --ephemeral --ignore-user-config --ignore-rules -C . -s read-only --json -o .planning/spikes/2026-05-02-codex-isolation-live/output.json --output-schema .planning/spikes/2026-05-02-codex-isolation-live/output.schema.json - < .planning/spikes/2026-05-02-codex-isolation-live/prompt.txt` exited 0; output schema validation passed; result artifact is `.planning/spikes/2026-05-02-codex-isolation-live/RESULT.md`.

This verifies the test suite, not `VISION.md` maturity.

Required next verification:

- planning reset: `git diff --check -- .planning AGENTS.md VISION.md docs/architecture.md docs/roadmap.md BUILD-LOG.md`;
- provenance/coverage slice: focused regressions passed; full `pytest -q` passed;
- producer-registry/run-manifest slice: focused regressions passed; full `pytest -q` passed;
- Codex isolation spike: local CLI help/version evidence recorded; no live model subprocess was run;
- benchmark baseline: deterministic MCP `src/git` run passed handoff and run-manifest validation; scope pollution by copied schemas recorded as a harness gap;
- benchmark/ledger fix slice: focused regressions passed; full `pytest -q` passed;
- guarded Codex CLI backend slice: fake executable regressions passed; full `pytest -q` passed;
- schema-source benchmark-harness slice: focused no-pollution regression passed; full `pytest -q` passed;
- Codex CLI smoke model-control slice: focused fake-executable regression passed; full `pytest -q` passed;
- schema packaging slice: package resource regression passed; wheel build/inspection passed; full `pytest -q` passed;
- live Codex CLI smoke slice: focused regressions passed; MCP `src/git` live smoke passed; full `pytest -q` passed;
- benchmark slice: generated artifacts must validate and show honest producer identity and coverage.
