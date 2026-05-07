---
schema_version: '1.2'
artifact_type: handoff
run_id: run-mcp-git-h1s2b-skeptic-1
produced_at: '2026-05-07T13:24:49Z'
produced_by: cbm-baseline-handoff@0.1
source_sha: 4503e2d12b79
inputs:
- path: .research/run-mcp-git-h1s2b-skeptic-1/surface-map.json
  sha256: ec7d3ac845bf143e15d6d08453a65b6f794adf34c5884ca4fd43af19f78e31eb
- path: .research/run-mcp-git-h1s2b-skeptic-1/project-type.json
  sha256: 7415360369036c12ee72c6c679714456565379acf04e56d2b3011360d55f91d5
- path: .research/run-mcp-git-h1s2b-skeptic-1/goal-binding.json
  sha256: fd390dda86120d7e4da9219fb7577f4dbe8f5d1411a3a6ad90722fcd49ee493f
- path: .research/run-mcp-git-h1s2b-skeptic-1/findings/int-0001.md
  sha256: 468301f4874f9a28d7adcb080d613c43ff92e43d4b133e85f3c0ca356e3b9c06
- path: .research/run-mcp-git-h1s2b-skeptic-1/skeptic-review/surface-map.md
  sha256: 0ec18b269a1cfb8cc8c1609995c78164d1b8318d9b3535da64fa2a66a7c7736d
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
user_goal: review H1.S1 Surface Mapper map for MCP git server surfaces
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
    entry_count: 34
    missing_citation_count: 0
    missing_citation_examples: []
  staleness_check:
    fresh: 5
    stale_artifacts: []
  skeptic_review:
    artifacts_reviewed: 1
    challenges_logged: 1
    challenges_resolved: 0
contestation_summary:
  claims_by_register:
    factual: 11
    inferential: 2
    interpretive: 2
  claims_by_status:
    active: 14
    challenged: 1
    contested: 0
    contradicted: 0
    superseded: 0
    retired: 0
  open_challenges: 1
  contested_claims: []
  contradicted_claims: []
artifacts:
- path: .research/run-mcp-git-h1s2b-skeptic-1/codebase-map.json
  artifact_type: codebase_map
  status: draft
  summary: Deterministic structural file inventory.
- path: .research/run-mcp-git-h1s2b-skeptic-1/project-type.json
  artifact_type: project_type_report
  status: draft
  summary: Phase 0 project-type detection report.
- path: .research/run-mcp-git-h1s2b-skeptic-1/surface-map.json
  artifact_type: surface_map
  status: draft
  summary: Runtime Surface Mapper output from surface-mapper@1.2 with 8 authorities,
    7 edges, and 1 unknown edge.
- path: .research/run-mcp-git-h1s2b-skeptic-1/goal-binding.json
  artifact_type: goal_binding
  status: draft
  summary: Goal-specific candidate binding over the surface map.
- path: .research/run-mcp-git-h1s2b-skeptic-1/findings/int-0001.md
  artifact_type: findings_card
  status: draft
  summary: Goal-bound structural findings card.
- path: .research/run-mcp-git-h1s2b-skeptic-1/skeptic-review/surface-map.md
  artifact_type: skeptic_review
  status: draft
  summary: Runtime Skeptic review output.
open_questions_count: 1
coverage_caveats:
- Baseline extractor coverage saw every in-scope file; I directly examined only the
  files needed for interpretive claims.
- No CI workflow files were present in scope, so CI gating could not be mapped.
recommended_next_action: Disposition the H1.S2b Skeptic challenge as accepted, revised,
  or unresolved contestation and carry the response into the handoff path.
---
# CBM Handoff

> This run includes deterministic baseline output. Cards and artifacts labeled cbm-baseline-* or dev-fixture-* are NOT runtime-agent readings; they inherit baseline guarantees only (schema-valid, citation-resolved, evidence-table-checked). Do not act on them as if they had Skeptic review.

CBM produced a draft handoff containing runtime Surface Mapper output; see frontmatter for producer identities, gate summary, coverage, and caveats.
