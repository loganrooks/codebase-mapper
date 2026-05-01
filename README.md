# CBM — Codebase Mapping & Intervention Planning Seed Kit

**Schema version: 1.2.** A seed kit for building an agentic system that maps arbitrary codebases and produces evidence-backed intervention plans. Designed Codex-first.

## What this kit is

This is **not** the system. It is the seed: the contracts, prompts, and architectural commitments needed to build the system using AI agents. A builder (human or agent) reads these docs and produces an implementation.

For the destination — what the system looks like when it is no longer a beta — see [`VISION.md`](VISION.md). It names the maturity criteria, the user the system serves, the experience of a mature run, and the things the system will explicitly not become.

## What the system does

Given a repository and a user goal, produce **intervention cards** (or research-only **findings cards**): evidence-backed proposals for changes, refactors, extension points, audits, migrations, or follow-up investigations. Every claim cites real bytes at a real revision. Every recommendation has a verification strategy. Every claim is labeled as factual, inferential, or interpretive — and the system handles each register differently.

The system supports goals from "understand this unfamiliar repo" to "plan a migration" to "produce research-only findings without implementation," across project types from prototypes to mature production systems.

## What's new in v1.2

- **Reuse made operational.** Five forms of reuse with documented workflows: goal-agnostic cache (different goals, same SHA, no re-mapping); incremental update; historical consultation (old artifacts as pinned readings); consultation mode (`cbm-consult` answers questions from the corpus); cross-run synthesis (deferred to v2.0).
- **Five staleness modes.** Validate, verify, refresh structural, refresh interpretive, re-run — escalating cost, decreasing interpretive continuity preserved. Pick the cheapest that addresses the question.
- **Refresh delta as first-class artifact.** New schema records carried_forward, updated, retracted, newly_added, newly_contested, plus per-challenge and per-open-question reconciliation status. The corpus accumulates trajectory, not just snapshots.
- **Optional `refreshed_from`** lineage block on artifacts that can be refreshed.
- **Reader skill (`consult.md`)** for read-existing-artifacts-without-rerunning.
- **Surface Mapper differential refresh mode** with migration protocol.
- **Compaction recovery integrates `cbm-validate-fresh`** so session resume never silently uses stale inputs.
- **`RUNTIME-CONSTITUTION.md` §25 on reuse and refresh discipline.** (See note below on the AGENTS.md / RUNTIME-CONSTITUTION.md split.)

## What's new in v1.1

- **Three-register claim model.** Every claim is `factual`, `inferential`, or `interpretive`. The Skeptic operates differently in each register: defect-finding for factual, inference-rule scrutiny for inferential, and *alternative-raising* for interpretive. Hermeneutic claims (about role, centrality, salience, framing) become first-class instead of being smuggled in as factual.
- **Claim-status lifecycle.** `active → challenged → contested → contradicted → superseded → retired`. Challenges are first-class: a competing reading with its own evidence, rather than a defect demanding withdrawal.
- **Evidence kinds.** Replaces the linear E1–E5 quality ladder with an orthogonal multi-set: `static_structure`, `static_relation`, `command_output`, `runtime_trace`, `maintainer_statement`, `external_doc`. Appropriateness is claim-relative; the Skeptic enforces a per-claim-type requirements table.
- **Extractor registry.** A typed catalogue of deterministic extractors with declared, mandatory `known_blind_spots`. Edges cite extractors by id; the Skeptic looks up blind spots when reviewing claims.
- **Coverage metadata.** Distinguishes `files_examined_directly` (an agent or human read it) from `files_inspected_via_extractor` (parsed deterministically without being read). Interpretive claims about a file require direct examination.
- **Three-mode execution.** Source mutation forbidden; declared verification commands runnable via `cbm-run-gate` with safety envelopes; external system access only with per-access approval.
- **Declarative staleness** with `depends_on_paths` and `scope_signature`.

## Two constitutions, two audiences

This kit has **two** constitution files, for two different audiences:

- **`AGENTS.md`** — for the agent (Codex, Claude, or a human) **developing CBM** from this seed kit. Read first if your job is to build CBM. Short; tells you how to operate against the rest of the kit.
- **`RUNTIME-CONSTITUTION.md`** — for the runtime CBM agents (Surface Mapper, Skeptic, Synthesizer, Intervention Planner, Reader) operating *inside* a CBM run on someone's codebase. This file is shipped with the implementation, not absorbed by the developer. (Implementations may rename it `AGENTS.md` in the deployed system, where the runtime agents are the ones operating in the directory.)

If you are unpacking this kit and pointing Codex `/goal` at `VISION.md`, the agent reading `AGENTS.md` is the dev agent — and the dev-agent file is the right thing for it to read. The runtime constitution is preserved separately for shipping.

## Reading order

1. **`AGENTS.md`** — if you are the dev agent or directing one. Stop here on first pass.
2. **`VISION.md`** — the destination. The maturity criteria there are what mature CBM looks like; what you are building toward.
3. **`docs/roadmap.md`** — what to build first. Phases are real gates.
4. **`RUNTIME-CONSTITUTION.md`** — the rules the runtime agents (the ones your implementation spawns) must follow. 25 sections; §3 covers the three-register claim model, §7 the claim-evidence requirements table, §17 the Skeptic's three modes, §25 reuse and refresh discipline.
5. **`docs/architecture.md`** — kernel + synthesis + goal packs, agent suite, phase model, the claim-register model, the reuse-and-refresh model.
6. **`docs/contracts.md`** — CLI command contracts, artifact catalog, claim-evidence requirements, hook integration points.
7. **`docs/reuse-and-refresh.md`** — five forms of reuse, five staleness modes, migration protocol.
8. **Skills** (`skills/*.md`) — runtime agent prompts. Loaded at runtime by the implementation, not absorbed by the dev agent.
9. **Schemas** (`schemas/*.json`) — JSON Schemas for every durable artifact. Authoritative; do not modify without explicit version bump.
10. **Example** (`examples/intervention-card-example.md`) — validation target. Your implementation produces artifacts shaped like this.

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
README.md                            this file (orientation)
AGENTS.md                            for the agent developing CBM (read first if that's you)
VISION.md                            end-state, maturity criteria, ideal version, anti-vision
RUNTIME-CONSTITUTION.md              constitution for runtime CBM agents (shipped with implementation)
docs/
  architecture.md                    the design (incl. three-register claim model, reuse-refresh model)
  contracts.md                       CLI + artifact catalog + claim-evidence table
  reuse-and-refresh.md               five forms of reuse, five staleness modes, migration protocol
  roadmap.md                         MVP, modes, deferred work, v1.1 and v1.2 changelogs
schemas/
  codebase-map.schema.json           deterministic structural baseline
  surface-map.schema.json            authorities + edges + verification (claim registers, challenges)
  intervention-card.schema.json      cards (claim_register on leverage, dependent_challenges)
  evidence-ledger.schema.json        append-only run log (with challenge entry kinds)
  handoff.schema.json                final run output (with contestation summary)
  extractor-registry.schema.json     typed extractor catalogue with declared blind spots
  refresh-delta.schema.json          v1.2: trajectory artifact for refresh runs
skills/
  surface-mapping.md                 produces surface-map.json; v1.2 differential refresh mode
  synthesizer.md                     cross-references; propagates contestation
  intervention-planner.md            card producer; treats leverage as interpretive
  skeptic.md                         hostile reviewer with three-mode protocol
  consult.md                         v1.2 Reader; answers from existing corpus or refuses
  compaction-recovery.md             session resume; v1.2 calls cbm-validate-fresh
examples/
  intervention-card-example.md       findings card with leverage challenge + dependent_challenges
```

That's twenty-two files total. The split of the original `AGENTS.md` into a dev-agent `AGENTS.md` and a runtime `RUNTIME-CONSTITUTION.md` is the operational change in this v1.2 amendment — schemas and runtime behavior are unchanged from v1.2's earlier release.

## What's deferred

- The **Tracer** skill (workflow tracing for runtime understanding) is part of the design but not seeded here. Add when standard mode proves out.
- **Goal packs** (specializations for `feature_add`, `refactor`, `migration`, etc.) are designed for but not seeded.
- **`cbm-run-gate`** for executing declared verification commands is contract-specified but not in MVP — added in standard mode (Phase B).
- **Project-type packs** (Django, Rails, MCP-server, monorepo) deferred to Phase E. Each will ship with type-specific extractor registry annotations.
- **Cross-run synthesis** (stable cross-run claim IDs, project-level claim register, persistent contestation across many independent runs) is v2.0 work. Within-lineage refresh handles same-codebase trajectory; the bigger persistence story is named in `VISION.md` open conjectures.

See `docs/roadmap.md`.
