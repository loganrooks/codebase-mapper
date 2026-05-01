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
