# Contracts

CLI commands, artifact catalog, citation format, validation chain, and hook adapter points. Schemas live in `schemas/`.

## Citation format

```
path/to/file.ext:START-END@SHA
```

- Repository-relative path, forward slashes.
- Inclusive line range. Single-line: `path:LINE@SHA`.
- Full or short SHA.

Cross-artifact references use JSON Pointer: `.research/<run_id>/dependency-graph.json#/edges/47`.

## Schema source

CBM validates generated artifacts against CBM's own schema source, not against arbitrary files in the target repository. Lookup order is: `CBM_SCHEMA_DIR` when set, the CBM checkout's `schemas/` directory, then a target-local `schemas/` directory only as a legacy fallback. Benchmark targets do not need copied CBM schemas.

## Universal frontmatter (v1.2)

```yaml
schema_version: "1.2"
artifact_type: <type>
run_id: <run_id>
produced_at: <ISO 8601 UTC>
produced_by: <role + skill version>
source_sha: <commit SHA>
inputs:
  - path: <artifact path>
    sha256: <hex digest>
status: draft | validated | reviewed | retired
coverage:
  scope:
    included_globs: [...]
    excluded_globs: [...]
  result:
    files_in_scope: <int>
    files_examined_directly: <int>
    files_inspected_via_extractor: <int>
    files_unread_in_scope: <int>
  limitations: [...]
staleness:
  stale_if_input_hash_changes: true
  depends_on_paths: [...]
  scope_signature: <hash>
refreshed_from:                       # optional; absent means fresh artifact
  artifact_path: <prior artifact>
  source_sha: <prior SHA>
  refresh_mode: structural | interpretive
  refresh_delta_path: <delta artifact>
```

## CLI command catalog

### `cbm-init`

Initialize a run. `--repo`, `--goal`, `--mode`. Writes `intake.json`, `state.json`, `extractor-registry.json` (default extractors for detected languages).

### `cbm-map`

Phase-1 deterministic baseline. Wraps per-language and per-system extractors declared in the registry. Outputs `codebase-map.json`. Schema-validated.

### `cbm-deps <lang>`

Per-language dependency extraction. Edges include `extractor_id` from registry.

### `cbm-verify-citations <artifact>`

Resolve every citation. Stdout per-citation status. Exit 0 if all ok.

### `cbm-validate <artifact>`

JSON Schema validation. Exit 0 on success.

### `cbm-stale <artifact>`

Compare recorded inputs and `staleness.depends_on_paths` to current state. Exit 0 fresh, 2 stale.

### `cbm-validate-fresh <artifact>` (v1.2)

Mode 1 staleness check. Re-hash every cited file at current HEAD; compare to citations' recorded SHAs. Output: per-citation freshness status. Cheaper than `cbm-verify`; does not re-resolve line ranges, only file-level hashes. Used by `compaction-recovery` on session start and as a precondition for `cbm-consult`. Exit 0 if all citations resolve at unchanged bytes; exit 2 with report otherwise.

### `cbm-verify <artifact>` (v1.2)

Mode 2 staleness check. Re-resolve every citation at current HEAD: file present? lines exist? bytes unchanged? Output: per-citation `still_grounded | needs_review | broken`. More expensive than `cbm-validate-fresh`; produces a verify report (artifact_type: `verify_report`) annotating each claim with current freshness state. Does not rewrite the artifact.

### `cbm-corpus-status` (v1.2)

Walks `.research/`, reports per-artifact freshness against current HEAD. Distinguishes "fresh," "stale (codebase moved)," and "pinned (still valid as historical reading)." Output is human-readable summary plus a machine-readable manifest. Use to decide which artifacts to refresh, consult, or leave alone.

### `cbm-refresh <artifact> --mode <structural|interpretive>` (v1.2)

Mode 3 or 4 refresh.

- `--mode structural`: re-runs the deterministic kernel at HEAD; updates the codebase map; emits a refresh delta listing added/removed/changed files; marks downstream interpretive artifacts as needing review.
- `--mode interpretive`: invokes the Surface Mapper in differential mode with the prior surface map as input; produces a successor surface map plus a refresh delta documenting what carried forward, what changed, what was retracted, what is new, what is newly contested.

Mode 5 (re-run) is just `cbm-init` again.

### `cbm-consult <question>` (v1.2)

Reader skill invocation. Identifies relevant artifacts from `.research/`; runs `cbm-validate-fresh` first; surfaces grounded answers from the corpus or refuses if the answer isn't there or freshness is too poor to trust. Output: a consultation response (markdown) plus optional ledger appends (`citation_reused`).

### `cbm-loop-status` (recovery)

Read-only recovery preflight. Checks that live planning files exist, authority/planning docs are not dirty, the requested recovery work category is allowed, and the checkpoint gate is satisfied for broad `/goal` scope. `--scope recovery-slice` reports a pending checkpoint as a warning; `--scope broad-goal` exits nonzero until the checkpoint is accepted or waived.

### `cbm-bind <goal-string>`

Produce `goal-binding.json`. Lists candidate surfaces with map citations and status flags (active/challenged/contested/contradicted). `cbm-bind` does **not** commit to a single intervention.

### `cbm-handoff`

Assemble handoff bundle. Pre-checks: schema, citations, ledger consistency, staleness, verification non-empty on cards, contestation summary populated.

### `cbm-gate <artifact>`

Composite check: schema + citations + staleness + (cards) verification non-empty + (graphs) unknown partition present + (claims) evidence-kinds matches RUNTIME-CONSTITUTION.md §7 table for each claim type.

### `cbm-run-gate <gate-id>` (standard+ mode)

Run a verification command declared in `verification-map.ci_gates`.

- **Inputs**: gate id, current user-approved safety envelope.
- **Pre-check**: gate's declared `safety_envelope` is within user-approved envelope. Refuse if not.
- **Execution**: runs in sandbox per envelope (network, install, mutation, max duration).
- **Output**: persists stdout/stderr to `command-outputs/<gate-id>-<ts>.txt`. Records `evidence_id`, `exit_code`, `duration_seconds`, `output_artifact_path`. Appends `command_executed` ledger entry.
- **Must not decide automatically**: whether failure is acceptable. Returns exit code; downstream interpretation is the agent's or human's.

### `cbm-extractor-registry validate`

Validate the extractor registry against its schema. Confirm every extractor has `known_blind_spots` non-empty.

### `cbm-challenge raise --claim <id> --artifact <path>` (interactive, post-MVP)

Programmatic interface for raising a challenge from a human reviewer. Defers to MVP+; for now, challenges come from the Skeptic only.

## Artifact catalog (v1.2)

| Artifact | Type | Path | Writer | MVP |
|---|---|---|---|---|
| `intake.json` | json | `intake.json` | `cbm-init` | yes |
| `state.json` | json | `state.json` | orchestrator | yes |
| `extractor-registry.json` | json | `extractor-registry.json` | `cbm-init` | yes |
| `codebase-map.json` | json | `codebase-map.json` | `cbm-map` | yes |
| `surface-map.json` | json | `surface-map.json` | Surface Mapper | yes |
| `authority-map.json` | json | `authority-map.json` | Authority Mapper | post-MVP |
| `dependency-graph.json` | json | `dependency-graph.json` | Dependency Mapper | post-MVP |
| `verification-map.json` | json | `verification-map.json` | Verification Mapper | post-MVP |
| `workflow-traces/*.json` | json | `workflow-traces/<n>.json` | Tracer | post-MVP |
| `synthesis-index.json` | json | `synthesis-index.json` | Synthesizer | yes (collapsed in MVP as `synthesis-notes.md`) |
| `uncertainty-register.jsonl` | jsonl | `uncertainty-register.jsonl` | all agents | yes |
| `evidence-ledger.jsonl` | jsonl | `evidence-ledger.jsonl` | all agents | yes |
| `goal-binding.json` | json | `goal-binding.json` | `cbm-bind` | yes |
| `interventions/<id>.md` | md+yaml | `interventions/<id>.md` | Planner | yes |
| `findings/<id>.md` | md+yaml | `findings/<id>.md` | Planner (research-only) | yes |
| `skeptic-review/<a>.md` | md+yaml | `skeptic-review/<a>.md` | Skeptic | yes |
| `command-outputs/<id>-<ts>.txt` | txt | `command-outputs/...` | `cbm-run-gate` | post-MVP |
| `refresh-delta.json` | json | `refreshes/<delta-id>.json` | `cbm-refresh` | post-MVP (v1.2 standard) |
| `verify-report.json` | json | (transient) | `cbm-verify` | post-MVP (v1.2) |
| `consultations/<id>.md` | md | `consultations/<id>.md` | `cbm-consult` | post-MVP (v1.2) |
| `handoff.md` | md+yaml | `handoff.md` | `cbm-handoff` | yes |

## Claim-evidence requirements

The Skeptic enforces these per claim type. Authoritative table is in RUNTIME-CONSTITUTION.md §7:

| Claim type | Required evidence_kinds | Forbidden alone | Min corroboration |
|---|---|---|---|
| `edge.import` | `static_relation` | — | 1 |
| `edge.call` | `static_relation` | — | 1 |
| `edge.runtime_workflow` | `runtime_trace` OR `command_output` | `static_structure` | 1 |
| `edge.test_exercises` | `static_relation` OR `command_output` | — | 1 |
| `edge.config_contract` | `static_relation` | — | 2 (config + read site) |
| `authority.config` | `static_relation` | — | 2 (config + read site) |
| `authority.routing` | `static_relation` OR `runtime_trace` | — | 1 |
| `authority.policy` | `static_relation` or `maintainer_statement` | — | 1 |
| any interpretive claim | rationale required | — | ≥1 evidence_kind |

## Append-only artifacts

`evidence-ledger.jsonl` and `uncertainty-register.jsonl` are append-only. The Skeptic verifies append-only-ness by recomputing line offsets; hooks reject mutations. Resolved uncertainties get a new `resolution` entry referencing the original id; the original is not edited.

## Status lifecycle

Artifacts begin `draft`. `cbm-validate` + `cbm-verify-citations` pass → `validated`. Skeptic review pass → `reviewed`. Superseded → `retired`.

Claims have their own lifecycle (active → challenged → contested → contradicted → superseded → retired). Distinct from artifact status.

## Hook integration points

Hooks are optional platform adapters. They may call the commands below, but they are not the source of truth and must not contain policy that is unavailable through explicit CBM commands.

| Trigger | Action | Type |
|---|---|---|
| Post-write to artifact | `cbm-validate` + `cbm-verify-citations` + claim-evidence-requirements check | hard gate |
| Post-validation of artifact | spawn Skeptic per mode policy | qualitative review |
| Pre-spawn of Intervention Planner | check `synthesis-index.json` validated | hard gate |
| Pre-spawn of Tracer | check `dependency-graph.json` validated | hard gate |
| Post-write to source files (during run) | mark consumer artifacts stale | warning gate |
| Pre-`cbm-handoff` | full gate sweep + contestation summary populated | hard gate |
| Pre-`cbm-run-gate` | safety envelope check | hard gate |
| Pre-`cbm-consult` | `cbm-validate-fresh` on artifacts to be consulted | hard gate |
| Pre-`cbm-refresh` (interpretive) | structural refresh has produced an updated codebase map | hard gate |
| Post-`cbm-refresh` | refresh-delta produced; downstream artifacts marked needs-review | hard gate |
| Session start | run compaction-recovery skill (which calls `cbm-validate-fresh`) | recovery |

## Extractor registry

Catalogue of deterministic extractors used in this run. Edges and authorities citing an extractor reference it by `extractor_id`. Schema requires non-empty `known_blind_spots`. The Skeptic looks up blind spots when reviewing claims and challenges if relevant. See `schemas/extractor-registry.schema.json`.

A starter registry shipped at `cbm-init` should include at minimum:
- One AST extractor per detected language.
- A manifest parser for the build system.
- A test discovery extractor.
- A CI parser.

Each must declare its blind spots specifically. Generic disclaimers ("might miss things") fail validation.

## Producer registry and run manifest

`producer-registry.json` records which producer backend is responsible for each artifact type in a run. Deterministic runs use explicit `cbm-baseline-*` or `dev-fixture-*` producer IDs. External-agent producer IDs are declared when `--backend external` is selected, and that backend currently refuses rather than fabricating outputs. `--backend codex-cli` is a guarded smoke backend: deterministic producers still create the baseline artifacts, while a Codex CLI smoke producer may write `skeptic-review/surface-map.md` only when `--allow-live-codex` is explicitly passed. The smoke backend defaults to `--codex-model gpt-5.4-mini` and `--codex-reasoning-effort medium`; both are recorded in the manifest command and can be overridden explicitly.

`run-manifest.json` records the selected backend, mode, goal, producer registry hash, and each run step's command, producer id, backend, status, and exit code. It is lifecycle evidence for `cbm run`; it is not a substitute for validating the artifacts produced by those steps.

## What the contracts do not commit to

- AST tooling per language (tree-sitter, language-server-protocol, language-native — implementer's choice).
- Orchestrator implementation language.
- Subagent spawn API (platform-specific).
- Caching strategy.

Schema validation makes these underspecifications safe.
