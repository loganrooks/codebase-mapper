# Architecture & Product Shape Review

Status: independent review
Last updated: 2026-05-01
Reviewer: external architecture auditor

## Executive verdict

CBM today is a deterministic structural extractor with strong artifact discipline, dressed in the schemas and provenance fields of an interpretive runtime that does not exist. The kernel is real, durable, and on the right side of the Vision. The "agents" — Surface Mapper, Skeptic, Authority Mapper, Dependency Mapper, Verification Mapper, Synthesis Index, Tracer, Refine, Approval Plan — are deterministic Python functions that emit artifacts stamped `produced_by: <role>@0.1` despite no agent ever running. This is the central architectural defect, and it is upstream of every other confusion in `.planning/` and `docs/`.

The single load-bearing decision is not "deterministic vs. runtime agents" — both are needed — but **who launches the runtime agents**. There are two coherent answers (CBM launches them; or an outer harness launches them and uses CBM as a tool). The current code accidentally implements neither, while the docs imply both. Pick one explicitly and a lot of the apparent disagreement between roadmap, vision, and STATE.md collapses into ordinary backlog.

The recommended shape is **Option C+E in the table below: CBM is a kernel + skill library that runtime agents call, with one canonical platform pack (Codex first) shipped to prove the contract**. This preserves ~all durable work, removes the false provenance problem, and lets the runtime layer evolve under the platform layer rather than inside the CLI.

## Observed facts

These are what the repo actually does, separated from interpretation.

### Code

- `cbm/cli.py` is ~4,525 lines, registering ~30 subcommands (`cbm/cli.py:4246-4399`). Console-script aliases are declared in `pyproject.toml:21-50`.
- The "Surface Mapper" implementation is `build_surface_map` (`cbm/cli.py:1071-1193`). It is pure Python: walks `codebase-map.json`, classifies authorities by filename pattern, runs Python AST import/call extraction, emits one hardcoded `edge-unknown-001`, and writes the artifact. It does not call any LLM.
- The "Skeptic" implementation is `review_dependency_graph` and `command_skeptic_review` (`cbm/cli.py:1277-1354`). It deterministically scans for any edge with `kind: unknown` and attaches a hardcoded challenge with hardcoded prose ("The dependency graph should not be read as complete while unknown dependency edges remain unresolved..."). It does not call any LLM. It does not read source. It cannot produce findings the schema's interpretive register requires (specific competing reading, specific competing evidence).
- `command_run` (`cbm/cli.py:4015-4083`) sequentially invokes `command_init`, `command_map`, `command_surface`, optionally `command_authority_map`, `command_skeptic_review`, `command_dependency_graph`, `command_verify_map`, `command_synthesis_index`, `command_bind`, optionally `command_trace_workflows`, `command_refine`, `command_approval_plan`, then `command_handoff`. No subprocess, no API call, no agent spawn anywhere in this path.
- The `tracer.md` skill exists (`skills/tracer.md`) but the deterministic `command_trace_workflows` is the only producer of workflow traces in the run path.

### Artifacts

- A real smoke run (`.research/run-phase-a-final-audit/surface-map.json`) carries `produced_by: surface-mapper@0.1` (line 6). No surface-mapper agent ran — `command_surface` produced it.
- Same run's `.research/run-phase-a-final-audit/skeptic-review/surface-map.md` carries `produced_by: skeptic@0.1`. No skeptic agent ran — `review_dependency_graph` produced it.
- Same run's surface map reports `coverage.result.files_examined_directly: 8` (line 32). The implementation sets that field to `len(authorities)` (`cbm/cli.py:1168` calls `coverage_block(..., examined=len(authorities))`). The Constitution defines `files_examined_directly` as files an agent or human opened and read (`RUNTIME-CONSTITUTION.md:209`). The CLI did not open any of these files; it pattern-matched their names. This is the exact misclassification §15 of the Constitution forbids.
- The same surface map's interpretive claims (e.g., `auth-008` `.codex/hooks.json` `claim_register: factual`) are emitted by the rule `claim_register = "factual" if kind in {"config", "ci_gate", "test_suite"} else "interpretive"` (`cbm/cli.py:1097`). No interpretive judgment is being made anywhere; the register is a string lookup.
- The "Skeptic challenge" `chl-00001` claims `interpretive_axis: completeness, relation_to_original: scope_dispute` and "competing_reading: ... unknown dependency closure ...". The competing_evidence is the citation of one arbitrary file already in the artifact. It is the same canned challenge in every smoke run from `run-phase-a-smoke-2` forward.

### Hooks

- The active `.codex/hooks.json` (and `platform/codex/hooks.json`) registers two lifecycle hooks: `SessionStart` calls `cbm hook-start`, `Stop` calls `cbm hook-stop` (`platform/codex/hooks.json:3-26`).
- `command_hook_start` and `command_hook_stop` (`cbm/cli.py:4116-4243`) operate on the latest run directory's `handoff.md`. They do not gate per-artifact writes. They do enforce evidence-ledger and uncertainty-register append-only manifests.
- These hooks are repo-local (in `.codex/`), not user-global. They do not install themselves into another repo. They do not require Codex to load global hook config. The Codex docs path was followed in `BUILD-LOG.md:88-100`.
- `cbm gate-artifact <artifact>` exists as the post-write gate, but no platform adapter wires it as an actual post-write hook. `platform/codex/gate-artifact.sh` is a 260-byte wrapper, manually invoked.

### Platform adapters

- `platform/codex/` has a working hook config and adapter README. It is the only working adapter.
- `platform/claude-code/` has a README only; no actual adapter exists. The portability checklist (`platform/PORTABILITY.md:19-32`) is satisfied only on Codex.

### Tests

- `tests/test_cli.py` is ~93k. The last reported result is `51 passed, 2 warnings` (`STATE.md:69-72`). All tests exercise the deterministic CLI's structural correctness. None of them exercise an agent producing a Surface Map / Skeptic Review against a non-trivial repo. The fixture `tests/fixtures/sample_repo/` is three files. There is no benchmark codebase committed.

### Build log pattern

- `BUILD-LOG.md` has ~30 entries from `2026-05-01` covering Phase A → mid Phase B. The pattern is "implement deterministic CLI command N → run smoke → next deterministic CLI command". At each self-critique the agent flags the same gap honestly: "this is deterministic scaffolding, not a real agentic Surface Mapper / Skeptic / Synthesizer." The gap is acknowledged ~20 times and never closed; new deterministic surface keeps shipping in front of it.

### Documents

- `VISION.md` is unambiguous about destination: a hermeneutic research instrument with runtime agent producers. It is also long (152 lines). It does not specify how the runtime agent layer is architected.
- `RUNTIME-CONSTITUTION.md` is constitutional for runtime agents that do not yet exist. Its rules are written for an LLM agent to follow ("Read the artifact in full. Do not skim.").
- `docs/architecture.md` describes a "modular deterministic kernel + agentic synthesis layer + goal packs" with five subagent role templates. None of those templates are wired in code.
- `docs/roadmap.md` Phase A acceptance is "end-to-end run, citations resolve, ≥1 actionable card, claim registers correctly assigned." The last criterion has been claimed met in `BUILD-LOG.md:163` because the CLI's *deterministic* surface map writes registers; whether they are *correctly* assigned is the question the deterministic implementation cannot answer.
- `AGENTS.md` is about the implementation agent (i.e., the LLM building CBM), not the runtime CBM agents. This distinction is correct and well-stated (`AGENTS.md:9-11`).
- `.planning/STATE.md` and `.planning/CURRENT-PLAN.md` are honest about the gap.

## Architecture options

The realistic shapes from here. Each option keeps the durable kernel; they differ on where the interpretive layer lives.

| Option | One-line | Where do agents run? | Who orchestrates? | Pros | Cons |
|---|---|---|---|---|---|
| **A. Pure deterministic CLI** | Drop the runtime agent layer; ship a high-quality structural extractor + corpus | nowhere | n/a | Honest, fast to finish, low complexity | Abandons the hermeneutic Vision; becomes a different product. |
| **B. CLI launches subprocess agents** | `cbm run` spawns `codex exec` (or equivalent) per skill, parses JSON-mode output, validates, advances | inside `cbm` process | `cbm` itself | Self-contained; one binary; testable in CI with model stubs | Couples CBM to a specific agent runtime; subprocess management; prompt/version/profile config inside the kernel; harder to use under an interactive harness. |
| **C. Outer agent orchestrates CBM subagents** | Codex/Claude Code session runs the orchestrator skill, spawns role subagents, calls CBM CLI as a tool | inside the host platform | the host platform | Clean separation: CBM is a tool, agents live in the platform; testing is simple; matches how dogfooding already happens | Requires the host platform to ship a working orchestrator; CBM cannot prove Vision adequacy without one. |
| **D. Hybrid baseline + pluggable agent backend** | `cbm baseline` is deterministic; `cbm map --backend codex|claude|http` invokes a configured backend | configurable | `cbm` (with backend abstraction) | Preserves both shapes; backend can be swapped per environment | Largest amount of new design; backend abstraction is one of the harder parts of any system to get right; risks doing none of B or C well. |
| **E. Tool + canonical platform packs** (recommended) | CBM is a CLI + schema + skill library. There is no `cbm run` that pretends to be agentic. Each platform ships a canonical orchestrator pack (Codex first) that uses the CLI as bedrock. | inside the host platform | the platform pack (a `cbm-codex` agent profile, a Claude Code subagent set, etc.) | Removes the false-agent problem; matches what the kit already mostly is; durable kernel does not depend on which runtime the user has; orchestrator can be iterated independently | Platform packs need to be real; without one, CBM is just a kernel; there is up-front cost to write the first pack |

Option C and Option E are very close. The difference is presentation: in C the host agent is doing the orchestrating ad hoc; in E the host agent loads a *canonical, versioned orchestrator pack shipped by CBM*. E is the version where CBM owns the orchestrator definition without owning the LLM runtime. That is the cleanest framing and the one I recommend.

## Findings

### Critical

1. **Mislabeled provenance is the central defect.** Artifacts produced by deterministic Python carry `produced_by: surface-mapper@0.1`, `produced_by: skeptic@0.1`, etc. Downstream consumers, hooks, and humans cannot tell whether interpretive work happened. This is the single change that, if reverted, makes the rest of the architecture misalignment visible and fixable. Today the system fails the "honest about what it didn't do" property in `VISION.md:31`.

2. **The Skeptic's deterministic stand-in violates its own constitution.** `RUNTIME-CONSTITUTION.md:70` says "A challenge without competing evidence is noise. The Skeptic does not raise vague disagreements." The implementation produces a single hardcoded challenge per run with reused boilerplate prose and an arbitrary citation lifted from the artifact under review. This is exactly the noise the constitution forbids. Worse, `BUILD-LOG.md:160` cites the existence of this challenge as evidence that "MVP proof 3, Skeptic catches ≥1 weak claim" is satisfied. It is satisfied formally and falsified materially.

3. **`coverage.result.files_examined_directly` is being lied about.** The Constitution makes this field load-bearing for which claims are defensible (`RUNTIME-CONSTITUTION.md:208-211`). The CLI sets it to a count of authority candidates that were never opened (`cbm/cli.py:1168`). Every interpretive claim in the surface map references files in this set. Per the Constitution's §15, every one of those interpretive claims is undefensible.

4. **`cbm run` impersonates an orchestrator.** The command name and the `command_run` signature (mode argument: lightweight | standard | deep) suggest it's the agent-orchestration surface described in `docs/architecture.md`. It is not. It is a deterministic pipeline. The `mode` argument changes which deterministic stand-ins fire, not which subagents run. This wording mismatch is the source of much of the planning-doc churn.

### Major

5. **The runtime agent boundary is not specified anywhere in code.** `skills/*.md` are skill prompts written for an LLM. Nothing imports them or invokes them. The integration point — how a skill prompt becomes an actual subagent run with input/output — is undefined. Until that boundary is specified, every prompt is an ornament.

6. **The schema requires fields the deterministic producer cannot honestly populate.** `claim_register`, `evidence_kinds`, `confidence`, `corroboration_count`, `rationale`, `produced_by` — all of these are interpretive judgments. The schema enforces presence; the CLI auto-fills them. The schemas are correctly designed for the runtime agent layer; using them for the deterministic baseline is what creates the false-provenance problem. Either the deterministic baseline should produce *different* artifacts (e.g., `codebase-map.json` only, plus structural-relation edges in a separate file), or the schemas need an honest "produced by deterministic kernel" mode that does not pretend to register.

7. **No real benchmark exists.** `tests/fixtures/sample_repo/` is three files. The roadmap requires a 5k-LOC repo for MVP exit. Smoke runs against this repository are unfit to demonstrate hermeneutic adequacy on unfamiliar codebases — the implementation agent and the runtime would share too much context.

8. **Hooks are sound but underbuilt.** The current `hook-start` / `hook-stop` are minimal lifecycle gates around the latest run; they do enforce append-only ledger integrity, which is real value. They are not "ambient global hooks" and the warning in `AGENTS.md:44` against installing user-global hooks is correct. But there is no post-write hook actually wired by an adapter — `cbm gate-artifact` exists and `platform/codex/gate-artifact.sh` exists, but no `.codex/hooks.json` event triggers it. The post-artifact-write enforcement promised in `docs/contracts.md:188` is not actually live.

9. **`docs/architecture.md` and `docs/contracts.md` describe a system that does not exist.** The architecture doc says "Tier 2 — Agentic synthesis (subagents): Five agent role templates" and the contracts doc lists hooks like "spawn Skeptic per mode policy". Nothing in the codebase spawns a subagent. These documents need an "as designed" vs. "as built" split, or to be updated to match reality, or to be moved into a `RUNTIME-DESIGN.md` that is clearly aspirational.

10. **The deterministic stand-ins are closing the gap they were meant to leave open.** Each "deterministic Authority Mapper / Dependency Mapper / Verification Mapper / Synthesizer / Tracer / Refine / Approval Plan" was added to satisfy a roadmap acceptance criterion mechanically. Each one creates a pre-existing artifact slot that the real subagent will then have to overwrite or compete with. Schemas and tests now encode the structural shape produced by the stand-ins; that's the shape the eventual real agents will be measured against. This is path-dependent foreclosure of the runtime layer's freedom.

### Minor

11. **The active hooks remain in this repository's `.codex/`.** They are clearly dogfooding. `STATE.md:85` already notes their final role is unsettled. They should either be moved into `platform/codex/` only (template, not live) or kept as live with a comment in `README.md` calling out that they are dogfood.

12. **Console-script proliferation.** ~30 `cbm-*` scripts are declared in `pyproject.toml`. Many are deferred-from-MVP per `roadmap.md`. The count itself is a symptom of "kernel feature creep before runtime layer settled."

13. **`docs/roadmap.md` mode taxonomy (lightweight/standard/deep) is implementation-coupled to the deterministic stand-ins.** Real modes are runtime-agent dispatch policy. Today's `--mode` flag picks how many deterministic stubs fire.

## Recommended architecture

Adopt **Option E**: CBM is a tool + schema + skill library. The deterministic CLI is a kernel; runtime agents live in platform packs.

Concretely, the system has three layers:

### Layer 1 — Deterministic kernel (already exists, mostly durable)

- `.research/<run_id>/` directory shape.
- Schemas for codebase-map, surface-map, authority-map, dependency-graph, verification-map, evidence-ledger, uncertainty-register, refresh-delta, intervention/findings card, handoff.
- Deterministic baseline producer: `cbm baseline` (rename of today's `cbm map` semantics, expanded). Produces *only* artifacts that don't require interpretive judgment: `codebase-map.json`, structural extractor outputs (imports, calls, public-api), `extractor-registry.json`, the uncertainty register seed.
- Validation gates: `cbm validate`, `cbm verify-citations`, `cbm gate-artifact`, `cbm check-evidence`, `cbm extractor-registry validate`.
- Freshness layer: `cbm validate-fresh`, `cbm verify`, `cbm corpus-status`, `cbm refresh`, `cbm consult`. These are durable and useful even when no agent has run.
- Lifecycle hooks: `cbm hook-start`, `cbm hook-stop` for append-only and freshness integrity.
- Append-only manifests for ledger and uncertainty register.

### Layer 2 — Runtime skill library (already exists in prompts; needs an integration contract)

- `skills/*.md` is the canonical skill prompt set. Versioned by `Skill version`.
- `RUNTIME-CONSTITUTION.md` is binding on whatever process loads the skill.
- A new explicit document — call it `docs/runtime-contract.md` or extend `contracts.md` — specifies the *integration contract*: what inputs an agent gets, what artifact paths it must write, what produced-by string it must use, what minimum claim-register discipline applies. This contract is platform-agnostic.
- Schemas should grow a `producer_class` enum (`deterministic | agent | human`) so `produced_by` can be honest in both directions. Implementation: bump `schema_version` minor; add the field as required; backfill deterministic outputs with `producer_class: deterministic`.

### Layer 3 — Platform packs (need work)

- A platform pack is the orchestrator: it knows how to load skills, spawn role subagents, route artifacts through gates, and obey the runtime contract.
- The first pack is `platform/codex/`. It should contain:
  - A profile / configuration that maps each skill to a Codex agent definition.
  - The hook configuration that gates artifact writes via `cbm gate-artifact`.
  - The orchestrator entry (Codex prompt or `codex exec` invocation script) that wraps the run loop.
- `platform/claude-code/` is a placeholder until verified.
- A platform pack ships its own README and its own portability assertions per `platform/PORTABILITY.md`.

### What this means for `cbm run`

Two acceptable shapes; pick one:

- **Rename**: today's `cbm run` becomes `cbm baseline`. There is no `cbm run` command in the kernel. The orchestrator entry is platform-specific.
- **Re-scope**: `cbm run` keeps its name but does only what's deterministic, with a frontmatter / output indicator that no agentic step happened. Mode flag is removed (mode is platform-pack policy, not kernel policy).

The first is cleaner. The second is less disruptive.

### What dies cleanly

- The deterministic stand-ins for Skeptic, Authority Mapper, Dependency Mapper, Verification Mapper, Synthesis Index, Tracer, Refine, Approval Plan, in their current "produces an artifact stamped as if an agent ran" form.

What happens instead:
- The skeptic-review artifacts and synthesis-index artifacts continue to exist as schemas, but they are populated only when a real agent (in a platform pack) runs.
- `cbm baseline` may produce a *separate*, honestly-named "structural-relation extractor output" that the real Surface Mapper ingests. It does not pretend to be a surface map.

### What stays

- All schemas, the citation format, the ledger discipline, the freshness/refresh/consult layer, the extractor registry, hooks-as-gates, the run directory layout, the validation commands. Probably 70–80% of the current ~4500-line CLI.

## Risks and tradeoffs

- **Demoting `cbm run` is psychologically expensive.** A lot of the build log and roadmap success criteria are framed around `cbm run` being end-to-end. They will read as regressions. This is honesty cost; it pays for itself once Codex orchestrator runs end-to-end with real agents.
- **Without a working platform pack, CBM does not demonstrate Vision.** The risk of Option E is that nobody ships the pack and CBM stays a kernel forever. Mitigation: the next slice after the architecture decision is *exactly* the first Codex platform pack, with one real agent role (Surface Mapper or Skeptic) producing one artifact end-to-end on a small but real repo (a small MCP server is a reasonable benchmark target).
- **Schema migration to add `producer_class` is a v1.2 → v1.3 bump.** This is a real cost; existing artifacts under `.research/` will look stale. Mitigation: deterministic backfill script; legacy artifacts grandfather as `producer_class: deterministic` since that's what they were.
- **If the user actually wants Option B (CBM launches subprocess agents)**, then a lot of this analysis is wrong. Option B and Option E differ on where subprocess management lives. Option B is *plausible* — `codex exec --output-schema` is real — but it puts CBM on a treadmill of supporting model versions, prompt formats, retry semantics, and rate-limit handling. Option E puts that in the platform pack, where it belongs.
- **Option C/E doesn't resolve who provides the orchestrator** for users who don't have Codex or Claude Code. Mitigation: a third "scripted orchestrator" pack (a plain Python script that simulates the orchestrator using user-supplied agent endpoints) can ship later as a fallback.
- **The deterministic stand-ins have produced real value as test fixtures.** Removing them naively breaks tests. Mitigation: convert them to "canonical example artifact generators" used only in tests, not in `cbm run`.
- **Hooks: the architecture says hooks are not the source of truth, and the implementation agrees.** The remaining question is whether the live `.codex/hooks.json` should stay in this repo. Recommendation: keep them, since this is a CBM-development repo and dogfooding is a feature; document explicitly in `README.md` that they are for this repo only and `platform/codex/` is the template intended for users.

## Decisions required from the user

These are the decisions blocking the next implementation slice. The first is load-bearing; the rest mostly fall out of it.

1. **Who launches runtime agents?** Pick one:
   - (A) CBM launches them (Option B in the table). Implies subprocess-management code goes inside `cbm/`.
   - (B) The host platform launches them; CBM is a tool (Options C/E). Implies the next slice is a platform pack, not a CLI feature.

2. **What happens to today's deterministic stand-ins?** Pick one:
   - Rename and demote them to "baseline" producers with honest `producer_class: deterministic`.
   - Delete them; let the schemas wait until real agents land.
   - Keep them temporarily but stop calling them in `cbm run`; expose them only as `cbm dev-stub-<role>` for fixture generation.

3. **Schema version: v1.2 stays, or v1.3 with explicit `producer_class`?** This is a small change but contract-bearing. Decision affects whether the false-provenance fix lands now or later.

4. **Is `cbm run` renamed to `cbm baseline`, kept and re-scoped, or removed?** Affects roadmap acceptance language and existing tests/smoke runs.

5. **Benchmark repo.** Which small real-world repo (MCP server, small CLI, small library) becomes the first non-fixture target? `STATE.md:103` already lists this question; it should not slip past this decision.

6. **`docs/architecture.md` and `docs/contracts.md` posture.** Pick one:
   - Edit to match what is built today (deterministic kernel only); push runtime-agent design into a separate aspirational doc.
   - Mark them "as designed" with a top-of-file caveat and ship `STATE.md` as the live ledger.

7. **`docs/roadmap.md`: revise or retire?** Recommended: replace with a runtime-agent-centric roadmap whose phases are scoped by platform-pack milestones, not CLI command counts.

## Concrete next steps

In order. Items 1–3 are non-code; 4–8 are first-slice work after the architecture decision. None should run in parallel with the others until item 1 is decided.

1. **Decide question 1 above** (who launches agents). Record the decision in `.planning/STATE.md` and `.planning/CURRENT-PLAN.md`. This is a one-paragraph commit; it unblocks everything else.

2. **Stop the deterministic stand-ins from claiming agent provenance.** Even before the architecture decision, change `produced_by` on artifacts emitted by `command_surface`, `command_skeptic_review`, `command_authority_map`, `command_dependency_graph`, `command_verify_map`, `command_synthesis_index`, `command_trace_workflows`, `command_refine`, `command_approval_plan` to honest strings (`cbm-baseline-surface@<v>`, `cbm-baseline-skeptic@<v>`, etc.). Same for `coverage.result.files_examined_directly`: it should be 0 unless an agent actually opened the file. Same for the canned challenge: stop emitting it; let the unknown edge stay `claim_status: active` until a real Skeptic moves it. This is a single PR; tests will need updating, but it removes the most damaging architectural lie in the repo.

3. **Update the hot docs.** `docs/architecture.md` and `docs/contracts.md` get a header: "This document describes the target runtime architecture. Sections marked Built describe what the kernel CLI delivers today. Sections marked Designed describe what the runtime layer will deliver." Or split into `docs/architecture-as-designed.md` and `docs/architecture-as-built.md`.

4. **Write `docs/runtime-contract.md`** (~one page). Specify what an agent producing artifact X gets as input, what file paths it writes, what `produced_by` string it must use, what minimum register discipline applies, and how the parent invokes `cbm gate-artifact` after each write. This is the integration contract the platform packs will obey.

5. **First platform-pack slice.** Pick one role (recommend Surface Mapper, since the deterministic version exists for diff comparison). In `platform/codex/`, add the Codex artifacts (profile/config + spawn invocation) for a real Surface Mapper agent run. The agent reads `codebase-map.json`, examines K files directly, writes a `surface-map.json` honoring the runtime contract. Validate via existing gates. Run on a small real benchmark repo. Compare to deterministic stand-in output to confirm divergence is real.

6. **Pick a benchmark.** A small open-source MCP server is a reasonable first target (5–10k LOC, mixed language, idiomatic Python). Pin its SHA. Commit the benchmark URL+SHA in `tests/benchmarks/`.

7. **Roadmap rewrite.** After the first platform-pack slice produces an honest agent-authored artifact, rewrite `docs/roadmap.md` so phases track platform-pack capabilities, not CLI command counts. Phase A becomes "deterministic kernel + first agent role end-to-end on benchmark." Phase B becomes "all five MVP agent roles + standard mode on benchmark." Etc.

8. **Hooks final disposition.** Decide whether `.codex/hooks.json` stays live in this repo (recommended: yes, with a clear README note) or moves to template-only. Decide whether `cbm gate-artifact` should be wired by `platform/codex/` as an actual `PostToolUse` hook for artifact writes during runtime-agent runs.

The single thing the user can do today, without code, that unblocks the most: **write down which person or process launches runtime agents.** Everything else is downstream of that sentence.
