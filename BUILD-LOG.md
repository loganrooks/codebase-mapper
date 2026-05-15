# BUILD LOG

## 2026-05-01 — Phase A implementation slice

- Decision: Treat the active `VISION.md` goal as the repo-defined instruction to build CBM from the seed kit, starting with `docs/roadmap.md` Phase A.
- Scope: Add a conservative Python CLI foundation for `cbm-init`, `cbm-map`, `cbm-validate`, `cbm-verify-citations`, and `cbm-handoff`, plus tests. This slice does not implement runtime subagent orchestration or qualitative Surface Mapper/Skeptic behavior.
- Rationale: The roadmap's first acceptance gate depends on deterministic schema validation and citation resolution. Those mechanical gates can be implemented without changing the kit's contracts.
- Alternative considered: Start by rewriting schemas or narrowing v1.2 docs back to the MVP's six-schema wording. Rejected because schema changes are contract-bearing and the current v1.2 kit already defines the authoritative artifact surface.
- Reversibility: Additive implementation files under `cbm/`, `tests/`, and packaging metadata. Existing kit documents remain unchanged in this slice.
- Verification plan: Run unit tests against a temporary git fixture; validate the shipped example frontmatter; run the CLI through init/map/handoff on the fixture and verify citations resolve.

## 2026-05-01 — Phase A smoke verification

- Implemented: Python package `cbm` with commands `cbm init`, `cbm map`, `cbm validate`, `cbm verify-citations`, and `cbm handoff`; console-script aliases are declared for the contract command names in `pyproject.toml`.
- Implemented: `cbm-init` writes `intake.json`, `state.json`, `extractor-registry.json`, `evidence-ledger.jsonl`, and `uncertainty-register.jsonl` under `.research/<run_id>/`.
- Implemented: `cbm-map` emits a schema-validated deterministic `codebase-map.json` with file inventory, language counts, build/test/CI/config candidates, coverage, and staleness metadata.
- Implemented: `cbm-handoff` emits a draft findings card and handoff from deterministic evidence, writes ledger and uncertainty entries, and reports the missing qualitative Skeptic review honestly.
- Verification run:
  - `pytest -q` passed: 2 tests.
  - `python3 -m cbm validate examples/intervention-card-example.md --repo .` passed.
  - Smoke run `run-phase-a-smoke-2`: `init`, `map`, and `handoff` completed.
  - `python3 -m cbm validate .research/run-phase-a-smoke-2/codebase-map.json --repo .` passed.
  - `python3 -m cbm validate .research/run-phase-a-smoke-2/findings/int-0001.md --repo .` passed.
  - `python3 -m cbm verify-citations .research/run-phase-a-smoke-2/findings/int-0001.md --repo .` resolved `AGENTS.md:1@59cecd752ff2`.
  - `python3 -m cbm validate .research/run-phase-a-smoke-2/handoff.md --repo .` passed.
- Self-critique:
  - Drift check: This slice stays inside the deterministic kernel and does not make CBM a code generator or chat surface.
  - Contract check: Generated codebase map, findings card, and handoff validate against current schemas; citation resolution works on the generated card.
  - Reviewer-eye check: The generated findings card is intentionally low-confidence and structural. It is not a substitute for Surface Mapper/Skeptic output; the handoff caveat names this boundary.
- Remaining Phase A gaps: runtime Surface Mapper production of `surface-map.json`; Skeptic weak-claim review; orchestrator flow that produces an actually goal-specific actionable card rather than the current structural proof card.

## 2026-05-01 — Draft surface map and lightweight Skeptic pass

- Decision: Add `cbm-surface` as an implementation helper for the Phase A Surface Mapper artifact. This is a CLI affordance around the MVP surface artifact, not a new runtime role.
- Implemented: `cbm-surface` produces schema-valid `surface-map.json` from `codebase-map.json`, classifying build/config/test/CI/doc surfaces as draft authorities and preserving an explicit `edge-unknown-001` dependency edge.
- Implemented: `cbm-handoff` now consumes `surface-map.json`, writes a lightweight `skeptic-review/surface-map.md`, appends a `skeptic_challenge` ledger entry, and marks the unknown dependency edge `claim_status: challenged` with challenge `chl-00001`.
- Implemented: findings card now propagates `chl-00001` through `dependent_challenges`; confidence stays low because dependency closure is unresolved.
- Verification run:
  - `pytest -q` passed: 2 tests.
  - Smoke run `run-phase-a-smoke-3`: `init`, `map`, `surface`, and `handoff` completed.
  - `python3 -m cbm validate .research/run-phase-a-smoke-3/codebase-map.json --repo .` passed.
  - `python3 -m cbm validate .research/run-phase-a-smoke-3/surface-map.json --repo .` passed.
  - `python3 -m cbm validate .research/run-phase-a-smoke-3/findings/int-0001.md --repo .` passed.
  - `python3 -m cbm verify-citations .research/run-phase-a-smoke-3/findings/int-0001.md --repo .` resolved `pyproject.toml:1@5d4e353512e4`.
  - `python3 -m cbm validate .research/run-phase-a-smoke-3/handoff.md --repo .` passed.
- Self-critique:
  - Drift check: The Skeptic pass critiques artifact weakness rather than pretending the deterministic kernel has done a human-grade reading.
  - Contract check: The surface map carries a real challenged claim and the card propagates that contestation.
  - Reviewer-eye check: The strongest objection is that `cbm-surface` is too mechanical to be a true Surface Mapper. Accepted; this is a Phase A bootstrap artifact, and the handoff says the next step is language-level extraction before promotion.
- Remaining Phase A gaps: import/call extraction, evidence-ledger cross-checking beyond entries written by `cbm-handoff`, and an orchestrated run command that completes the whole MVP path in one invocation.

## 2026-05-01 — Python static import extraction

- Implemented: `ext-python-imports-v1` registry entry with explicit blind spots for relative imports, dynamic imports, `importlib`, and `sys.path` mutation.
- Implemented: Python AST import extraction in `cbm-surface`; resolved local absolute imports become `kind: import` edges with `evidence_kinds: [static_relation]`, `claim_register: factual`, and source-line citations.
- Implemented: citation generation now refuses to cite modified or untracked working-tree bytes as if they were present at the recorded `source_sha`; citation verification resolves against the cited SHA rather than current dirty worktree length.
- Verification run:
  - `pytest -q` passed: 2 tests, including a temp git fixture with `tests/test_app.py -> src/app.py` import edge emitted by `ext-python-imports-v1`.
  - Smoke run `run-phase-a-smoke-5`: `init`, `map`, `surface`, and `handoff` completed on this dirty repo.
  - `python3 -m cbm validate .research/run-phase-a-smoke-5/surface-map.json --repo .` passed.
  - `python3 -m cbm verify-citations .research/run-phase-a-smoke-5/surface-map.json --repo .` resolved `pyproject.toml:1@9fe5e15c3bf2`.
  - `python3 -m cbm validate .research/run-phase-a-smoke-5/handoff.md --repo .` passed.
- Self-critique:
  - Drift check: Import extraction strengthens the deterministic kernel without turning CBM into a code editor.
  - Contract check: Import edges cite source lines and use the extractor registry id; unknown dependency edge remains because calls/runtime/dynamic edges are still out of scope.
  - Reviewer-eye check: The current smoke run on this repo does not show import edges because the relevant Python files are modified after the recorded `source_sha`; this is correct behavior, not a miss. The clean temp fixture verifies the import extractor.
- Remaining Phase A gaps: call extraction or a clearer MVP boundary for deferring call extraction; ledger consistency checks that compare artifact citations against ledger entries; one-command orchestrator for `init -> map -> surface -> handoff`.

## 2026-05-01 — Orchestrator and ledger consistency

- Implemented: `cbm run` / `cbm-run` orchestrates the Phase A path: `init -> map -> surface -> handoff`.
- Implemented: `cbm-surface` appends `citation_introduced` ledger entries for citations in `surface-map.json`.
- Implemented: `cbm-handoff` checks surface/card citations against `evidence-ledger.jsonl` before reporting `ledger_consistency.append_only_verified: true`.
- Verification run:
  - `pytest -q` passed: 3 tests, including the one-command orchestrated path.
  - Smoke run `run-phase-a-smoke-6`: `python3 -m cbm run --repo . --goal "Phase A orchestrated smoke test" --run-id run-phase-a-smoke-6` completed.
  - `python3 -m cbm validate .research/run-phase-a-smoke-6/surface-map.json --repo .` passed.
  - `python3 -m cbm verify-citations .research/run-phase-a-smoke-6/surface-map.json --repo .` resolved `.gitignore:1@4613408baf86`.
  - `python3 -m cbm validate .research/run-phase-a-smoke-6/findings/int-0001.md --repo .` passed.
  - `python3 -m cbm verify-citations .research/run-phase-a-smoke-6/findings/int-0001.md --repo .` resolved `.gitignore:1@4613408baf86`.
  - `python3 -m cbm validate .research/run-phase-a-smoke-6/handoff.md --repo .` passed.
- Self-critique:
  - Drift check: Orchestration still produces artifacts on disk and does not become a chat workflow.
  - Contract check: Ledger consistency now checks that emitted surface/card citations are represented in the ledger, but it does not yet verify append-only history across prior file versions.
  - Reviewer-eye check: The dirty-repo smoke fell back to `.gitignore` because changed files are intentionally not citable at the recorded source SHA. This is conservative but not an ideal demonstration artifact; clean test fixtures cover the intended import-edge path.
- Remaining Phase A gaps: true append-only mutation detection for ledger files, hook configuration, and deciding whether the Phase A card is sufficiently "actionable" or should wait for a stronger generated findings card.

## 2026-05-01 — Codex Stop hook configuration

- Source checked: OpenAI Codex Hooks docs at `https://developers.openai.com/codex/hooks`. Relevant points: hooks require `features.codex_hooks = true`; repo-local `.codex/hooks.json` is a supported location for trusted projects; `Stop` hooks can return JSON with `continue`, `stopReason`, and `systemMessage`; command hooks run with the session working directory.
- Implemented: `.codex/config.toml` enables `codex_hooks`.
- Implemented: `.codex/hooks.json` registers a `Stop` command hook that runs `python3 -m cbm hook-stop` with `PYTHONPATH` resolved from the git root.
- Implemented: `cbm hook-stop` validates the latest `.research/<run_id>/handoff.md` when present. Missing or invalid handoff returns `continue: false`; a valid handoff returns `continue: true` with a status message.
- Verification run:
  - `pytest -q` passed: 4 tests, including direct hook-stop validation against an orchestrated temp run.
  - Manual smoke: `printf '{"cwd":"/Users/rookslog/Development/cbm"}' | python3 -m cbm hook-stop --repo .` returned `{"continue": true, "systemMessage": "CBM handoff gate passed for run-phase-a-smoke-6."}`.
- Self-critique:
  - Drift check: The hook enforces an artifact gate; it does not add conversational behavior.
  - Contract check: This covers the pre-handoff/stop boundary, not true post-artifact-write hooks for every artifact write.
  - Reviewer-eye check: Repo-local Codex hooks only load when the project `.codex/` layer is trusted. The implementation cannot force that; the limitation is documented here.
- Remaining Phase A gaps: stronger card actionability and append-only ledger mutation detection across historical revisions.

## 2026-05-01 — Import-edge-backed findings card

- Implemented: `cbm-handoff` now prefers a grounded `import` edge when producing the draft findings card. If present, the card's primary file role names the imported target and `related_dependencies.certain` points back to the surface-map edge.
- Fallback behavior: if no citable import edge exists at the recorded `source_sha`, the card falls back to the first citable authority as before.
- Verification run:
  - `pytest -q` passed: 4 tests. The clean temp fixture verifies that a generated card names `Imports src/app.py` and references `.research/<run_id>/surface-map.json#/edges/0`.
- Self-critique:
  - Drift check: The card remains research-only and recommends a reading slice, not source mutation.
  - Contract check: The card propagates the unknown-edge challenge and does not raise confidence above medium even when an import edge exists.
  - Reviewer-eye check: This is now meaningfully more actionable on codebases with local Python imports, but non-Python or dirty repos can still fall back to a weaker structural card.
- Remaining Phase A gap: append-only ledger mutation detection across historical revisions. Current ledger consistency checks presence of artifact citations, not whether previous ledger lines were edited.

## 2026-05-01 — Ledger append-only integrity manifest

- Implemented: `evidence-ledger.jsonl.integrity.json` sidecar manifest. It records the hash of every non-empty ledger line after each append.
- Implemented: every ledger append first verifies that existing ledger line hashes match the sidecar manifest; if a previous line has been edited or removed, the append fails.
- Implemented: `cbm-handoff` now includes append-only verification in `gate_summary.ledger_consistency.append_only_verified`, not just citation presence.
- Verification run:
  - `pytest -q` passed: 5 tests, including a tamper test that mutates an existing ledger line after `cbm-surface`; `cbm-handoff` fails as expected.
  - Smoke run `run-phase-a-smoke-7`: `python3 -m cbm run --repo . --goal "Phase A ledger integrity smoke test" --run-id run-phase-a-smoke-7` completed.
  - `python3 -m cbm validate .research/run-phase-a-smoke-7/surface-map.json --repo .` passed.
  - `python3 -m cbm verify-citations .research/run-phase-a-smoke-7/surface-map.json --repo .` resolved `.codex/config.toml:1@f558c51cd6b6`, `.codex/hooks.json:1@f558c51cd6b6`, and `pyproject.toml:1@f558c51cd6b6`.
  - `python3 -m cbm validate .research/run-phase-a-smoke-7/findings/int-0001.md --repo .` passed.
  - `python3 -m cbm verify-citations .research/run-phase-a-smoke-7/findings/int-0001.md --repo .` resolved `pyproject.toml:1@f558c51cd6b6`.
  - `python3 -m cbm validate .research/run-phase-a-smoke-7/handoff.md --repo .` passed.
- Self-critique:
  - Drift check: This strengthens the mechanical evidence gate and stays within CBM's artifact discipline.
  - Contract check: The sidecar is additive and does not alter the v1.2 evidence-ledger entry schema.
  - Reviewer-eye check: The sidecar detects edits after it exists; it cannot prove the original ledger was never wrong before the first manifest. `cbm-init` creates an empty manifest immediately, so normal runs are covered from the start.
- Remaining Phase A gap: phase completion audit against roadmap acceptance criteria.

## 2026-05-01 — Durable test repo with expected outputs

- Implemented: committed fixture repository under `tests/fixtures/sample_repo/` with `pyproject.toml`, `src/app.py`, and `tests/test_app.py`.
- Implemented: expected Phase A assertions in `tests/fixtures/expected_phase_a.json`, covering the Python import edge, unknown-edge challenge, and findings-card role/confidence/dependent challenge.
- Implemented: tests now copy the fixture repo into a temp git repository instead of synthesizing the repo entirely in test code.
- Verification run:
  - `pytest -q` passed: 5 tests.
- Self-critique:
  - Drift check: The expected outputs are structural assertions, not brittle timestamp/hash snapshots, so they remain focused on the CBM contract.
  - Contract check: The fixture exercises schema validation, citation resolution, ledger integrity, Skeptic challenge propagation, and card generation.
  - Reviewer-eye check: The expected output fixture is not a full golden `.research/` directory. That avoids unstable hashes/timestamps but gives less artifact-level diffing than a complete golden output bundle.

## 2026-05-01 — Phase A completion audit

Objective restated: build toward `VISION.md` by completing `docs/roadmap.md` Phase A MVP foundation, not the full mature CBM vision. Phase A success means the repository can run a Codex-first MVP path that creates schema-valid artifacts, resolves citations, catches at least one weak claim, produces at least one actionable research-only card, and preserves claim-register discipline.

Prompt-to-artifact checklist:

- Phase A item 1, CLI commands: `cbm-init`, `cbm-map`, `cbm-validate`, `cbm-verify-citations`, `cbm-handoff`, plus implementation helpers `cbm-surface`, `cbm-run`, and `cbm hook-stop` are declared in `pyproject.toml` and implemented in `cbm/cli.py`.
- Phase A item 2, JSON schemas: existing `schemas/*.json` validate generated `codebase-map.json`, `surface-map.json`, findings card frontmatter, and handoff frontmatter. The current kit is v1.2 and has more than the original MVP six schemas; implementation treats the existing schemas as authoritative rather than rewriting them.
- Phase A item 3, skill prompts: existing runtime skills remain in `skills/`. This implementation loads no prompts yet; the lightweight Surface Mapper/Skeptic behavior is deterministic scaffolding, not a true subagent prompt run.
- Phase A item 4, Codex hook configuration: `.codex/config.toml` enables hooks; `.codex/hooks.json` registers a Stop hook; `cbm hook-stop` validates the latest handoff.
- Phase A item 5, orchestrator script: `cbm run` executes `init -> map -> surface -> handoff`.
- Phase A item 6, test repo with expected outputs: `tests/fixtures/sample_repo/` and `tests/fixtures/expected_phase_a.json` define a durable fixture and expected structural outputs.
- MVP proof 1, citations resolve end-to-end: final audit run `run-phase-a-final-audit` resolved citations in `surface-map.json` and `findings/int-0001.md`.
- MVP proof 2, schema validation rejects malformed artifacts: `test_validate_rejects_malformed_codebase_map` covers rejection; final audit validated generated map, surface map, card, and handoff.
- MVP proof 3, Skeptic catches >=1 weak claim: generated handoff reports `skeptic_review.challenges_logged: 1`, and `surface-map.json` carries `edge-unknown-001` as `claim_status: challenged`.
- MVP proof 4, cards are actionable: generated findings card recommends a concrete next reading slice: read `tests/test_cli.py` and `cbm/cli.py` around the cited import and classify the relation. It remains low-confidence and research-only because the unknown dependency edge is unresolved.
- MVP proof 5, claim registers are correctly assigned: final audit surface map has factual `edge-import-001` active and inferential `edge-unknown-001` challenged. The unknown-edge challenge no longer attaches to the factual import edge.

Evidence inspected:

- `pytest -q` passed: 5 tests.
- `python3 -m cbm run --repo . --goal "Phase A final audit smoke" --run-id run-phase-a-final-audit` completed.
- `python3 -m cbm validate .research/run-phase-a-final-audit/codebase-map.json --repo .` passed.
- `python3 -m cbm validate .research/run-phase-a-final-audit/surface-map.json --repo .` passed.
- `python3 -m cbm verify-citations .research/run-phase-a-final-audit/surface-map.json --repo .` resolved all reported citations.
- `python3 -m cbm validate .research/run-phase-a-final-audit/findings/int-0001.md --repo .` passed.
- `python3 -m cbm verify-citations .research/run-phase-a-final-audit/findings/int-0001.md --repo .` resolved its reported citation.
- `python3 -m cbm validate .research/run-phase-a-final-audit/handoff.md --repo .` passed.
- Final audit artifact state: handoff lists `codebase_map`, `surface_map`, `findings_card`, and `skeptic_review`; gate summary reports schema validation passed, citation unresolved count 0, ledger append-only verified true, and one Skeptic challenge.

Phase A disposition: pass as MVP foundation. Limitations remain explicit: deterministic scaffolding is not a mature agentic Surface Mapper/Skeptic, direct file examination is still minimal, and the overall `VISION.md` objective is not complete. Proceed to Phase B.

## 2026-05-01 — Phase B slice: goal binding

- Decision: Start Phase B with `cbm-bind` and `goal-binding.json`, because goal binding is the narrowest standard-mode step that preserves the goal-agnostic baseline while enabling goal-specific card planning.
- Implemented: additive `schemas/goal-binding.schema.json`. This does not change existing artifact schemas.
- Implemented: `cbm-bind` / `cbm bind`, which reads `surface-map.json` and `intake.json`, ranks bindable authorities and import edges, and writes `goal-binding.json`.
- Implemented: `cbm run` now executes `init -> map -> surface -> bind -> handoff`.
- Verification run:
  - `pytest -q` passed: 5 tests.
  - Smoke run `run-phase-b-bind-smoke`: `python3 -m cbm run --repo . --goal "Phase B goal binding smoke" --run-id run-phase-b-bind-smoke` completed and produced `goal-binding.json`.
  - `python3 -m cbm validate .research/run-phase-b-bind-smoke/goal-binding.json --repo .` passed.
  - `python3 -m cbm verify-citations .research/run-phase-b-bind-smoke/goal-binding.json --repo .` resolved all reported citations.
- Self-critique:
  - Drift check: Goal binding enters only after surface mapping; `codebase-map.json` and `surface-map.json` remain goal-agnostic.
  - Contract check: Binding candidates carry surface refs, citations, claim registers, and claim statuses. The artifact is schema-validated.
  - Reviewer-eye check: `cbm-handoff` still generates its card directly from `surface-map.json`; it does not yet consume `goal-binding.json`. That is the next integration gap.

## 2026-05-01 — Goal binding consumed by handoff

- Implemented: `cbm-bind` now ranks grounded import edges before authority candidates, so research-only cards prefer concrete static relations when available.
- Implemented: `cbm-handoff` reads `goal-binding.json` when present, selects the first binding candidate, and includes goal binding in handoff inputs and artifact list.
- Verification run:
  - `pytest -q` passed: 5 tests. Tests assert the fixture goal binding ranks the import edge first and handoff includes `goal_binding`.
  - Smoke run `run-phase-b-bind-handoff-smoke`: `python3 -m cbm run --repo . --goal "Phase B binding handoff smoke" --run-id run-phase-b-bind-handoff-smoke` completed.
  - `python3 -m cbm validate .research/run-phase-b-bind-handoff-smoke/goal-binding.json --repo .` passed.
  - `python3 -m cbm validate .research/run-phase-b-bind-handoff-smoke/handoff.md --repo .` passed.
- Self-critique:
  - Drift check: Handoff now consumes the goal-specific artifact rather than making a silent local choice.
  - Contract check: Goal binding remains downstream of `surface-map.json`; upstream artifacts stay goal-agnostic.
  - Reviewer-eye check: The dirty-repo smoke selected a config authority because uncommitted Python files cannot be cited at the recorded SHA. The committed fixture test covers the import-edge path.

## 2026-05-01 — Phase B slice: stale artifact gate

- Implemented: `cbm-stale` / `cbm stale <artifact>`. It checks recorded `inputs[].sha256` and `staleness.depends_on_paths` against current disk state relative to `source_sha`.
- Verification run:
  - `pytest -q` passed: 6 tests, including a test that mutates a dependent source path after a run and gets exit code 2 from `cbm stale`.
  - Smoke run `run-phase-b-stale-smoke`: `python3 -m cbm run --repo . --goal "Phase B stale smoke" --run-id run-phase-b-stale-smoke` completed.
  - `python3 -m cbm stale .research/run-phase-b-stale-smoke/findings/int-0001.md --repo .` returned fresh with exit code 0.
- Self-critique:
  - Drift check: Staleness is a mechanical warning gate and does not alter source code or interpretive claims.
  - Contract check: This implements the basic `cbm-stale` contract. It is not yet the richer v1.2 `cbm-validate-fresh` or `cbm-verify` report flow.
  - Reviewer-eye check: The command checks file bytes against `source_sha`; it does not distinguish harmless whitespace from semantic changes.

## 2026-05-01 — Phase B slice: validate-fresh and verify

- Implemented: `cbm-validate-fresh` / `cbm validate-fresh <artifact>`, the v1.2 Mode 1 freshness check. It compares each cited file's bytes at the cited SHA with that file's bytes at current `HEAD` and exits 2 when any cited evidence has shifted.
- Implemented: `cbm-verify` / `cbm verify <artifact>`, the v1.2 Mode 2 check. It writes a `verify_report` JSON artifact and reports each citation as `still_grounded`, `needs_review`, or `broken`.
- Verification run:
  - `pytest -q` passed: 7 tests, including a freshness test that commits a changed cited file and then removes it, producing `needs_review` and `broken` statuses.
  - Smoke run `run-phase-b-freshness-smoke`: `python3 -m cbm run --repo . --goal "Phase B freshness smoke" --run-id run-phase-b-freshness-smoke` completed.
  - `python3 -m cbm validate-fresh .research/run-phase-b-freshness-smoke/findings/int-0001.md --repo .` reported the card citation fresh.
  - `python3 -m cbm verify .research/run-phase-b-freshness-smoke/findings/int-0001.md --repo . --output .research/run-phase-b-freshness-smoke/verify-report.json` produced a verify report with `still_grounded: 1`, `needs_review: 0`, `broken: 0`.
- Self-critique:
  - Drift check: These commands annotate freshness and do not rewrite interpretive artifacts.
  - Contract check: Mode 1 produces no artifact; Mode 2 writes a transient verify report and leaves the original artifact unchanged.
  - Reviewer-eye check: The verify report is schema-shaped but currently has no dedicated schema, because the kit names `verify_report` as transient without shipping a schema.

## 2026-05-01 — Phase B slice: corpus status

- Implemented: `cbm-corpus-status` / `cbm corpus-status`, which walks `.research/`, classifies artifacts as `fresh`, `stale`, `pinned`, or `broken`, and writes a machine-readable `corpus-status.json` manifest.
- Verification run:
  - `pytest -q` passed: 8 tests, including a corpus-status test that first reports fresh artifacts, then commits a cited-file change and reports stale-but-historically-valid artifacts.
  - Smoke run: `python3 -m cbm corpus-status --repo . --output .research/corpus-status-smoke.json` completed and wrote the manifest. Existing local smoke runs are a mix of fresh, stale, and pinned artifacts because the branch has advanced through multiple implementation commits.
- Self-critique:
  - Drift check: The command inventories artifact freshness without rewriting any run artifacts.
  - Contract check: It distinguishes current freshness from historical validity by retaining `historical_valid` per artifact.
  - Reviewer-eye check: This walks the current flattened `.research/<run_id>/` layout, not the recommended future `.research/runs/<run_id>/` layout. It uses recursive discovery, so it should tolerate either layout later.

## 2026-05-01 — Phase B slice: structural refresh

- Implemented: `cbm-refresh <codebase-map> --mode structural`. It re-runs the deterministic codebase-map kernel at current `HEAD`, writes a refreshed successor map under `refreshes/`, and emits a schema-valid refresh delta.
- Implemented: refreshed codebase maps include `refreshed_from` lineage pointing back to the prior artifact and the refresh delta.
- Implemented: structural refresh delta records carried-forward, updated, retracted, and newly-added file claims, plus downstream invalidation entries for surface map, goal binding, and handoff when present.
- Verification run:
  - `pytest -q` passed: 9 tests, including a structural refresh test that commits a new file and verifies the delta records `file:src/new_module.py` in `newly_added`.
  - Smoke run `run-phase-b-refresh-smoke`: `python3 -m cbm refresh .research/run-phase-b-refresh-smoke/codebase-map.json --repo . --mode structural` produced a successor codebase map and `refresh-delta-structural-913a55fbed6b.json`.
  - `python3 -m cbm validate .research/run-phase-b-refresh-smoke/refreshes/codebase-map-913a55fbed6b.json --repo .` passed.
  - `python3 -m cbm validate .research/run-phase-b-refresh-smoke/refreshes/refresh-delta-structural-913a55fbed6b.json --repo .` passed.
- Self-critique:
  - Drift check: Structural refresh updates deterministic baseline only and marks downstream interpretive artifacts for review instead of silently carrying them forward.
  - Contract check: Refresh delta uses the existing v1.2 schema and the successor map uses the existing optional `refreshed_from` block.
  - Reviewer-eye check: This writes successor artifacts under the same run's `refreshes/` directory and does not replace `codebase-map.json`; callers must choose the successor explicitly.

## 2026-05-01 — Skeptic challenge target fix

- Audit finding: once Python import extraction exists, `cbm-handoff` must not assume the unknown edge is `surface.edges[0]`. A current-head smoke showed the Skeptic challenge was attached to the first edge by index, which could incorrectly challenge a factual import edge.
- Fix: `cbm-handoff` now locates `edge-unknown-001` by id before setting `claim_status: challenged` and adding `chl-00001`.
- Verification run:
  - `pytest -q` passed: 5 tests. The main flow test now asserts import edges remain `active` while the unknown edge is `challenged`.
  - Smoke run `run-phase-a-audit-fixed` completed and produced a valid surface map, findings card, and handoff with `ledger_consistency.append_only_verified: true`.
- Self-critique:
  - Drift check: This preserves factual claims from interpretive/coverage challenge pollution.
  - Contract check: The ledger challenge entry already named `edge-unknown-001`; the surface map now matches that ledger claim target.
  - Reviewer-eye check: The smoke run on the dirty repo still falls back to a structural card because uncommitted source files are intentionally not cited at `source_sha`. Re-run after this commit to audit current committed behavior.

## 2026-05-01 — Phase B slice: consultation mode

- Implemented: `cbm-consult` / `cbm consult <question>`, which searches fresh cited artifacts in `.research/` and writes a consultation artifact under `.research/consultations/`.
- Implemented: consultation answers require at least one citation whose recorded source still matches current `HEAD`; uncited artifacts are not used as answer sources.
- Implemented: unanswered questions are recorded as explicit refusal artifacts instead of producing unsupported advice.
- Verification run:
  - `pytest -q` passed: 10 tests, including a consultation test that answers from a fresh run for `src/app.py` and refuses a missing query.
- Self-critique:
  - Drift check: Consultation mode reuses existing research artifacts and does not introduce a new interpretive runtime agent.
  - Contract check: Answers are gated on citations that are still grounded at `HEAD`, matching the reuse-and-refresh direction.
  - Reviewer-eye check: Matching is token-based and intentionally narrow. It can miss semantically related questions until a richer index exists, but refusal is safer than synthesizing from an insufficient corpus.

## 2026-05-01 — Phase B slice: interpretive refresh

- Implemented: `cbm-refresh <surface-map> --mode interpretive`. It writes a refreshed codebase map input, a successor surface map, and a `refresh-delta-interpretive-<sha>.json` under the run's `refreshes/` directory.
- Implemented: differential surface comparison by claim signature. Claims that still match are carried forward when their citations remain grounded at `HEAD`, updated when their evidence moved, and retracted when no successor claim exists. New successor claims are recorded in `newly_added`.
- Implemented: existing challenge state is carried into surviving successor claims and recorded in `challenges_carried_forward`.
- Verification run:
  - `pytest -q` passed: 11 tests, including an interpretive-refresh test that changes a cited import file, adds a new import edge, validates the successor surface map and refresh delta, and confirms `chl-00001` stays active.
- Self-critique:
  - Drift check: This preserves prior readings and challenge state instead of overwriting the old surface map.
  - Contract check: The successor surface map uses `refreshed_from`, and the delta validates against the v1.2 refresh-delta schema.
  - Reviewer-eye check: This is a deterministic differential refresh, not yet a true Surface Mapper rereading pass. It can classify a still-matching changed claim as `updated`, but it does not make a qualitative judgment about whether the interpretation still holds beyond the static signature match.

## 2026-05-01 — Phase B slice: run gate safety envelope

- Implemented: `cbm-run-gate` / `cbm run-gate <gate-id>`, reading declared commands from a surface map's `verification.ci_gates`.
- Implemented: safety-envelope refusal before execution for unapproved network, install, filesystem mutation, excessive duration, or cwd outside the repository.
- Implemented: command execution without shell interpolation, captured output artifacts under `command-outputs/`, and `command_executed` evidence-ledger entries.
- Verification run:
  - `pytest -q` passed: 12 tests, including a run-gate test that executes a safe local command, records output and ledger evidence, and refuses a network-requiring gate without approval.
- Self-critique:
  - Drift check: The command adds controlled verification execution without allowing source mutation by default.
  - Contract check: Output path, exit code, duration, and command id are recorded in the append-only ledger.
  - Reviewer-eye check: The implementation enforces declared envelope metadata but does not provide OS-level sandboxing for filesystem mutation or network isolation. It refuses declared risky gates unless approved; it cannot detect a dishonest command declaration.

## 2026-05-01 — Phase B slice: verification-map schema

- Implemented: `schemas/verification-map.schema.json` for standard-mode verification gates and command declarations.
- Implemented: `cbm-validate` support for `artifact_type: verification_map`; `cbm-run-gate` can now execute gates from `verification-map.json` as described in the contracts.
- Verification run:
  - `pytest -q` passed: 13 tests, including a verification-map validation test that drives `cbm-run-gate` from `verification-map.json`.
- Self-critique:
  - Drift check: This moves run-gate toward the standard-mode artifact contract instead of leaving it coupled to the MVP surface map.
  - Contract check: The schema covers the universal artifact envelope, `ci_gates`, citations, command argv, cwd, and safety envelope.
  - Reviewer-eye check: This is only the verification-map schema and execution integration. It does not yet add a Verification Mapper that produces this artifact automatically.

## 2026-05-01 — Phase B slice: deterministic verification mapper

- Implemented: `cbm-verify-map` / `cbm verify-map`, producing `verification-map.json` from the deterministic codebase map's discovered tests.
- Implemented: standard and deep `cbm run` now include verification-map generation before goal binding and handoff.
- Implemented: generated test gates declare repo-local pytest commands with no network, no install, no filesystem mutation, and bounded duration.
- Verification run:
  - `pytest -q` passed: 15 tests, including direct `cbm verify-map`, standard-mode run artifact generation, schema validation, and executing a generated `test-001` gate through `cbm-run-gate`.
- Self-critique:
  - Drift check: This adds a deterministic verification surface without turning CBM into a source-mutating executor.
  - Contract check: Generated verification maps validate against the v1.2 schema and command execution is recorded through the existing run-gate ledger path.
  - Reviewer-eye check: This maps discovered test files only. It does not infer lint, typecheck, build, or framework-specific verification gates beyond the deterministic test inventory.

## 2026-05-01 — Phase B slice: authority-map split

- Implemented: `schemas/authority-map.schema.json` for standard-mode authority surfaces.
- Implemented: `cbm-authority-map` / `cbm authority-map`, deriving `authority-map.json` from the combined surface map's authorities with citations, registers, statuses, and staleness metadata preserved.
- Implemented: standard and deep `cbm run` now generate `authority-map.json`.
- Verification run:
  - `pytest -q` passed: 16 tests, including direct authority-map generation, schema validation, and standard-mode run artifact creation.
- Self-critique:
  - Drift check: The split artifact preserves the existing surface-map authorities rather than changing the reading discipline.
  - Contract check: The new schema validates the universal artifact envelope and authority claim fields with challenge/contradiction lifecycle constraints.
  - Reviewer-eye check: This is a mechanical split, not yet three independent Surface Mapper subagents. It gives standard-mode consumers the artifact boundary before adding true parallel mapper production.

## 2026-05-01 — Phase B slice: dependency-graph split

- Implemented: `schemas/dependency-graph.schema.json` for standard-mode dependency edges and explicit certain/suspected/advisory/unknown partition counts.
- Implemented: `cbm-dependency-graph` / `cbm dependency-graph`, deriving `dependency-graph.json` from the combined surface map's edges while preserving citations, registers, claim statuses, extractor ids, and challenges.
- Implemented: standard and deep `cbm run` now generate `dependency-graph.json`.
- Verification run:
  - `pytest -q` passed: 17 tests, including direct dependency-graph generation, schema validation, unknown partition checks, and standard-mode run artifact creation.
- Self-critique:
  - Drift check: The graph carries unknown dependency closure as structured content rather than hiding it behind a successful run.
  - Contract check: Non-unknown edges still require citations, extracted relation edges require extractor ids, and challenged/contested claims require challenges.
  - Reviewer-eye check: This graph is mechanically split from the combined surface map. It does not yet add richer call/runtime dependency extraction beyond existing Python import edges and the explicit unknown edge.

## 2026-05-01 — Phase B slice: synthesis-index artifact

- Implemented: `schemas/synthesis-index.schema.json` for the standard-mode synthesis boundary across surface, authority, dependency, and verification artifacts.
- Implemented: `cbm-synthesis-index` / `cbm synthesis-index`, producing `synthesis-index.json` with input artifact hashes, claim counts, artifact references, and contestation summary.
- Implemented: standard and deep `cbm run` now generate `synthesis-index.json`.
- Verification run:
  - `pytest -q` passed: 18 tests, including direct synthesis-index generation, schema validation, contestation propagation from a challenged dependency edge, and standard-mode run artifact creation.
- Self-critique:
  - Drift check: The index keeps synthesis as an artifact on disk rather than a chat-only summary.
  - Contract check: The schema records inputs and hashes for every indexed artifact, plus challenged claim references.
  - Reviewer-eye check: This is deterministic indexing over existing maps, not full agentic synthesis or uncertainty reconciliation. It creates the validated boundary that a richer Synthesizer can later replace.

## 2026-05-01 — Phase B slice: dependency Skeptic review

- Implemented: `schemas/skeptic-review.schema.json` for validateable Skeptic review frontmatter.
- Implemented: `cbm-skeptic-review` / `cbm skeptic-review <artifact>`. For `dependency_graph`, it challenges unresolved unknown dependency edges, appends `skeptic_challenge` ledger entries, writes `skeptic-review/dependency-graph.md`, and preserves the challenge in the graph artifact.
- Implemented: standard and deep `cbm run` now review `dependency-graph.json` before synthesis so `synthesis-index.json` sees the live challenge.
- Verification run:
  - `pytest -q` passed: 19 tests, including direct Skeptic review validation, graph mutation to `claim_status: challenged`, ledger challenge recording, and standard-mode synthesis seeing the open challenge.
- Self-critique:
  - Drift check: The review reinforces unknown dependency closure as live contestation rather than pretending the graph is complete.
  - Contract check: Review artifacts are schema-validated and challenge entries are append-only ledger records.
  - Reviewer-eye check: This is deterministic gate skepticism for dependency unknowns only. It is not yet full per-artifact subagent review across every map or multi-perspective adversarial review.

## 2026-05-01 — Phase B slice: standard map review fanout

- Implemented: standard and deep `cbm run` now write Skeptic review artifacts for `authority-map.json`, `dependency-graph.json`, `verification-map.json`, and `synthesis-index.json`.
- Verification run:
  - `pytest -q` passed: 19 tests, including standard-mode validation of all four map review artifacts.
- Self-critique:
  - Drift check: Review fanout keeps qualitative gate results in artifacts instead of only in handoff prose.
  - Contract check: Each review artifact validates against `schemas/skeptic-review.schema.json`.
  - Reviewer-eye check: Only dependency-graph review currently emits a substantive challenge. Authority, verification, and synthesis reviews are explicit no-finding artifacts until richer Skeptic logic is implemented.

## 2026-05-01 — Phase B slice: Python call extraction

- Implemented: `ext-python-calls-v1` in the extractor registry with explicit blind spots.
- Implemented: deterministic Python call-edge extraction for direct calls to local functions and symbols imported with absolute `from ... import ...` statements.
- Implemented: surface maps and dependency graphs now include factual `call` edges where the extractor can ground them with source citations, while preserving the unknown edge for methods, dynamic dispatch, runtime workflows, relative imports, and dynamic loading.
- Verification run:
  - `pytest -q` passed: 19 tests, including assertions for a `tests/test_app.py -> src/app.py::hello` call edge and active status preservation after handoff.
- Self-critique:
  - Drift check: This narrows a real dependency unknown without removing the explicit unknown partition.
  - Contract check: Call edges carry `extractor_id`, `static_relation` evidence, citations, and factual register.
  - Reviewer-eye check: The extractor is intentionally shallow. It does not resolve method calls, module attribute calls, alias-heavy flows, decorators, monkeypatching, relative imports, or dynamic dispatch.

## 2026-05-01 — Phase C slice: goal-pack binding

- Implemented: goal-pack ranking in `cbm-bind` for `understand_repo`, `research_only`, `feature_add`, `refactor`, and `audit`.
- Implemented: call edges are now candidate binding surfaces; `feature_add` and `refactor` prioritize call relations, while `audit` prioritizes test/CI/config authorities.
- Verification run:
  - `pytest -q` passed: 20 tests, including a same-run reuse test where `feature_add` and `audit` produce different top-ranked candidates without re-running or modifying the surface map.
- Self-critique:
  - Drift check: Goal packs affect only goal binding and card recommendation type, not goal-agnostic maps.
  - Contract check: `goal-binding.json` remains schema-valid and records the chosen goal class and research-only flag.
  - Reviewer-eye check: These are minimal ranking packs, not full planner prompt/template packs. They prove pack loading behavior at the binding layer but do not yet generate materially different card bodies.

## 2026-05-01 — Phase C slice: goal-pack card emission

- Implemented: `cbm-handoff` now consumes `goal-binding.json` as the source of goal, goal class, research-only flag, selected candidate, and recommended card type.
- Implemented: feature/refactor/audit-style goal packs emit `interventions/int-0001.md` as an `intervention_card`; research-style packs keep emitting `findings/int-0001.md` as a `findings_card`.
- Implemented: selected call edges now flow into the generated card role and dependency reference instead of falling back to import edges.
- Verification run:
  - `pytest -q` passed: 21 tests, including a feature-goal handoff test that validates and citation-checks the generated intervention card.
- Self-critique:
  - Drift check: The card type now follows the bound goal pack without changing the underlying goal-agnostic surface map.
  - Contract check: The generated intervention card validates against the existing shared intervention/findings card schema and citation resolution still passes.
  - Reviewer-eye check: The card body remains generic. This closes the pack-to-artifact integration gap, but richer pack-specific planning language is still future work.

## 2026-05-01 — Phase C slice: goal-pack loader

- Implemented: goal packs now live as package data under `cbm/goal_packs/*.json` instead of as inline Python constants.
- Implemented: a small loader validates pack shape and returns the same pack interface consumed by `cbm-bind`, with a reversible fallback for unknown goal classes.
- Verification run:
  - `pytest -q` passed: 22 tests, including package-data loading for `understand_repo`, `research_only`, `feature_add`, `refactor`, and `audit`.
- Self-critique:
  - Drift check: Pack-specific ranking data moved out of the kernel while the deterministic binding algorithm stayed in the kernel.
  - Contract check: The loader enforces required pack fields, boolean research mode, allowed card types, priority map shape, and rationale presence.
  - Reviewer-eye check: Pack validation is intentionally local and lightweight, not yet a published JSON schema. That is acceptable for Phase C because these are bundled kernel packs, but external pack loading would need a formal schema.

## 2026-05-01 — Phase C acceptance check

- Verified: one mapped run can bind `feature_add`, emit a call-edge intervention card, then rebind `audit` without changing the surface map and emit a different audit-oriented card.
- Verification run:
  - `pytest -q` passed: 22 tests, including the same-run pack rebinding card check.
- Self-critique:
  - Drift check: The acceptance check exercises pack reuse over the same kernel map rather than adding a new mapping path.
  - Contract check: Both cards validate through the existing handoff/card schema path and use the current citation verification flow.
  - Reviewer-eye check: Re-running handoff still refreshes handoff-side Skeptic metadata on the surface map. The important Phase C guarantee is that rebinding itself does not re-run or mutate mapper output.

## 2026-05-01 — Phase C disposition

- Acceptance status: pass for the Phase C roadmap target.
- Met: bundled `feature_add`, `refactor`, `audit`, and `research_only` packs exist and load through `cbm-bind`.
- Met: the same mapped run can produce different goal-bound cards by rebinding packs without re-running mappers.
- Known limitation: generated card prose is still mostly generic; the meaningful difference is currently in selected candidate, card type, goal metadata, dependency reference, and primary-file role.
- Verification run:
  - `pytest -q` passed: 22 tests.
- Self-critique:
  - Drift check: Phase C stayed at the goal-pack layer and did not contaminate map extraction with goal-specific behavior.
  - Contract check: Pack outputs continue through existing `goal-binding`, card, citation, and handoff schemas.
  - Reviewer-eye check: This is sufficient for roadmap acceptance, but external/user-authored packs would need a formal pack schema and stronger duplicate-handoff behavior.

## 2026-05-01 — Phase D slice: workflow trace artifact

- Implemented: `schemas/workflow-trace.schema.json` for deep-mode workflow traces with inputs, coverage, staleness, trigger, ordered steps, unknowns, and confidence rationale.
- Implemented: `cbm-trace-workflows` / `cbm trace-workflows`, deriving a low-confidence static trace from `dependency-graph.json` and the current `goal-binding.json`.
- Implemented: deep `cbm run` now binds the goal before tracing, writes `workflow-traces/trace-0001.json`, and includes workflow traces in handoff artifacts and inputs.
- Verification run:
  - `pytest -q` passed: 23 tests, including deep-mode trace schema validation, citation resolution, selected call-step content, and handoff inclusion.
- Self-critique:
  - Drift check: The tracer artifact is explicitly low-confidence and static-derived; it does not pretend to observe runtime behavior.
  - Contract check: Trace steps carry registers, claim status, evidence kinds, citations, and staleness dependencies through a schema-validated artifact.
  - Reviewer-eye check: This is an artifact boundary, not a full Tracer subagent or runtime instrumentation. It starts Phase D without weakening the evidence model.

## 2026-05-01 — Phase D slice: refinement report

- Implemented: `schemas/refinement-report.schema.json` for deep-mode refinement rounds over unresolved Skeptic challenges and workflow trace unknowns.
- Implemented: `cbm-refine` / `cbm refine`, which records challenge and trace-unknown dispositions with re-entry targets instead of silently treating them as resolved.
- Implemented: deep `cbm run` now writes `refinements/refinement-0001.json` after tracing, and handoff includes refinement reports as artifacts and inputs.
- Verification run:
  - `pytest -q` passed: 24 tests, including refinement report schema validation, citation resolution, live challenge disposition, trace-unknown disposition, and handoff inclusion.
- Self-critique:
  - Drift check: The refinement report keeps uncertainty and contestation live; it does not mark challenges resolved without new evidence.
  - Contract check: Every refinement item carries source artifact, claim id, disposition, re-entry targets, rationale, and citations.
  - Reviewer-eye check: This is the durable protocol boundary for multi-round refinement, not a full second mapper/tracer execution loop. The next deeper slice would consume these re-entry targets to decide whether to run another mapper/tracer round.

## 2026-05-01 — Phase D slice: approval plan

- Implemented: `schemas/approval-plan.schema.json` for deep-mode manual approval items covering command execution and refinement escalation.
- Implemented: `cbm-approval-plan` / `cbm approval-plan`, which reads `verification-map.json` and refinement reports, then writes `approvals/approval-plan.json` with pending approval items and safety envelopes.
- Implemented: deep `cbm run` now writes the approval plan before handoff, and handoff includes it as an artifact and input.
- Verification run:
  - `pytest -q` passed: 25 tests, including approval-plan schema validation, command-execution approvals, manual-review approvals, safety envelope presence, and handoff inclusion.
- Self-critique:
  - Drift check: Approval remains a plan artifact; the system does not auto-approve or execute commands.
  - Contract check: Every approval item records source artifact, action, risk level, status, safety envelope, and rationale.
  - Reviewer-eye check: This is a file-based manual approval UX, not an interactive approval prompt. It satisfies the deep-mode artifact boundary while preserving explicit human control.

## 2026-05-01 — Phase D slice: Tracer skill

- Implemented: `skills/tracer.md`, defining the runtime Tracer protocol for workflow seed selection, evidence classification, ordered steps, unknown preservation, refinement feedback, and anti-patterns.
- Verification run:
  - `pytest -q` passed: 26 tests, including a shipping check for the Tracer skill and its workflow-trace schema reference.
- Self-critique:
  - Drift check: The skill keeps static projections distinct from observed runtime behavior and forbids confidence inflation without runtime or command evidence.
  - Contract check: The skill points to `schemas/workflow-trace.schema.json` and requires citation resolution, unknowns, and refinement feedback.
  - Reviewer-eye check: This adds the missing skill surface. The current CLI still implements a deterministic tracer command rather than launching an isolated Tracer subagent.

## 2026-05-01 — Phase D disposition

- Acceptance status: partial pass for the CLI/artifact kernel, with one explicit platform-integration gap.
- Met: Tracer skill exists and the deterministic tracer command emits schema-valid `workflow-traces/trace-0001.json`.
- Met: deep mode is mode-aware and produces standard maps, Skeptic reviews, goal binding, workflow traces, refinement reports, approval plans, and handoff.
- Met: multi-round refinement has a durable protocol artifact that keeps challenges and trace unknowns live with re-entry targets.
- Met: manual approval has a durable UX artifact listing pending command execution and manual-review approvals with safety envelopes.
- Gap: the implementation does not yet launch an isolated Tracer subagent; it uses the deterministic `cbm trace-workflows` command as the current runtime boundary.
- Verification run:
  - `pytest -q` passed: 26 tests.
- Self-critique:
  - Drift check: Phase D did not turn CBM into a code mutator or auto-executor; approval remains explicit.
  - Contract check: New Phase D artifacts validate and are included in handoff.
  - Reviewer-eye check: The largest objection is legitimate: "subagent" is currently represented by a skill plus CLI boundary, not by actual platform subagent invocation. This should remain visible until platform integration work closes it.

## 2026-05-01 — Phase E slice: project-pack detection

- Implemented: bundled project packs under `cbm/project_packs/*.json` for Python packages, Django, Rails, Phoenix, MCP servers, agent orchestration projects, and monorepos.
- Implemented: `project-type.json` as a Phase 0 detection artifact written during `cbm init`, with evidence citations, extractor annotations, authority hints, and known blind spots.
- Implemented: handoff now includes the project-type report when present.
- Verification run:
  - `pytest -q` passed: 27 tests, including project-pack loading, project-type schema validation, Python package detection, and handoff inclusion.
- Self-critique:
  - Drift check: Project-type signals are reported in a separate artifact and do not contaminate goal-agnostic maps yet.
  - Contract check: Detections cite source files and carry pack annotations through `schemas/project-type.schema.json`.
  - Reviewer-eye check: Detection is intentionally manifest/content-marker based. It does not yet modify extractor registry behavior based on the detected pack.

## 2026-05-01 — Phase E slice: extractor pack annotations

- Implemented: `extractor-registry.json` now carries `project_pack_annotations` derived from detected project packs.
- Implemented: `schemas/extractor-registry.schema.json` now validates those annotations as top-level registry context for Skeptic and mapper consumers.
- Verification run:
  - `pytest -q` passed: 27 tests, including initialized extractor-registry validation and Python package annotation propagation.
- Self-critique:
  - Drift check: Pack annotations inform extractor blind spots without changing extractor output or claim registers.
  - Contract check: Registry annotations are schema-validated and remain separate from extractor definitions.
  - Reviewer-eye check: This is annotation propagation, not project-specific extraction. Django/Rails/Phoenix/MCP packs still need extractors that consume these annotations.

## 2026-05-01 — Phase E disposition

- Acceptance status: partial pass for project-pack scaffolding.
- Met: Phase 0 project-type detection exists as `project-type.json`.
- Met: bundled packs exist for Django, Rails, Phoenix, MCP servers, agent orchestration projects, monorepos, plus a generic Python package pack used by the test fixture.
- Met: detected pack annotations propagate into `extractor-registry.json`.
- Gap: project-type-specific extractors are not yet implemented; current packs provide detection, hints, annotations, and blind spots only.
- Verification run:
  - `pytest -q` passed: 27 tests.
- Self-critique:
  - Drift check: Phase E did not invent framework-specific claims without extractors.
  - Contract check: Project-type and extractor-registry artifacts validate.
  - Reviewer-eye check: This is useful scaffolding, not mature Django/Rails/Phoenix/MCP understanding. The gap remains visible for future extractor work.

## 2026-05-01 — Phase F slice: platform portability docs

- Implemented: `platform/PORTABILITY.md` with the kernel-vs-adapter boundary and verification checklist.
- Implemented: `platform/codex/` with the current Codex hook boundary and mirrored Stop hook command.
- Implemented: `platform/claude-code/README.md` documenting the Claude Code adapter semantics and explicit portability deltas without claiming unverified hook syntax.
- Verification run:
  - `pytest -q` passed: 28 tests, including shipped platform portability docs.
- Self-critique:
  - Drift check: Platform work stayed outside schemas, skills, and CLI contracts.
  - Contract check: The docs require the same CLI, schemas, artifacts, skills, and citation format across platforms.
  - Reviewer-eye check: This is not a fully verified Claude Code adapter. It records the port boundary and the required verification checklist while leaving exact syntax to a docs-verified adapter pass.

## 2026-05-01 — Guardrail slice: claim-evidence check

- Implemented: `cbm-check-evidence` / `cbm check-evidence`, enforcing the claim-evidence requirements table for authorities and dependency edges.
- Fixed: manifest files discovered by structure alone are no longer overclaimed as `authority.config`; build manifests become `authority.build`, and other uncorroborated config-like files become `authority.other`.
- Verification run:
  - `pytest -q` passed: 29 tests, including a regression where schema validation passes but `cbm check-evidence` rejects an import edge missing `static_relation` evidence.
- Self-critique:
  - Drift check: The gate strengthens the existing evidence discipline instead of adding new interpretive claims.
  - Contract check: The deterministic check covers import, call, runtime workflow, test-exercises, config-contract, config/routing/policy authority, and interpretive-rationale requirements.
  - Reviewer-eye check: This is not yet wired into every post-write hook invocation, but the command exists and has a regression test for a schema-valid evidence violation.

## 2026-05-01 — Guardrail slice: handoff evidence gate

- Implemented: `cbm-handoff` now runs the claim-evidence check against `surface-map.json` before writing handoff artifacts.
- Verification run:
  - `pytest -q` passed: 30 tests, including a handoff regression that mutates a call edge to invalid evidence and confirms handoff fails.
- Self-critique:
  - Drift check: This makes the existing handoff gate stricter without changing artifact semantics.
  - Contract check: A final handoff can no longer proceed from a surface map that violates the claim-evidence table.
  - Reviewer-eye check: The post-write hook contract still needs a broader generalized hook runner; this slice covers the final handoff boundary.

## 2026-05-01 — Guardrail slice: stop-hook freshness and evidence

- Implemented: `cbm hook-stop` now verifies handoff input hashes and re-runs claim-evidence checks for `surface-map.json`.
- Verification run:
  - `pytest -q` passed: 31 tests, including a Stop-hook regression that mutates `surface-map.json` after handoff and confirms the hook blocks with an input-hash error.
- Self-critique:
  - Drift check: The Stop hook remains a gate; it does not rewrite artifacts or decide whether failures are acceptable.
  - Contract check: The final platform hook now checks schema, handoff input freshness, and claim-evidence discipline.
  - Reviewer-eye check: This catches post-handoff mutation and evidence-invalid surfaces, but generalized post-write hooks are still not modeled as a separate reusable runner.

## 2026-05-01 — Guardrail slice: reusable artifact gate

- Implemented: `cbm-gate-artifact` / `cbm gate-artifact`, which runs schema validation, citation resolution, and claim-evidence checks through one deterministic command.
- Verification run:
  - `pytest -q` passed: 32 tests, including a gate-artifact regression that catches both unresolved citations and invalid evidence on an otherwise JSON-loadable surface map.
- Self-critique:
  - Drift check: The command is a gate only; it does not mutate artifacts or interpret failures.
  - Contract check: This provides the reusable entry point required by the post-artifact-write hook contract.
  - Reviewer-eye check: Platform adapters still need to call this command at the right lifecycle points; this slice makes that possible without encoding platform syntax.

## 2026-05-01 — Platform slice: artifact gate adapter

- Implemented: `platform/codex/gate-artifact.sh`, a small command-hook wrapper around `python3 -m cbm gate-artifact`.
- Updated: portability docs and Claude Code adapter requirements now name the post-artifact-write gate command.
- Verification run:
  - `pytest -q` passed: 32 tests, including checks that platform docs ship both `hook-stop` and `gate-artifact` adapter semantics.
- Self-critique:
  - Drift check: The adapter script only invokes the kernel gate; it does not encode platform-independent policy in shell.
  - Contract check: The Codex adapter, Claude Code adapter, and portability checklist now point at the same reusable gate.
  - Reviewer-eye check: This still does not prove Claude Code syntax. It proves the command boundary a Claude Code hook must call once syntax is verified.

## 2026-05-01 — Human review slice: challenge command

- Implemented: `cbm-challenge` / `cbm challenge`, allowing a reviewer to add a structured challenge to a claim in `surface-map`, `authority-map`, or `dependency-graph` artifacts.
- Implemented: challenge writes append-only `claim_challenged` ledger entries, validates the mutated artifact, and preserves competing evidence citations.
- Verification run:
  - `pytest -q` passed: 33 tests, including a human challenge regression that challenges an import edge, validates the artifact through `cbm gate-artifact`, and verifies the ledger entry.
- Self-critique:
  - Drift check: Human review enters as structured contestation, not as silent mutation or chat-only feedback.
  - Contract check: Challenges use the existing schema shape and ledger entry kind.
  - Reviewer-eye check: Resolution UX is still missing; this slice adds challenge creation only.

## 2026-05-01 — Human review slice: challenge resolution

- Implemented: `cbm-resolve-challenge` / `cbm resolve-challenge`, allowing a reviewer to mark a challenge as withdrawn, accepted as alternative/replacement, or resolved to contradiction.
- Implemented: resolution updates claim status from challenge state and appends `challenge_resolved` ledger entries.
- Verification run:
  - `pytest -q` passed: 33 tests, including a reviewer challenge lifecycle from challenge creation through withdrawal and ledger verification.
- Self-critique:
  - Drift check: Resolution is explicit and ledger-backed; it does not erase prior challenges.
  - Contract check: Challenge status uses the existing schema enum and append-only ledger kind.
  - Reviewer-eye check: The command resolves one challenge at a time. Batch review workflows and downstream card confidence recalculation remain future work.

## 2026-05-01 — Handoff slice: dynamic contestation summary

- Implemented: `cbm-handoff` now computes `contestation_summary` from actual surface-map authorities and edges instead of hardcoded Phase A counts.
- Implemented: handoff Skeptic challenge count now reflects all logged claim challenges in the surface map, including human reviewer challenges.
- Verification run:
  - `pytest -q` passed: 34 tests, including a handoff regression where a human challenge and the Skeptic unknown-edge challenge both appear in final counts.
- Self-critique:
  - Drift check: Handoff reports live contestation; it does not resolve or collapse competing readings.
  - Contract check: Counts derive from claim registers, claim statuses, and challenge statuses in the artifact itself.
  - Reviewer-eye check: The summary currently covers surface-map claims. Cross-artifact contestation from split maps should be folded in later.

## 2026-05-01 — Card slice: selected-surface challenge propagation

- Implemented: generated cards now include `dependent_challenges` for the selected goal-binding surface when that selected authority or relation has live challenges.
- Verification run:
  - `pytest -q` passed: 34 tests, including a card regression where a challenged import edge appears alongside the unknown-edge challenge.
- Self-critique:
  - Drift check: Cards preserve contestation instead of raising confidence or silently selecting one reading.
  - Contract check: The card continues using the existing `dependent_challenges` schema field.
  - Reviewer-eye check: The card still does not recompute confidence from the number or severity of selected-surface challenges; it preserves the dependency so a reviewer can see it.

## 2026-05-01 — Handoff slice: split-map contestation

- Implemented: `cbm-handoff` now includes claims from `authority-map.json` and `dependency-graph.json` in `contestation_summary` when those split maps exist.
- Verification run:
  - `pytest -q` passed: 34 tests, including a standard-mode handoff check that counts both surface and dependency-graph challenges.
- Self-critique:
  - Drift check: The handoff now reports contestation across maps without trying to adjudicate it.
  - Contract check: Summary counts derive from each artifact's claim statuses and challenge lists.
  - Reviewer-eye check: Verification-map, workflow-trace, and refinement-report contestation are not yet folded into this summary because they do not expose the same authority/edge claim shape.

## 2026-05-01 — Card slice: live contestation confidence rationale

- Implemented: generated card confidence rationale now responds to live selected-surface challenges while filtering withdrawn or otherwise resolved challenge history out of `dependent_challenges`.
- Implemented: challenge liveness now uses the same status set as claim status recalculation (`open`, `accepted_as_alternative`, `accepted_as_replacement`).
- Verification run:
  - `pytest -q` passed: 34 tests, including live selected-surface challenge rationale and withdrawn challenge exclusion from card dependencies.
- Self-critique:
  - Drift check: Cards still treat unresolved dependency closure as low confidence and now explain when human contestation also affects the selected surface.
  - Contract check: The change stays inside existing `confidence`, `confidence_rationale`, and `dependent_challenges` fields without schema drift.
  - Reviewer-eye check: Confidence remains a coarse enum; this slice improves the audit trail before introducing any richer confidence scoring model.

## 2026-05-01 — Synthesis slice: surface contestation coverage

- Implemented: `synthesis-index.json` now includes challenged claims from `surface-map.json`, not only `authority-map.json` and `dependency-graph.json`.
- Verification run:
  - `pytest -q` passed: 35 tests, including a regression where a human challenge on a surface import appears in synthesis contestation.
- Self-critique:
  - Drift check: Synthesis now preserves contestation introduced before split maps exist instead of losing it between surface mapping and handoff.
  - Contract check: The change reuses the existing `contestation.challenged_claims` structure without changing the schema.
  - Reviewer-eye check: Workflow-trace and refinement report contestation still need a distinct representation because those artifacts do not expose the same challenge-bearing claim shape.

## 2026-05-01 — Contestation slice: live challenge counting

- Implemented: synthesis challenged-claim references, handoff contestation summaries, and handoff Skeptic challenge counts now use the shared live challenge status set instead of counting withdrawn or resolved challenge history.
- Verification run:
  - `pytest -q` passed: 35 tests, including a mixed-status surface challenge where synthesis carries only the still-live challenge id.
- Self-critique:
  - Drift check: Historical challenge records remain in the artifact and ledger, but live summaries now describe only unresolved contestation.
  - Contract check: This changes counting semantics without schema changes; the existing summary descriptions already frame these fields as live/open contestation.
  - Reviewer-eye check: `open_challenges` still counts only `status=open`, while accepted alternatives/replacements make a claim live through `challenged_claims` and claim status rather than increasing the open count.

## 2026-05-01 — Verify slice: card contestation propagation audit

- Implemented: `cbm-verify` now audits findings/intervention cards by following `related_dependencies` artifact refs and checking that challenged or contested dependency claims appear in `dependent_challenges`.
- Implemented: verify reports now include `contestation_propagation` details plus summary counts for missing or stale propagated contestation.
- Verification run:
  - `pytest -q` passed: 36 tests, including a tampered card that drops a live dependency challenge and fails `cbm-verify`.
- Self-critique:
  - Drift check: This makes contestation propagation auditable instead of relying on card generation intent or schema shape alone.
  - Contract check: The verify report remains the existing transient JSON artifact; this slice adds fields without introducing a new schema.
  - Reviewer-eye check: The audit only follows explicit `related_dependencies` refs, so card dependencies not expressed there remain outside this verifier.

## 2026-05-01 — Gate slice: card contestation propagation hard gate

- Implemented: `cbm-gate-artifact` / `cbm gate-artifact` now runs the same card contestation propagation audit as `cbm-verify`.
- Verification run:
  - `pytest -q` passed: 36 tests, including a tampered card rejected by both `gate-artifact` and `verify`.
- Self-critique:
  - Drift check: Contestation propagation is now a hard artifact gate, aligning with the vision's zero-exception audit criterion for challenged dependencies.
  - Contract check: The gate uses existing card and map fields; no schema changes or new artifact formats were introduced.
  - Reviewer-eye check: This strengthens card gating but still depends on cards expressing their dependency surface through `related_dependencies`.

## 2026-05-01 — Handoff slice: card propagation gate integration

- Implemented: `cbm-handoff` now runs the card contestation propagation audit before completing handoff, and generated cards name `cbm-gate-artifact` as their hard-gate command.
- Verification run:
  - `pytest -q` passed: 36 tests, including a generated-card assertion that the hard gate points at `cbm-gate-artifact`.
- Self-critique:
  - Drift check: Handoff no longer relies only on schema validation for cards; it verifies the contestation discipline before finalizing the bundle.
  - Contract check: The integration reuses the same propagation checker as `verify` and `gate-artifact`.
  - Reviewer-eye check: The handoff check currently covers card contestation propagation, while broader full-run gate orchestration remains split across existing command boundaries.

## 2026-05-01 — Gate slice: contested card confidence

- Implemented: `cbm-verify`, `cbm-gate-artifact`, and `cbm-handoff` now reject findings/intervention cards that claim `confidence: high` while carrying non-empty `dependent_challenges`.
- Implemented: verify reports now include `card_confidence` details and `summary.confidence_violations`.
- Verification run:
  - `pytest -q` passed: 36 tests, including a tampered card that keeps live dependent challenges while inflating confidence to high.
- Self-critique:
  - Drift check: The gate now enforces the vision rule that contestation must visibly lower card confidence instead of being hidden behind a high-confidence label.
  - Contract check: This makes an existing schema description executable without changing the schema.
  - Reviewer-eye check: The rule is intentionally coarse: it only prohibits high confidence with dependent challenges; it does not yet calibrate low versus medium.

## 2026-05-01 — Verify slice: stale dependent challenge ids

- Implemented: card contestation propagation audit now rejects stale `dependent_challenges` ids when a card cites a dependency claim but carries challenge ids that are not live on that claim.
- Verification run:
  - `pytest -q` passed: 36 tests, including a tampered card with an extra stale challenge id in an otherwise valid dependent challenge entry.
- Self-critique:
  - Drift check: The card now carries current live disputes rather than historical or invented challenge ids.
  - Contract check: Stale challenge ids are reported through the existing `contestation_propagation.stale` report field.
  - Reviewer-eye check: This still validates against currently referenced artifacts only; if the referenced artifact itself is stale, freshness verification remains a separate gate.

## 2026-05-01 — Gate slice: card coverage honesty

- Implemented: `cbm-verify`, `cbm-gate-artifact`, and `cbm-handoff` now reject findings/intervention cards whose `primary_files` role claims exceed `coverage.result.files_examined_directly`.
- Implemented: verify reports now include `coverage_honesty` details and `summary.coverage_violations`.
- Verification run:
  - `pytest -q` passed: 36 tests, including a tampered card that claims a primary file role while reporting zero directly examined files.
- Self-critique:
  - Drift check: Card role claims now have at least count-level coverage support rather than relying on schema shape alone.
  - Contract check: This enforces existing coverage fields without schema changes.
  - Reviewer-eye check: The maturity criterion asks for path-level traceability to `files_examined_directly`; the current schema stores counts, not examined paths, so this is a partial gate until coverage evidence becomes path-aware.

## 2026-05-01 — Gate slice: coverage count consistency

- Implemented: `cbm-verify` and `cbm-gate-artifact` now reject artifacts whose `coverage.result.files_unread_in_scope` does not match `files_in_scope - files_examined_directly`.
- Verification run:
  - `pytest -q` passed: 36 tests, including a tampered card with inconsistent coverage counts.
- Self-critique:
  - Drift check: Coverage summaries now have a basic arithmetic invariant instead of trusting self-reported counts blindly.
  - Contract check: The gate uses existing coverage fields shared by schemas; no schema changes were needed.
  - Reviewer-eye check: This still does not prove which specific paths were directly examined, only that the reported counts are internally coherent.

## 2026-05-01 — Handoff slice: coverage caveat specificity

- Implemented: `cbm-handoff` now writes data-bearing coverage caveats that name direct-examination counts, unread in-scope file counts, and extractor-only inspection limits.
- Verification run:
  - `pytest -q` passed: 36 tests, including assertions that handoff caveats mention directly examined files, unread files, and deterministic extractor-only limits.
- Self-critique:
  - Drift check: Handoffs now say what the run did not read instead of using only a generic Phase A caveat.
  - Contract check: This uses the existing `coverage_caveats` handoff field and shared coverage counts.
  - Reviewer-eye check: Caveats still report counts, not path lists; path-aware direct-examination evidence remains a future schema improvement.

## 2026-05-01 — Gate slice: primary-file citation path support

- Implemented: card coverage-honesty checks now require each `primary_files` role claim to include at least one citation whose path matches the claimed primary file path.
- Verification run:
  - `pytest -q` passed: 36 tests, including a tampered card whose primary file role is backed by a valid citation to a different path.
- Self-critique:
  - Drift check: File-role claims now need direct path-specific evidence instead of any resolving citation.
  - Contract check: The gate uses existing `primary_files.path` and `primary_files.citations` fields, so no schema change was required.
  - Reviewer-eye check: This proves citation path support, not that an agent deeply read the cited file; path-aware direct-examination logs remain future work.

## 2026-05-01 — Handoff slice: dynamic schema validation summary

- Implemented: `cbm-handoff` now derives `gate_summary.schema_validation.passed` from the actual artifact list and validates each listed artifact instead of using a hardcoded count.
- Verification run:
  - `pytest -q` passed: 36 tests, including an assertion that handoff schema-validation passed count equals the number of listed artifacts.
- Self-critique:
  - Drift check: Handoff gate summaries now track the real bundle shape as modes add project-type, trace, refinement, and approval artifacts.
  - Contract check: `failed_artifacts` stays compatible with the existing string-array schema.
  - Reviewer-eye check: This records validation failures in the summary but does not yet promote them into a separate failed-run handoff artifact.

## 2026-05-01 — Handoff slice: dynamic staleness summary

- Implemented: `cbm-handoff` now derives `gate_summary.staleness_check.fresh` and `stale_artifacts` by rechecking the recorded hashes for the actual handoff inputs.
- Verification run:
  - `pytest -q` passed: 36 tests, including an assertion that handoff staleness fresh count equals the number of listed inputs.
- Self-critique:
  - Drift check: Handoff staleness summary now reflects real input hashes instead of a mode-era hardcoded count.
  - Contract check: The summary stays within the existing `staleness_check` schema.
  - Reviewer-eye check: This checks handoff input hashes at generation time; post-handoff mutation is still enforced by `cbm hook-stop`.

## 2026-05-01 — Handoff slice: skeptic review count

- Implemented: `cbm-handoff` now derives `gate_summary.skeptic_review.artifacts_reviewed` from the actual skeptic review artifacts listed in the handoff.
- Verification run:
  - `pytest -q` passed: 36 tests, including a standard-mode assertion that the reviewed count equals the number of listed `skeptic_review` artifacts.
- Self-critique:
  - Drift check: Standard/deep handoffs no longer underreport reviewed artifacts as one when multiple review artifacts exist.
  - Contract check: This stays within the existing handoff gate summary schema.
  - Reviewer-eye check: The count proves review artifact presence, not the qualitative adequacy of each Skeptic finding.

## 2026-05-01 — Handoff slice: bundle citation summary

- Implemented: `cbm-handoff` now derives `gate_summary.citation_resolution` from citations extracted across every listed handoff artifact, not just the selected card citation.
- Implemented: ledger citation coverage now uses the same bundle-wide citation set.
- Verification run:
  - `pytest -q` passed: 36 tests, including an independent extraction of citations from handoff-listed artifacts and comparison to the handoff resolved count.
- Self-critique:
  - Drift check: Handoff citation reporting now reflects the whole artifact bundle, matching the vision's all-promoted-artifacts citation discipline.
  - Contract check: The summary stays within the existing `citation_resolution` schema.
  - Reviewer-eye check: An initial test run caught a stale return path from the old single-citation check; fixed before commit.

## 2026-05-01 — Handoff slice: ledger citation coverage details

- Implemented: `cbm-handoff` now reports `missing_citation_count` and `missing_citation_examples` under `gate_summary.ledger_consistency` for bundle citations absent from the evidence ledger.
- Verification run:
  - `pytest -q` passed: 36 tests, including a clean-run assertion that no bundle citations are missing from the ledger.
- Self-critique:
  - Drift check: Ledger consistency now exposes why the boolean would fail instead of hiding missing citation coverage behind `append_only_verified: false`.
  - Contract check: This is an additive summary field on an object schema that already permits extension.
  - Reviewer-eye check: The handoff still fails after writing when missing ledger citations exist; a separate failed-run artifact would make that failure easier to review.

## 2026-05-01 — Hook slice: card semantic gate

- Implemented: `cbm hook-stop` now re-runs the reusable artifact gate for handoff-listed findings/intervention cards, not only handoff schema, input hashes, and surface evidence.
- Implemented: `artifact_gate_failures` centralizes the gate logic used by `cbm gate-artifact` and the stop hook.
- Verification run:
  - `pytest -q` passed: 37 tests, including a tampered card with refreshed input hash that is still blocked by the stop hook due to a card confidence violation.
- Self-critique:
  - Drift check: Final platform gating now checks card semantics even when simple input-hash freshness is satisfied.
  - Contract check: The hook reuses existing gate logic and does not introduce a new platform contract.
  - Reviewer-eye check: Hook-stop still validates only handoff-listed card artifacts; broader per-artifact hook orchestration remains future work.

## 2026-05-01 — Consultation slice: citation reuse ledger

- Implemented: `cbm-consult` now appends `citation_reused` entries to the originating run's `evidence-ledger.jsonl` for citations surfaced from fresh corpus artifacts.
- Implemented: consultation reuse entries preserve the source artifact path and best available claim id, keeping Reader outputs auditable without introducing fresh source claims.
- Verification run:
  - `pytest -q` passed: 37 tests, including a consultation regression that checks surfaced citations appear as `citation_reused` ledger entries and the ledger integrity manifest updates.
- Self-critique:
  - Drift check: Consultation now behaves more like a Reader over an artifact corpus rather than an unaudited search result.
  - Contract check: The entries use the existing `citation_reused` ledger schema; no schema changes were needed.
  - Reviewer-eye check: The Reader still records reuse only for matched artifacts with run-local ledgers; consultation artifacts under `.research/consultations` are not themselves recursively ledgered.

## 2026-05-01 — Consultation slice: refusal uncertainty

- Implemented: refused `cbm-consult` questions now append an open uncertainty to the latest run's `uncertainty-register.jsonl`.
- Implemented: each consultation refusal uncertainty is mirrored with an `uncertainty_logged` evidence-ledger entry, preserving append-only auditability.
- Verification run:
  - `pytest -q` passed: 37 tests, including a consultation refusal regression that checks both the uncertainty register entry and matching ledger event.
- Self-critique:
  - Drift check: Reader refusal now becomes durable corpus knowledge instead of disappearing into a transient consultation artifact.
  - Contract check: This follows the existing handoff uncertainty JSONL shape because the kit does not currently include a separate uncertainty-register schema.
  - Reviewer-eye check: Refusals are attached to the latest run as a pragmatic per-run store; a project-level uncertainty register would be cleaner for cross-run consultation later.

## 2026-05-01 — Consultation slice: stale-match refusal

- Implemented: `cbm-consult` now distinguishes "no grounded match" from "matching artifacts exist but their cited bytes changed at HEAD."
- Implemented: stale consultation refusals include `refusal_reason: stale_corpus_match`, list `stale_matches`, and tell the Reader to refresh or re-run before consulting the question.
- Verification run:
  - `pytest -q` passed: 37 tests, including a consultation regression where matched artifacts become stale after cited files change and consultation refuses with a refresh recommendation.
- Self-critique:
  - Drift check: Reader mode now refuses stale answers explicitly instead of making stale corpus state look like absence of knowledge.
  - Contract check: The consultation artifact remains markdown with YAML frontmatter; new refusal metadata is additive.
  - Reviewer-eye check: Freshness is still evaluated at artifact granularity, so one stale citation blocks a matching artifact even when some claims inside it remain fresh.

## 2026-05-01 — Consultation slice: live challenge metadata

- Implemented: `cbm-consult` now carries `live_challenges` metadata when a matched artifact claim is challenged or contested.
- Implemented: consultation answer text names live challenge ids for matched challenged claims instead of flattening disputes into ordinary matches.
- Verification run:
  - `pytest -q` passed: 37 tests, including a consultation query for `edge-unknown-001` that surfaces live challenge metadata and challenge ids in the answer body.
- Self-critique:
  - Drift check: Reader mode now preserves dispute visibility for matched claims, aligning consultation with the system's contestation discipline.
  - Contract check: The metadata is additive in the consultation artifact and reuses existing claim/challenge fields.
  - Reviewer-eye check: Challenge metadata is claim-text matched; broader artifact-level disputes are intentionally not attached to unrelated query hits.

## 2026-05-01 — Refresh slice: open question reconciliation

- Implemented: structural and interpretive refresh deltas now populate `open_questions_reconciled` from open entries in the run's `uncertainty-register.jsonl`.
- Implemented: unresolved questions are explicitly marked `still_open` with refresh-mode-specific rationale instead of being silently omitted from the delta.
- Verification run:
  - `pytest -q` passed: 37 tests, including structural and interpretive refresh regressions that validate `unc-00001` appears as `still_open` in the refresh delta.
- Self-critique:
  - Drift check: Refresh now carries known unknowns through time rather than treating trajectory as only file and claim diffs.
  - Contract check: This uses the existing `refresh-delta.schema.json` `open_questions_reconciled` field without schema changes.
  - Reviewer-eye check: The current implementation conservatively marks open questions as still open; it does not attempt to prove resolution during deterministic refresh.

## 2026-05-01 — Refresh slice: replacement challenge classification

- Implemented: interpretive refresh now detects a same-kind successor edge/authority when a challenged prior claim disappears, records `superseded_by`, and classifies carried-forward challenge status as `resolved_by_refresh`.
- Implemented: unmatched challenged claims without a replacement continue to be classified as `obsolete_target_retracted`.
- Verification run:
  - `pytest -q` passed: 38 tests, including a new regression where a challenged import edge is replaced by a new import target and the refresh delta records the challenge as resolved by refresh.
- Self-critique:
  - Drift check: Refresh now records more precise challenge trajectory instead of treating every disappeared challenged claim as merely obsolete.
  - Contract check: This uses existing `retracted.superseded_by` and `challenges_carried_forward.post_refresh_status` schema fields.
  - Reviewer-eye check: Replacement detection is heuristic: same claim kind, extractor, and source side. It does not prove semantic equivalence.

## 2026-05-01 — Hook slice: session start freshness

- Implemented: `cbm hook-start` for session-start recovery. It reads the latest handoff, checks recorded input hashes, and revalidates input artifact citations against current `HEAD`.
- Implemented: stale input citations produce a blocking hook response so resumed sessions do not silently act on stale evidence.
- Verification run:
  - `pytest -q` passed: 39 tests, including a start-hook regression that passes before a cited source file changes and blocks after that file is committed at a new `HEAD`.
- Self-critique:
  - Drift check: Session resume now has a mechanical freshness gate matching the compaction-recovery and reuse discipline.
  - Contract check: The command is additive and uses existing citation freshness logic rather than new schemas.
  - Reviewer-eye check: The hook validates latest handoff inputs only; runs without handoff still continue with an informational message.

## 2026-05-01 — Platform slice: start hook exposure

- Implemented: console-script aliases `cbm-hook-start` and `cbm-hook-stop` for lifecycle hook entry points.
- Implemented: Codex adapter config/docs now include the session-start freshness hook alongside the stop hook; Claude Code and portability docs list the same required lifecycle semantics.
- Implemented: the live `.codex/hooks.json` mirrors the Codex adapter template so local Codex runs execute the same start/stop lifecycle gates.
- Verification run:
  - `pytest -q` passed: 40 tests, including portability checks for `hook-start` in live `.codex/hooks.json`, Codex hooks/docs, Claude adapter docs, portability checklist, and console-script declarations.
- Self-critique:
  - Drift check: The session-start freshness gate is now reachable from platform glue rather than existing only as an internal subcommand.
  - Contract check: Platform docs preserve the kernel boundary: adapters call `python3 -m cbm hook-start` and do not reimplement freshness policy.
  - Reviewer-eye check: The Codex hook event name remains adapter syntax; non-Codex adapters must still verify their own lifecycle hook syntax before production use.

## 2026-05-01 — Registry slice: extractor validation command

- Implemented: `cbm extractor-registry validate [registry]` and the `cbm-extractor-registry` console-script alias.
- Implemented: the command validates the registry schema and explicitly rejects extractors with empty `known_blind_spots`.
- Verification run:
  - `pytest -q` passed: 41 tests, including a registry validation regression that accepts the initialized registry and rejects a tampered registry with empty blind spots.
- Self-critique:
  - Drift check: Extractor blind spots now have a dedicated mechanical gate instead of relying on generic schema validation alone.
  - Contract check: This closes the command named in `docs/contracts.md` without changing artifact shape.
  - Reviewer-eye check: The command validates extractor declarations, not whether the blind-spot prose is sufficiently specific or empirically complete.

## 2026-05-01 — Evidence slice: registered extractor references

- Implemented: claim-evidence validation now checks edge `extractor_id` values against the run's `extractor-registry.json` when a registry is available.
- Implemented: `cbm check-evidence`, `cbm gate-artifact`, challenge resolution, handoff, and stop-hook evidence checks now use registry-aware validation.
- Verification run:
  - `pytest -q` passed: 41 tests, including a regression where a schema-valid surface map with `extractor_id: ext-unregistered-v1` fails both `check-evidence` and `gate-artifact`.
- Self-critique:
  - Drift check: Claims can no longer cite arbitrary extractor ids while bypassing the registry/blind-spot discipline.
  - Contract check: This enforces existing registry references without schema changes.
  - Reviewer-eye check: The check requires existence in the registry, but does not yet compare each extractor's declared evidence kinds against the claim's evidence kinds.

## 2026-05-01 — Evidence slice: extractor evidence-kind compatibility

- Implemented: registry-aware claim-evidence validation now checks that each edge's `evidence_kinds` are supported by the referenced extractor's `produces_evidence_kinds`.
- Implemented: schema-valid claims that combine a registered static extractor with unsupported evidence such as `command_output` now fail `check-evidence` and `gate-artifact`.
- Verification run:
  - `pytest -q` passed: 41 tests, including a regression where `ext-python-imports-v1` is asked to support `command_output` and the artifact is rejected.
- Self-critique:
  - Drift check: Extractor declarations now constrain not just identity but what evidence a claim may derive from them.
  - Contract check: This uses existing extractor-registry fields and edge evidence fields; no schema changes.
  - Reviewer-eye check: This is per-edge validation only. It does not yet verify authorities against extractors because authority claims currently do not carry `extractor_id`.

## 2026-05-01 — Registry slice: project-pack annotation validation

- Implemented: `cbm extractor-registry validate` now rejects project-pack annotations with empty `extractor_annotations` or empty `known_blind_spots`.
- Verification run:
  - `pytest -q` passed: 41 tests, including a registry regression that rejects a detected project-pack annotation with its extractor annotations removed.
- Self-critique:
  - Drift check: Project-type context now remains available to Skeptic/mapping consumers instead of being silently stripped from a schema-valid registry.
  - Contract check: This strengthens the dedicated registry command without changing the registry schema.
  - Reviewer-eye check: The command checks presence, not the quality or specificity of the annotation prose.

## 2026-05-01 — Guardrail slice: uncertainty register append-only integrity

- Implemented: `cbm-init` now creates an integrity manifest for `uncertainty-register.jsonl`, and all runtime uncertainty writes update it through an append-only helper.
- Implemented: handoff and consult refusal paths now fail cleanly if the uncertainty register's prior lines no longer match the manifest.
- Implemented: the stop hook now rejects a handoff when `uncertainty-register.jsonl` has been mutated after its integrity manifest was recorded.
- Verification run:
  - `pytest -q` passed: 42 tests, including regressions for uncertainty integrity sidecar updates and stop-hook rejection of a tampered uncertainty register.
- Self-critique:
  - Drift check: This aligns the uncertainty register with the same append-only review posture already used for the evidence ledger.
  - Contract check: The change preserves the existing JSONL shape and adds only a sidecar manifest; no schema change was needed.
  - Reviewer-eye check: The manifest detects mutation and truncation of existing lines, but it is not a cryptographic signature against deletion of the sidecar itself.

## 2026-05-01 — Hook slice: evidence ledger append-only stop gate

- Implemented: `cbm hook-stop` now verifies the evidence ledger append-only integrity manifest, matching the existing handoff-time ledger check and the uncertainty-register stop-hook check.
- Verification run:
  - `pytest -q` passed: 43 tests, including a stop-hook regression that mutates an already-handoffed `evidence-ledger.jsonl` line and confirms the hook blocks.
- Self-critique:
  - Drift check: The stop hook now enforces both append-only audit logs instead of only validating handoff/card surfaces.
  - Contract check: This implements the existing hook rejection contract without changing artifact formats.
  - Reviewer-eye check: As with the uncertainty register, this detects changed prior lines when the sidecar exists; separate sidecar deletion hardening remains a future guardrail.

## 2026-05-01 — Guardrail slice: required integrity manifests

- Implemented: append-only verification can now require an integrity manifest, and current-run ledger/register append paths require it after `cbm-init` creates the sidecars.
- Implemented: handoff and stop-hook gates fail closed when required integrity sidecars are missing, preventing sidecar deletion from resetting append-only history.
- Verification run:
  - `pytest -q` passed: 45 tests, including regressions for missing `evidence-ledger.jsonl.integrity.json` before handoff and missing `uncertainty-register.jsonl.integrity.json` at stop-hook time.
- Self-critique:
  - Drift check: This closes a bypass in the append-only audit surface without changing the artifact semantics.
  - Contract check: Bootstrap still creates empty sidecars in `cbm-init`; post-init writes and hooks now treat missing manifests as integrity failures.
  - Reviewer-eye check: Legacy runs created before sidecars existed may now need a deliberate migration or re-run before appending new audit entries.

## 2026-05-01 — Hook slice: start-hook audit integrity

- Implemented: `cbm hook-start` now verifies evidence-ledger and uncertainty-register append-only integrity before allowing a resumed session to trust the latest handoff.
- Implemented: stop/start hooks share the same append-only integrity helper so lifecycle gates cannot drift independently.
- Verification run:
  - `pytest -q` passed: 46 tests, including a start-hook regression that mutates an already-handoffed evidence ledger line before resume and confirms the hook blocks.
- Self-critique:
  - Drift check: Resume now validates both freshness and audit-log integrity, matching the compaction-recovery discipline.
  - Contract check: This reuses existing hook JSON behavior and append-only manifests; no adapter or schema change was needed.
  - Reviewer-eye check: Hook-start still validates only the latest run by modification time; selecting an older run explicitly remains outside this hook path.

## 2026-05-01 — Hook slice: explicit run selection

- Implemented: `cbm hook-start --run-id <id>` and `cbm hook-stop --run-id <id>` so lifecycle gates can validate a specific run instead of only the most recently modified run.
- Verification run:
  - `pytest -q` passed: 47 tests, including a regression that creates two runs, tampers the older run's ledger, blocks `hook-start --run-id` for the older run, and still passes `hook-stop --run-id` for the newer run.
- Self-critique:
  - Drift check: Explicit run selection makes recovery/debug gates more precise without changing default platform hook behavior.
  - Contract check: Existing platform adapters can keep omitting `--run-id`; the option is additive and defaults to latest-run behavior.
  - Reviewer-eye check: The hook still treats a missing explicit run as non-blocking informational output; stricter missing-run behavior may be desirable for scripted CI use.

## 2026-05-01 — Hook slice: missing explicit run fails closed

- Implemented: `cbm hook-start --run-id <id>` and `cbm hook-stop --run-id <id>` now return blocking hook responses when the explicitly requested run directory does not exist.
- Verification run:
  - `pytest -q` passed: 48 tests, including a regression that checks both start and stop hooks reject a missing explicit run id.
- Self-critique:
  - Drift check: Explicit recovery/CI-style validation now fails closed instead of silently falling back to a no-op informational path.
  - Contract check: Default no-run behavior remains non-blocking for freshly initialized repositories with no `.research` data.
  - Reviewer-eye check: The platform adapters still do not pass `--run-id`; this is an operator/scripting hardening, not a change to normal Codex hook invocation.

## 2026-05-01 — Citation slice: uncited artifacts fail verification

- Implemented: `cbm verify-citations` now exits nonzero when an artifact contains no citations, rather than treating an empty citation set as success.
- Implemented: `cbm verify` reports `summary.missing_citations` and fails when no citations are present.
- Verification run:
  - `pytest -q` passed: 49 tests, including a regression with a synthetic uncited consultation artifact rejected by both verification commands.
- Self-critique:
  - Drift check: This reinforces the evidence-bound artifact discipline from `VISION.md` and `RUNTIME-CONSTITUTION.md`.
  - Contract check: Citation resolution still verifies normal cited artifacts; the new behavior only changes the no-citation case.
  - Reviewer-eye check: Some administrative artifacts may be intentionally citationless; this stricter command behavior means callers should not use citation verification as a vacuous success check for those artifacts.

## 2026-05-01 — Gate slice: uncited artifacts fail composite gate

- Implemented: `cbm gate-artifact` now fails with `citation: no citations found` when an artifact has no citations.
- Verification run:
  - `pytest -q` passed: 49 tests, including the uncited-artifact regression now covering `gate-artifact` as well as `verify` and `verify-citations`.
- Self-critique:
  - Drift check: The reusable post-write gate now enforces evidence presence instead of only checking citation resolution when citations happen to exist.
  - Contract check: Existing cited artifacts still pass; the new failure mode is limited to empty citation sets.
  - Reviewer-eye check: Citationless administrative artifacts should be gated by schema/status-specific checks rather than the evidence-bound artifact gate.

## 2026-05-01 — Freshness slice: uncited artifacts fail validate-fresh

- Implemented: `cbm validate-fresh` now exits stale/nonzero when an artifact has no citations, matching `verify`, `verify-citations`, and `gate-artifact`.
- Verification run:
  - `pytest -q` passed: 49 tests, including the uncited-artifact regression now covering the freshness precondition as well.
- Self-critique:
  - Drift check: Consultation and compaction-recovery freshness checks no longer treat uncited artifacts as trustworthy by default.
  - Contract check: Cited artifacts keep the same byte-comparison behavior; only empty citation sets fail differently.
  - Reviewer-eye check: Artifact types that are truly citationless need a different freshness/status command rather than passing through this evidence freshness gate.

## 2026-05-01 — Corpus slice: uncited evidence artifacts are broken

- Implemented: `cbm corpus-status` now marks citation-required artifacts as `broken` when they contain no citations, instead of classifying them as fresh or pinned.
- Implemented: generated Skeptic review bodies now cite the evidence supporting their findings, so normal run reviews remain evidence-bound under corpus status.
- Verification run:
  - `pytest -q` passed: 50 tests, including a corpus-status regression for an uncited answered consultation and the existing corpus freshness test.
- Self-critique:
  - Drift check: Corpus reuse now refuses uncited answer artifacts and keeps Skeptic review findings tied to cited evidence.
  - Contract check: Administrative artifacts may remain citationless; the missing-citation broken status applies only to citation-required artifact types.
  - Reviewer-eye check: The citation-required type list is code-level policy; a future schema or contract field would make this less implicit.

## 2026-05-01 — Corpus slice: missing citation summary

- Implemented: `cbm corpus-status` now includes `summary.missing_citations`, aggregating citation-required artifacts with empty citation sets.
- Verification run:
  - `pytest -q` passed: 50 tests, including assertions that clean corpus status reports zero missing citations and an uncited answered consultation increments the summary.
- Self-critique:
  - Drift check: Reviewers can now see missing citation failures from the corpus summary without scanning every artifact entry.
  - Contract check: The field is additive in the generated corpus-status manifest.
  - Reviewer-eye check: This is still a summary counter; detailed remediation remains in the per-artifact `citation_summary`.

## 2026-05-01 — Handoff slice: schema failures block completion

- Implemented: `cbm-handoff` now exits nonzero when any listed handoff artifact fails schema validation, while still writing the handoff summary that records the failed artifact.
- Verification run:
  - Focused regression passed: `pytest -q tests/test_cli.py::test_handoff_rejects_schema_invalid_listed_artifact`.
- Self-critique:
  - Drift check: Final handoff completion now matches the schema-validation-in-CI guardrail instead of merely documenting a failed artifact.
  - Contract check: No schema shape changed; `gate_summary.schema_validation.failed_artifacts` remains the durable audit surface.
  - Reviewer-eye check: The command still writes a failed-run handoff artifact before returning nonzero, which is deliberate for asynchronous review.

## 2026-05-01 — Registry slice: duplicate extractor IDs

- Implemented: `cbm extractor-registry validate` now rejects duplicate extractor ids before they can collapse into a last-write-wins lookup.
- Verification run:
  - Focused regression passed: `pytest -q tests/test_cli.py::test_extractor_registry_validate_command_enforces_blind_spots`.
- Self-critique:
  - Drift check: Registry identity is now stable enough for extractor-backed claim validation to remain auditable.
  - Contract check: This is command-level validation over the existing schema shape; no schema edit was needed.
  - Reviewer-eye check: Duplicate project-pack annotations are still permitted; only extractor id identity is hardened in this slice.

## 2026-05-01 — Registry slice: duplicate pack annotations

- Implemented: `cbm extractor-registry validate` now rejects duplicate project-pack annotation entries for the same `(project_type, pack_id)` pair.
- Verification run:
  - Focused regression passed: `pytest -q tests/test_cli.py::test_extractor_registry_validate_command_enforces_blind_spots`.
- Self-critique:
  - Drift check: Project-pack annotations now stay one-to-one with the pack identity they document.
  - Contract check: This uses existing `project_type` and `pack_id` fields and does not require a schema edit.
  - Reviewer-eye check: The command still validates annotation presence and identity only; it does not judge annotation quality.

## 2026-05-01 — Registry slice: gates validate registry health

- Implemented: artifact evidence gates now validate the run's `extractor-registry.json` before trusting extractor lookups.
- Implemented: `check-evidence`, `gate-artifact`, challenge mutation paths, handoff, and stop-hook evidence checks now fail on invalid or duplicate-bearing registries.
- Verification run:
  - Focused regressions passed: `pytest -q tests/test_cli.py::test_check_evidence_enforces_claim_requirements tests/test_cli.py::test_extractor_registry_validate_command_enforces_blind_spots`.
- Self-critique:
  - Drift check: Claim evidence validation no longer depends on a separately-run registry validation command.
  - Contract check: Registry failures are surfaced through existing command error paths and do not change artifact schemas.
  - Reviewer-eye check: Missing registry files still remain tolerated for legacy or external artifacts; invalid registries fail when present.

## 2026-05-01 — Verify slice: evidence and registry checks

- Implemented: `cbm verify` now includes extractor-registry health and claim-evidence requirement checks in the durable verify report.
- Implemented: verify summaries now report `extractor_registry_errors` and `claim_evidence_errors`, and the command exits nonzero when either count is nonzero.
- Verification run:
  - Focused regressions passed: `pytest -q tests/test_cli.py::test_check_evidence_enforces_claim_requirements` and `pytest -q tests/test_cli.py::test_verify_reports_missing_card_contestation tests/test_cli.py::test_verify_commands_reject_artifacts_without_citations`.
- Self-critique:
  - Drift check: The durable verify report is no longer weaker than the artifact gate for evidence-bound artifacts.
  - Contract check: This adds report fields to the generated `verify_report` artifact, which currently has no dedicated schema.
  - Reviewer-eye check: Schema validation itself is still handled by `cbm validate` and `cbm gate-artifact`; `cbm verify` remains focused on freshness and semantic guardrails.

## 2026-05-01 — Planning reset: live state and review surface

- Decision: Add `.planning/STATE.md` and `.planning/CURRENT-PLAN.md` as the live operational truth because `docs/roadmap.md` is now partially superseded by implementation reality.
- Decision: Update `AGENTS.md` so future agents read `.planning/STATE.md` and `.planning/CURRENT-PLAN.md` before assuming phase status, and so Codex hooks are not treated as the core CBM deployment or correctness mechanism.
- Decision: Create `.planning/reviews/2026-05-01-opus-architecture-audit/` with `REVIEW-SPEC.md`, `PROMPT.md`, and pending `DISPOSITION.md` for a cross-vendor architecture audit.
- Rationale: The implementation has moved beyond a clean Phase A-only build, while the runtime agent architecture remains unsettled. The build log is too chronological to serve as current state or plan.
- Verification plan: Run `git diff --check -- AGENTS.md BUILD-LOG.md .planning` for this documentation/planning slice; run code tests only after code changes or if the audit disposition requires them.
- Self-critique:
  - Drift check: This pauses feature work to correct planning and architecture visibility.
  - Contract check: No runtime artifact schema changed.
  - Reviewer-eye check: Committing `AGENTS.md` may include a pre-existing uncommitted rewrite of that file; this should be called out because the working tree was already dirty.

## 2026-05-01 — Review reset: neutral multi-track audit

- Decision: Abort the first Opus review packet because its prompt overdetermined the diagnosis by foregrounding the current agent's hook and architecture framing.
- Decision: Create `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/` with separate prompts for architecture/product shape, development workflow/governance, and `VISION.md` quality.
- Decision: Treat `VISION.md` as currently authoritative but reviewable. The vision itself may need improvements if it is unclear, too aspirational, or insufficiently operational.
- Decision: Make automated `/goal` governance a first-class review target, including drift detection, stale-plan handling, repeated-failure recovery, and escalation thresholds.
- Rationale: An independent review should diagnose the problem space and compare candidate explanations, not ratify the agent's latest theory.
- Verification plan: Run `git diff --check -- .planning BUILD-LOG.md`; do not launch reviewers until the neutral packet is inspected.
- Self-critique:
  - Drift check: This directly addresses the user's concern that the review framing was biased.
  - Contract check: This changes planning/review artifacts only.
  - Reviewer-eye check: The project now has two review directories; the aborted one is retained as audit evidence and explicitly superseded.

## 2026-05-01 — Recovery intervention: review disposition applied

- Decision: Treat the Cowork disposition files as the operative review layer and synthesize them into `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/SYNTHESIS.md` and `DISPOSITION.md`.
- Decision: Replace the stale `.planning/STATE.md` and `.planning/CURRENT-PLAN.md` with recovery-specific state and plan documents.
- Decision: Lock the recovery defaults selected by the user: producer registry architecture, surgical `VISION.md` edits, and checkpoint gate before broad unattended `/goal` resumes.
- Decision: Amend `AGENTS.md` so "default proceed" applies only inside the active plan, checkpoint reviews block phase pass/main merge/broad `/goal` restart, and per-slice self-critique is no longer treated as sufficient review.
- Decision: Require a minimal `cbm-loop-status` preflight before broad unattended `/goal` resumes. The full R6 drift-signal implementation remains queued, but the narrow preflight is load-bearing now.
- Decision: Amend `VISION.md` surgically with minimum useful CBM, deployment shape, measurement honesty, revision protocol, and v1-blocking conjecture classification.
- Decision: Update architecture/roadmap/contracts language so hooks are adapter glue and deterministic runs are baseline-only until runtime producers exist.
- Rationale: The reviews converged that the previous workflow let deterministic kernel-hardening substitute for runtime-agent evidence. The reset must constrain the next autonomous loop, not just summarize the problem.
- Verification plan: Run `git diff --check -- .planning AGENTS.md VISION.md docs/architecture.md docs/roadmap.md docs/contracts.md BUILD-LOG.md` before committing the planning/governance reset.

## 2026-05-01 — Recovery slice: minimal loop-status preflight

- Implemented: `cbm-loop-status` / `cbm loop-status` as a read-only recovery preflight.
- Implemented: broad `/goal` scope fails while the checkpoint gate is pending; recovery-slice scope reports that condition as a warning so bounded recovery work can continue.
- Implemented: dirty authority/planning docs and disallowed recovery work categories fail the preflight.
- Rationale: The workflow disposition's R6 recommendation is load-bearing enough that a minimal preflight should exist before broad unattended `/goal` resumes, even though the full drift-signal suite remains later work.
- Verification run:
  - Focused regressions passed: `pytest -q tests/test_cli.py::test_loop_status_blocks_broad_goal_until_checkpoint_satisfies_resume tests/test_cli.py::test_loop_status_blocks_dirty_authority_docs_and_disallowed_work`.
  - `git diff --check -- cbm/cli.py tests/test_cli.py pyproject.toml docs/contracts.md BUILD-LOG.md` passed.
  - `pytest -q` passed: 53 tests, 2 existing `jsonschema.RefResolver` deprecation warnings.

## 2026-05-01 — Recovery slice: false provenance and coverage honesty

- Implemented: deterministic baseline artifacts now use explicit `cbm-baseline-*` producer labels instead of role-like runtime agent names.
- Implemented: dev fixture artifacts now use explicit `dev-fixture-*` labels instead of implying real Skeptic, Planner, Tracer, Approval, or Refinement agent execution.
- Implemented: deterministic Skeptic review no longer fabricates `skeptic_challenge` ledger entries or mutates unknown edges to challenged status. Unknown dependency edges stay active until a real isolated Skeptic or human challenge contests them.
- Implemented: deterministic surface, verification, and trace artifacts no longer report direct file examination from static extraction counts.
- Implemented: no-finding Skeptic review stubs cite the reviewed artifact so corpus freshness/citation checks remain honest.
- Implemented: high-confidence cards now fail gates if they still have unread in-scope files, in addition to failing when dependent challenges exist.
- Updated tests so human challenge, refresh, consult, handoff, corpus-status, hook-stop, synthesis, and deep-mode refinement behavior are asserted without relying on the removed synthetic Skeptic challenge.
- Rationale: Cross-vendor dispositions identified counterfeit agent provenance and overclaimed coverage as immediate blockers for trustworthy `/goal` recovery.
- Verification run:
  - Focused regressions passed: `pytest -q tests/test_cli.py::test_init_map_handoff_and_citation_resolution tests/test_cli.py::test_standard_run_writes_verification_map tests/test_cli.py::test_skeptic_review_challenges_dependency_unknowns tests/test_cli.py::test_synthesis_index_connects_standard_maps tests/test_cli.py::test_verification_map_schema_can_drive_run_gate`.
  - Full suite passed: `pytest -q` reported 53 passed, 2 existing `jsonschema.RefResolver` deprecation warnings.
- Self-critique:
  - Drift check: This removes the most misleading deterministic substitutes while preserving explicit unknowns for later runtime-agent work.
  - Contract check: Existing schema producer patterns are preserved; schema enum values for reentry targets remain domain roles such as `tracer`, not producer labels.
  - Reviewer-eye check: Producer labels are still hard-coded, not registry-backed. The next architectural step remains producer-registry and run-manifest work rather than more validators.

## 2026-05-01 — Recovery slice: producer registry and run manifest

- Implemented: `cbm run --backend deterministic|external`.
- Implemented: deterministic runs write `producer-registry.json` and `run-manifest.json`.
- Implemented: the run manifest records backend, mode, goal, producer registry hash, step IDs, producer IDs, step status, and exit codes.
- Implemented: external backend selection writes a producer registry and refused run manifest, then exits nonzero instead of producing fake external-agent artifacts.
- Added schemas for `producer_registry` and `run_manifest`, and updated contracts/README orientation.
- Rationale: The recovery plan requires CBM to own the run lifecycle explicitly before adding real external/Codex agent backends.
- Verification run:
  - Recovery preflight passed via module entry point: `python3 -m cbm.cli loop-status --repo . --scope recovery-slice --work-category producer-registry` exited 0 and emitted the existing `jsonschema.RefResolver` deprecation warning.
  - Focused regressions passed: `pytest -q tests/test_cli.py::test_run_backend_deterministic_writes_manifest_and_producer_registry tests/test_cli.py::test_run_backend_external_refuses_without_fake_agent_outputs tests/test_cli.py::test_run_orchestrates_phase_a_flow`.
  - Full suite passed: `pytest -q` reported 55 passed, 2 existing `jsonschema.RefResolver` deprecation warnings.
- Self-critique:
  - Drift check: This is lifecycle plumbing, not a claim that runtime agents exist.
  - Contract check: New durable artifacts have schemas and validation tests.
  - Reviewer-eye check: The registry is still static and command-run only; standalone subcommands do not yet dispatch through it. That is acceptable for the recovery slice but must be addressed before treating the registry as the full orchestration layer.

## 2026-05-01 — Recovery spike: Codex CLI isolation controls

- Created `.planning/spikes/2026-05-01-codex-cli-isolation.md`.
- Evidence gathered from local CLI help/version only: `command -v codex`, `codex --version`, `codex --help`, `codex exec --help`, `codex exec review --help`, `codex debug --help`, and `codex debug prompt-input --help`.
- Observed `codex-cli 0.128.0`.
- Finding: `codex exec` exposes useful isolation controls including `--ephemeral`, `--ignore-user-config`, `--ignore-rules`, `--output-schema`, `--json`, `-C`, `--add-dir`, sandbox selection, approval policy, model/profile/config overrides.
- Decision: Do not wire a `codex_cli` backend yet. The CLI surface is promising, but a live model subprocess smoke is still required before using Codex CLI for Skeptic.
- Boundary: No paid/live model subprocess was run in this spike.
- Verification run:
  - `git diff --check -- .planning/spikes/2026-05-01-codex-cli-isolation.md .planning/CURRENT-PLAN.md .planning/STATE.md BUILD-LOG.md` passed.
- Self-critique:
  - Drift check: This keeps Codex CLI as a candidate backend rather than silently assuming it satisfies runtime-agent isolation.
  - Contract check: Planning artifact only; no runtime schema or code changed.
  - Reviewer-eye check: Help output is weaker evidence than a live subprocess transcript. The next backend slice must include a bounded live smoke or remain unwired.

## 2026-05-01 — Recovery slice: external deterministic benchmark baseline

- Implemented: `cbm/cli.py` now has a `__main__` guard so `python3 -m cbm.cli ...` actually dispatches commands.
- Correction: Prior build-log/commit-message references to `python3 -m cbm.cli loop-status ...` as a passing preflight were invalid because the module previously only imported. After adding the guard, the same preflight actually ran, printed checkpoint-pending warning, printed `loop-status: ok`, and exited 0.
- Implemented: project-type citations are now recorded in the evidence ledger during `cbm init`.
- Added regression: `test_init_records_project_type_citations_in_ledger`.
- Ran the first pinned external deterministic baseline on MCP servers `src/git` at `4503e2d12b799448cd05f789dd40f9643a8d1a6c`.
- Result artifact: `.planning/benchmarks/2026-05-01-mcp-git-baseline/RESULT.md`.
- Rationale: The recovery plan required at least one external baseline before further autonomous work so CBM's deterministic behavior is tested beyond the tiny fixture.
- Verification run:
  - Actual recovery preflight passed: `python3 -m cbm.cli loop-status --repo . --scope recovery-slice --work-category benchmark`.
  - Focused regressions passed: `pytest -q tests/test_cli.py::test_init_records_project_type_citations_in_ledger tests/test_cli.py::test_run_backend_deterministic_writes_manifest_and_producer_registry tests/test_cli.py::test_init_map_handoff_and_citation_resolution`.
  - Benchmark command passed: `python3 -m cbm.cli run --repo /tmp/cbm-benchmark-mcp-servers-4503e2d/src/git --goal "understand MCP git server surfaces" --backend deterministic --mode standard --run-id run-mcp-git-baseline-2`.
  - Benchmark `handoff.md` and `run-manifest.json` both validated.
  - Full suite passed: `pytest -q` reported 56 passed, 2 existing `jsonschema.RefResolver` deprecation warnings.
- Self-critique:
  - Drift check: This is still deterministic baseline evidence, not a Phase B+ or runtime-agent pass.
  - Contract check: Handoff caught the missing project-type ledger citations before the fix; the gate behaved correctly.
  - Reviewer-eye check: The benchmark required copying CBM schemas into the target checkout, polluting file scope. This is now a recorded benchmark-harness gap and should be fixed before comparing quality.

## 2026-05-01 — Recovery closure: checkpoint accepted

- Implemented: normalized `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/CHECKPOINT.md` after the bounded reviewer accepted the recovery gate.
- Decision: Treat the same-model checkpoint as sufficient for `/goal` readiness because it has an adversarial mandate, records limitations, and accepts only the narrow runtime-producer evidence track.
- Decision: Broad unattended `/goal` may resume only for the first real agent-produced benchmark artifact. It may not claim Phase B+, use Codex CLI for Skeptic before isolation is proven, treat deterministic artifacts as runtime-agent output, or add unrelated kernel-only hardening.
- Nonblocking findings carried forward:
  - benchmark harness scope pollution from copied schemas;
  - Codex CLI isolation controls are plausible but not proven by live subprocess;
  - `cbm-loop-status` category names require operator care.
- Verification plan:
  - Run `git diff --check -- .planning BUILD-LOG.md`.
  - Run `python3 -m cbm.cli loop-status --repo . --scope broad-goal --work-category benchmark` after committing planning changes, because dirty authority docs should fail before commit.
  - Run `pytest -q`.

## 2026-05-01 — Runtime-producer slice: guarded Codex CLI smoke backend

- Implemented: `cbm run --backend codex-cli` as a guarded smoke backend.
- Implemented: `--allow-live-codex` is required before CBM invokes a Codex CLI subprocess; without it the run writes `producer-registry.json` and a refused `run-manifest.json`, then exits 2.
- Implemented: `--codex-command` allows tests or operators to provide the executable path; regression tests use a fake executable and do not call the live Codex CLI.
- Implemented: the `codex-cli` backend keeps deterministic producers for baseline artifacts and assigns `skeptic_review` to `codex-cli-smoke@0.1`.
- Implemented: the smoke step invokes `codex exec` with `--ephemeral`, `--ignore-user-config`, `--ignore-rules`, read-only sandboxing, no approval prompts, `--json`, `-o`, and `--output-schema`; the full invocation is recorded in `run-manifest.json`.
- Implemented: `cbm-handoff` now preserves an existing valid `skeptic-review/surface-map.md` instead of overwriting external producer output with the deterministic dev fixture.
- Boundary: no live model subprocess was run in this slice. The fake-executable regression proves dispatch, manifest recording, schema validation, and handoff preservation; it does not prove model-visible isolation or runtime-agent quality.
- Verification run:
  - Red test first: `pytest -q tests/test_cli.py::test_run_backend_codex_cli_requires_explicit_live_flag` initially failed because `codex-cli` was not an accepted backend.
  - Red test next: `pytest -q tests/test_cli.py::test_run_backend_codex_cli_fake_producer_writes_agent_review` initially failed because handoff overwrote the fake producer review with `dev-fixture-skeptic@0.1`.
  - Focused regressions passed: `pytest -q tests/test_cli.py::test_run_backend_deterministic_writes_manifest_and_producer_registry tests/test_cli.py::test_run_backend_external_refuses_without_fake_agent_outputs tests/test_cli.py::test_run_orchestrates_phase_a_flow tests/test_cli.py::test_run_backend_codex_cli_requires_explicit_live_flag tests/test_cli.py::test_run_backend_codex_cli_fake_producer_writes_agent_review`.
  - Full suite passed: `pytest -q` reported 58 passed, 2 existing `jsonschema.RefResolver` deprecation warnings.
- Self-critique:
  - Drift check: This advances the runtime-producer evidence track without claiming a real Skeptic exists yet.
  - Contract check: New backend enum values are reflected in producer-registry and run-manifest schemas; artifacts are validated in tests.
  - Reviewer-eye check: `--allow-live-codex` is a sharp guard but still operator-controlled. The next slice must run a user-approved live smoke on the pinned external benchmark or keep the backend classified as unproven.

## 2026-05-01 — Benchmark harness slice: CBM schema source

- Implemented: artifact validation now uses CBM's own schema source instead of requiring `<target-repo>/schemas`.
- Implemented: schema lookup order is `CBM_SCHEMA_DIR`, the CBM checkout's `schemas/`, then target-local `schemas/` only as a legacy fallback.
- Added regression: `test_run_validates_with_cbm_schema_source_without_polluting_target_repo` runs `cbm run` on a sample repo without copying schemas and verifies `codebase-map.json` does not include a polluted `schemas/` subtree.
- Updated contracts and planning state so future benchmark runs do not repeat the MCP baseline's copied-schema scope pollution.
- Verification run:
  - Red test first: `pytest -q tests/test_cli.py::test_run_validates_with_cbm_schema_source_without_polluting_target_repo` initially failed with `FileNotFoundError` for `<target-repo>/schemas/evidence-ledger.schema.json`.
  - Focused regression passed: `pytest -q tests/test_cli.py::test_run_validates_with_cbm_schema_source_without_polluting_target_repo tests/test_cli.py::test_run_backend_codex_cli_fake_producer_writes_agent_review`.
  - Full suite passed: `pytest -q` reported 59 passed, 2 existing `jsonschema.RefResolver` deprecation warnings.
- Self-critique:
  - Drift check: This removes a benchmark harness blocker rather than adding unrelated kernel strictness.
  - Contract check: The schema source rule is now documented in `docs/contracts.md` and covered by regression.
  - Reviewer-eye check: This is source-checkout fallback, not a packaging proof. A future package smoke should verify installed package data includes schemas before distribution claims.

## 2026-05-01 — Runtime-producer slice: Codex CLI smoke model controls

- Implemented: `cbm run --backend codex-cli` now defaults smoke subprocesses to `gpt-5.4-mini` with `model_reasoning_effort="medium"`.
- Implemented: `--codex-model` and `--codex-reasoning-effort` are explicit override flags for the smoke backend.
- Implemented: the manifest command records `-m <model>` and `-c model_reasoning_effort="<effort>"`.
- Evidence: local `codex exec --help` shows `-m/--model` and `-c/--config <key=value>`; it does not expose a dedicated reasoning-effort flag, so the backend uses the documented config override surface.
- Verification run:
  - Focused regression passed: `pytest -q tests/test_cli.py::test_run_backend_codex_cli_fake_producer_writes_agent_review`.
- Self-critique:
  - Drift check: This controls the cost/profile of harness agents before any live smoke, rather than escalating quality prematurely.
  - Contract check: The fake executable asserts the model and reasoning config argv entries, and the manifest string is asserted.
  - Reviewer-eye check: This verifies command construction, not that the live Codex CLI accepts the selected model in the current account. The live smoke remains approval-sensitive.

## 2026-05-01 — Packaging slice: schemas as package data

- Implemented: CBM schemas are copied under `cbm/schemas/` and declared as package data.
- Implemented: setuptools package discovery is scoped to `cbm*` so root-level kit directories such as `skills/`, `schemas/`, and `platform/` are not treated as Python packages.
- Updated schema lookup to prefer `CBM_SCHEMA_DIR`, then package resources, then the source checkout's `schemas/`, then target-local `schemas/` as a legacy fallback.
- Added regression: package schema resources must exactly match the root schema file contents.
- Verification run:
  - Red test first: `pytest -q tests/test_cli.py::test_package_schema_resources_match_root_schemas` initially failed because `cbm/schemas` did not exist.
  - Focused regressions passed: `pytest -q tests/test_cli.py::test_package_schema_resources_match_root_schemas tests/test_cli.py::test_run_validates_with_cbm_schema_source_without_polluting_target_repo`.
  - Wheel build initially failed because setuptools discovered multiple top-level packages; adding explicit package discovery fixed it.
  - Wheel inspection passed: built `cbm-0.1.0-py3-none-any.whl`, found 19 `cbm/schemas/*.schema.json` files, and top-level wheel entries were limited to `cbm` and `cbm-0.1.0.dist-info`.
  - Installed-package smoke passed from `/tmp` with `PYTHONPATH` pointing only at the installed wheel target. The warning path confirmed import from `/tmp/.../pkg/cbm/cli.py`; `cbm run` completed on a sample repo without copied schemas; `cbm validate handoff.md` passed.
- Self-critique:
  - Drift check: This supports clean external benchmark runs and installed validation, rather than adding new artifact policy.
  - Contract check: Package data and schema-source behavior are both tested; wheel contents were inspected directly.
  - Reviewer-eye check: Duplicating root schemas into package data creates drift risk. The content-equality regression is now the guard.

## 2026-05-02 — Runtime-producer slice: live Codex CLI smoke on MCP git

- Ran a live Codex CLI smoke on MCP servers `src/git` at `4503e2d12b799448cd05f789dd40f9643a8d1a6c`.
- Command: `python3 -m cbm.cli run --repo /tmp/cbm-live-mcp-servers-4503e2d/src/git --goal "understand MCP git server surfaces" --backend codex-cli --allow-live-codex --codex-model gpt-5.4-mini --codex-reasoning-effort medium --mode lightweight --run-id run-mcp-git-codex-smoke-4`.
- Implemented during smoke remediation: `codex exec` approval policy is passed with `-c approval_policy="never"` instead of invalid `-a never`.
- Implemented during smoke remediation: Codex smoke reviews append their introduced citations to `evidence-ledger.jsonl`.
- Implemented during smoke remediation: citation parsing excludes Markdown backticks from citation paths.
- Result artifact: `.planning/benchmarks/2026-05-02-mcp-git-codex-smoke/RESULT.md`.
- Durable evidence copied into the result directory: `run-manifest.json`, `producer-registry.json`, `skeptic-review-surface-map.md`, and `handoff.md`.
- Outcome: live run exited 0; run manifest status is `succeeded`; smoke review `produced_by` is `codex-cli-smoke@0.1`; handoff gate summary reports `citation_resolution.unresolved_count: 0` and `ledger_consistency.missing_citation_count: 0`.
- Failed attempts preserved in the result:
  - `run-mcp-git-codex-smoke-1`: invalid `-a never` for `codex exec`.
  - `run-mcp-git-codex-smoke-2`: live smoke citation missing from ledger.
  - `run-mcp-git-codex-smoke-3`: backticked citation parsed with a leading backtick.
- Boundary: This is the first live Codex CLI-produced CBM artifact on the pinned external benchmark. It is not a Phase B+ pass claim and not the `VISION.md` minimum useful CBM floor, because the surface map remains deterministic baseline output and the live artifact is a bounded smoke review rather than a full isolated Skeptic review.
- Verification run:
  - Focused regressions passed: `pytest -q tests/test_cli.py::test_extract_citations_ignores_markdown_backticks tests/test_cli.py::test_run_backend_codex_cli_fake_producer_writes_agent_review`.
  - Live run passed: `run-mcp-git-codex-smoke-4`.
- Self-critique:
  - Drift check: This directly advances the runtime-producer evidence track and explicitly avoids Phase B+ overclaim.
  - Contract check: Parent-side validation and handoff gates caught two integration defects before the successful run.
  - Reviewer-eye check: The smoke review is deliberately shallow; the next quality target must be real Surface Mapper/Skeptic behavior, not more smoke infrastructure.

## 2026-05-02 — Cross-vendor audit and readiness hardening

- Ran a Claude Opus max-effort cross-vendor audit from `.planning/reviews/2026-05-02-opus-cross-vendor-audit/PROMPT.md`.
- First launch attempt was terminated before output because the cmux Claude wrapper injected hook settings. Relaunch used `CMUX_CLAUDE_HOOKS_DISABLED=1` and narrowed setting sources to avoid hook confusion.
- Captured review artifacts:
  - `.planning/reviews/2026-05-02-opus-cross-vendor-audit/OUTPUT-CLAUDE-OPUS.md`;
  - `.planning/reviews/2026-05-02-opus-cross-vendor-audit/INTERVENTIONS.md`;
  - `.planning/reviews/2026-05-02-opus-cross-vendor-audit/DISPOSITION.md`.
- Disposition accepted the immediate blockers: orphaned review-session detection, Codex CLI timeout handling, and run-id validation.
- Implemented: `cbm-loop-status` checks review-session completion and blocks broad `/goal` when a review has prompts without non-empty output, stop note, or aborted disposition.
- Implemented: unsafe run IDs are rejected before `.research/<run_id>` path construction.
- Implemented: Codex CLI smoke subprocesses have a configurable timeout; timed-out runs return 124 and write `interrupted` run/step manifest status.
- Implemented: run-manifest schema now accepts `interrupted`; run-id shape is enforced at the CLI boundary to avoid a breaking schema-version bump.
- Added stop note for the empty `.planning/reviews/2026-05-01-claude-cowork-architecture-review/` packet.
- Verification run:
  - Focused regressions passed: `pytest -q tests/test_cli.py::test_loop_status_blocks_incomplete_review_sessions_for_broad_goal tests/test_cli.py::test_run_rejects_unsafe_run_id_before_writing_outside_research tests/test_cli.py::test_run_backend_codex_cli_timeout_marks_manifest_interrupted tests/test_cli.py::test_run_backend_codex_cli_fake_producer_writes_agent_review tests/test_cli.py::test_package_schema_resources_match_root_schemas`.
  - Full suite passed: `pytest -q` reported 64 passed, 2 existing `jsonschema.RefResolver` deprecation warnings.
  - Post-commit broad-goal preflight passed: `python3 -m cbm.cli loop-status --repo . --scope broad-goal --work-category loop-status --json` reported `status: ok`, no issues, and no warnings.
- Boundary:
  - The audit's GSDR/GSD-2 and external-research claims are parked until independently verified.
  - This slice hardens `/goal` readiness; it still does not satisfy the `VISION.md` minimum-useful CBM floor.

## 2026-05-02 — Runtime-producer spike: live Codex isolation probe

- Ran a live Codex CLI subprocess isolation probe with `gpt-5.4-mini`, medium reasoning, `--ephemeral`, `--ignore-user-config`, `--ignore-rules`, read-only sandboxing, and `approval_policy="never"`.
- Probe artifact: `.planning/spikes/2026-05-02-codex-isolation-live/RESULT.md`.
- Parent-only token SHA-256 was recorded after the run; the token itself was not included in the prompt or pre-run files.
- Outcome: spawned Codex CLI session reported `can_access_parent_context: false`, `claimed_parent_token: null`, and high confidence.
- Verification run:
  - Codex CLI exited 0.
  - `stderr.txt` was empty.
  - `output.json` validated against `output.schema.json` using `jsonschema.Draft202012Validator`.
- Boundary:
  - This supports the Codex CLI backend as an isolated runtime-agent candidate.
  - It does not prove Skeptic quality, cross-platform isolation, or the `VISION.md` minimum-useful CBM floor.

## 2026-05-02 — Runtime-producer slice: skill-loaded Codex Skeptic

- Implemented: runtime skills are packaged under `cbm/runtime_skills/` and loaded from disk via `cbm.skill_loader`.
- Implemented: `cbm run --backend codex-cli --codex-skeptic-mode skill` injects `skills/skeptic.md` into the Codex CLI producer prompt.
- Implemented: run-manifest steps can record a loaded skill `{name, path, sha256}`.
- Implemented: skill mode labels the runtime producer as `skeptic@1.2` instead of `codex-cli-smoke@0.1`.
- Added regressions for packaged runtime skill equality, Skeptic skill hash loading, and skill-mode fake Codex producer behavior.
- Ran a live skill-loaded Skeptic benchmark on MCP `src/git` at `4503e2d12b799448cd05f789dd40f9643a8d1a6c`.
- Result artifact: `.planning/benchmarks/2026-05-02-mcp-git-skeptic-skill/RESULT.md`.
- Outcome:
  - First attempt `run-mcp-git-codex-skeptic-skill-1` failed under disk pressure; parent later hit `OSError: [Errno 28] No space left on device` while updating `run-manifest.json`.
  - After clearing generated temp/test artifacts and using `TMPDIR=/var/tmp`, `run-mcp-git-codex-skeptic-skill-2` exited 0.
  - `run-mcp-git-codex-skeptic-skill-2` produced `skeptic@1.2` review output with `findings_logged: 1` and `challenge_ids: ["chl-00001"]`, but did not structurally integrate challenges.
  - `run-mcp-git-codex-skeptic-skill-3` produced an interpretive challenge but failed parent-side ingestion because `competing_evidence` included artifact JSON pointers and a source citation collapsed into one invalid citation string.
  - Implemented structured runtime challenge ingestion and tightened citation syntax/prompting so `competing_evidence` accepts source citations only.
  - `run-mcp-git-codex-skeptic-skill-4` exited 0 and produced an ingested interpretive challenge against `auth-001`.
- Verification run:
  - Focused regressions passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_package_runtime_skill_resources_match_root_skills tests/test_cli.py::test_load_skill_records_skeptic_hash tests/test_cli.py::test_run_backend_codex_cli_skill_mode_loads_skeptic_skill tests/test_cli.py::test_run_backend_codex_cli_fake_producer_writes_agent_review tests/test_cli.py::test_package_schema_resources_match_root_schemas`.
  - Full suite passed: `TMPDIR=/var/tmp pytest -q` reported 67 passed, 2 existing `jsonschema.RefResolver` deprecation warnings.
  - Wheel inspection passed: built a temp wheel under `/var/tmp`, found 7 `cbm/runtime_skills/*.md` package entries, then removed the temp wheel directory.
  - Structured challenge focused regressions passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_extract_citations_rejects_json_pointer_noise tests/test_cli.py::test_extract_citations_ignores_markdown_backticks tests/test_cli.py::test_run_backend_codex_cli_skill_mode_loads_skeptic_skill`.
  - Full suite after citation tightening passed: `TMPDIR=/var/tmp pytest -q` reported 68 passed, 2 existing `jsonschema.RefResolver` deprecation warnings.
  - Live benchmark run passed: `run-mcp-git-codex-skeptic-skill-4`; handoff validation and run-manifest validation both passed.
- Boundary:
  - This is real skill-loaded runtime-producer evidence, not just smoke.
  - Correction recorded on 2026-05-02: this is a runtime-producer/Skeptic evidence slice, not the full `VISION.md` minimum-useful CBM floor. The full floor requires real Surface Mapper output, isolated Skeptic review, a non-trivial cited interpretive claim or challenge, and a validated handoff.
  - It is still not a Phase B+ pass claim; repeatability and broader runtime-agent orchestration remain open.

## 2026-05-02 — Recovery slice: I-S3 loop-status checkpoint gates

- Implemented: `cbm-loop-status` now supports `--scope pass-claim` and blocks pass claims when the latest checkpoint lacks `reviewer_model_id`.
- Implemented: pass-claim scope rejects reviewers matching the configured current dev-agent family from `cbm/loop_status_config.json`.
- Implemented: same-model fallback is tolerated only for recovery-slice scope when the checkpoint records `same_model_fallback: true`.
- Implemented: review-packet completion tests were expanded to cover orphaned prompt packets and empty review folders by name.
- Implemented: a recent corrective-slice BUILD-LOG heuristic emits a non-blocking `repeated_rework_pattern` warning.
- Updated the historical recovery checkpoint with `reviewer_model_id: gpt-5-codex-same-model-fallback` and `same_model_fallback: true`, matching its existing prose label.
- Decision: configured current dev-agent families as `gpt`, `openai`, and `codex` because this active implementation loop is Codex/OpenAI. A Claude-family checkpoint is therefore cross-model for this loop; the old Codex checkpoint remains only a labeled same-model recovery fallback.
- Verification run:
  - Red tests initially failed as expected: `pass-claim` was not an accepted loop-status scope and `repeated_rework_pattern` was not emitted.
  - Focused regressions passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_loop_status_blocks_broad_goal_on_orphaned_review_packet tests/test_cli.py::test_loop_status_blocks_broad_goal_on_empty_review_folder tests/test_cli.py::test_loop_status_blocks_pass_claim_with_missing_reviewer_model_id tests/test_cli.py::test_loop_status_blocks_pass_claim_with_same_model_reviewer tests/test_cli.py::test_loop_status_accepts_pass_claim_with_cross_model_reviewer tests/test_cli.py::test_loop_status_warns_on_repeated_rework_pattern tests/test_cli.py::test_loop_status_recovery_slice_tolerates_labeled_same_model_fallback`.
  - Cross-regressions passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_loop_status_blocks_broad_goal_until_checkpoint_satisfies_resume tests/test_cli.py::test_loop_status_blocks_dirty_authority_docs_and_disallowed_work`.
  - Self-test passed: `python3 -m cbm.cli loop-status --repo . --scope broad-goal --work-category loop-status --json` reported `status: ok`, no issues, and no warnings.
  - Pass-claim self-test blocked as expected: `python3 -m cbm.cli loop-status --repo . --scope pass-claim --work-category loop-status --json` reported `same_model_checkpoint` for the historical same-model fallback checkpoint.
- Boundary:
  - This builds the mechanical checkpoint gate; it does not create the future cross-model pass-claim review packet itself.

## 2026-05-02 — Recovery slice: I-S4a Codex timeout and run-id hardening completion

- Implemented: Codex CLI timeout handling now writes `cause: timeout` into the interrupted run-manifest step.
- Implemented: timeout partial stdout/stderr is preserved under `.research/<run_id>/codex_outputs/<step>.partial` when a subprocess emits output before timing out.
- Added exact I-S4a regression names for timeout manifest behavior, init/run path-traversal rejection, and valid run-id acceptance.
- Verification run:
  - Red test initially failed as expected because interrupted Codex steps had no `cause` field.
  - Focused regressions passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_codex_cli_subprocess_times_out_and_writes_interrupted_manifest tests/test_cli.py::test_run_id_rejects_path_traversal_in_init tests/test_cli.py::test_run_id_rejects_path_traversal_in_run tests/test_cli.py::test_run_id_accepts_valid_identifiers`.
  - Cross-regressions passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_run_backend_codex_cli_fake_producer_writes_agent_review tests/test_cli.py::test_run_backend_codex_cli_requires_explicit_live_flag tests/test_cli.py::test_init_map_handoff_and_citation_resolution tests/test_cli.py::test_run_orchestrates_phase_a_flow`.
  - Diff check passed: `git diff --check -- cbm/cli.py tests/test_cli.py docs/contracts.md BUILD-LOG.md schemas/run-manifest.schema.json cbm/schemas/run-manifest.schema.json`.
- Boundary:
  - This completes the timeout/run-id behavior; it does not implement the I-S4b stdout/stderr log hashing contract.

## 2026-05-02 — Recovery slice: I-S4b Codex output-path and log hashing

- Implemented: Codex CLI smoke runs tee non-empty subprocess stdout and stderr into `.research/<run_id>/logs/<step>.stdout|stderr`.
- Implemented: successful smoke runs continue to parse only `--output-path`; stdout noise is preserved but never parsed as model JSON.
- Implemented: nonzero Codex subprocess failures report the log path instead of printing raw subprocess stderr/stdout directly.
- Implemented: run-manifest Codex steps record `stdout_sha256`, `stderr_sha256`, and `output_path_sha256`, using an empty-string sentinel for absent or empty files.
- Verification run:
  - Red tests initially failed as expected because stdout/stderr logs were absent and manifest log hashes were not recorded.
  - Focused regressions passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_codex_cli_smoke_fails_when_output_path_not_written tests/test_cli.py::test_codex_cli_smoke_tees_stderr_to_log_file tests/test_cli.py::test_codex_cli_smoke_records_log_shas_in_manifest tests/test_cli.py::test_codex_cli_smoke_tolerates_stdout_when_output_path_is_valid`.
  - Cross-regressions passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_run_backend_codex_cli_fake_producer_writes_agent_review tests/test_cli.py::test_run_backend_codex_cli_requires_explicit_live_flag tests/test_cli.py::test_init_map_handoff_and_citation_resolution tests/test_cli.py::test_run_orchestrates_phase_a_flow tests/test_cli.py::test_extract_citations_ignores_markdown_backticks`.
  - Diff check passed: `git diff --check -- cbm/cli.py schemas/run-manifest.schema.json cbm/schemas/run-manifest.schema.json tests/test_cli.py BUILD-LOG.md`.
- Boundary:
  - Additive schema fields were used; no schema-version bump is required.

## 2026-05-02 — Recovery slice: I-S5 ADR ledger seed

- Implemented: seeded `.planning/decisions/` with five accepted ADRs for run lifecycle ownership, hooks as adapter glue, producer registry, deterministic-baseline boundaries, and cross-model pass-claim checkpoints.
- Updated cross-links in `.planning/STATE.md`, `.planning/CURRENT-PLAN.md`, and `AGENTS.md` so the load-bearing decisions are reachable from live governance surfaces.
- Verification run:
  - Preflight passed: `python3 -m cbm.cli loop-status --repo . --scope recovery-slice --work-category recovery-governance --json` reported `status: ok`, no issues, and no warnings.
  - Diff check passed: `git diff --check -- .planning/decisions .planning/STATE.md .planning/CURRENT-PLAN.md AGENTS.md BUILD-LOG.md`.
  - Full suite passed: `TMPDIR=/var/tmp pytest -q` reported 83 passed, 2 existing `jsonschema.RefResolver` deprecation warnings.
- Boundary:
  - The ADRs record accepted recovery decisions; they do not introduce new architecture beyond the current plan/state.

## 2026-05-02 — Recovery slice: I-X2 per-phase artifact bundle

- Implemented: added the per-phase artifact bundle convention to `AGENTS.md`.
- Implemented: archived the recovery intervention as `.planning/phases/00-recovery-intervention/` with `PLAN.md`, `VERIFICATION.md`, and `SUMMARY.md`.
- Implemented: opened `.planning/phases/01-first-runtime-producer-evidence/` with active `PLAN.md` and close-time `VERIFICATION.md` / `SUMMARY.md` stubs.
- Updated `.planning/STATE.md` and `.planning/CURRENT-PLAN.md` to point at `.planning/phases/`.
- Verification run:
  - Preflight passed: `python3 -m cbm.cli loop-status --repo . --scope recovery-slice --work-category recovery-governance --json` reported `status: ok`, no issues, and no warnings.
  - Diff check passed: `git diff --check -- AGENTS.md .planning/phases BUILD-LOG.md .planning/STATE.md .planning/CURRENT-PLAN.md`.
  - Full suite passed: `TMPDIR=/var/tmp pytest -q` reported 83 passed, 2 existing `jsonschema.RefResolver` deprecation warnings.
- Boundary:
  - The archived recovery plan preserves the original prose under `## Original Recovery Plan`; it is not rewritten into a rigid template.

## 2026-05-02 — Recovery slice: I-X1 native checkpoint primitive

- Implemented: `cbm checkpoint` creates `.planning/reviews/<date-slug>/` packets with `PROMPT.md`, `CHECKPOINT.md`, and `DISPOSITION.md`.
- Implemented: checkpoint prompts include `.planning/STATE.md`, `.planning/CURRENT-PLAN.md`, the pass criterion, and a diff since the last tracked checkpoint across authority, docs, code, tests, schemas, and live planning files.
- Implemented: checkpoint frontmatter records `reviewer_model_id`, `same_model_fallback`, `scope`, and `pass_criterion`.
- Implemented: `cbm-checkpoint` console script and `docs/contracts.md` command documentation.
- Decision: I-X1 tests use GPT/Codex as same-model and Claude as cross-model, matching `cbm/loop_status_config.json` for this active Codex/OpenAI implementation loop.
- Verification run:
  - Red tests initially failed as expected because `checkpoint` was not a recognized CLI subcommand.
  - Focused regressions passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_checkpoint_command_emits_packet_with_required_files tests/test_cli.py::test_checkpoint_packet_includes_diff_since_last_checkpoint tests/test_cli.py::test_checkpoint_records_reviewer_model_id_when_provided tests/test_cli.py::test_checkpoint_recovery_slice_allows_same_model_fallback_with_flag tests/test_cli.py::test_checkpoint_pass_claim_warns_on_same_model_fallback tests/test_cli.py::test_loop_status_pass_claim_blocked_until_cross_model_disposition`.
  - Cross-regressions passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_loop_status_blocks_broad_goal_on_orphaned_review_packet tests/test_cli.py::test_loop_status_blocks_broad_goal_on_empty_review_folder tests/test_cli.py::test_loop_status_blocks_pass_claim_with_missing_reviewer_model_id tests/test_cli.py::test_loop_status_blocks_pass_claim_with_same_model_reviewer tests/test_cli.py::test_loop_status_accepts_pass_claim_with_cross_model_reviewer tests/test_cli.py::test_loop_status_warns_on_repeated_rework_pattern tests/test_cli.py::test_loop_status_recovery_slice_tolerates_labeled_same_model_fallback tests/test_cli.py::test_loop_status_blocks_broad_goal_until_checkpoint_satisfies_resume tests/test_cli.py::test_loop_status_blocks_dirty_authority_docs_and_disallowed_work`.
  - Diff check passed: `git diff --check -- cbm/cli.py cbm/loop_status_config.json tests/test_cli.py docs/contracts.md AGENTS.md BUILD-LOG.md pyproject.toml`.
  - Full suite passed: `TMPDIR=/var/tmp pytest -q` reported 89 passed, 2 existing `jsonschema.RefResolver` deprecation warnings.
- Boundary:
  - This builds the checkpoint packet primitive only. The actual minimum-useful-CBM pass-claim checkpoint must be created and reviewed separately by a non-current-model reviewer.

## 2026-05-02 — Recovery slice: I-S6 Codex CLI failure-mode regressions

- Implemented: completed the named Codex CLI failure-mode regression set for timeout, invalid JSON, missing output file, schema-invalid output, and stderr noise with valid output-path JSON.
- Verification run:
  - Focused regressions passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_codex_cli_smoke_handles_subprocess_timeout tests/test_cli.py::test_codex_cli_smoke_rejects_invalid_json_output tests/test_cli.py::test_codex_cli_smoke_rejects_missing_output_file tests/test_cli.py::test_codex_cli_smoke_rejects_schema_invalid_output tests/test_cli.py::test_codex_cli_smoke_tolerates_stderr_noise_with_valid_json`.
  - Cross-regressions passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py -k codex_cli` reported 14 passed, 80 deselected, 2 warnings.
  - Diff check passed: `git diff --check -- tests/test_cli.py BUILD-LOG.md .planning/phases/01-first-runtime-producer-evidence/PLAN.md`.
  - Full suite passed: `TMPDIR=/var/tmp pytest -q` reported 94 passed, 2 existing `jsonschema.RefResolver` deprecation warnings.
- Boundary:
  - This is regression coverage for existing adapter behavior; no runtime behavior was changed in this slice.

## 2026-05-02 — Recovery slice: I-S7 honest baseline banner

- Implemented: handoff markdown renders the exact deterministic-baseline warning when listed artifacts/cards were produced by `cbm-baseline-*` or `dev-fixture-*`.
- Implemented: baseline/dev-fixture findings and intervention cards render `[BASELINE]` in the card title.
- Verification run:
  - Red tests initially failed as expected because the banner/render helpers did not exist.
  - Focused regressions passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_handoff_renders_baseline_banner_when_any_card_is_baseline tests/test_cli.py::test_handoff_omits_baseline_banner_when_all_cards_are_runtime_agent tests/test_cli.py::test_handoff_marks_each_baseline_card_with_inline_marker`.
  - Cross-regressions passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py -k handoff` reported 11 passed, 86 deselected, 2 warnings.
  - Diff check passed: `git diff --check -- cbm/cli.py tests/test_cli.py BUILD-LOG.md .planning/phases/01-first-runtime-producer-evidence/PLAN.md`.
  - Full suite passed: `TMPDIR=/var/tmp pytest -q` reported 97 passed, 2 existing `jsonschema.RefResolver` deprecation warnings.
- Boundary:
  - Presentation-only change; artifact schemas are unchanged.

## 2026-05-02 — Recovery slice: I-S1 supplemental CBM-run isolation probe

- Implemented: passed the `cbm run --goal` text into the Codex CLI smoke subprocess prompt so CBM-run isolation probes can actually carry the probe objective.
- Ran two live `cbm run --backend codex-cli` probes on tiny `/var/tmp` scratch repos with parent-only token values kept out of files and command arguments.
- Added formal spike artifact `.planning/spikes/2026-05-02-codex-isolation-live.md`.
- Outcome: `verified`; neither run emitted a concrete `isolation-probe-xxxxxxxx` token string, and Probe B explicitly reported no parent conversation context.
- Verification run:
  - Focused Codex CLI regression passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_run_backend_codex_cli_fake_producer_writes_agent_review tests/test_cli.py -k codex_cli` reported 14 passed, 83 deselected, 2 warnings.
  - Probe A and Probe B live runs exited 0.
  - Regex search for `isolation-probe-[0-9a-f]{8}` across both run directories returned no matches.
  - Both probe handoffs validated with `python3 -m cbm.cli validate`.
- Boundary:
  - This verifies the current Codex CLI backend isolation property for parent-only token visibility; it does not prove cross-platform isolation or full runtime-agent quality.

## 2026-05-02 — Recovery slice: I-S2 skill-loader compatibility surface

- Implemented: added `cbm/skills.py` as the formal skill-loader compatibility module named by I-S2, wrapping the existing runtime `cbm.skill_loader` implementation.
- Implemented: exposed `SkillNotFoundError` and a dict-shaped `load_skill(name)` result with `name`, `path`, `sha256`, and `body`.
- Verification run:
  - Focused regressions passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_load_skill_returns_path_sha256_and_body tests/test_cli.py::test_load_skill_raises_skill_not_found_on_missing tests/test_cli.py::test_load_skill_is_pure tests/test_cli.py::test_run_backend_codex_cli_skill_mode_loads_skeptic_skill`.
  - Diff check passed: `git diff --check -- cbm/skills.py tests/test_cli.py BUILD-LOG.md`.
  - Full suite passed: `TMPDIR=/var/tmp pytest -q` reported 100 passed, 2 existing `jsonschema.RefResolver` deprecation warnings.
- Boundary:
  - Compatibility wrapper only; the runtime Codex backend continues to use `cbm.skill_loader`.

## 2026-05-02 — Recovery intervention completion audit

- Completed: all Tier 1 and Tier 5 R-OK interventions from `.planning/reviews/2026-05-02-opus-cross-vendor-audit/INTERVENTIONS.md` are implemented and committed.
- Updated: `.planning/STATE.md`, `.planning/CURRENT-PLAN.md`, and `.planning/phases/01-first-runtime-producer-evidence/` now record the completion boundary.
- Verification run:
  - `TMPDIR=/var/tmp pytest -q` reported 100 passed, 2 existing `jsonschema.RefResolver` deprecation warnings.
  - `python3 -m cbm.cli loop-status --repo . --scope recovery-slice --work-category runtime-producer --json` reported `status: ok`, no issues, and no warnings.
  - `python3 -m cbm.cli loop-status --repo . --scope broad-goal --work-category runtime-producer --json` reported `status: ok`, no issues, and no warnings.
  - `python3 -m cbm.cli loop-status --repo . --scope pass-claim --work-category runtime-producer --json` reported `status: fail` with `same_model_checkpoint`.
- Boundary:
  - The pass-claim failure is intentional. The next claim-level gate requires a non-current-model checkpoint disposition; this loop did not fabricate that review.

## 2026-05-02 — Governance slice: horizon ladder for autonomous `/goal`

- Implemented: added `.planning/HORIZONS.md` as the autonomous execution ladder between `VISION.md` and `/goal`.
- Corrected: planning docs now classify the current evidence as a runtime-producer/Skeptic slice, not the full `VISION.md` minimum-useful CBM floor.
- Implemented: `.planning/CURRENT-PLAN.md` now names `Current horizon: H1` and `Current stage: H1.S1`.
- Implemented: `AGENTS.md` now requires horizon/stage-bounded autonomous execution and classifies pushback as `bug`, `plan_gap`, `tooling_gap`, `vision_ambiguity`, or `out_of_scope`.
- Implemented: `cbm-loop-status` now blocks broad unattended scopes when `.planning/HORIZONS.md` is missing or `.planning/CURRENT-PLAN.md` points to an unknown/missing horizon stage.
- Verification run:
  - Focused regressions passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_loop_status_blocks_broad_goal_when_horizons_missing tests/test_cli.py::test_loop_status_blocks_broad_goal_when_current_plan_has_unknown_horizon tests/test_cli.py::test_loop_status_blocks_broad_goal_when_current_plan_lacks_stage tests/test_cli.py::test_loop_status_blocks_dirty_authority_docs_and_disallowed_work tests/test_cli.py::test_checkpoint_command_emits_packet_with_required_files` reported 5 passed, 2 existing `jsonschema.RefResolver` deprecation warnings.
  - Loop-status/checkpoint regression band passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py -k 'loop_status or checkpoint'` reported 19 passed, 84 deselected, 2 existing `jsonschema.RefResolver` deprecation warnings.
  - Full suite passed: `TMPDIR=/var/tmp pytest -q` reported 103 passed, 2 existing `jsonschema.RefResolver` deprecation warnings.
  - Diff check passed: `git diff --check -- .planning AGENTS.md README.md cbm/cli.py tests/test_cli.py docs/contracts.md BUILD-LOG.md`.
- Boundary:
  - This does not rewrite `VISION.md`; it adds an executable bridge and enforcement. H1.S1 remains the next implementation target.

## 2026-05-02 — H1.S1 real Surface Mapper producer

- Implemented: `cbm run --backend codex-cli` can now dispatch the Surface Mapper as `surface-mapper@1.2` with `--codex-surface-mode skill`.
- Implemented: parent-side Surface Mapper validation rejects baseline/dev-fixture producer identities, mismatched run/source metadata, zero direct-examination coverage, missing source citations, unresolved citations, missing substantive claims, and the missing `edge-unknown-001` handoff dependency.
- Implemented: Codex Surface Mapper output uses a strict outer response schema plus a parsed `surface_map_json` payload. If the first payload fails parent validation, the same producer gets one bounded repair pass with the concrete validation errors and rejected output.
- Implemented: `--codex-skeptic-mode none` keeps H1.S1 scoped to Surface Mapper evidence and leaves real Skeptic review for H1.S2.
- Live benchmark: `TMPDIR=/var/tmp python3 -m cbm.cli run --repo /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git --goal "produce real Surface Mapper map for MCP git server surfaces" --backend codex-cli --allow-live-codex --codex-surface-mode skill --codex-skeptic-mode none --codex-model gpt-5.4-mini --codex-reasoning-effort medium --mode lightweight --run-id run-mcp-git-surface-mapper-h1s1-6 --codex-timeout 600` exited 0.
- Evidence: `.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/RESULT.md` preserves the map, manifest, registry, handoff, goal binding, Codex output, ledger, codebase map, and extractor registry.
- Verification run:
  - Focused regressions passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_run_backend_codex_cli_skill_surface_writes_non_baseline_surface_map tests/test_cli.py::test_run_backend_codex_cli_skill_surface_rejects_baseline_producer`.
  - Surface artifact validation passed: `TMPDIR=/var/tmp python3 -m cbm.cli validate /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git/.research/run-mcp-git-surface-mapper-h1s1-6/surface-map.json --repo /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git`.
  - Citation resolution passed: `TMPDIR=/var/tmp python3 -m cbm.cli verify-citations /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git/.research/run-mcp-git-surface-mapper-h1s1-6/surface-map.json --repo /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git`.
  - Evidence validation passed: `TMPDIR=/var/tmp python3 -m cbm.cli check-evidence /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git/.research/run-mcp-git-surface-mapper-h1s1-6/surface-map.json --repo /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git`.
  - Manifest and handoff validation passed for the same run.
  - Diff check passed: `git diff --check -- cbm/cli.py tests/test_cli.py .planning BUILD-LOG.md`.
  - Full suite passed: `TMPDIR=/var/tmp pytest -q` reported 105 passed, 2 existing `jsonschema.RefResolver` deprecation warnings.
- Boundary:
  - H1.S1 is complete only. The run deliberately skipped real Skeptic review with `--codex-skeptic-mode none`; H1.S2 remains the next horizon stage.

## 2026-05-02 — Post-H1.S1 Opus review

- Ran: `claude --setting-sources project -p --model opus --effort max --tools Read,Bash --permission-mode dontAsk --output-format text < .planning/reviews/2026-05-02-h1s1-opus-review/PROMPT.md > .planning/reviews/2026-05-02-h1s1-opus-review/OUTPUT.md`.
- Note: `--setting-sources project` was required because the user-level Claude config file was corrupted and the CLI refused to start when loading it.
- Output verdict: `ACCEPT_WITH_BLOCKERS_FOR_NEXT_STAGE`.
- Disposition: accepted in `.planning/reviews/2026-05-02-h1s1-opus-review/DISPOSITION.md`.
- Accepted blockers before H1.S2:
  - fix handoff honesty for non-baseline Surface Mapper output;
  - omit or clearly label/count dev-fixture Skeptic fallback output;
  - replace the hard-coded `edge-unknown-001` producer requirement with unknown-edge lookup;
  - add repair-pass regressions and preserve `logs/` plus `codex_outputs/`;
  - preserve full live benchmark evidence or stop citing missing artifacts.
- Boundary:
  - H1.S1 remains accepted narrowly. H1.S2 live Skeptic work is blocked until the accepted remediation group is implemented and committed.

## 2026-05-07 — H1.S2a evidence-bundle repair

- Implemented: `cbm-handoff` now detects non-baseline `surface_map` artifacts as runtime Surface Mapper output, summarizes the runtime producer id plus authority/edge counts, derives handoff coverage and caveats from `surface-map.json`, and avoids Phase A-only body language for promoted runtime maps.
- Implemented: dev-fixture Skeptic fallback artifacts are no longer promoted in handoff `inputs`/`artifacts` and no longer increment `gate_summary.skeptic_review.artifacts_reviewed` when no real `skeptic@...` producer ran.
- Implemented: runtime Surface Mapper acceptance now requires any edge with `kind == "unknown"` instead of the literal `edge-unknown-001` id. The H1.S1 artifact may still contain that id, but acceptance logic no longer depends on it.
- Implemented: Surface Mapper repair passes preserve rejected output, repair prompt, repair output, attempt stdout/stderr, repair stdout/stderr, and additive `run-manifest.json` repair metadata for success and failure cases.
- Repaired evidence packet: `.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/handoff.md` now describes the promoted runtime map honestly and omits unavailable dev-fixture Skeptic evidence. `RESULT.md` records that the original publication did not preserve the full `.research/<run_id>/` tree, including `logs/` and `codex_outputs`; future runtime benchmark publication must preserve that tree or avoid citing unpreserved files.
- Decision: H1.S2a is a repair slice only. It does not run the live Skeptic and does not claim H1 complete, minimum-useful CBM complete, or Phase B+.
- Verification:
  - Red H1.S2a regression group initially failed on handoff summary/coverage/body language, dev-fixture review counting, literal unknown-edge id, and missing repair evidence.
  - Focused H1.S2a regression group passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_handoff_uses_runtime_surface_map_summary_for_nonbaseline_surface_producer tests/test_cli.py::test_handoff_uses_runtime_surface_map_coverage_for_nonbaseline_surface_producer tests/test_cli.py::test_handoff_body_does_not_describe_runtime_surface_map_as_phase_a_only tests/test_cli.py::test_handoff_does_not_count_dev_fixture_skeptic_as_real_review tests/test_cli.py::test_unknown_edge_requirement_accepts_any_kind_unknown tests/test_cli.py::test_unknown_edge_requirement_rejects_no_unknown_edges tests/test_cli.py::test_surface_mapper_repair_success_preserves_logs_and_codex_outputs tests/test_cli.py::test_surface_mapper_repair_failure_preserves_logs_and_codex_outputs`.
  - Nearby regression group passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_init_map_handoff_and_citation_resolution tests/test_cli.py::test_run_backend_codex_cli_skill_surface_writes_non_baseline_surface_map tests/test_cli.py::test_run_backend_codex_cli_skill_surface_rejects_baseline_producer tests/test_cli.py::test_standard_run_writes_verification_map tests/test_cli.py::test_package_schema_resources_match_root_schemas`.
  - Full suite passed: `TMPDIR=/var/tmp pytest -q` reported 113 passed, 2 existing `jsonschema.RefResolver` deprecation warnings.
  - Diff check passed: `git diff --check -- cbm tests .planning BUILD-LOG.md schemas`.
  - Pre-commit broad-goal loop-status failed only on `dirty_authority_docs`, as expected because `.planning/CURRENT-PLAN.md`, `.planning/HORIZONS.md`, and `.planning/STATE.md` were intentionally updated by this slice. Re-run after the atomic commit is required.

## 2026-05-07 — H1.S2b real isolated Skeptic production

- Implemented: `cbm run --backend codex-cli --codex-surface-mode existing --surface-artifact <path> --codex-skeptic-mode skill` can import an existing runtime Surface Mapper artifact, record its input path/hash in `run-manifest.json`, and launch `skeptic@1.2` over that artifact without remapping the target.
- Implemented: Codex CLI manifest entries now record the model output path in addition to the output hash.
- Live benchmark: `TMPDIR=/var/tmp python3 -m cbm.cli run --repo /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git --goal "review H1.S1 Surface Mapper map for MCP git server surfaces" --backend codex-cli --allow-live-codex --codex-surface-mode existing --surface-artifact /Users/rookslog/Development/cbm/.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/surface-map.json --codex-skeptic-mode skill --codex-model gpt-5.4-mini --codex-reasoning-effort high --mode lightweight --run-id run-mcp-git-h1s2b-skeptic-1 --codex-timeout 600` exited 0.
- Evidence: `.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/RESULT.md` preserves the full `.research/run-mcp-git-h1s2b-skeptic-1/` tree, including `logs/` and `codex_outputs/`, plus convenience copies of the review, manifest, registry, handoff, challenged surface map, and raw Codex output.
- Skeptic output: `skeptic@1.2` logged one interpretive challenge against `auth-001`, arguing that routing authority is distributed across `pyproject.toml`, `src/mcp_server_git/__main__.py`, and `src/mcp_server_git/__init__.py` rather than centered only on `__init__.py`.
- Manual support check: the cited lines substantively support the challenge. `pyproject.toml:25-26` declares the console entrypoint, `__main__.py:1-5` imports and calls `main`, and `__init__.py:7-24` defines the command callable that configures logging and calls `serve(repository)`.
- Prohibited-context check: search of the Skeptic review and raw model output for parent-session/prohibited-context terms found only the expected review title reference to Codex CLI, with no substantive parent-session leak signal.
- Boundary: H1.S2b only. This does not claim H1 complete, minimum-useful CBM complete, or Phase B+; H1.S2c mapper response/disposition remains next.
- Verification:
  - Red focused regression failed before implementation because `--codex-surface-mode existing` did not exist.
  - Focused regression passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_run_backend_codex_cli_skill_skeptic_reviews_existing_surface_artifact`.
  - Nearby regression group passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_run_backend_codex_cli_skill_skeptic_reviews_existing_surface_artifact tests/test_cli.py::test_run_backend_codex_cli_skill_mode_loads_skeptic_skill tests/test_cli.py::test_run_backend_codex_cli_skill_surface_writes_non_baseline_surface_map tests/test_cli.py::test_package_schema_resources_match_root_schemas`.
  - Input H1.S1 surface validation and citation resolution passed against the pinned target checkout.
  - Live Skeptic review validation, citation resolution, run-manifest validation, handoff validation, and challenged surface-map evidence validation all passed.
  - Preserved benchmark convenience copies validated for `skeptic-review-surface-map.md` and `run-manifest.json`.
  - Full suite passed: `TMPDIR=/var/tmp pytest -q` reported 114 passed, 2 existing `jsonschema.RefResolver` deprecation warnings.
  - Diff check passed: `git diff --check -- cbm tests .planning BUILD-LOG.md schemas`.
  - Pre-commit broad-goal loop-status failed only on `dirty_authority_docs`, as expected because `.planning/CURRENT-PLAN.md`, `.planning/HORIZONS.md`, and `.planning/STATE.md` were intentionally updated by this slice. Re-run after the atomic commit is required.

## 2026-05-07 — H1.S2c challenge disposition

- Implemented: real `skeptic@1.2` rendered review output now uses durable ingested challenge ids in the generated body and omits the smoke citation anchor for runtime skill Skeptic reviews. Raw model output under `codex_outputs/` remains untouched.
- Implemented: `respond-challenge` provides a narrow mapper-response path over the existing ledger-safe challenge resolver. It sets the challenge disposition, recomputes parent claim status, appends mapper response text to the claim rationale, and records a `challenge_resolved` ledger entry through the append-only integrity helper.
- Implemented: handoff contestation summary now counts only `open` challenges as open, while accepted alternatives remain live contestation and appear under `contested_claims`.
- H1.S2b cleanup: `.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/skeptic-review-surface-map.md` and the preserved `.research/.../skeptic-review/surface-map.md` now use `CHL-10001` in the rendered body and omit the smoke citation anchor; `handoff.md` now recommends disposition rather than another real Skeptic run.
- H1.S2c benchmark: `.planning/benchmarks/2026-05-07-mcp-git-h1s2c-disposition/RESULT.md` preserves the disposition packet. `auth-001.claim_status` is `contested`; `chl-10001.status` is `accepted_as_alternative`; handoff reports `open_challenges: 0`, `claims_by_status.contested: 1`, and H1.S3 as next action.
- Boundary: H1.S2c only. This does not claim H1 complete, minimum-useful CBM complete, or Phase B+; H1.S3 remains next.
- Verification:
  - Focused regression group passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_run_backend_codex_cli_skill_mode_loads_skeptic_skill tests/test_cli.py::test_run_backend_codex_cli_skill_skeptic_reviews_existing_surface_artifact tests/test_cli.py::test_respond_challenge_accepts_alternative_marks_claim_contested tests/test_cli.py::test_handoff_counts_accepted_alternative_as_contested_not_open`.
  - Disposition command passed: `TMPDIR=/var/tmp python3 -m cbm.cli respond-challenge .research/run-mcp-git-h1s2c-disposition-1/surface-map.json --repo /private/var/tmp/cbm-h1-mcp-servers-4503e2d/src/git --challenge-id chl-10001 --decision accepted_as_alternative --resolution "accepted_as_alternative: preserved original auth-001 reading and accepted distributed-routing reading as a live alternative" --response-note "accept chl-10001 as an alternative reading. __init__.py remains the shared command implementation, while launch/routing authority is also distributed across pyproject.toml and __main__.py." --resolved-by surface-mapper@1.2`.
  - Handoff regeneration passed: `TMPDIR=/var/tmp python3 -m cbm.cli handoff --repo /private/var/tmp/cbm-h1-mcp-servers-4503e2d/src/git --run-id run-mcp-git-h1s2c-disposition-1`.
  - Artifact validation/citation/evidence checks passed for `.planning/benchmarks/2026-05-07-mcp-git-h1s2c-disposition/surface-map.json` and `handoff.md` against `/private/var/tmp/cbm-h1-mcp-servers-4503e2d/src/git`.
  - Full suite passed: `TMPDIR=/var/tmp pytest -q` reported 116 passed, 2 existing `jsonschema.RefResolver` deprecation warnings.

## 2026-05-07 — H1.S3 minimum-useful handoff packet

- Prepared: `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/` with `HANDOFF.md`, `RESULT.md`, `VERIFY.md`, `LINEAGE.md`, `INCLUDED-ARTIFACTS.md`, `CHECKPOINT-PACKET.md`, `CHECKPOINT-PROMPT.md`, final `surface-map.json`, rendered `skeptic-review-surface-map.md`, source H1.S2c `handoff.md`, preserved `evidence-ledger.jsonl`, and source `.research/` run trees for H1.S1, H1.S2b, and H1.S2c.
- Prepared: `.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/` with `PROMPT.md`, `CHECKPOINT.md`, `DISPOSITION.md`, `EVIDENCE-MANIFEST.md`, and `STOP-NOTE.md`.
- Implemented: `cbm-loop-status` now selects the latest accepted checkpoint for `broad-goal`/`broad-goal-restart` resume gating while preserving the latest checkpoint for `pass-claim`. This lets a pending H1 pass-claim packet coexist with the prior accepted recovery checkpoint; pass-claim still fails until reviewer identity and accepted disposition are present.
- Resolved/documented H1.S3 preflight concerns:
  - final surface lineage is documented in `LINEAGE.md`;
  - historical smoke-anchor ledger entry `lg-00030` is documented and not promoted as H1.S3 evidence;
  - mixed run-id provenance on `lg-00029` is documented as H1.S2b challenging an imported H1.S1 map;
  - local verification evidence is recorded in `VERIFY.md`.
- Boundary: this prepares the H1 pass claim for non-current-model review. It does not claim H1 complete, minimum-useful CBM complete, Phase B+, repeatability, beta readiness, or broad product maturity. Reviewer identity, confidence, and disposition are intentionally pending.
- Verification:
  - Initial artifact validation attempt used relative artifact paths with `--repo /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git`; the CLI correctly looked under the target repo and raised `FileNotFoundError`. Re-run used absolute artifact paths.
  - H1.S3 handoff validation passed: `TMPDIR=/var/tmp python3 -m cbm.cli validate /Users/rookslog/Development/cbm/.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/HANDOFF.md --repo /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git`.
  - H1.S3 handoff citation resolution passed for `pyproject.toml:25-26@4503e2d12b79`, `src/mcp_server_git/__main__.py:1-5@4503e2d12b79`, and `src/mcp_server_git/__init__.py:7-24@4503e2d12b79`.
  - Final surface validation, citation resolution, and evidence check passed against `/var/tmp/cbm-h1-mcp-servers-4503e2d/src/git`.
  - Promoted Skeptic review and source H1.S2c handoff validation/citation checks passed.
  - Focused loop-status regression passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_loop_status_broad_goal_uses_prior_accepted_checkpoint_when_pass_claim_pending tests/test_cli.py::test_loop_status_blocks_incomplete_review_sessions_for_broad_goal tests/test_cli.py::test_loop_status_accepts_pass_claim_with_cross_model_reviewer` reported 3 passed, 2 warnings.
  - Full suite passed: `TMPDIR=/var/tmp pytest -q` reported 117 passed, 2 existing `jsonschema.RefResolver` deprecation warnings.
  - Diff check passed: `git diff --check -- .planning BUILD-LOG.md cbm tests schemas`.
  - Pre-commit broad-goal loop-status failed only on intentionally dirty planning docs.
  - Post-commit broad-goal loop-status passed with `status: ok`, no issues, and no warnings.
  - Post-commit pass-claim loop-status failed on expected `missing_reviewer_model_id` plus `checkpoint_pending`; this remains correct until a non-current-model reviewer fills and accepts the checkpoint.

## 2026-05-07 — H1.S3 checkpoint packet hardening audit

- Audited: post-H1.S3 packet and reusable CLI/test surfaces before non-current-model checkpoint submission.
- Fixed: generic handoff `recommended_next_action` text no longer embeds H1.S2b, H1.S3, or minimum-useful planning labels. Tests now assert the intended generic product-level wording for challenge disposition and validated-handoff/pass-claim review preparation.
- Clarified: H1.S3 `LINEAGE.md`, `INCLUDED-ARTIFACTS.md`, and `RESULT.md` now state that preserved `codex_outputs/` and `logs/` are source-stage H1.S1/H1.S2b/H1.S2c audit evidence, not newly produced H1.S3 live model output.
- Confirmed: final H1 surface state, historical smoke-anchor ledger caveat, mixed run-id ledger caveat, and pending checkpoint boundary were already documented and were not rewritten.
- Boundary: no H1 completion, minimum-useful-CBM completion, Phase B+, repeatability, beta readiness, or H2 readiness claim is made. The non-current-model checkpoint review remains pending.
- Verification:
  - Focused handoff regressions passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_run_backend_codex_cli_skill_skeptic_reviews_existing_surface_artifact tests/test_cli.py::test_handoff_counts_accepted_alternative_as_contested_not_open` reported 2 passed, 2 warnings.
  - Full suite passed: `TMPDIR=/var/tmp pytest -q` reported 117 passed, 2 warnings.
  - Diff check passed: `git diff --check -- .planning BUILD-LOG.md cbm tests schemas`.
  - Broad-goal loop-status passed with `status: ok`, no issues, and no warnings.
  - Pass-claim loop-status failed as expected on `missing_reviewer_model_id` with `checkpoint_pending`; reviewer fields remain intentionally blank.

## 2026-05-07 — Handoff next-action enum

- Implemented: `handoff` artifacts now include optional `recommended_next_action_kind` so the machine-readable next state is separate from human prose.
- Schema: added optional enum field to both `schemas/handoff.schema.json` and packaged `cbm/schemas/handoff.schema.json`; `schema_version` remains `1.2` because the change is additive and not required.
- Enum values: `run_skeptic_review`, `respond_to_open_challenges`, `prepare_pass_claim_review`, and `review_handoff`.
- Generation: `cbm handoff` computes the enum first, then renders generic prose from that enum. The resolved-Skeptic-challenge count is passed explicitly from gate summary state.
- Tests: added direct mapping coverage for all enum states and updated handoff tests to assert `recommended_next_action_kind` for no-real-Skeptic, open-challenge, and carried-contestation paths. Prose assertions remain narrow exact checks for the two intentionally stable generic strings.
- H1.S3 packet: current `HANDOFF.md` now includes `recommended_next_action_kind: prepare_pass_claim_review`; historical source handoff copies were not mass-rewritten.
- Boundary: no H1 completion, minimum-useful-CBM completion, Phase B+, repeatability, beta readiness, or H2 readiness claim is made. The non-current-model checkpoint review remains pending.
- Verification:
  - Schema parity and focused handoff tests passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_package_schema_resources_match_root_schemas tests/test_cli.py::test_recommended_handoff_next_action_kind_mapping tests/test_cli.py::test_recommended_handoff_next_action_prose_is_rendered_from_kind tests/test_cli.py::test_handoff_does_not_count_dev_fixture_skeptic_as_real_review tests/test_cli.py::test_run_backend_codex_cli_skill_skeptic_reviews_existing_surface_artifact tests/test_cli.py::test_handoff_counts_accepted_alternative_as_contested_not_open` reported 6 passed, 2 warnings.
  - Updated H1.S3 `HANDOFF.md` validation passed against `/var/tmp/cbm-h1-mcp-servers-4503e2d/src/git`.
  - Full suite passed: `TMPDIR=/var/tmp pytest -q` reported 119 passed, 2 warnings.
  - Diff check passed: `git diff --check -- cbm tests schemas .planning BUILD-LOG.md`.
  - Broad-goal loop-status passed with `status: ok`, no issues, and no warnings.

## 2026-05-08 — Handoff next-action runtime-surface state correction

- Fixed: `recommended_handoff_next_action_kind` now treats missing promoted runtime Surface Mapper evidence as the first state-machine branch instead of recommending Skeptic review for baseline-only handoffs.
- Schema: added optional enum value `produce_runtime_surface_evidence` to both root and packaged handoff schemas; `schema_version` remains unchanged because this is an additive optional enum expansion.
- Boundary: no H1.S3 packet rewrite, checkpoint review, pass claim, or phase status change.
- Verification:
  - Schema parity and focused handoff tests passed: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_package_schema_resources_match_root_schemas tests/test_cli.py::test_recommended_handoff_next_action_kind_mapping tests/test_cli.py::test_recommended_handoff_next_action_prose_is_rendered_from_kind tests/test_cli.py::test_init_map_handoff_and_citation_resolution tests/test_cli.py::test_handoff_does_not_count_dev_fixture_skeptic_as_real_review tests/test_cli.py::test_run_backend_codex_cli_skill_skeptic_reviews_existing_surface_artifact tests/test_cli.py::test_handoff_counts_accepted_alternative_as_contested_not_open` reported 7 passed, 2 warnings.
  - Full suite passed: `TMPDIR=/var/tmp pytest -q` reported 119 passed, 2 warnings.
  - Diff check passed: `git diff --check -- cbm tests schemas .planning BUILD-LOG.md`.
  - Broad-goal loop-status passed with `status: ok`, no issues, and no warnings.

## 2026-05-08 — Generic cross-vendor review skill

- Spiked: Claude Code CLI `2.1.126` can run non-interactive review packets, write declared outputs directly, emit stream-json with session/model/usage/cost metadata, and resume explicitly by session name. Result recorded at `.planning/spikes/2026-05-07-claude-code-review-runner/RESULT.md`.
- Implemented: repo-local `cross-vendor-review` skill under `.codex/skills/cross-vendor-review/` with valid skill frontmatter, progressive-disclosure instructions, generic review-spec contract, Claude Code runbook, failure-mode catalogue, preflight/run/verify/recover scripts, and focused fake-run tests.
- Adjusted: default runner command omits hard `--max-turns` and `--max-budget-usd`; those remain explicit spec overrides/failure classifications only. Default permission mode is `auto` with `Read,Write,Edit,Bash` so real reviews can inspect code and run local commands while post-run verification enforces declared outputs and allowed write roots.
- Clarified: review types are open labels, not a closed ontology. The runner supports checkpoint, architecture/design, provenance/artifact, code/diff, and future review types through `REVIEW-SPEC.md` and `PROMPT.md` without hard-coding H1, Phase 01, CBM pass-claim, or minimum-useful semantics.
- Added: `AGENTS.md` pointer requiring cross-vendor/non-current-model reviews to use the repo-local skill and recovery workflow rather than chat-only execution.
- Boundary: did not run the H1 checkpoint review, fill reviewer identity/confidence/disposition, mark H1 complete, move to H2, inspect undocumented Claude session storage, use `--continue`, or use `--dangerously-skip-permissions`.
- Verification:
  - Skill frontmatter parsed successfully with required `name` and `description`.
  - Script syntax/compile checks passed: `bash -n .codex/skills/cross-vendor-review/scripts/*.sh` and `python3 -m py_compile .codex/skills/cross-vendor-review/scripts/*.py`.
  - Focused fake-run suite passed: `TMPDIR=/var/tmp pytest -q tests/test_cross_vendor_review_skill.py` reported 9 passed.
  - Diff check passed: `git diff --check -- .codex .planning AGENTS.md BUILD-LOG.md tests`.
  - Pre-commit broad-goal loop-status failed only on expected dirty authority docs: `AGENTS.md` is modified by this slice. Post-commit loop-status must be rerun.

## 2026-05-08 — H1 checkpoint review recovery state

- Added: `.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/REVIEW-SPEC.md` so the repo-local cross-vendor review runner had a declared pass-claim checkpoint contract.
- Ran: `.codex/skills/cross-vendor-review/scripts/run-claude-code-review.sh .planning/reviews/2026-05-07-h1-minimum-useful-checkpoint`.
- Result: Claude Code completed with exit code 0 as observed model `claude-opus-4-7`, session `b6cbc7cf-fde2-43ca-881c-5166caea7a38`, and reviewer-written `CHECKPOINT.md` / `DISPOSITION.md`.
- Recovery: the generic verifier exited 1 because `DISPOSITION.md` lacks the exact `disposition: <value>` field expected by `verify-review-output.sh`; the runner wrote `RECOVERY.md` and preserved raw logs under `.xvr-runs/xvr-20260508T023055Z-10836/`.
- Boundary: no dev-agent edits were made to reviewer identity, confidence, checkpoint findings, or disposition. No follow-up paid Claude resume/rerun was launched. H1 remains active because the required runner success and pass-claim loop-status gate have not both passed.
- Verification:
  - `REVIEW-SPEC.md` parsed with PyYAML and declared `CHECKPOINT.md` / `DISPOSITION.md`.
  - The wrapper's `REVIEW-RUN.json` records `status: failed`, `requested_model: opus`, `observed_model: claude-opus-4-7`, `exit_code: 0`, and `verification_exit_code: 1`.
  - The wrapper's `VERIFY.json` records one issue: `invalid_disposition` with detail `missing disposition field`.

## 2026-05-08 — Structured disposition envelope and H1 closure

- Added: deterministic `DISPOSITION.json` support for cross-vendor review gates. The structured envelope records only gate-level machine facts: reviewer model identity, same-model fallback flag, accepted disposition, and optional gate-level confidence if provided. Nuanced confidence, caveats, and finding-level judgment remain in `CHECKPOINT.md` / `DISPOSITION.md`.
- Added: `.codex/skills/cross-vendor-review/scripts/write-disposition.py` to write the structured envelope after a reviewer has actually supplied the decision facts.
- Updated: cross-vendor verification and `cbm-loop-status` read `DISPOSITION.json` first while preserving legacy Markdown metadata fallback.
- Resolved: H1 checkpoint verifier now passes for preserved run `xvr-20260508T023055Z-10836` without a Claude rerun. `DISPOSITION.json` records reviewer model `claude-opus-4-7` and disposition `accept`.
- Closed: H1 and Phase 01 are complete for one pinned external target. Next focus is H2 repeatability planning only.
- Boundary: this is not Phase B+, repeatability, beta readiness, mature orchestration, or H2 execution.
- Verification:
  - Script checks passed: `python3 -m py_compile .codex/skills/cross-vendor-review/scripts/*.py` and `bash -n .codex/skills/cross-vendor-review/scripts/*.sh`.
  - Focused tests passed: `TMPDIR=/var/tmp pytest -q tests/test_cross_vendor_review_skill.py tests/test_cli.py::test_loop_status_accepts_pass_claim_with_structured_disposition_json tests/test_cli.py::test_loop_status_accepts_pass_claim_with_cross_model_reviewer tests/test_cli.py::test_loop_status_pass_claim_blocked_until_cross_model_disposition tests/test_cli.py::test_loop_status_broad_goal_uses_prior_accepted_checkpoint_when_pass_claim_pending tests/test_cli.py::test_checkpoint_command_emits_packet_with_required_files` reported 16 passed, 2 warnings.
  - Focused integration regression passed after preserving the separate broad-goal resume gate: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_loop_status_blocks_broad_goal_until_checkpoint_satisfies_resume tests/test_cli.py::test_loop_status_accepts_pass_claim_with_structured_disposition_json tests/test_cross_vendor_review_skill.py` reported 13 passed, 2 warnings.
  - Full suite passed: `TMPDIR=/var/tmp pytest -q` reported 131 passed, 2 warnings.
  - Diff check passed: `git diff --check -- .codex cbm tests`.
  - H1 review verifier passed: `.codex/skills/cross-vendor-review/scripts/verify-review-output.sh .planning/reviews/2026-05-07-h1-minimum-useful-checkpoint xvr-20260508T023055Z-10836` exited 0.
  - Loop status passed: `python3 -m cbm.cli loop-status --repo . --scope broad-goal --work-category runtime-producer --json` and `python3 -m cbm.cli loop-status --repo . --scope pass-claim --work-category runtime-producer --json` both reported `status: ok`.

## 2026-05-15 — PR #1 review remediation: checkpoint scope match and DISPOSITION template vocabulary

- Context: Codex inline review on PR #1 surfaced four findings against the H1 close branch. The P1 finding (`cbm/cli.py:5640`) named a real gate hole: `checkpoint_pass_claim_issues` reads reviewer/disposition from checkpoint metadata but never compares the checkpoint's recorded `scope` against the requested gate scope. A recovery-slice checkpoint with cross-model reviewer + `disposition: accept` therefore satisfied pass-claim gate requests, undermining ADR-005. The P2 finding at `cbm/cli.py:5628` named a real reader/writer vocabulary drift: the generated `DISPOSITION.md` template prompted the reviewer to fill `Decision:`, but `markdown_metadata` only allowlists `disposition`, `reviewer_model_id`, `same_model_fallback`, `status`, and `satisfies_resume_gate` — a reviewer following the template would set `Decision: accept` and the gate would still read no disposition.
- Implemented:
  - Added a `checkpoint_scope_mismatch` issue in `checkpoint_pass_claim_issues` (`cbm/cli.py`) that fires when `scope == "pass-claim"` and the checkpoint metadata's `scope` field is anything other than `pass-claim`.
  - Added `"scope"` to the body-line allowlist in `markdown_metadata` so checkpoints with body-line metadata (as in test fixtures and in the live H1 packet) can carry scope consistently with frontmatter form.
  - Changed the generated `DISPOSITION.md` template body from `Decision:` to `Disposition:` so a reviewer who fills the template lands a field name the gate parses.
  - Updated `AGENTS.md:24` to point at `cbm/schemas/*.json` as the authoritative tree and note that `schemas/` mirrors it under pytest-enforced identity (`test_package_schema_resources_match_root_schemas`).
  - Added a `_documentation` field to `cbm/loop_status_config.json` clarifying that `current_dev_agent_model_families` lists runtime-producer families, not build-agent families. The loader ignores keys it does not consume, so the doc field is inert at runtime.
- Tests:
  - New: `tests/test_cli.py::test_loop_status_blocks_pass_claim_when_checkpoint_scope_is_recovery_slice` asserts the F3 gate fix (recovery-slice checkpoint with cross-model reviewer + accept disposition fails the pass-claim gate).
  - New: `tests/test_cli.py::test_loop_status_blocks_pass_claim_when_checkpoint_scope_is_unset` asserts a checkpoint with no `scope` field also fails the pass-claim gate.
  - New: `tests/test_cli.py::test_checkpoint_command_disposition_template_uses_disposition_field` asserts the generated `DISPOSITION.md` contains `Disposition:` and does NOT contain `Decision:`.
  - Updated: `test_loop_status_accepts_pass_claim_with_cross_model_reviewer`, `test_loop_status_accepts_pass_claim_with_structured_disposition_json`, and `test_loop_status_pass_claim_blocked_until_cross_model_disposition` now set `scope: pass-claim` in checkpoint bodies, which is the new precondition for clearing the pass-claim gate.
- Deferred (separate follow-up slice; not blocking PR #1 merge):
  - F2 (`cbm/cli.py:2655`): runtime Skeptic ingestion appends `claim_challenged` ledger entries before validating the post-mutation artifact. Failure mode requires a validation failure on a partially mutated artifact; the H1 evidence path never triggers it.
  - F4 (`cbm/cli.py:4867`): baseline handoff appends ledger and uncertainty entries before checking that the surface map has an `unknown` edge and passes schema/evidence validation. Failure mode is the same class as F2.
  - W2 forward-looking concern: model-families config is correct for the H1 runtime-producer claim; only matters if pass-claim scope is later extended to gate code-change PRs reviewed by Claude.
  - W1: dual schema tree at `schemas/` and `cbm/schemas/`. The existing `test_package_schema_resources_match_root_schemas` test enforces identity, so divergence cannot silently merge; the consolidation is a contributor-clarity cleanup, not a correctness gap.
- Boundary: this is PR-review remediation against PR #1 in scope, not a new horizon stage. CURRENT-PLAN.md remains on H2.S1 (repeatability planning); no horizon claim is advanced or retired here. F3 and F1 fit the "narrow verifier/tooling fixes required to keep the H2 plan executable" category in CURRENT-PLAN.md:81-88.
- Verification:
  - Focused regressions: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_loop_status_blocks_pass_claim_with_missing_reviewer_model_id tests/test_cli.py::test_loop_status_blocks_pass_claim_with_same_model_reviewer tests/test_cli.py::test_loop_status_accepts_pass_claim_with_cross_model_reviewer tests/test_cli.py::test_loop_status_blocks_pass_claim_when_checkpoint_scope_is_recovery_slice tests/test_cli.py::test_loop_status_blocks_pass_claim_when_checkpoint_scope_is_unset tests/test_cli.py::test_loop_status_accepts_pass_claim_with_structured_disposition_json tests/test_cli.py::test_loop_status_recovery_slice_tolerates_labeled_same_model_fallback tests/test_cli.py::test_loop_status_pass_claim_blocked_until_cross_model_disposition tests/test_cli.py::test_checkpoint_command_emits_packet_with_required_files tests/test_cli.py::test_checkpoint_command_disposition_template_uses_disposition_field` reported 10 passed, 2 warnings.
  - Full suite passed: `TMPDIR=/var/tmp pytest -q` reported 134 passed, 2 warnings.
  - Loop-status after staging (pre-commit): `python3 -m cbm.cli loop-status --repo . --scope pass-claim --work-category runtime-producer --json` issued only `dirty_authority_docs` for the in-flight AGENTS.md edit; checkpoint scope-match passed on the H1 packet.

## 2026-05-15 — PR #1 review remediation pass 2: W-NEW-1 main-merge/broad-goal-restart parity and S-NEW-1 frontmatter guard

- Context: Claude survey on PR #1 (running at default effort on the OLD caller stub from main, before PR #10 landed the workflow uplift to main) caught a net-new P1: the F3 fix earlier this day extended `checkpoint_pass_claim_issues` to require cross-model reviewer + scope-match — but only for `--scope pass-claim`. Per ADR-005 and AGENTS.md:34, `main-merge` and `broad-goal-restart` also require cross-model checkpoints; they were silently passing through `checkpoint_satisfies_resume` alone. The earlier F3 fix was therefore too narrow. Survey also caught S-NEW-1: `markdown_metadata` unpacks `text.split("---", 2)` as a 3-tuple, which raises `ValueError` on a truncated frontmatter (no closing `---`).
- Implemented:
  - Introduced `SCOPES_REQUIRING_CROSS_MODEL = {"pass-claim", "main-merge", "broad-goal-restart"}` in `cbm/cli.py`. Extended `checkpoint_pass_claim_issues` so its same-model check, scope-match check, and disposition-accept check all fire for any scope in the set, with the scope-match message and disposition-not-accepted message templated against the requested scope. Updated `command_loop_status` to dispatch `checkpoint_pass_claim_issues` for all three scopes (previously only `pass-claim`).
  - Guarded `markdown_metadata` against truncated frontmatter: `text.split("---", 2)` is now checked for `len(parts) == 3` before unpacking; partial frontmatter no longer raises and falls through to the body-line allowlist parser, which is the existing safety net.
- Tests added (`tests/test_cli.py`):
  - `test_loop_status_blocks_main_merge_with_same_model_reviewer`
  - `test_loop_status_blocks_main_merge_when_checkpoint_scope_is_pass_claim` (a pass-claim checkpoint must not clear a main-merge gate)
  - `test_loop_status_accepts_main_merge_with_matching_scope_and_cross_model`
  - `test_loop_status_blocks_broad_goal_restart_with_same_model_reviewer`
  - `test_loop_status_accepts_broad_goal_restart_with_matching_scope_and_cross_model`
  - `test_markdown_metadata_handles_truncated_frontmatter`
- Verification:
  - Focused suite: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_loop_status_blocks_main_merge_* tests/test_cli.py::test_loop_status_accepts_main_merge_* tests/test_cli.py::test_loop_status_blocks_broad_goal_restart_* tests/test_cli.py::test_loop_status_accepts_broad_goal_restart_* tests/test_cli.py::test_markdown_metadata_handles_truncated_frontmatter` reported 6 passed, 2 warnings.
  - Full suite: `TMPDIR=/var/tmp pytest -q` reported 140 passed, 2 warnings.
  - `python3 -m cbm.cli loop-status --repo . --scope pass-claim --work-category runtime-producer --json` returned `status: ok` on the H1 checkpoint.
- Boundary:
  - Workflow-only review-discovery iteration, not a horizon advance. CURRENT-PLAN.md remains on H2.S1.
  - W-NEW-2 (`DEFAULT_CODEX_CLI_MODEL = "gpt-5.4-mini"` plausibility) deferred — live regressions exercise this default and pass; no current evidence of breakage. Will revisit if a Codex live run begins failing model selection.

## 2026-05-15 — PR #1 review remediation pass 3: W-OP-1 selector parity for cross-model scopes + S-OP-1 dedup + ADR-005 vocab clarification

- Context: `@claude opus cbm/cli.py` at Opus 4.7 / effort=max caught a P1 (W-OP-1) that the W-NEW-1 fix earlier this day introduced as a regression. The W-NEW-1 fix made the checkpoint's declared scope load-bearing in `checkpoint_pass_claim_issues` (scope-mismatch is a returned issue), but `checkpoint_for_loop_scope` still selected checkpoints by mtime alone for cross-model scopes. In a multi-checkpoint repo, a newer-mtime checkpoint with a different scope would shadow a valid scope-matching checkpoint and the gate would emit a spurious `checkpoint_scope_mismatch`. Same class of bug as F3 (gate vs reader/writer drift), one layer up.
- Opus also raised P2 W-OP-2 (ADR-005 says "minimum-useful-CBM" but code uses "broad-goal-restart"; this is vocabulary drift between the ADR claim-type taxonomy and the implementation's scope-id taxonomy) and P3 S-OP-1 (duplicate `missing_checkpoint` issue emission for new cross-model scopes when the checkpoint is absent).
- Implemented:
  - Extended `checkpoint_for_loop_scope` to filter by declared scope for any scope in `SCOPES_REQUIRING_CROSS_MODEL`. The selector now iterates checkpoints (newest mtime first) and returns the first whose declared scope matches the requested gate scope. If no match is found, falls through to the existing `checkpoints[0]` fallback so the gate emits `checkpoint_scope_mismatch` (specific) rather than `missing_checkpoint` (generic) — preserves the existing error vocabulary.
  - Guarded the `checkpoint_pass_claim_issues` call in `command_loop_status` against the `checkpoint_path is None` case so the dispatcher does not emit `missing_checkpoint` twice when a missing checkpoint is also a cross-model scope.
  - Updated ADR-005 to record the mapping: minimum-useful-CBM claim is gated under `pass-claim` scope in the implementation; `SCOPES_REQUIRING_CROSS_MODEL = {"pass-claim", "main-merge", "broad-goal-restart"}` in `cbm/cli.py`; the selector now filters by scope so a newer checkpoint for a different scope does not shadow a valid scope-matching one.
- Tests added:
  - `test_loop_status_selects_scope_matching_checkpoint_when_newer_mismatched_exists` writes a valid main-merge checkpoint and a newer pass-claim checkpoint to separate review directories; asserts both `--scope main-merge` and `--scope pass-claim` return `status: ok` (each picks the scope-matching checkpoint).
- Deferred:
  - Opus S-OP-2 (mkdir before reviewer validation): low confidence; minor cleanup; defer.
  - Opus S-OP-3 (substring-match disposition in `checkpoint_satisfies_resume`): low impact; only affects `--scope broad-goal` which is the lightest scope; defer.
  - Gates W1-W4 + S1-S6 (10 findings on `.codex/skills/cross-vendor-review/scripts/`): all real; bundled into a separate follow-up slice (post-PR-#1 merge). Most load-bearing items are W3 (preflight/verify checkpointish drift, same class as F1) and W4 (model-identity cross-check between observed_model and reviewer_model_id). Both 2-line fixes.
- Verification:
  - Focused: `TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_loop_status_selects_scope_matching_checkpoint_when_newer_mismatched_exists tests/test_cli.py::test_loop_status_blocks_main_merge_when_checkpoint_scope_is_pass_claim tests/test_cli.py::test_loop_status_blocks_pass_claim_when_checkpoint_scope_is_recovery_slice tests/test_cli.py::test_loop_status_accepts_pass_claim_with_cross_model_reviewer` reported 4 passed, 2 warnings.
  - Full suite: `TMPDIR=/var/tmp pytest -q` reported 141 passed, 2 warnings.
  - `python3 -m cbm.cli loop-status --scope pass-claim --work-category runtime-producer --json` returns `status: ok` on the H1 checkpoint.
- Boundary:
  - This regression and the workflow-uplift cycle that surfaced it are review-discovery iterations on PR #1, not a horizon advance.
  - The fix scope-matches the H1 checkpoint correctly: H1 packet declares `scope: pass-claim`, gate request is `--scope pass-claim`, selector picks the H1 packet, gate passes.
