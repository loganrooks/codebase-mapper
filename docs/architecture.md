# Architecture

The recommended architecture is a **modular deterministic kernel + agentic synthesis layer + goal packs**, with evidence-provenance discipline enforced by hooks, and a **three-register claim model** for handling factual, inferential, and interpretive content.

This document describes the architecture in implementable form. For operational rules, see `AGENTS.md`. For artifact and CLI contracts, see `contracts.md`. For mode-by-mode scope, see `roadmap.md`.

## Three tiers

### Tier 1 — Deterministic kernel (CLI tools)

CLI commands produce structural truth. No LLM judgment.

- File-system inventory, language classification.
- Per-language import/dependency extraction (AST-based; declared in extractor registry).
- Build/package metadata extraction.
- Test discovery.
- CI/workflow file enumeration.
- Schema/config detection by pattern.

Outputs are JSON validated against schemas. Cacheable by commit SHA. The kernel is not where the system gets clever; it is where the system gets reliable.

### Tier 2 — Agentic synthesis (subagents)

Five agent role templates:

| Role | Instances per run | Purpose |
|---|---|---|
| **Surface Mapper** | 3 (Authority, Dependency, Verification) — or 1 combined in lightweight | Turn baseline into typed interpretive maps. |
| **Tracer** | 1 per workflow of interest, deep mode | Runtime workflow traces with per-step confidence. |
| **Synthesizer** | 1, in main orchestrator context | Cross-reference maps; index + uncertainty register; propagate contestation. |
| **Intervention Planner** | 1 per candidate surface | Cards bound to user intent. |
| **Skeptic** | 1 per gate boundary (per artifact in deep mode) | Hostile review with isolated context; **operates in three modes by claim register**. |

Five templates is the cap. New agent additions require justification.

Each role has a skill prompt in `skills/`.

### Tier 3 — Goal packs

Specializations bound to user intent class: `feature_add`, `refactor`, `migration`, `audit`, `extension_points`, `research_only`, `understand_repo`. Goal packs are not agents; they are templates and prompt fragments consumed by the Intervention Planner. MVP ships with `understand_repo`.

## The three-register claim model

The central discipline of v1.1. Every claim in every artifact carries a `claim_register`:

- **factual**: settled by direct citation. Bytes at the SHA settle it.
- **inferential**: derived by reasoning over factual claims. Settled by checking the inference rule plus the factual base.
- **interpretive**: depends on a reading. Has defensible alternatives. Resolved through challenge protocol, not refutation.

The register determines the Skeptic's protocol:

- For factual claims: defect-finding mode. Find errors, force fixes.
- For inferential claims: defect-finding plus inference-rule scrutiny.
- For interpretive claims: alternative-raising mode. Specific competing readings with evidence; the artifact may carry both readings as `challenged` or `contested`.

The register makes hermeneutic content first-class without smuggling it in as factual. Interpretive claims that pretend to be factual either get challenged for register misclassification or quietly corrupt the artifact. The register/protocol pair prevents both.

## Claim status lifecycle

Every claim has a `claim_status`:

- `active` — live and uncontested.
- `challenged` — alternative reading raised.
- `contested` — multiple readings live.
- `contradicted` — refuted by evidence.
- `superseded` — replaced.
- `retired` — removed.

Status transitions are recorded in the evidence ledger. The handoff reports counts by status so consumers see what's contested.

## The phase model

```
Phase 0  Intake                 sequential
Phase 1  Deterministic baseline parallel CLI mappers
Phase 2  Surface mapping        parallel subagents (3 standard+, 1 lightweight)
Phase 3  Workflow tracing       parallel subagents (deep, conditional)
Phase 4  Synthesis              sequential, main context
Phase 5  Goal binding           sequential, lightweight
Phase 6  Intervention planning  parallel subagents (1 per candidate)
Phase 7  Verification planning  in-card; revisited deep mode
Phase 8  Skeptic gate + handoff sequential
```

Hooks enforce phase prerequisites at the platform layer.

## The evidence-provenance discipline

Every artifact carries citations: `path:lines@sha`. Every citation in the `evidence-ledger.jsonl` records what was introduced and which claim it supports.

Three mechanical checks gate every artifact write:
1. Schema validation.
2. Citation resolution (every cited `path:lines@sha` resolves to real bytes).
3. Ledger consistency (citations in the artifact appear in the ledger).

A fourth, claim-evidence-requirements check enforces AGENTS.md §7 — for example, edges of kind `runtime_workflow` cannot rely solely on `static_structure` evidence.

The Skeptic adds a fifth, interpretive check: are claims actually supported by their citations? And, in interpretive mode: are there competing readings that should be acknowledged?

## The unknown taxonomy

Four claim partitions:

- **certain** — direct mechanical evidence.
- **suspected** — inferred from naming/patterns.
- **advisory** — supported only by docs or convention.
- **unknown** — cannot be determined.

Every artifact aggregating claims (notably `dependency-graph.json` and intervention cards' `blast_radius`) reports counts in all four. **Reporting `unknown: 0` is suspect** on any non-trivial codebase.

## Three-mode execution

Research mode does not mean "no execution." It means "no source mutation." The system distinguishes:

- **Source mutation**: forbidden in any mode.
- **Build/test execution via `cbm-run-gate <id>`**: permitted with declared safety envelope and user approval. Output becomes `command_output` evidence.
- **External system access**: only with explicit per-access approval.

`cbm-run-gate` runs commands declared in `verification-map.json` with a `safety_envelope` (network/install/mutation booleans, max duration). The user pre-approves an envelope; gates outside refuse to run.

This distinguishes the system from a strict "static-only" research tool while staying conservative about mutation. Verification maps without execution are static descriptions; they may not reflect what actually runs.

## The extractor registry

A typed catalogue of deterministic extractors used in the run:

```yaml
extractors:
  - id: ext-treesitter-python-v1
    kind: ast
    deterministic: true
    produces_evidence_kinds: [static_relation, static_structure]
    known_blind_spots:
      - description: "Does not resolve dynamic imports via __import__"
        category: dynamic_dispatch
      - description: "Does not handle exec() or eval()"
        category: string_eval
```

Edges of kinds `import | call | public_api | generated_from` cite an extractor by `extractor_id`. The Skeptic looks up the extractor's known blind spots when reviewing claims that depend on it. If a codebase uses `importlib` and the extractor's blind spots include dynamic imports, the Skeptic flags missing edges.

This converts "extractor used: tree-sitter" (free string) into a typed reference into a registry that knows what the extractor cannot do.

## The kernel-vs-pack boundary

| In the kernel | In a pack |
|---|---|
| Codebase map | Card templates per goal class |
| Authority/Dependency/Verification maps | Surface-detection heuristics specific to project type |
| Synthesis index | Vocabulary specific to goal |
| Uncertainty register | Verification strategies typical of the goal |
| Evidence ledger | Goal-specific decision protocols |
| Extractor registry | Project-type-specific blind-spot annotations |

If specialization is creeping into the kernel, that's drift; refactor it back into a pack.

## Project-type packs vs. goal packs

- **Project-type pack**: heuristics for "this is a Rails app" or "this is an MCP server." Authority-detection rules, known-blind-spots, surface vocabularies.
- **Goal pack**: heuristics for "the user wants a refactor" or "research-only." Card templates, verification strategies, surface-prioritization.

A run loads at most one of each. They compose without conflict because they specialize different layers.

## The MVP cut

Strict subset: collapses Surface Mapper instances into one, defers Tracer, defers project-type packs, ships with `understand_repo` goal pack. The Skeptic is in MVP — too valuable to defer.

See `roadmap.md`.

## Why this and not the alternatives

Other architectures considered:

- **Generalist research agent.** Hallucinates paths and counts; quality collapses past ~50 files.
- **Fixed multi-agent pipeline.** Forks per project type; rigid.
- **Modular kernel + packs (without CLI determinism).** Hallucination at the kernel layer.
- **CLI-first deterministic mapper + agentic synthesis (without packs).** Harder to specialize without contaminating the baseline.

The recommended hybrid combines kernel modularity, CLI determinism, the three-register claim model, and goal/project-type packs. Scales down (skip mappers, skip Tracer, single Skeptic) and up (full suite + per-artifact Skeptic + multi-round refinement) without changing schemas.

## Portability

Platform-neutral by design. Codex-specific concerns live in `platform/codex/`; Claude Code adaptations live in `platform/claude-code/`. Only platform-specific files are: hook configuration syntax, subagent definition format, orchestrator entry point. Everything else — schemas, skills, CLI commands, artifact formats — is identical across platforms.
