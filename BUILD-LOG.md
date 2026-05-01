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
