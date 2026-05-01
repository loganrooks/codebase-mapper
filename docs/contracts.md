# Contracts

CLI commands, artifact catalog, citation format, hook integration. Schemas live in `schemas/`.

## Citation format

```
path/to/file.ext:START-END@SHA
```

- Repository-relative path, forward slashes.
- Inclusive line range. Single-line: `path:LINE@SHA`.
- Full or short SHA.

Cross-artifact references use JSON Pointer: `.research/<run_id>/dependency-graph.json#/edges/47`.

## Universal frontmatter (v1.1)

```yaml
schema_version: "1.1"
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

### `cbm-bind <goal-string>`

Produce `goal-binding.json`. Lists candidate surfaces with map citations and status flags (active/challenged/contested/contradicted). `cbm-bind` does **not** commit to a single intervention.

### `cbm-handoff`

Assemble handoff bundle. Pre-checks: schema, citations, ledger consistency, staleness, verification non-empty on cards, contestation summary populated.

### `cbm-gate <artifact>`

Composite check: schema + citations + staleness + (cards) verification non-empty + (graphs) unknown partition present + (claims) evidence-kinds matches AGENTS.md §7 table for each claim type.

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

## Artifact catalog (v1.1)

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
| `handoff.md` | md+yaml | `handoff.md` | `cbm-handoff` | yes |

## Claim-evidence requirements

The Skeptic enforces these per claim type. Authoritative table is in AGENTS.md §7:

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

| Trigger | Action | Type |
|---|---|---|
| Post-write to artifact | `cbm-validate` + `cbm-verify-citations` + claim-evidence-requirements check | hard gate |
| Post-validation of artifact | spawn Skeptic per mode policy | qualitative review |
| Pre-spawn of Intervention Planner | check `synthesis-index.json` validated | hard gate |
| Pre-spawn of Tracer | check `dependency-graph.json` validated | hard gate |
| Post-write to source files (during run) | mark consumer artifacts stale | warning gate |
| Pre-`cbm-handoff` | full gate sweep + contestation summary populated | hard gate |
| Pre-`cbm-run-gate` | safety envelope check | hard gate |
| Session start | run compaction-recovery skill | recovery |

## Extractor registry

Catalogue of deterministic extractors used in this run. Edges and authorities citing an extractor reference it by `extractor_id`. Schema requires non-empty `known_blind_spots`. The Skeptic looks up blind spots when reviewing claims and challenges if relevant. See `schemas/extractor-registry.schema.json`.

A starter registry shipped at `cbm-init` should include at minimum:
- One AST extractor per detected language.
- A manifest parser for the build system.
- A test discovery extractor.
- A CI parser.

Each must declare its blind spots specifically. Generic disclaimers ("might miss things") fail validation.

## What the contracts do not commit to

- AST tooling per language (tree-sitter, language-server-protocol, language-native — implementer's choice).
- Orchestrator implementation language.
- Subagent spawn API (platform-specific).
- Caching strategy.

Schema validation makes these underspecifications safe.
