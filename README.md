# CBM — Codebase Mapping & Intervention Planning Seed Kit

**Schema version: 1.1.** A seed kit for building an agentic system that maps arbitrary codebases and produces evidence-backed intervention plans. Designed Codex-first.

## What this kit is

This is **not** the system. It is the seed: the contracts, prompts, and architectural commitments needed to build the system using AI agents. A builder (human or agent) reads these docs and produces an implementation.

## What the system does

Given a repository and a user goal, produce **intervention cards** (or research-only **findings cards**): evidence-backed proposals for changes, refactors, extension points, audits, migrations, or follow-up investigations. Every claim cites real bytes at a real revision. Every recommendation has a verification strategy. Every claim is labeled as factual, inferential, or interpretive — and the system handles each register differently.

The system supports goals from "understand this unfamiliar repo" to "plan a migration" to "produce research-only findings without implementation," across project types from prototypes to mature production systems.

## What's new in v1.1

- **Three-register claim model.** Every claim is `factual`, `inferential`, or `interpretive`. The Skeptic operates differently in each register: defect-finding for factual, inference-rule scrutiny for inferential, and *alternative-raising* for interpretive. Hermeneutic claims (about role, centrality, salience, framing) become first-class instead of being smuggled in as factual.
- **Claim-status lifecycle.** `active → challenged → contested → contradicted → superseded → retired`. Challenges are first-class: a competing reading with its own evidence, rather than a defect demanding withdrawal.
- **Evidence kinds.** Replaces the linear E1–E5 quality ladder with an orthogonal multi-set: `static_structure`, `static_relation`, `command_output`, `runtime_trace`, `maintainer_statement`, `external_doc`. Appropriateness is claim-relative; the Skeptic enforces a per-claim-type requirements table.
- **Extractor registry.** A typed catalogue of deterministic extractors with declared, mandatory `known_blind_spots`. Edges cite extractors by id; the Skeptic looks up blind spots when reviewing claims.
- **Coverage metadata.** Distinguishes `files_examined_directly` (an agent or human read it) from `files_inspected_via_extractor` (parsed deterministically without being read). Interpretive claims about a file require direct examination.
- **Three-mode execution.** Source mutation forbidden; declared verification commands runnable via `cbm-run-gate` with safety envelopes; external system access only with per-access approval.
- **Declarative staleness** with `depends_on_paths` and `scope_signature`.

## Reading order

1. **`AGENTS.md`** — the constitution. Operational rules every agent must follow. Drops into real projects as-is. (24 sections; §3 covers the three-register claim model, §7 the claim-evidence requirements table, §17 the Skeptic's three modes.)
2. **`docs/architecture.md`** — kernel + synthesis + goal packs, agent suite, phase model, the claim-register model.
3. **`docs/contracts.md`** — CLI command contracts, artifact catalog, claim-evidence requirements, hook integration points.
4. **`docs/roadmap.md`** — MVP scope, mode taxonomy, deferred work, v1.1 changelog.
5. **Skills** (`skills/*.md`) — the agent prompts. Skeptic skill is the largest in v1.1 because of the three-mode protocol.
6. **Schemas** (`schemas/*.json`) — JSON Schemas for every durable artifact. Validation runs on every write.
7. **Example** (`examples/intervention-card-example.md`) — worked findings card showing claim_register on leverage, a populated `dependent_challenges` block, and a card propagating an interpretive challenge from the surface map.

## Core commitments

- **Evidence over assertion.** Every claim cites `path:lines@sha` and carries a `claim_register`. No claim without a citation; no citation that doesn't resolve.
- **Determinism before judgment.** Mechanical work (file inventory, import extraction, build graph) belongs in CLI tools that emit JSON, run by extractors with declared blind spots. Agents synthesize over machine-readable artifacts; they do not produce raw structural truth.
- **Three-register claims, three Skeptic modes.** Factual claims face defect-finding; inferential claims face inference-rule scrutiny; interpretive claims face alternative-raising. Mismatching register and protocol corrupts the artifact.
- **Goal-agnostic baseline.** The codebase map and surface maps contain no reference to a user goal. Goals enter only at the binding phase.
- **Hard gates are mechanical.** Schema validation, citation resolution, append-only ledger checks, and the per-claim-type evidence-kinds check are deterministic. Confidence, leverage, and risk are advisory and never block.
- **Skeptic by default.** A hostile reviewer with isolated context runs at every gate boundary.
- **Artifacts on disk, always.** State lives in files, not in agent context. Compaction and crashes are routine; recovery reads disk.
- **Unknown is a first-class category.** Dependency graphs report unknown edges as edges. A graph with zero unknowns is suspect.
- **Coverage is honest.** Distinguishes direct examination from extractor-only inspection.
- **Contestation propagates.** Cards built on challenged claims carry the contestation forward via `dependent_challenges`. The system does not collapse interpretive disagreement to look stronger.

## What this kit refuses to do

- It does not promise full coverage of any codebase. Coverage is reported with partitions (`certain | suspected | advisory | unknown`) and per-file (`examined_directly | inspected_via_extractor | unread`).
- It does not produce a single confidence number for the system. Confidence is per-claim.
- It does not let agents recommend interventions from context they didn't write down.
- It does not auto-resolve interpretive disagreement. Contested claims stay contested in the artifact until a human or new evidence adjudicates.
- It does not commit to platform features it cannot verify in official documentation.

## Platform notes

Codex-first. Codex hooks and subagents are confirmed to exist (per the user). Specific hook syntax and subagent definition format are not verified in this kit; only the platform glue files (in a future `platform/codex/`) need to change between platforms. Schemas, skills, and CLI contracts are platform-neutral.

## File map

```
README.md                            this file
AGENTS.md                            constitution (24 sections); ships with every implementation
docs/
  architecture.md                    the design (incl. three-register claim model)
  contracts.md                       CLI + artifact catalog + claim-evidence table
  roadmap.md                         MVP, modes, deferred work, v1.1 changelog
schemas/
  codebase-map.schema.json           deterministic structural baseline
  surface-map.schema.json            authorities + edges + verification (claim registers, challenges)
  intervention-card.schema.json      cards (claim_register on leverage, dependent_challenges)
  evidence-ledger.schema.json        append-only run log (with challenge entry kinds)
  handoff.schema.json                final run output (with contestation summary)
  extractor-registry.schema.json     typed extractor catalogue with declared blind spots
skills/
  surface-mapping.md                 produces surface-map.json with claim registers
  synthesizer.md                     cross-references; propagates contestation
  intervention-planner.md            card producer; treats leverage as interpretive
  skeptic.md                         hostile reviewer with three-mode protocol
  compaction-recovery.md             session resume; surfaces active contestation
examples/
  intervention-card-example.md       findings card with leverage challenge + dependent_challenges
```

That's seventeen files total: one new schema (`extractor-registry.schema.json`) and the example reworked to demonstrate v1.1 features.

## What's deferred

- The **Tracer** skill (workflow tracing for runtime understanding) is part of the design but not seeded here. Add when standard mode proves out.
- **Goal packs** (specializations for `feature_add`, `refactor`, `migration`, etc.) are designed for but not seeded.
- **`cbm-run-gate`** for executing declared verification commands is contract-specified but not in MVP — added in standard mode (Phase B).
- **Project-type packs** (Django, Rails, MCP-server, monorepo) deferred to Phase E. Each will ship with type-specific extractor registry annotations.

See `docs/roadmap.md`.
