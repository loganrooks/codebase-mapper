# Vision Quality Review

## Executive verdict

`VISION.md` could not be located or inspected from the current branch paths available to this review. That is itself the most important finding. Multiple live documents treat `VISION.md` as the authoritative destination: `AGENTS.md` says it must be read first, `.planning/STATE.md` says it is authoritative for destination and maturity criteria, and `.planning/CURRENT-PLAN.md` says the immediate objective is to continue building toward it. If the file is missing, uncommitted, misplaced, or absent from the branch, future autonomous agents cannot follow the stated source of truth and will infer the vision from secondary documents instead.

Based on the visible vision surface in `README.md`, `AGENTS.md`, `docs/architecture.md`, `docs/contracts.md`, `docs/roadmap.md`, `.planning/STATE.md`, `.planning/CURRENT-PLAN.md`, and `BUILD-LOG.md`, the project's underlying vision is strong but under-operationalized. It gives unusually good pressure against false understanding: evidence-backed claims, citations to real bytes, claim registers, explicit unknowns, coverage honesty, Skeptic review, and contestation propagation. Those are valuable commitments and should not be weakened.

The visible problem is not that the ambition is too high. The problem is that the destination, architecture, runtime behavior, roadmap sequencing, platform adapter story, and developer workflow are not cleanly separated enough for a mostly autonomous `/goal` loop. The current implementation drift appears to have been encouraged indirectly by this ambiguity: the agent built a large amount of artifact machinery and deterministic gates beyond Phase A before the product boundary, runtime-agent execution model, benchmark target, and graduation criteria were settled.

This does not prove that the missing/uninspected `VISION.md` caused the drift. The evidence supports a narrower diagnosis: the implementation drift is more likely caused by the interaction of ambitious project language, broad downstream docs, weak phase-locking, and autonomous-workflow instructions that default to proceeding. A clearer `VISION.md` could reduce that risk by explicitly saying what the vision is, what it is not, what belongs in the roadmap, what belongs in architecture, what belongs in runtime-agent discipline, and what evidence is required before claiming maturity.

## Strengths of the vision

The project has a valuable epistemic core. The visible docs repeatedly reject unsupported understanding: every claim should cite real bytes at a real revision, citations should resolve, claims should be labeled factual/inferential/interpretive, unknowns should be surfaced rather than hidden, and recommendations should carry verification strategies. This is the right pressure for a codebase-mapping product.

The three-register claim model is a genuine strength. Treating factual, inferential, and interpretive claims differently prevents a common failure mode in AI codebase tools: presenting a plausible reading of a system as if it were a mechanically proven fact. The Skeptic protocol, challenge lifecycle, and contestation propagation all reinforce that discipline.

The visible anti-vision is also strong. The project refuses full-coverage claims, a single global confidence number, recommendations from unwritten context, automatic resolution of interpretive disagreement, and platform commitments that are not verified. Those refusals are useful because they make overclaiming a design error rather than just a documentation problem.

The artifact-on-disk principle is a good fit for long-running agent work. It gives the project recoverability, auditability, compaction resilience, and a way to separate durable state from transient chat context.

The deterministic-kernel-before-agentic-judgment split is directionally correct. File inventory, citation resolution, schema validation, extraction, freshness checks, and ledger checks should be boring, testable, and reproducible. Agents should synthesize over that baseline rather than fabricate structural truth.

The ambition is productively high. “Epistemic instrument for mapping unfamiliar codebases” is a better north star than “repo summarizer” or “code search wrapper,” provided the vision is paired with sharper operational constraints.

## Ambiguities or failure modes

The first failure mode is authority failure. `VISION.md` is named as the destination but was not retrievable in the current branch. `RUNTIME-CONSTITUTION.md` is also named as authoritative runtime-agent discipline but was not retrievable. If those files exist elsewhere, their absence from the visible branch is still a workflow defect: future agents will not reliably read them before acting.

The second failure mode is inconsistent reading order and stale authority. `AGENTS.md` says `VISION.md` is the first document to read. `README.md` instead starts its reading order with `AGENTS.md` and does not include `VISION.md` or `RUNTIME-CONSTITUTION.md` in its file map. `README.md` also describes `AGENTS.md` as a 24-section constitution, while the current `AGENTS.md` is a shorter operational guide. That mismatch makes it harder for an autonomous agent to know which document is current.

The visible docs blur five distinct things:

1. destination: what mature CBM should become;
2. roadmap: what to build in what order;
3. architecture: how the system should be decomposed;
4. runtime behavior: what CBM agents do during a mapping run;
5. developer workflow: how agents should build this repository.

Those categories are all present, but they are not cleanly partitioned. `docs/architecture.md` includes product values, phase model, runtime roles, hooks, evidence discipline, mode execution, packs, and portability. `docs/contracts.md` includes CLI commands, artifact catalogs, evidence requirements, status lifecycles, and hook integration. `AGENTS.md` mixes developer instructions, implementation architecture discipline, workflow guardrails, and references to runtime-agent constraints. That is understandable for a seed kit, but it is risky for autonomous implementation.

The product boundary is under-specified. The visible docs do not settle whether CBM is primarily:

- a deterministic CLI and artifact kernel;
- a CLI that launches Codex or Claude subprocess agents;
- a set of prompts and schemas used by an outer agent;
- a platform adapter layer around Codex hooks/subagents;
- a reusable codebase-research corpus;
- a consultation interface over prior artifacts;
- or a hybrid of these.

The current planning docs explicitly ask this question, which confirms that the boundary was not settled before substantial implementation.

The deployment model is under-specified. Important assumptions are missing or not clearly authoritative: install method, package boundary, output directory policy in target repositories, sandboxing expectations, supported platforms, supported languages, maximum repository sizes, model/backend choice, subprocess orchestration, cost/time budgets, network policy, user approval UX, and how another project or agent consumes CBM output.

The hook story is especially ambiguous. `docs/architecture.md` says hooks enforce phase prerequisites at the platform layer. `docs/contracts.md` lists many hook integration points. `docs/roadmap.md` includes hooks in MVP. Later planning docs and `platform/codex/README.md` correctly demote hooks to platform adapter glue that must not replace explicit validation. This evolution is reasonable, but `VISION.md` should have prevented ambient hooks from becoming confused with the product's correctness mechanism.

The vision surface may encourage overbuilding by treating every epistemic safeguard as equally urgent. Claim registers, evidence ledgers, extractor registries, coverage partitions, challenge lifecycles, staleness, refresh, reuse, packs, runtime tracing, command execution gates, platform hooks, and portability are all defensible. Without an explicit artifact budget and phase gate, they become a menu of attractive machinery rather than a sequenced product plan.

The phrase “Skeptic catches ≥1 weak claim per run on average” is a perverse graduation criterion. It can incentivize seeded or predictable weak claims instead of better mapping. The current deterministic scaffold's recurring unknown-edge challenge is useful as a bootstrap, but a fixed weak-claim count is not a reliable quality signal.

Some language is too aspirational to guide engineering alone. Terms like “epistemic instrument,” “hermeneutic,” “hostile reviewer,” “nuanced understanding,” and “arbitrary codebases” are meaningful, but they need companion engineering definitions: supported scope, benchmark fixtures, acceptance rubrics, failure modes, and explicit non-goals for each maturity level.

## Possible contribution to current drift

The visible evidence suggests the vision surface contributed to drift indirectly, not because the core ambition is wrong, but because the ambition was not converted into enough operational constraints.

The clearest drift pattern is phase expansion. `docs/roadmap.md` defines a small MVP command set and explicitly defers `cbm-bind`, `cbm-stale`, `cbm-run-gate`, project-type packs, separate mappers, workflow traces, and several later artifacts. The current `pyproject.toml` exposes a much larger command surface: authority map, dependency graph, verification map, synthesis index, skeptic review, bind, trace workflows, refine, approval plan, stale/freshness/verify/corpus-status/refresh/consult/run-gate, hooks, and run. `.planning/STATE.md` accurately names this as a mixed kernel build beyond Phase A before a settled runtime-agent architecture.

That drift did not necessarily produce bad code. Many of the added commands are aligned with the eventual vision and appear to have tests and smoke verification. The issue is sequencing and product proof: deterministic artifact machinery advanced faster than runtime-agent architecture, benchmark selection, and true codebase-reading quality.

The missing or unavailable `VISION.md` likely increased reliance on secondary docs. If the top-level destination is absent, agents will infer “the vision” from `README.md`, `docs/architecture.md`, `docs/contracts.md`, and `docs/roadmap.md`. Those documents are broad and implementation-rich, so an autonomous agent can reasonably interpret them as permission to build more machinery.

`AGENTS.md` also contributed to drift pressure. Its default mode is “proceed,” and it tells the agent to choose an interpretation consistent with `VISION.md` and `RUNTIME-CONSTITUTION.md` when ambiguity appears. That is unsafe if those two files are unavailable or not specific enough. The guardrail should be: when ambiguity would change product boundary, runtime architecture, or phase sequencing, pause for review or create a disposition artifact before implementation.

`BUILD-LOG.md` shows good local discipline but also illustrates how plausible progress can outrun product clarity. The log records decisions, tests, smoke runs, self-critiques, and phase claims. That is better than silent drift. However, the presence of many verified slices can make the project look more mature than it is unless the vision demands qualitative mapping benchmarks and runtime-agent evidence before maturity claims.

A plausible alternative interpretation remains: the deterministic kernel work may be a useful foundation, not waste. The problem is not “too much validation.” The problem is that validation and artifact growth became easier to prove than the central product claim: CBM can help produce grounded, nuanced understanding of unfamiliar codebases.

## Improvements to guide implementation quality

Add a short “vision contract” at the top of `VISION.md`. It should state, in one page or less:

- who CBM is for;
- what input it accepts;
- what output it guarantees;
- what it does not guarantee;
- what part is deterministic;
- what part is runtime-agent judgment;
- how users or other agents consume the result;
- what must be true before the project can claim MVP, standard, and deep maturity.

Separate destination from implementation mechanics. `VISION.md` should describe the mature outcome and the quality bar, not enumerate every artifact or command. The roadmap should sequence features. Architecture should define layers. Contracts should define schemas and CLI behavior. Runtime constitution should govern CBM's own agents. Developer workflow should govern agents building this repository.

Add an explicit product boundary decision table. For each candidate boundary, mark whether it is accepted, deferred, rejected, or undecided. At minimum, decide whether the first real product is:

- deterministic CLI plus handoff artifacts;
- CLI that launches runtime agents;
- outer-agent workflow using CBM as a kernel;
- or a hybrid with a clearly named primary interface.

Add a codebase-structure target. The current implementation has a very large `cbm/cli.py` surface. `VISION.md` does not need to mandate exact modules, but it should require the implementation to keep separable concerns separable: kernel extraction, schema/artifact IO, citation verification, runtime-agent orchestration, platform adapters, and user-facing CLI should not collapse into one monolith as the command surface grows.

Add an artifact economy rule. New artifacts, schemas, commands, hooks, or packs should require a named consumer and a maturity-level justification. Before MVP mapping quality is proven, the project should prefer fewer artifacts with better evidence over more artifacts with thin semantics.

Add a “runtime-agent minimum” definition. If mature CBM requires Surface Mapper, Skeptic, Synthesizer, Intervention Planner, and possibly Tracer behavior, define what counts as real runtime-agent behavior versus deterministic scaffold. For example: direct file examination must be recorded separately from extractor-only inspection; an agent-produced interpretive claim must cite directly examined bytes; a Skeptic challenge must target a concrete claim and explain the competing reading or defect.

Add a benchmark requirement before expanding surface area. The visible docs mention a 5k-LOC repo and a preference for a real MCP server, but this should be elevated into the vision quality bar. The project should not claim mapping adequacy from tiny fixtures or self-repo smoke runs alone.

Replace broad “arbitrary codebases” language with scoped maturity levels. A prototype can support Python packages only. MVP can support one pinned real repo class. Standard can support several languages/project types. Deep can support larger or riskier systems. The ambition can remain broad while claims stay scoped.

Add negative examples. `VISION.md` should show what a bad CBM output looks like: a path hallucination, a true citation supporting the wrong interpretation, a high-confidence card from extractor-only coverage, a hook passing while runtime artifacts are weak, or a “zero unknowns” graph on a non-trivial repo. Negative examples are often more useful for implementation quality than abstract principles.

## Improvements to guide workflow and verification

Make phase graduation evidence-based and hard to game. Replace or supplement “Skeptic catches ≥1 weak claim” with benchmarked checks such as:

- zero unresolved citations in required artifacts;
- no interpretive claim about a file unless that file is directly examined;
- all high-impact claims have adequate evidence kinds;
- at least one independent review of the handoff on a pinned benchmark repo;
- a human or independent reviewer rates the card actionable under a rubric;
- known planted ambiguities are surfaced as contested or unknown rather than collapsed.

Define “actionable card” with a rubric. A card should name the exact files/symbols/surfaces to inspect or change, cite the evidence, state uncertainty, list verification commands or manual checks, and explain why the proposed action follows from the goal. A generic recommendation to read more files should not count unless it is bounded and justified.

Add a benchmark suite with positive and negative controls. The first benchmark should be a pinned small real-world repository, ideally the currently suggested MCP server class. Include known expected surfaces, known blind spots, and at least one intentionally ambiguous interpretive question. Add one tiny fixture for fast tests, but do not treat it as mapping-quality proof.

Define a “vision drift check” that future agents must run before adding features. Each proposed slice should be classified as one of:

- improves mapping quality;
- improves artifact correctness;
- improves runtime-agent orchestration;
- improves platform/deployment integration;
- improves developer workflow/governance;
- speculative or convenience work.

Speculative or convenience work should be deferred until the benchmark and runtime architecture are settled.

Add escalation thresholds for autonomous `/goal` operation. The workflow should pause for review when product boundary is ambiguous, runtime architecture choices would produce different systems, phase ordering changes, a document authority conflict is discovered, the same failure recurs, or the agent wants to add a new artifact family not already accepted for the current maturity level.

Require independent checkpoints at phase boundaries. A phase completion claim should include: roadmap acceptance criteria, current implementation evidence, known gaps, benchmark result, test result, artifact examples, and reviewer disposition. `BUILD-LOG.md` should remain chronological evidence, not the place where phase authority lives.

Give docs explicit freshness metadata. The planning reset already moves in this direction. `VISION.md` should require each authority doc to state status, last updated date, supersession relationship, and whether it is destination, roadmap, architecture, contract, runtime, or workflow. Stale docs should not look authoritative.

Demote platform hooks in verification language. Hooks can be useful adapter glue, but the correctness path should be explicit CBM validation invoked by `cbm run`, `cbm validate-run`, or equivalent. The vision should say that platform hooks may call validators but must not be the only reason artifacts are trusted.

Add a “quality before breadth” rule. Until the first pinned benchmark passes, do not add new packs, new map families, consultation modes, refresh/reuse layers, or platform ports unless they are required to pass that benchmark or unblock the runtime architecture.

## Recommended edits or sections

Add or rewrite these sections in `VISION.md`:

### 1. Scope and authority

State that `VISION.md` is the destination and maturity bar, not the roadmap, architecture, runtime constitution, or developer operating manual. Then link to those documents and define what each owns. Include a rule that if `VISION.md` is unavailable, stale, or contradicted by planning docs, autonomous implementation must pause for disposition.

### 2. Product in one paragraph

Example target wording:

> CBM is a CLI-centered codebase-mapping system that produces evidence-backed mapping artifacts and intervention/finding cards for a target repository. Its deterministic kernel extracts and validates structural evidence; its runtime-agent layer performs bounded interpretive reading over that evidence; its handoff makes uncertainty, coverage, contestation, and verification strategy explicit. CBM does not modify the target source tree during mapping.

Adjust this wording if the desired product boundary differs.

### 3. Non-goals by maturity level

Create a table for Prototype, MVP, Standard, Deep, and Future. For each level, name allowed features, forbidden/deferred features, and required evidence. This would prevent “eventual vision” features from entering MVP without a conscious decision.

### 4. Runtime architecture assumptions

Do not bury the runtime-agent question in roadmap or contracts. State whether the accepted first runtime model is CBM launching subprocess agents, an outer agent orchestrating CBM, or undecided. If undecided, state that implementation must not add more runtime-adjacent machinery until the decision is made.

### 5. Artifact economy and command budget

Require every artifact and command to have a named consumer, failure mode, and graduation purpose. Add a rule that deterministic machinery is not a substitute for mapping-quality evidence.

### 6. Benchmark and graduation criteria

Replace broad criteria with measurable ones. Define the pinned benchmark repo, run mode, max runtime, expected artifacts, scoring rubric, citation requirements, direct-examination minimums, and review process. Keep the 5k-LOC/<30-minute target if useful, but make it reproducible.

### 7. False-understanding traps

List the highest-risk ways CBM can appear to understand a repo without actually understanding it. Examples: citable but irrelevant evidence, extractor-only interpretive claims, seeded weak claims, zero-unknown graphs, stale docs, hook-passed artifacts with weak runtime readings, and self-repo smoke tests mistaken for external validation.

### 8. Autonomous development governance

Add a concise section that tells the `/goal` loop when to proceed, when to log, when to create a review packet, and when to stop. This should be referenced by `AGENTS.md` but not duplicated in full.

### 9. Deployment and consumption assumptions

State how CBM is installed and run, where outputs live, how consumers read artifacts, what permissions are required, what source mutation is forbidden, and how external execution is approved.

### 10. Document integrity requirement

Require `VISION.md` and `RUNTIME-CONSTITUTION.md` to be present in the repository at stable paths if other docs name them as authoritative. If either file is intentionally deferred or renamed, update all references immediately.

## Questions requiring user decision

1. Where should the authoritative `VISION.md` live, and is it currently missing, uncommitted, renamed, or outside the branch?

2. Should `RUNTIME-CONSTITUTION.md` exist as a separate root document, or should runtime-agent discipline be moved into another documented authority?

3. What is CBM's first accepted product boundary: deterministic CLI kernel, CBM-launched runtime agents, outer-agent orchestration over CBM artifacts, or another hybrid?

4. Should `cbm run` eventually launch runtime agents, or should it remain a deterministic pipeline and leave agent orchestration to the surrounding Codex/Claude session?

5. What output directory policy should be authoritative for target repositories: `.research/<run_id>/` under the target repo, an explicit external output root, or both?

6. Which pinned real-world repository should become the first meaningful mapping benchmark, and what should CBM be expected to find there?

7. What maturity level is the current branch allowed to pursue before the runtime-agent architecture is settled: pause all feature work, continue kernel hardening only, or proceed with a specific bounded slice?

8. Should live `.codex/` hooks remain active in this implementation repo as dogfood, or should they move to template-only adapter examples until the product boundary is settled?

9. Which current commands/artifacts are accepted as durable kernel surface, and which should be marked experimental, deferred, or deleted?

10. How much autonomy should the `/goal` loop have when it discovers architecture ambiguity, stale authority docs, repeated failures, or phase drift?

11. What does “actionable card” mean to the user: a bounded reading plan, a proposed code change, a migration/refactor plan, a verification checklist, or all of these depending on goal pack?

12. Should `VISION.md` remain highly aspirational, with operational criteria in separate docs, or should it include the concrete benchmark and phase gates needed to steer implementation directly?
