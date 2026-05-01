# Roadmap

How to phase the build from seed to deep-mode-capable system. Schema version 1.2.

## What changed in v1.2

- **Reuse made operational.** Five forms (goal-agnostic cache, incremental update, historical consultation, consultation mode, deferred cross-run synthesis). Documented workflows; no more implicit-only.
- **Five staleness modes.** Validate, verify, refresh structural, refresh interpretive, re-run. Each command has its own CLI; each preserves a different amount of interpretive continuity.
- **Refresh delta as first-class artifact.** New schema (`refresh-delta.schema.json`) records carried_forward, updated, retracted, newly_added, newly_contested, plus per-challenge and per-open-question reconciliation status. The corpus accumulates trajectory.
- **Optional `refreshed_from` block** on artifacts that can be refreshed (codebase map, surface map, intervention card). Lineage made explicit at the artifact level.
- **New Reader skill (`consult.md`)** for the read-existing-artifacts-without-rerunning case. Refuses honestly when the corpus doesn't contain the answer or is too stale.
- **Compaction recovery integrates `cbm-validate-fresh`** so session resume never silently uses stale inputs.
- **Surface Mapper gains differential refresh mode** with the per-claim migration protocol.

## What changed in v1.1

- **Claim registers** (factual / inferential / interpretive) are first-class on every claim.
- **Claim status lifecycle** with `challenged` and `contested` for hermeneutic disputes.
- **Challenges as first-class artifact elements** distinct from contradictions.
- **Evidence kinds** as orthogonal multi-set, replacing the single linear quality ladder.
- **Extractor registry** with declared blind spots; edges cite extractors by id.
- **Coverage metadata** distinguishing files examined directly vs. inspected via extractor only.
- **Declarative staleness** with `depends_on_paths` and `scope_signature`.
- **Three-mode execution** distinguishing source mutation, declared command execution, and external access.
- **Contradicted as a claim status** separate from retraction.
- **Skeptic operates in three modes by claim register**.

## MVP — the smallest useful Codex-first system

The MVP test: on a 5k-LOC repo (e.g., a real MCP server), run from intake to handoff in <30 minutes of agent time. Produce at least one usable card whose citations resolve and whose verification strategy is concrete.

### Agents in MVP (3 templates)

- **Surface Mapper** (combined): produces single `surface-map.json`.
- **Intervention Planner**: one per candidate.
- **Skeptic**: end-of-run in lightweight; per-gate in standard.

Synthesizer collapsed into orchestrator pre-planning. Tracer deferred.

### Skills in MVP (5)

- `surface-mapping.md`
- `intervention-planner.md`
- `skeptic.md`
- `synthesizer.md` (used by orchestrator pre-planning)
- `compaction-recovery.md`

### CLI in MVP (5)

- `cbm-init` (creates run + extractor registry seed)
- `cbm-map`
- `cbm-validate`
- `cbm-verify-citations`
- `cbm-handoff`

`cbm-bind`, `cbm-stale`, `cbm-deps`, `cbm-gate`, `cbm-run-gate`, `cbm-extractor-registry validate` deferred. `cbm-deps` inlined into `cbm-map`. `cbm-gate` checks inlined into `cbm-handoff`.

### Artifacts in MVP (9)

- `intake.json`
- `state.json`
- `extractor-registry.json`
- `codebase-map.json`
- `surface-map.json`
- `interventions/<id>.md` or `findings/<id>.md`
- `evidence-ledger.jsonl`
- `uncertainty-register.jsonl`
- `handoff.md`

`authority-map`, `dependency-graph`, `verification-map`, `synthesis-index`, `goal-binding`, `workflow-traces`, `skeptic-review`, `command-outputs` deferred.

### Hooks in MVP

- Post-artifact-write: `cbm-validate` + `cbm-verify-citations` + claim-evidence-requirements check.
- Pre-`cbm-handoff`: full gate sweep + contestation summary populated.
- Session start: load `compaction-recovery` skill.

Per-artifact Skeptic spawning deferred.

### Goal packs in MVP

One: `understand_repo`. The pack defaults the Planner to findings cards (research-only).

### Explicitly deferred from MVP

- Tracer + workflow traces.
- Separate Authority/Dependency/Verification mappers.
- Synthesizer as distinct subagent.
- Goal packs beyond default.
- Project-type packs.
- Multi-mode dispatch (MVP is standard-only).
- MCP servers beyond what's already configured.
- `cbm-run-gate` and command execution.
- `cbm-stale` warning gate.
- Per-artifact Skeptic spawning.
- `cbm-challenge` programmatic challenge interface.

### What MVP must prove

1. Citations resolve end-to-end.
2. Schema validation rejects malformed artifacts.
3. Skeptic catches ≥1 weak claim per run on average.
4. Cards are actionable.
5. Claim registers are correctly assigned (no interpretive smuggled as factual).

If all five hold, the foundation is sound.

## Mode taxonomy

Same artifact schemas across modes. Modes differ in *which* gates fire, *how many* subagents spawn, and *whether* execution is permitted.

### Lightweight mode

- Use: small repos, quick research, single goal, <1 hour.
- Agents: combined Surface Mapper, Intervention Planner, Skeptic at end.
- Artifacts: MVP set.
- Time: 15–45 min agent time.
- Verification: hard gates only (schema, citations, claim-evidence). No `cbm-run-gate`.

### Standard mode

- Use: most cases.
- Agents: full Phase 1 CLI; three Surface Mappers in parallel; Synthesizer; Planner per candidate; Skeptic at gate boundaries.
- Artifacts: full kernel suite minus workflow traces.
- Time: 1–3 hrs agent time.
- Verification: hard + warning gates. `cbm-run-gate` available with user-approved safety envelope.

### Deep mode

- Use: large/critical changes, migrations, audits with stakes, monorepos.
- Agents: standard + Tracer + multi-round refinement (Skeptic findings re-enter mappers).
- Artifacts: full suite including workflow traces and per-artifact skeptic review.
- Time: 4–12+ hrs across sessions.
- Verification: hard + warning + advisory + manual approval gates. Multiple `cbm-run-gate` invocations expected.

## Build phases

### Phase A — MVP foundation (week 1–2)

1. CLI commands listed above.
2. JSON schemas (6 in `schemas/`).
3. Skill prompts (5).
4. Codex hook configuration.
5. Orchestrator script.
6. Test repo with expected outputs.

Acceptance: end-to-end run, citations resolve, ≥1 actionable card, claim registers correctly assigned.

### Phase B — Standard mode (week 3–4)

1. Three Surface Mapper subagents.
2. Synthesizer skill and orchestrator integration.
3. Per-artifact Skeptic spawning.
4. Schemas: `authority-map`, `dependency-graph`, `verification-map`, `synthesis-index`.
5. `cbm-bind` and `goal-binding.json`.
6. `cbm-stale` and warning gate.
7. `cbm-run-gate` with safety envelope discipline.
8. v1.2 reuse and refresh: `cbm-validate-fresh`, `cbm-verify`, `cbm-corpus-status`, `cbm-refresh --mode <structural|interpretive>`, `cbm-consult`. Reader skill. Differential refresh mode for Surface Mapper. Refresh-delta artifact.

Acceptance: 50k-LOC repo, coherent maps with non-trivial unknown partitions, Skeptic catches ≥1 weak claim per gate, ≥1 interpretive challenge per run on real codebases. Reuse: a second goal against the same SHA produces cards without re-mapping; a substantive codebase change refreshed via Mode 4 carries forward ≥80% of prior surface-map claims; consultation answers well-scoped questions in <30 seconds with grounded citations.

### Phase C — Goal packs (week 5–6)

1. `feature_add`, `refactor`, `audit`, `research_only` packs.
2. Pack-loading mechanism in `cbm-bind`.

Acceptance: same kernel run produces meaningfully different cards under different packs without re-running mappers.

### Phase D — Deep mode (week 7–8)

1. Tracer subagent and skill.
2. `workflow-traces/` artifact format.
3. Multi-round refinement protocol.
4. Mode-aware orchestrator.
5. Manual approval gate UX.

### Phase E — Project-type packs (week 9+)

1. Project-type detection in Phase 0.
2. Packs: Django/Rails/Phoenix; MCP servers; agent orchestration; monorepos.

Each pack ships with project-type-specific extractor registry annotations (e.g., "Django metaprogramming creates dynamic edges; AST extractors miss them").

### Phase F — Claude Code port

Replace `platform/codex/` with `platform/claude-code/`. Verify schemas, skills, CLI commands run unchanged. Document portability deltas.

## What's not on the roadmap (and why)

- Web UI, central artifact store, cross-repo synthesis, agent self-modification, auto-execution of cards. Future products or out of scope.

## Risks the roadmap accepts

- MVP's combined Surface Mapper produces lower-quality maps than split version. Acceptable: MVP is research-only by default.
- Per-artifact Skeptic in deep mode multiplies invocations. Acceptable in deep mode by definition.
- Project-type packs deferred to Phase E. Until then, runs on idiomatic Django apps will miss things a Rails-aware system would catch. Universal heuristics catch obvious surfaces.
- Interpretive challenges may accumulate without resolution on contested codebases. The handoff surfaces this; humans adjudicate.
