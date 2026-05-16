---
schema_version: '1.2'
artifact_type: handoff
run_id: run-mcp-git-codex-smoke-4
produced_at: '2026-05-02T02:42:18Z'
produced_by: cbm-baseline-handoff@0.1
source_sha: 4503e2d12b79
inputs:
- path: .research/run-mcp-git-codex-smoke-4/surface-map.json
  sha256: ea90c99042df83b9f5245071829c118f62e8297e6bd655092926bee203f4a91f
- path: .research/run-mcp-git-codex-smoke-4/project-type.json
  sha256: e2e5330a57e7113a4023896c3d4261e9cc74ea391d638c5784ea8ac5be3f0fcd
- path: .research/run-mcp-git-codex-smoke-4/goal-binding.json
  sha256: d8d10bd2a9a052dc60d854c16cc930ca31e698623de06e88e2abfe0f5de4e9f2
- path: .research/run-mcp-git-codex-smoke-4/findings/int-0001.md
  sha256: 3c5e43ff85d36ea78123f8e1b45765c9484de8798572d700b0a2754184201205
- path: .research/run-mcp-git-codex-smoke-4/skeptic-review/surface-map.md
  sha256: f83381083b5bc58d5a4a6d1e9d43314596394d7da0cfd1fcfbb2266a37c803ee
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
    files_examined_directly: 1
    files_inspected_via_extractor: 12
    files_unread_in_scope: 11
  limitations:
  - Phase A kernel records structure only; interpretive review remains a runtime-agent
    task.
mode: lightweight
user_goal: understand MCP git server surfaces
goal_class: understand_repo
research_only: true
gate_summary:
  schema_validation:
    passed: 6
    failed_artifacts: []
  citation_resolution:
    resolved: 21
    unresolved_count: 0
    unresolved_examples: []
  ledger_consistency:
    append_only_verified: true
    entry_count: 23
    missing_citation_count: 0
    missing_citation_examples: []
  staleness_check:
    fresh: 5
    stale_artifacts: []
  skeptic_review:
    artifacts_reviewed: 1
    challenges_logged: 0
    challenges_resolved: 0
contestation_summary:
  claims_by_register:
    factual: 17
    inferential: 1
    interpretive: 1
  claims_by_status:
    active: 19
    challenged: 0
    contested: 0
    contradicted: 0
    superseded: 0
    retired: 0
  open_challenges: 0
  contested_claims: []
  contradicted_claims: []
artifacts:
- path: .research/run-mcp-git-codex-smoke-4/codebase-map.json
  artifact_type: codebase_map
  status: draft
  summary: Deterministic structural file inventory.
- path: .research/run-mcp-git-codex-smoke-4/project-type.json
  artifact_type: project_type_report
  status: draft
  summary: Phase 0 project-type detection report.
- path: .research/run-mcp-git-codex-smoke-4/surface-map.json
  artifact_type: surface_map
  status: draft
  summary: Draft deterministic surface map with explicit unknown dependency edge.
- path: .research/run-mcp-git-codex-smoke-4/goal-binding.json
  artifact_type: goal_binding
  status: draft
  summary: Goal-specific candidate binding over the surface map.
- path: .research/run-mcp-git-codex-smoke-4/findings/int-0001.md
  artifact_type: findings_card
  status: draft
  summary: Goal-bound structural findings card.
- path: .research/run-mcp-git-codex-smoke-4/skeptic-review/surface-map.md
  artifact_type: skeptic_review
  status: draft
  summary: Lightweight Skeptic finding against unknown dependency closure.
open_questions_count: 1
coverage_caveats:
- 1 of 12 in-scope file(s) were directly examined for role claims; 11 file(s) remain
  unread by an agent or human.
- 11 file(s) were inspected via deterministic extractors only; those observations
  support structural claims, not settled interpretive role claims.
- Phase A surface mapping is deterministic and has not performed language-level import/call
  extraction.
recommended_next_action: Implement call and runtime workflow extraction so the unknown
  dependency edge can be narrowed with grounded relations.
---
# CBM Handoff

Phase A mechanical gates produced a draft handoff. See frontmatter for gate summary and caveats.
