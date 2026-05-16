---
schema_version: '1.2'
artifact_type: handoff
run_id: run-mcp-git-surface-mapper-h1s1-6
produced_at: '2026-05-02T20:53:42Z'
produced_by: cbm-baseline-handoff@0.1
source_sha: 4503e2d12b79
inputs:
- path: surface-map.json
  sha256: ff48b3d6efdcd49e62ef6b9b3590a07da5fd7e9a65872d3480e465e7a5fb36ae
- path: goal-binding.json
  sha256: ef2072641359765f96d77f9a277e27dc72bb96e108492e94266976c56654e1fa
status: draft
coverage:
  scope:
    included_globs:
    - '**/*'
    excluded_globs:
    - .git/**
    - .research/**
    - .venv/**
    - node_modules/**
    - '**/__pycache__/**'
    - .pytest_cache/**
    - .DS_Store
  result:
    files_in_scope: 12
    files_examined_directly: 7
    files_inspected_via_extractor: 12
    files_unread_in_scope: 0
  limitations:
  - Baseline extractor coverage saw every in-scope file; I directly examined only
    the files needed for interpretive claims.
  - No CI workflow files were present in scope, so CI gating could not be mapped.
mode: lightweight
user_goal: produce real Surface Mapper map for MCP git server surfaces
goal_class: understand_repo
research_only: true
gate_summary:
  schema_validation:
    passed: 6
    failed_artifacts: []
  citation_resolution:
    resolved: 28
    unresolved_count: 0
    unresolved_examples: []
  ledger_consistency:
    append_only_verified: true
    entry_count: 30
    missing_citation_count: 0
    missing_citation_examples: []
  staleness_check:
    fresh: 2
    stale_artifacts: []
  skeptic_review:
    artifacts_reviewed: 0
    challenges_logged: 0
    challenges_resolved: 0
contestation_summary:
  claims_by_register:
    factual: 11
    inferential: 2
    interpretive: 2
  claims_by_status:
    active: 15
    challenged: 0
    contested: 0
    contradicted: 0
    superseded: 0
    retired: 0
  open_challenges: 0
  contested_claims: []
  contradicted_claims: []
artifacts:
- path: codebase-map.json
  artifact_type: codebase_map
  status: draft
  summary: Deterministic structural file inventory.
- path: surface-map.json
  artifact_type: surface_map
  status: draft
  summary: Runtime Surface Mapper output from surface-mapper@1.2 with 8 authorities,
    7 edges, and 1 unknown edge.
- path: goal-binding.json
  artifact_type: goal_binding
  status: draft
  summary: Goal-specific candidate binding over the surface map.
open_questions_count: 1
coverage_caveats:
- Baseline extractor coverage saw every in-scope file; I directly examined only
  the files needed for interpretive claims.
- No CI workflow files were present in scope, so CI gating could not be mapped.
recommended_next_action: Run a real isolated Skeptic review over the runtime Surface
  Mapper artifact.
---
# CBM Handoff

> This run includes deterministic baseline output. Cards and artifacts labeled cbm-baseline-* or dev-fixture-* are NOT runtime-agent readings; they inherit baseline guarantees only (schema-valid, citation-resolved, evidence-table-checked). Do not act on them as if they had Skeptic review.

CBM produced a draft handoff containing runtime Surface Mapper output; see frontmatter for producer identities, gate summary, coverage, and caveats.
