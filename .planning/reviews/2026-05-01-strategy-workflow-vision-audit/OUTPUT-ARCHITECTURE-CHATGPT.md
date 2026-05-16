# Architecture and Product Shape Review

## Executive verdict

CBM should be treated as a **verifiable codebase-mapping artifact system**, not as a hook framework, not as a general autonomous coding agent, and not as a purely deterministic code-indexer.

The durable product boundary is:

> Given a target repository, a pinned revision, a user goal, and an execution mode, CBM produces a run bundle of schema-validated, citation-backed artifacts that another human or agent can safely consume to understand the codebase and plan interventions.

The current implementation has a valuable deterministic kernel: inventory, static extraction, schemas, citations, ledgers, staleness, freshness, refresh, gates, goal binding, and artifact production. That kernel should be preserved. The current implementation does **not** yet demonstrate the runtime-agent layer that the product shape implies: direct examination of files by role-specific agents, qualitative mapping, alternative readings, and independent Skeptic review beyond deterministic scaffolding.

The next architectural decision should be made before more implementation is added:

> Decide whether `cbm run` is the full product runner that owns runtime-agent orchestration, or whether CBM is the artifact/gate kernel used by an outer agent. My recommendation is to choose the second as the immediate architecture and the first as a future backend-backed product mode: outer agents orchestrate now; CBM owns artifacts, schemas, gates, and run validation; later `cbm run --backend codex|claude|external` can launch runtime producers once the backend contract is proven.

Concretely: stop expanding deterministic feature surface until the run contract, producer boundary, artifact manifest, and platform-adapter boundary are settled.

## Observed facts

These observations are from the branch available for review, especially `SHARED-CONTEXT.md`, planning files, docs, implementation files, tests, and platform adapter docs.

1. `SHARED-CONTEXT.md` for the active review is under `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/`, not at repo root. It frames CBM as an intended epistemic instrument for mapping unfamiliar codebases and warns reviewers not to ratify the current agent’s diagnosis.

2. `README.md` still describes the repository as a seed kit, not the finished system. It says the kit provides contracts, prompts, and architectural commitments used to build the system. It also states the intended system output: intervention cards or research-only findings cards whose claims cite real bytes at a real revision and carry factual, inferential, or interpretive claim registers.

3. `AGENTS.md` now draws a useful level distinction: the builder agent produces an implementation; runtime CBM agents produce intervention cards. It also explicitly warns not to describe the current `cbm run` as a full agent orchestrator unless it actually launches and coordinates runtime agents.

4. `.planning/STATE.md` states that the project is in a mixed kernel build beyond Phase A, with many deterministic features implemented, but without production-grade runtime agent orchestration. `.planning/CURRENT-PLAN.md` similarly identifies the immediate objective as correcting the boundary between deterministic kernel, runtime agent producers, validation gates, and optional platform hooks/adapters.

5. `docs/architecture.md` defines the intended architecture as three tiers: deterministic kernel, agentic synthesis, and goal packs. It also says hooks enforce phase prerequisites at the platform layer, which is now in tension with later planning docs that demote hooks from product core to adapter glue.

6. `docs/contracts.md` defines the citation format, universal artifact frontmatter, CLI command catalog, artifact catalog, claim-evidence requirements, append-only artifacts, artifact and claim lifecycles, and hook integration points. This is close to a real consumer contract, but it is scattered across artifact schemas, CLI contracts, and hook notes rather than expressed as a single “how another project consumes CBM” interface.

7. `pyproject.toml` exposes a broad command surface: `cbm`, `cbm-init`, `cbm-map`, `cbm-surface`, `cbm-authority-map`, `cbm-dependency-graph`, `cbm-verify-map`, `cbm-synthesis-index`, `cbm-skeptic-review`, `cbm-bind`, `cbm-trace-workflows`, `cbm-refine`, `cbm-approval-plan`, `cbm-run-gate`, `cbm-run`, `cbm-hook-start`, and `cbm-hook-stop`, among others. This is much broader than the original MVP described in `docs/roadmap.md`.

8. `tests/test_cli.py` demonstrates that `cbm run` currently orchestrates deterministic phases and, in standard mode, writes artifacts such as `authority-map.json`, `dependency-graph.json`, `verification-map.json`, `synthesis-index.json`, and deterministic skeptic-review files. The tests verify contract shape and gating behavior, not real runtime-agent comprehension.

9. `platform/PORTABILITY.md` states that the kernel, schemas, skills, artifact layout, citation format, and validation/freshness/ledger checks are platform-neutral. It assigns hook syntax, subagent definition/spawn syntax, orchestrator entry, and environment setup to platform adapters.

10. `platform/codex/README.md` says the current CLI uses deterministic commands for mapper, skeptic, tracer, planner, and approval-plan boundaries, and that actual Codex subagent spawning remains platform glue that must preserve artifact contracts.

11. `.codex/hooks.json` configures only `SessionStart` and `Stop` hooks. A separate `platform/codex/gate-artifact.sh` exists for post-artifact-write gating, but it is not registered in the live `.codex/hooks.json` shown in this branch.

12. `platform/claude-code/README.md` is honest that Claude Code hook/subagent syntax is not verified and belongs in that adapter only once checked against current platform documentation.

13. The branch references `VISION.md` and `RUNTIME-CONSTITUTION.md` as authoritative in `AGENTS.md` and `SHARED-CONTEXT.md`, but those files were not fetchable at repo root through the reviewed branch. If they exist only in an uncommitted local tree, the committed architecture is depending on absent authority documents.

14. There is visible version drift: `README.md` describes schema version 1.1, while the implementation uses `SCHEMA_VERSION = "1.2"` and later build-log/planning language refers to v1.2-style capabilities. That drift is manageable, but it should not remain ambiguous while defining the product contract.

15. The tests use a tiny fixture repository. That is appropriate for schema and CLI regression, but not sufficient evidence that CBM can map a non-trivial unfamiliar codebase.

## Architecture options

### Option 1 — CLI-only deterministic pipeline

CBM remains a deterministic CLI suite. `cbm run` means run mechanical extractors, produce maps, run validations, and emit a low-confidence handoff.

**Strengths**

- Most reliable and testable.
- Easy to package, run locally, and port across platforms.
- Keeps hallucination out of structural claims.
- Strong fit for CI-style artifact validation and refresh.

**Weaknesses**

- Does not satisfy the product vision of nuanced codebase understanding.
- Cannot legitimately produce interpretive claims about file roles unless some actor actually reads the files.
- Risks becoming a code-indexing tool with elaborate epistemic packaging.
- The current deterministic Skeptic and Tracer names become misleading.

**Disposition**

Useful as a kernel and as a `--backend deterministic` or `cbm baseline` mode. Not sufficient as the product architecture.

### Option 2 — CLI launches Codex/Claude subprocess agents

`cbm run` becomes a parent controller. It creates the run directory, pins the SHA, runs the deterministic baseline, launches Codex or Claude subprocesses with role prompts and output schemas, validates each produced artifact, and assembles handoff.

**Strengths**

- Makes CBM a self-contained product runner.
- Gives `cbm run` the intuitive meaning users expect.
- Parent-side validation can keep the runtime agent layer honest.
- Platform adapters have a clear job: spawn syntax, hook syntax, environment setup.

**Weaknesses**

- Backend behavior may be brittle and platform-specific.
- Codex/Claude subprocess invocation, profile/config isolation, output-schema enforcement, and tool permissions need verification.
- If implemented too soon, it may bake Codex-specific assumptions into the kernel.
- More expensive to test than deterministic commands.

**Disposition**

Good long-term direction, but should be reached through a narrow backend spike, not assumed.

### Option 3 — Outer agent orchestrates CBM subagents; CBM CLI is artifact/gate kernel

The user’s outer Codex `/goal` loop or another orchestrator runs the runtime agents. CBM supplies the deterministic baseline, artifact schemas, validation gates, run directories, skills, and handoff assembly. Runtime agents write artifacts to disk; CBM validates them.

**Strengths**

- Matches the current working reality.
- Highly reversible.
- Avoids premature commitment to Codex or Claude subprocess details.
- Keeps product correctness in CBM artifacts/gates, not in ambient hooks.
- Allows independent reviews to use the same artifacts.

**Weaknesses**

- CBM is not yet a fully self-contained product for another project.
- Different outer agents may orchestrate inconsistently.
- The user must understand that `cbm run` is not yet the whole runtime.
- More discipline is needed around artifact writes and validation between agent steps.

**Disposition**

Best immediate architecture. It should be made explicit and honest, not treated as an accidental transitional state.

### Option 4 — Hybrid deterministic baseline plus runtime-agent backend

CBM has a stable kernel and a pluggable producer backend. Backends can be `deterministic`, `external`, `codex`, `claude`, or later `mcp/server`. `cbm run` owns the lifecycle, but each producer declares which artifacts it can produce and how validation is enforced.

**Strengths**

- Preserves the kernel while allowing runtime-agent depth.
- Gives a future path from outer-agent orchestration to self-contained product.
- Backend-independent validation remains the source of truth.
- Enables portability without pretending all platforms are equivalent.

**Weaknesses**

- Requires a clean producer contract.
- Risks abstraction overhead before one real backend is proven.
- Needs clear semantics for incomplete or deterministic-only runs.

**Disposition**

Best target architecture. Implement only after the immediate product boundary is documented.

### Option 5 — CBM as local MCP/artifact service

CBM exposes a local service or MCP server. Other agents request mapping, status, artifact reads, consultation, and validation through tools instead of raw CLI commands.

**Strengths**

- Most natural interface for “another agent asks CBM for codebase mapping information.”
- Can hide run-directory details while preserving artifact contracts.
- Supports multiple clients and repeated queries over a run corpus.
- Encourages a clear request/response API.

**Weaknesses**

- Premature until the artifact contract and producer boundary settle.
- Adds server lifecycle, routing, concurrency, and auth concerns.
- Could distract from the missing runtime-agent layer.

**Disposition**

Promising downstream interface, not the next implementation slice.

## Findings

### Finding 1 — The product boundary is implied but not yet cleanly stated

CBM should not be described as “the hooks,” “the deterministic CLI,” or “the agent loop.” The product is the artifact contract and run lifecycle that lets another human or agent ask: “what is known, how do you know it, what is uncertain, and what should I do next?”

A clean product boundary would say:

- CBM accepts a repo path, source revision, user goal, mode, and optional backend.
- CBM does not mutate source code.
- CBM produces a run bundle.
- Every claim is schema-validated, citation-backed, freshness-checkable, and register-labeled.
- Runtime-agent output is allowed only if it passes the same gates as deterministic output.
- Consumers depend on artifact schemas and a run manifest, not on Codex hooks or implementation internals.

### Finding 2 — `cbm run` is currently semantically overloaded

The current `cbm run` is useful, but its meaning is ambiguous. It can be read as:

1. a deterministic smoke pipeline;
2. a Phase A/Phase B kernel orchestrator;
3. a product-level runtime-agent orchestrator;
4. a platform-adapter entrypoint.

Those should not all share one unqualified meaning.

Recommended semantics:

> `cbm run` owns the run lifecycle: create/pin run, run deterministic baseline, invoke declared producer backend, gate each artifact, assemble handoff, and emit a machine-readable run result.

If no runtime backend is configured, `cbm run` must be visibly a deterministic/baseline run. It should either require `--backend deterministic` or emit a top-level field such as `runtime_agent_layer: not_run` and `run_completeness: baseline_only`.

### Finding 3 — The consumer contract needs a manifest

The artifacts are individually well-specified, and `handoff.md` is useful. But a downstream consumer should not have to infer the run shape by walking `.research/<run_id>/`.

Add a durable machine-readable `run-manifest.json` or `run.json` with:

- `schema_version`
- `run_id`
- `repo_root`
- `source_sha`
- `goal`
- `mode`
- `backend`
- `started_at` / `completed_at`
- `run_status`
- `run_completeness`
- artifact list with paths, artifact types, schema versions, validation status, citation status, freshness status, and producer
- challenge/contestation summary
- coverage summary
- validation command used
- handoff path

Consumers should depend first on the manifest, then on artifact schemas. `handoff.md` can remain the human-readable summary.

### Finding 4 — The deterministic kernel is the strongest durable part of the current implementation

Durable kernel pieces include:

- citation format and resolution;
- JSON/YAML frontmatter schemas;
- `claim_register` and `claim_status`;
- extractor registry and known blind spots;
- evidence ledger and append-only integrity sidecar;
- uncertainty register;
- staleness/freshness/verify/refresh mechanics;
- `goal-binding.json` concept;
- `cbm-gate-artifact` / claim-evidence checks;
- `cbm-run-gate` safety-envelope concept;
- artifact layout and run directory discipline;
- platform-neutral separation of CLI/schemas/skills from adapter syntax.

These should be protected from platform-specific contamination.

### Finding 5 — Several current pieces are useful scaffolding, not product kernel

Likely accidental or transitional scaffolding:

- deterministic substitutes for Surface Mapper, Skeptic, Synthesizer, Tracer, Planner, and Approval Planner when named as if they were runtime agents;
- live `.codex/` dogfooding config in the implementation repo;
- the tiny fixture as the only evidence of mapping behavior;
- monolithic `cbm/cli.py`;
- roadmap phase labels after opportunistic implementation moved ahead of them;
- any deterministic “Skeptic” behavior that always emits a known challenge rather than independently reviewing claims;
- current output layout if it is kept only because tests expect `.research/<run_id>/`.

These are not bad. They are just not the part consumers should depend on.

### Finding 6 — Hooks are adapter glue, not correctness infrastructure

Hooks can be valuable when the platform offers them. But the correctness mechanism must be explicit CBM validation commands run by the parent controller or consumer.

Right relationship:

- Deterministic commands produce structural facts.
- Runtime agents produce interpretive artifacts.
- Validation gates verify artifact shape, citations, evidence requirements, ledger consistency, freshness, and run completeness.
- Hooks call those gates opportunistically at platform lifecycle points.
- Platform adapters translate platform-specific events into CBM commands.
- No hook should contain unique policy that is unavailable from `cbm validate-run` or `cbm gate-artifact`.

Current docs are moving in this direction, but `docs/architecture.md` and `docs/contracts.md` still give hooks more architectural prominence than they should have.

### Finding 7 — The runtime-agent layer is still the main missing product capability

Skills exist. Artifact schemas exist. Deterministic artifacts exist. But there is no demonstrated loop where a role-specific runtime agent:

- directly examines selected files;
- writes a role artifact;
- distinguishes direct examination from extractor-only coverage;
- receives isolated Skeptic review;
- responds to challenges or propagates contestation;
- is validated by parent-side CBM gates.

Until that exists, CBM can honestly claim a mapping kernel and artifact discipline, but not mature codebase understanding.

### Finding 8 — Documentation authority is inconsistent

The repo currently depends on documents that were not available in the committed branch during this review: `VISION.md` and `RUNTIME-CONSTITUTION.md`. Also, version references drift between v1.1 and v1.2.

This matters because autonomous `/goal` execution depends heavily on document authority. If the authority hierarchy is stale or missing, the agent loop can keep building plausible features while moving away from the intended product.

### Finding 9 — The benchmark is not strong enough for architecture claims

The small fixture proves commands and schemas. It does not prove that CBM can map a real unfamiliar repo.

Before claiming standard-mode mapping adequacy, add a pinned small real-world benchmark repo, preferably one with:

- more than one subsystem;
- actual config/read-site relationships;
- tests and CI;
- some dynamic or framework behavior;
- enough ambiguity to require unknowns and interpretive claims.

## Recommended architecture

Adopt a **kernel-plus-producer architecture**.

### Product contract

CBM’s stable product contract should be:

```text
Input:
  repo, source revision, goal, mode, backend, output root, optional safety envelope

Output:
  run manifest, validated artifacts, handoff, and machine-checkable gates

Guarantee:
  claims are cited, register-labeled, freshness-checkable, schema-valid, and contestation-aware;
  source code is not mutated;
  runtime-agent output is accepted only through CBM gates.
```

### Execution model

1. **Run initialization**
   - Create run directory.
   - Pin `source_sha`.
   - Write `intake.json`, `state.json`, `run-manifest.json`, `extractor-registry.json`.
   - Record backend and mode.

2. **Deterministic baseline**
   - Produce `codebase-map.json`.
   - Produce structural edges where extractors are trustworthy.
   - Populate known blind spots.
   - Gate the artifact.

3. **Producer phase**
   - Producer backend writes higher-order artifacts.
   - Initial backends:
     - `deterministic`: current scaffolding; honest baseline-only run.
     - `external`: outer agent writes artifacts; CBM only gates.
   - Later backends:
     - `codex`: CBM launches Codex subprocess agents.
     - `claude`: CBM launches Claude Code subprocess agents.
   - Each producer declares which artifacts it can emit and which skill/schema governs them.

4. **Validation phase**
   - `cbm gate-artifact` after every artifact.
   - `cbm validate-run` before handoff.
   - No hook-only policy.

5. **Goal binding and card production**
   - Baseline/surface artifacts remain goal-agnostic.
   - Goal enters through `goal-binding.json`.
   - Planner or deterministic fallback produces `interventions/` or `findings/`.
   - Cards propagate challenges.

6. **Handoff**
   - `handoff.md` summarizes for humans.
   - `run-manifest.json` summarizes for machines.

### `cbm run`

`cbm run` should mean:

```sh
cbm run   --repo <target-repo>   --goal "<goal>"   --mode lightweight|standard|deep   --backend deterministic|external|codex|claude   --run-id <id>   --output-root <path>
```

For the immediate implementation, use:

```sh
cbm run --backend deterministic ...
```

or:

```sh
cbm run --backend external ...
```

Do not silently imply that deterministic scaffolding is runtime-agent orchestration.

### How another project or agent should request mapping information

For now:

1. Start a run:
   ```sh
   cbm run --repo <repo> --goal "<goal>" --mode standard --backend deterministic --run-id <id>
   ```

2. Validate:
   ```sh
   cbm validate-run --repo <repo> --run-id <id>
   ```

3. Consume:
   - read `.research/<run_id>/run-manifest.json`;
   - read `.research/<run_id>/handoff.md`;
   - follow artifact paths and JSON Pointer refs from the manifest/handoff;
   - treat `claim_register`, `claim_status`, citations, freshness, and coverage as part of the contract.

4. Ask follow-up questions from existing artifacts:
   ```sh
   cbm consult "<question>" --repo <repo> --run-id <id>
   ```

Future interface:

- Provide an MCP adapter over the same contract, with tools such as:
  - `start_run`
  - `get_run_status`
  - `get_handoff`
  - `get_artifact`
  - `consult`
  - `validate_run`
  - `refresh_run`

The MCP adapter should be a consumer interface over the kernel, not a replacement for artifacts on disk.

### Artifact location

Immediate recommendation:

- Keep the current `.research/<run_id>/` contract for compatibility.
- Add `--output-root` so users can place artifacts outside the target repo.
- Add a manifest so consumers do not depend on directory walking.
- Consider migrating later to `.cbm/runs/<run_id>/` only with a deliberate schema/contract migration.

Required artifacts by run maturity:

**Every run**
- `run-manifest.json`
- `intake.json`
- `state.json`
- `extractor-registry.json`
- `codebase-map.json`
- `evidence-ledger.jsonl`
- `uncertainty-register.jsonl`
- `handoff.md`

**Lightweight mapping**
- `surface-map.json`
- `goal-binding.json`
- `findings/<id>.md` or `interventions/<id>.md`
- `skeptic-review/<artifact>.md` if a runtime or deterministic reviewer was run

**Standard mapping**
- `authority-map.json`
- `dependency-graph.json`
- `verification-map.json`
- `synthesis-index.json`
- per-artifact `skeptic-review/*.md`

**Deep mapping**
- `workflow-traces/*.json`
- `refinement-report.json`
- `approval-plan.json`
- `command-outputs/*.txt` for approved gates

Consumers should rely on the schemas and manifest, not on filenames alone.

## Risks and tradeoffs

1. **Making `cbm run` backend-aware adds upfront design work.**
   Worth it because it prevents the central command from meaning different things in tests, docs, and product usage.

2. **Outer-agent orchestration is less productized than subprocess orchestration.**
   Accept this temporarily. It is safer than inventing a Codex/Claude subprocess model before verifying platform controls.

3. **A manifest is another artifact to maintain.**
   Worth it because it creates a stable consumer boundary and prevents `.research/` directory layout from becoming accidental API.

4. **Demoting hooks may feel like losing useful automation.**
   It is not. Hooks remain useful as event triggers. The demotion only says they cannot be the sole correctness mechanism.

5. **Keeping `.research/<run_id>/` may preserve an awkward name.**
   Acceptable for now. Changing output layout before the run contract is stable would create churn.

6. **Deterministic scaffolding may continue to be useful in tests.**
   Keep it, but name it honestly. The risk is not that scaffolding exists; the risk is that it is mistaken for runtime-agent capability.

7. **Codex subprocess backend may become the desired product quickly.**
   Run a narrow spike after the contract is fixed: one role, one artifact, one schema, one validation loop. Do not implement a full multi-agent system first.

## Decisions required from the user

1. **Primary architecture decision:** Should the immediate product be:
   - CBM as artifact/gate kernel used by an outer agent; or
   - CBM as self-contained CLI that launches runtime agents?

   Recommendation: choose artifact/gate kernel for the next slice, with a future pluggable backend path.

2. **`cbm run` semantics:** Should current deterministic orchestration remain `cbm run`, or be explicitly marked as `--backend deterministic` / renamed to `cbm baseline`?

   Recommendation: keep `cbm run`, but require or record `--backend deterministic|external|codex|claude` and add `run_completeness`.

3. **Consumer contract:** Should consumers depend on `handoff.md` alone, or should CBM add `run-manifest.json` as the machine-readable source of truth?

   Recommendation: add `run-manifest.json`.

4. **Output location:** Should CBM default to artifacts inside the target repo or require explicit output root?

   Recommendation: default inside target repo for local-first reproducibility, but add `--output-root`.

5. **Hook posture:** Should live `.codex/` remain in this implementation repo?

   Recommendation: keep only if explicitly labeled dogfood. Otherwise move live hook config to a template/example and make platform adapters opt-in.

6. **Authority docs:** Are `VISION.md` and `RUNTIME-CONSTITUTION.md` supposed to be committed product authorities?

   Recommendation: commit them, or remove/replace references before the next autonomous build slice.

7. **Benchmark:** Which real small repository should become the first meaningful mapping benchmark?

   Recommendation: choose one before claiming standard-mode mapping quality.

## Concrete next steps

1. **Write an architecture disposition.**
   - Accept, modify, or reject this review.
   - Record the chosen product boundary and `cbm run` semantics.

2. **Add or restore missing authority docs.**
   - Commit `VISION.md` and `RUNTIME-CONSTITUTION.md`, or revise `AGENTS.md` and review context so they do not point to absent files.

3. **Align docs before code.**
   - Update `docs/architecture.md` so hooks are adapter glue, not product correctness.
   - Update `docs/contracts.md` with the consumer contract and backend/run semantics.
   - Update `docs/roadmap.md` so current phase labels match implementation reality.

4. **Add `run-manifest.json`.**
   - Create schema.
   - Write it at run start and update it after each stage.
   - Make `handoff.md` reference it.
   - Make tests assert manifest contents.

5. **Add `cbm validate-run`.**
   - Validate all artifacts listed in the manifest.
   - Check citations, evidence requirements, ledger integrity, freshness, artifact presence, backend completeness, and handoff consistency.
   - Make hooks call this where appropriate; do not duplicate policy in hooks.

6. **Make backend semantics explicit.**
   - Add `--backend deterministic|external` immediately.
   - Record backend in run manifest and handoff.
   - Mark deterministic runs as `baseline_only` unless runtime-agent artifacts are externally supplied and gated.

7. **Fence deterministic stand-ins.**
   - Rename or label deterministic Surface/Skeptic/Tracer outputs as scaffolding unless a runtime agent actually produced them.
   - Ensure artifact `produced_by` distinguishes `deterministic_kernel` from `runtime_agent:<role>`.

8. **Run one runtime-producer spike.**
   - After the manifest/validate-run contract lands, test one producer path:
     - external agent writes `surface-map.json`;
     - CBM gates it;
     - Skeptic or outer reviewer challenges it;
     - handoff propagates contestation.
   - Only then consider `codex exec` or Claude subprocess orchestration.

9. **Add a real benchmark repo.**
   - Pin a small external repo or checked-in fixture snapshot.
   - Define expected qualitative outcomes: at least one real authority, one unresolved unknown, one contested/alternative reading, and one actionable card.
   - Keep the tiny fixture for unit tests, but stop using it as evidence of mapping quality.

10. **Defer more deterministic feature expansion.**
    - Do not add another artifact type or gate until the run/product boundary is clear.
