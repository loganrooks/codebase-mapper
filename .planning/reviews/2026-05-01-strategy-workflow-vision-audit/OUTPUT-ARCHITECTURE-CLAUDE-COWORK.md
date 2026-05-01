# Architecture and Product Shape Review — Independent

Reviewer: Claude (Cowork session)
Date: 2026-05-01
Scope: CBM repository at HEAD as of 2026-05-01
Independence note: this review was conducted without reading any other reviewer's output (the two review folders at `.planning/reviews/` were left unread). `SHARED-CONTEXT.md` was also skipped because the only copy lives inside another reviewer's folder. Diagnosis is from primary sources: `VISION.md`, `RUNTIME-CONSTITUTION.md`, `README.md`, `AGENTS.md`, `.planning/STATE.md`, `.planning/CURRENT-PLAN.md`, `docs/architecture.md`, `docs/contracts.md`, `cbm/cli.py`, `pyproject.toml`, `schemas/*.json`, `skills/*.md`, `platform/*`, `.codex/*`, the recent tail of `BUILD-LOG.md`.

## Executive verdict

CBM has built a strong, honest deterministic kernel and a clear, unusually well-written set of contracts and schemas. What it has not built is the runtime agent layer that `VISION.md` requires for the system to be the thing it says it is. The deterministic kernel has, in several places, been used to produce *artifact-shaped stand-ins* for that missing layer — a templated `cbm-handoff` card, a `cbm-skeptic-review` that issues stock challenges, a `cbm-consult` that keyword-matches the corpus. The shape is right; the substance is missing. The recent build-log shows the dev agent locally optimizing the kernel's gate strictness in many small slices while the hard, ill-defined work of standing up a real runtime backend remains untouched. This is a workflow drift as much as an architectural one.

The right move is **not** to keep adding deterministic features. The right move is to (a) demote or fixture-mark the deterministic stand-ins so they stop reading as agent output, (b) commit to a pluggable runtime-agent backend behind a producer registry, (c) verify a single real agent-produced artifact end-to-end on a real (non-fixture) repository, and (d) split `cbm/cli.py` so the kernel/agent/adapter boundary the project says it cares about is visible at the file level. Of the architecture options the prompt names, the closest match is the *outer-agent-orchestrator + CBM-as-kernel* option blended with the *hybrid deterministic-plus-runtime-backend* option. Either of the pure variants leaves the project with a discipline mismatch.

## Observed facts

The deterministic kernel is real and well-tested. `cbm/cli.py` provides 32 console scripts (`pyproject.toml:17-47`) covering inventory, extraction, validation, freshness, ledger, registry health, gate composition, refresh, consultation, run-gate execution, and lifecycle. `tests/test_cli.py` is 1800 lines against a 4525-line CLI and `STATE.md:68-72` reports `pytest -q` at 51 passing. The schema package is substantial — 17 schemas, 2617 total lines (`schemas/*.json`) — and the contract document (`docs/contracts.md`) precisely defines the artifact catalog, claim-evidence requirements per claim type, and hook integration points. The reuse-and-refresh design (`docs/reuse-and-refresh.md`, `RUNTIME-CONSTITUTION.md` §25) is operationally complete on paper.

The runtime agent layer is unbuilt. The `skills/` directory contains seven prompt files (`compaction-recovery.md`, `consult.md`, `intervention-planner.md`, `skeptic.md`, `surface-mapping.md`, `synthesizer.md`, `tracer.md`). A grep of `skills/` across the Python source (`cbm/`) finds zero loads — the only reference is an `authority_hints` mention inside `cbm/project_packs/agent_orchestration.json:11` (CBM pointing at its own repo as a project worth mapping). The skills sit on disk waiting for an orchestrator that does not exist.

`cbm run` is a sequential in-process Python pipeline, not an agent orchestrator. `command_run` (`cbm/cli.py:4015-4083`) iterates a fixed list of `(command_function, namespace)` tuples — `command_init`, `command_map`, `command_surface`, then mode-conditional `command_authority_map`, `command_skeptic_review`, `command_dependency_graph`, `command_verify_map`, `command_synthesis_index`, optionally `command_bind`, `command_trace_workflows`, `command_refine`, `command_approval_plan`, then `command_handoff`. No subprocess spawn, no platform indirection, no skill load.

Several deterministic commands counterfeit agent output. `command_skeptic_review` (`cbm/cli.py:1344-1383`) produces a meaningful artifact only when the input is a `dependency_graph`; for every other artifact type it emits `"No deterministic Skeptic finding was produced for this artifact.\n"`. The dependency-graph branch (`review_dependency_graph`, `cbm/cli.py:1277-1342`) issues a stock challenge per unknown edge with a hardcoded `competing_reading` string at line 1294 and `interpretive_axis: completeness`. A second hardcoded `competing_reading` lives at `cbm/cli.py:3749` inside the handoff path, attached to a draft surface-map "skeptic" challenge — same pattern. This is shape-conformant under `RUNTIME-CONSTITUTION.md` §5 and `schemas/skeptic-review.schema.json`, but it is a mechanical "graph has unknowns" rule wearing the costume of a hermeneutic challenge. `command_handoff` (`cbm/cli.py:3592` onward) builds card prose by templating English: `"Calls {target}; this grounded static relation is the selected goal-binding candidate"` and `"leverage is bounded by the unresolved unknown dependency edge"` (`cbm/cli.py:3641-3654`). `command_consult` (`cbm/cli.py:3362-3434`) uses keyword tokenization (`tokenize_query`, `consult_scan`) — there is no Reader skill behind it, only string match.

Hooks are dual-located and deeply baked in. `.codex/hooks.json` and `platform/codex/hooks.json` are byte-identical and both wire `SessionStart` to `python3 -m cbm hook-start` and `Stop` to `python3 -m cbm hook-stop`. Two console scripts (`pyproject.toml:46-47`), `cbm-hook-start` and `cbm-hook-stop`, implement the Codex hook protocol (stdin JSON in, structured `{continue, stopReason, systemMessage}` JSON out — `cbm/cli.py:4116-4243`). The hook bodies do honest work — they aggregate validators that already exist (schema validation, citation freshness, ledger append-only, hash drift, gate sweep) — so AGENTS.md's "hooks should call the same validators, not contain unique policy" rule holds. But the *placement* contradicts CURRENT-PLAN.md: live `.codex/hooks.json` ships at the repo root, even though `.planning/CURRENT-PLAN.md:48-50` says repo-local hooks should be opt-in only.

The architecture and contracts docs prescribe what is missing. `docs/architecture.md:22-36` describes Tier 2 — Surface Mapper, Tracer, Synthesizer, Intervention Planner, Skeptic — explicitly as agentic subagents, with `skills/` as the prompt library and per-claim-register Skeptic protocol (`docs/architecture.md:42-56`, `RUNTIME-CONSTITUTION.md` §17). The contract document (`docs/contracts.md:140-156`) lists each artifact's writer; six of those writers (`Surface Mapper`, `Authority Mapper`, `Dependency Mapper`, `Verification Mapper`, `Tracer`, `Synthesizer`, `Planner`, `Skeptic`) are agents that don't exist yet — they are the deterministic commands renamed.

The kernel/agent/adapter boundary is invisible at the file level. `cbm/cli.py` is one 4525-line file holding everything: file scan and language detection (lines 91-167), AST extractors (180-289), schema and ledger plumbing (359-769), every per-command function, the orchestrator (`command_run` at 4015), the hook adapters (`command_hook_*` at 4116-4243), and the argument parser (`build_parser` at 4246-4400). The structural separation the project says is load-bearing — kernel vs. agent vs. adapter — is exactly the separation not visible by opening the file.

The build log shows local-optimization drift. `BUILD-LOG.md` contains 100 entries dated 2026-05-01 alone (`grep -c '^## 2026-05-01' BUILD-LOG.md`); the most recent ten in the tail are representative — all ratcheting kernel-side gate strictness (uncited artifacts now fail `gate-artifact`, `validate-fresh`, and `corpus-status`; duplicate extractor ids are rejected; duplicate pack annotations are rejected; handoffs fail on schema-invalid listed artifacts; verify reports include registry health). Each slice has a self-critique stanza ("Drift / Contract / Reviewer-eye") that catches local drift but not systemic drift. None of these slices advance the runtime-agent layer. The dev agent appears to be feeding on the kernel's easy verifications; this is the workflow signal that produced `STATE.md` and `CURRENT-PLAN.md`'s call for a planning reset.

## Architecture options

### A. CLI-only deterministic pipeline

Keep the current shape. Never add runtime agents. Refactor the templated stand-ins into honest deterministic outputs.

This is incompatible with `VISION.md`. Three of the ten graduation criteria (`VISION.md:91-104`) — Skeptic factual-defect catch rate matching expert review, Skeptic interpretive-challenge precision, cross-platform parity — and the central commitment of `VISION.md:9-13` (legible interpretive work, three-register claims) require something that interprets. Determinism cannot. Choosing A means rewriting VISION downward.

Strength: ships, holds, stays simple. The kernel is good at the kernel's job. Weakness: counterfeits the rest, and the counterfeits propagate. A skeptic-review with a stock `competing_reading` teaches downstream consumers to read challenges as noise. The contestation machinery is then load-bearing infrastructure for content the system cannot produce.

### B. CLI launching Codex/Claude subprocess agents

The candidate from `.planning/CURRENT-PLAN.md:32-50`. Parent CBM owns the run directory, validation, output paths, and prompts. The backend is `codex exec --cd <repo> --profile <cbm-profile> --output-schema <schema> ...` (or the Claude Code analogue). Skills get loaded as system instructions to the launched subprocess.

Strength: CBM stays in control of the contract. Cross-platform parity (graduation criterion #8) becomes a backend swap. Weakness: a `codex exec` subprocess is an *agent session*, not a *subagent inside* a session. `RUNTIME-CONSTITUTION.md` §17 requires the Skeptic to have isolated context. Whether `codex exec` provides that, vs. inheriting whatever the parent had, is platform-specific and needs verification before committing to this as the Skeptic backend. Treat this as a strong candidate, not a chosen option.

### C. Outer agent orchestrating CBM subagents while using CBM CLI as artifact/gate kernel

CBM is kernel-only. The outer orchestrator — a Codex or Claude Code session, or a human — is the agent runtime. Skills load into the *orchestrator's* native subagent system. CBM provides validators (`cbm validate`, `cbm gate-artifact`, `cbm verify-citations`, `cbm validate-fresh`), schemas, ledger plumbing, and run-gate execution. `cbm run` becomes optional.

Strength: clean boundaries. CBM is what it is good at. The host platform does subagent isolation natively (Codex Code's isolated-context subagents satisfy §17 directly). Skills load as the platform expects. Cross-platform parity is "same kernel, different orchestrator" — exactly what `platform/PORTABILITY.md` already commits to. Weakness: less control over execution. There is no single `cbm run` that produces an end-to-end run; the user (or outer agent) drives. This is honest about what CBM is — a discipline kit plus a kernel — but it cedes the "type one command and walk away" experience.

### D. Hybrid: deterministic baseline + runtime-agent backend behind a producer registry

The deterministic kernel (codebase-map, dependency-graph extractors, build/test discovery) stays CLI. The interpretive producers — Surface Mapper, Skeptic, Synthesizer, Planner, Reader, Tracer — are pluggable behind a *producer registry* mapping `artifact_type → producer`. A producer is either a CLI command (deterministic stand-in, marked as such) or an external invocation contract (skill prompt + spawn semantics + output schema). `cbm run` becomes a thin orchestrator that reads the registry, dispatches per artifact, and validates after each.

Strength: matches what is actually built (strong baseline + gates) plus what is missing (pluggable agent producers). The kernel/agent boundary becomes a registry entry, not a class hierarchy. Backend choices live in `platform/<backend>/` and are separately verifiable. Weakness: requires designing the registry and the spawn protocol, which is non-trivial. This is real work, not a refactor.

### E. (Proposed alternative) D, plus structural surgery

D is right architecturally; it should be paired with structural surgery the architecture has already earned. Specifically: split `cbm/cli.py` into `cbm/kernel/` (extractors, schemas, validators, ledger), `cbm/commands/` (CLI command bodies), `cbm/orchestrator/` (run.py, producer registry), `cbm/hooks/` (hook adapters). Move `.codex/hooks.json` out of the repo root into `platform/codex/`. Mark the templated handoff card, `command_skeptic_review`, `command_refine`, `command_trace_workflows` as `produced_by: dev-fixture@x.y.z` in their frontmatter so they cannot be read as agent output even by a casual reader. The structural change is the architecture made visible.

This is the recommended option.

## Findings

The product boundary is artifacts on disk under `.research/<run_id>/`, with the contract being schema validity, citation resolution, append-only ledger, freshness reporting, and contestation propagation (`docs/contracts.md`, `RUNTIME-CONSTITUTION.md` §13–14). This boundary is correct and should not move. Any consumer of CBM — another agent, a CI system, a human reviewer, a different project — interacts with `.research/<run_id>/` as the source of truth, with `cbm-validate-fresh` and `cbm-gate-artifact` as the validators and `cbm-consult` as the read-without-rerunning channel. This contract is the durable kernel.

`cbm run` should mean *"produce a complete CBM run, validating after each step"*. The semantics should be stable; the producers behind it should be pluggable. Today `cbm run` ships as a fixed in-process pipeline of deterministic commands; tomorrow the same command should dispatch to the producer registry. The command name does not need to change; the implementation under it should.

The durable kernel is roughly: file inventory and language detection (`iter_repo_files`, `language_for`), per-language extractors (`extract_python_import_edges`, `extract_python_call_edges`), schema validation (`validate_data`, `extractor_registry_validation_errors`, `check_claim_evidence`), citation resolution (`resolve_citation`, `verify_citation_at_head`), ledger append-only enforcement (`verify_ledger_append_only`, `append_only_integrity_errors`), freshness (`command_validate_fresh`, `command_verify`, `command_corpus_status`), refresh deltas (`structural_refresh_delta`, `interpretive_refresh_delta`), composite gates (`artifact_gate_failures`, `command_gate_artifact`), and the run-gate sandbox (`command_run_gate`). The schemas in `schemas/*.json`, the skills in `skills/*.md`, and the contract in `docs/contracts.md` are also durable. This is a respectable kernel and should be protected.

The accidental scaffolding is everything that puts on the appearance of agent work without doing the work. `command_skeptic_review`'s template; the `command_handoff` card prose; `command_refine`'s deterministic refinement; `command_trace_workflows`'s deterministic projection (the file labels itself "deterministic projection" in the build-log entries — honest); `command_consult`'s keyword-match Reader. None of these should be deleted yet — they exercise the contestation, refresh, gate, and consultation machinery — but each should be either pulled out of `cbm run` or marked `produced_by: dev-fixture@...` so its output cannot be read as a real Surface Mapper / Skeptic / Reader / Planner artifact. Today they pass through the same gates as real artifacts will, and downstream readers cannot tell them apart. This is the strongest hidden risk in the codebase.

The relationship between the four layers (deterministic CLI, runtime agents, validation gates, hooks, platform adapters) should be: validators and gates are *kernel-internal CLI commands*; runtime agents are *backend producers* dispatched by the orchestrator; platform adapters are *hooks plus spawn semantics*; CBM core depends on none of the platforms; each platform depends on CBM core. Today, `.codex/hooks.json` lives at the root, the hook implementations live in `cbm/cli.py`, and the runtime-agent layer is a deterministic stand-in. The order of the dependency graph is correct (platform depends on core, not the other way), but the file structure obscures it.

The architecture is being held back by a structural problem the dev agent's slice-by-slice workflow cannot fix. Each slice in `BUILD-LOG.md` self-critiques against the slice's own scope; none can ask "is the project that I am being a strict gate-builder for the project VISION describes?". The reset in `STATE.md`/`CURRENT-PLAN.md` is the right move; the architecture review's job is to ratify or rebut it. I ratify it: the deterministic-only path leads further from VISION every slice. The next slice should not be another gate, regardless of how easy it is to verify.

## Recommended architecture

Adopt option E (D + structural surgery), in three coupled changes.

First, define a producer registry. Add `cbm/orchestrator/producers.json` (or a generated file from declarative entries) mapping every `artifact_type` to a producer descriptor: `{ kind: "cli" | "agent", invoker: "<command>" or { backend, skill, system_prompt, output_schema }, validator_chain: ["validate", "verify-citations", "gate-artifact", ...] }`. The current deterministic commands continue to satisfy the registry as `kind: cli` entries. The interpretive producers (`surface_map`, `skeptic_review`, `synthesis_index`, `intervention_card`, `consultation`) get `kind: agent` entries pointing at a backend that does not yet exist, with skills already on disk. `cbm run` reads the registry and dispatches.

Second, stand up one real backend, end to end, for one artifact, on one repository. The cheapest credible target is the Surface Mapper via Codex CLI subprocess (`codex exec --cd <repo> --profile cbm-surface --output-schema schemas/surface-map.schema.json ...`), against the existing `tests/fixtures/sample_repo`. Verify: the Codex subprocess loads `skills/surface-mapping.md`, produces a `surface-map.json` that passes `cbm gate-artifact`, with citations that resolve. *Before* committing to Codex CLI as the canonical backend, verify that `codex exec` provides the *isolated context* §17 requires — if it inherits the parent's context, it is fine for the Surface Mapper but cannot host the Skeptic. If isolation is unavailable, the Skeptic backend is a separate problem from the Mapper backend, and option C (outer-agent orchestrator) becomes the fallback for the Skeptic specifically.

Third, refactor `cbm/cli.py` along the kernel/commands/orchestrator/hooks split. This is a pure structural change with no functional payoff *except* that the architecture becomes visible at the file level and future reviewers can answer "is this file part of the kernel?" by looking at its directory. The existing test suite is large enough (1800 lines of tests for 4525 lines of CLI) to cover the refactor.

In parallel: pin a real benchmark repository (`STATE.md:103` already names this — likely an MCP server). Mark or remove the deterministic stand-ins from `cbm run` until the producer registry exists. Move `.codex/hooks.json` to `platform/codex/` only; document hook adoption as an opt-in template. Keep `cbm-hook-start`, `cbm-hook-stop`, and `cbm-gate-artifact` as the platform-glue surface.

This is option D in shape and option E in execution. It accepts what the project has built (a strong kernel and contract package), names what it has not built (the runtime-agent layer and the structural separation), and lets each problem be solved on its own clock.

## Risks and tradeoffs

Building a producer registry plus one real backend is the biggest piece of new design in this recommendation. It risks turning into a "build a generic backend abstraction" project that is itself a slice trap. The mitigation is to insist on one specific backend for one specific artifact end-to-end before generalizing. If the registry has only one real entry, that is fine; the abstraction earns generality by being filled, not by being designed.

Removing or fixturing the deterministic stand-ins risks breaking the current test surface — 51 tests pass today, partly against templated handoff prose and stock skeptic challenges. The mitigation is to convert those tests from "the templated prose says X" to "the artifact validates and the citations resolve", which is what the kernel actually guarantees. Tests that depend on the *content* of stand-in output were always testing scaffolding, not the system.

Verifying `codex exec` isolation semantics is a small piece of platform research that, if it returns the wrong answer, invalidates the chosen backend. Treat backend-choice and isolation-verification as a coupled task; don't commit to a backend before the answer is known.

Splitting `cbm/cli.py` is churn-heavy and produces no user-visible change. The argument for doing it now is that the file is at the readability cliff and the architecture review has identified its monolithic shape as a contributor to the kernel/agent boundary becoming invisible. The argument against is that any churn now competes with real architecture work. A reasonable compromise is to do the split *as part of* introducing the orchestrator's producer registry, since that is when the kernel/orchestrator boundary first acquires real meaning in code.

Keeping `.codex/hooks.json` live at the root is a small risk that mostly manifests for users who clone CBM and find their Codex sessions doing CBM gate checks against repositories that have no `.research/`. Today the hooks degrade gracefully (`continue: true` with a friendly system message — `cbm/cli.py:4136`, `cbm/cli.py:4209`), so the immediate harm is low. The longer-term risk is that "hooks at the root of the implementation repo" sets a precedent for users; CBM should not advocate that.

The largest tradeoff is between *time-to-first-real-agent-run* and *cross-platform parity*. Option D gives both eventually but slowly. Option C gives parity immediately (CBM is just the kernel; the platform does the rest) but cedes the orchestrator narrative. The team's choice between these will depend on how much it values "type `cbm run` and walk away" versus "use CBM inside whatever agent session you already have." The graduation criterion (`VISION.md:100`) explicitly names cross-platform parity, so option C is closer to VISION's letter; option D is closer to its spirit.

## Decisions required from the user

The following decisions block the next implementation slice and cannot be derived from evidence alone.

The first is the architecture fork: option D (with E's structural surgery) versus option C versus revising VISION. Picking C means CBM ships as kernel-plus-discipline and the orchestrator is whatever the user is already running; picking D means CBM keeps its `cbm run` story but builds a backend abstraction; picking the third means VISION shrinks to match the deterministic kernel. The current trajectory chooses none of these explicitly and continues to ship deterministic gate slices that do not move toward any of them.

The second is the first runtime backend: Codex CLI subprocess (the `.planning/CURRENT-PLAN.md` candidate), Claude Code subagent, or a backend abstraction designed before either is built. Choosing Codex CLI first only works if `codex exec` provides isolated subagent context for the Skeptic — that needs to be confirmed before commitment.

The third is the disposition of the deterministic stand-ins: keep them as scaffolding, mark them as `produced_by: dev-fixture@...`, or remove them from `cbm run` until a real backend exists. The current state — they pass through the same gates as real artifacts will — is the worst of the three, because downstream readers cannot tell stand-in from real.

The fourth is whether to split `cbm/cli.py` now or defer until the producer registry forces the issue. The split has no functional payoff but makes the architecture readable. Coupling it to the registry work is the cheapest path; deferring further continues the slow growth of the file.

The fifth is the live `.codex/hooks.json` policy: keep, move to template-only, or remove. AGENTS.md prohibits user-level/global hooks; CURRENT-PLAN.md says repo-local hooks should be opt-in only; the implementation ships them as live ambient adapters.

The sixth, smaller decision: the benchmark repo. STATE.md names an MCP server as the target. Pinning one and adding it as a fixture (or recording its SHA) is a small step that turns "we have not yet proven mapping adequacy" from a planning note into a concrete next experiment.

## Concrete next steps

In priority order, with the smallest credible step first:

Pin a benchmark repo. Pick a small MCP server, vendor it under `tests/fixtures/` or record its name and SHA in `STATE.md`. Run `cbm run --mode lightweight` against it. Read the resulting artifacts as if you had not built CBM. The thinness of the templated handoff card on a real repository is a stronger argument for the recommended architecture than any review document can be.

Mark the deterministic stand-ins. Edit `produced_by` in `command_skeptic_review`, the templated parts of `command_handoff`, `command_refine`, `command_trace_workflows`, and `command_consult` to `dev-fixture@0.1` (or similar). This is a one-line change per command and immediately disambiguates them from real producers in any future artifact reader. Update the `produced_by` regex in the schemas if it requires it.

Move `.codex/hooks.json` to `platform/codex/hooks.json` only and remove the live root copy. Document opt-in in `README.md`. Two byte-identical copies of the hook config in one repo is a smell.

Define the producer registry contract as a JSON file with a schema. Begin with one entry per artifact_type, all currently `kind: cli` pointing at the existing commands. This is a no-op refactor in terms of behavior but makes the future agent backend a one-entry change instead of a refactor.

Verify `codex exec` subagent semantics. Specifically: does a `codex exec` invocation start a subagent whose context is isolated from the parent's, in the sense `RUNTIME-CONSTITUTION.md` §17 requires? Document the answer in `platform/codex/README.md`. The answer determines whether Codex CLI is a viable Skeptic backend.

Stand up the Surface Mapper as the first agent producer, end to end, on the pinned benchmark. Codex CLI subprocess, `skills/surface-mapping.md` loaded as system prompt, `--output-schema schemas/surface-map.schema.json`. Run the full kernel gate chain on the result. Iterate on the spawn contract until the result validates without templated patches.

Split `cbm/cli.py` along the kernel/commands/orchestrator/hooks lines. Do this as part of introducing the orchestrator's producer-registry dispatch. Ship as one PR with green tests; do not bundle other behavior changes.

Update `docs/architecture.md` and `docs/contracts.md` after the architecture decision is taken (per `.planning/CURRENT-PLAN.md:64`). The current architecture doc still describes Tier 2 as if it exists; this is a small but real source of confusion for future agents and reviewers.

Stop ratcheting kernel gate strictness. Until a runtime-agent producer ships, additional kernel gate slices are local optimizations that do not move the project toward VISION. The dev agent's per-slice self-critique cannot detect this, because the goal it's checking against is the slice's, not VISION's. The architecture correction needs an explicit guard: no merged slices that do not advance the runtime-agent layer or directly support its imminent introduction, until at least one real agent-produced artifact passes the kernel gates on the benchmark repo.

That is the bar.
