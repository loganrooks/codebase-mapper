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
