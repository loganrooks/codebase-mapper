---
schema_version: '1.2'
artifact_type: handoff
run_id: run-mcp-git-baseline-2
produced_at: '2026-05-01T20:24:46Z'
produced_by: cbm-baseline-handoff@0.1
source_sha: 4503e2d12b79
inputs:
- path: .research/run-mcp-git-baseline-2/surface-map.json
  sha256: 24f662f3b17b65a6b37398f495b0ce21a6dba40697f08e63f83d4910f888032d
- path: .research/run-mcp-git-baseline-2/project-type.json
  sha256: b00dfacbaef1cced2f1661dfba0e7c06bd5fcd54d16d28dd17b394c8eac1b6d6
- path: .research/run-mcp-git-baseline-2/goal-binding.json
  sha256: 2fe3818db38cd58b5daadef271e46e6928bb92eaf81d93180fec4344b51f38a3
- path: .research/run-mcp-git-baseline-2/findings/int-0001.md
  sha256: fb8cd79aa8e705a7fd95d6d8f65bcd46685c279c9ff0fdeb6f91520722747aed
- path: .research/run-mcp-git-baseline-2/skeptic-review/surface-map.md
  sha256: e9035a26906a8a3c3539666141094c208e7ead3f52903c48804fd0d7e6a83301
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
    files_in_scope: 31
    files_examined_directly: 1
    files_inspected_via_extractor: 31
    files_unread_in_scope: 30
  limitations:
  - Phase A kernel records structure only; interpretive review remains a runtime-agent
    task.
mode: standard
user_goal: understand MCP git server surfaces
goal_class: understand_repo
research_only: true
gate_summary:
  schema_validation:
    passed: 6
    failed_artifacts: []
  citation_resolution:
    resolved: 20
    unresolved_count: 0
    unresolved_examples: []
  ledger_consistency:
    append_only_verified: true
    entry_count: 22
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
    factual: 34
    inferential: 2
    interpretive: 2
  claims_by_status:
    active: 38
    challenged: 0
    contested: 0
    contradicted: 0
    superseded: 0
    retired: 0
  open_challenges: 0
  contested_claims: []
  contradicted_claims: []
artifacts:
- path: .research/run-mcp-git-baseline-2/codebase-map.json
  artifact_type: codebase_map
  status: draft
  summary: Deterministic structural file inventory.
- path: .research/run-mcp-git-baseline-2/project-type.json
  artifact_type: project_type_report
  status: draft
  summary: Phase 0 project-type detection report.
- path: .research/run-mcp-git-baseline-2/surface-map.json
  artifact_type: surface_map
  status: draft
  summary: Draft deterministic surface map with explicit unknown dependency edge.
- path: .research/run-mcp-git-baseline-2/goal-binding.json
  artifact_type: goal_binding
  status: draft
  summary: Goal-specific candidate binding over the surface map.
- path: .research/run-mcp-git-baseline-2/findings/int-0001.md
  artifact_type: findings_card
  status: draft
  summary: Goal-bound structural findings card.
- path: .research/run-mcp-git-baseline-2/skeptic-review/surface-map.md
  artifact_type: skeptic_review
  status: draft
  summary: Lightweight Skeptic finding against unknown dependency closure.
open_questions_count: 1
coverage_caveats:
- 1 of 31 in-scope file(s) were directly examined for role claims; 30 file(s) remain
  unread by an agent or human.
- 30 file(s) were inspected via deterministic extractors only; those observations
  support structural claims, not settled interpretive role claims.
- Phase A surface mapping is deterministic and has not performed language-level import/call
  extraction.
recommended_next_action: Implement call and runtime workflow extraction so the unknown
  dependency edge can be narrowed with grounded relations.
---
# CBM Handoff

Phase A mechanical gates produced a draft handoff. See frontmatter for gate summary and caveats.
