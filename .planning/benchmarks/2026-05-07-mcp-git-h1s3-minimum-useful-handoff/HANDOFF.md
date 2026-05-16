---
schema_version: '1.2'
artifact_type: handoff
run_id: run-mcp-git-h1s3-minimum-useful-handoff-1
produced_at: '2026-05-07T14:30:00Z'
produced_by: cbm-handoff@0.1
source_sha: 4503e2d12b79
inputs:
- path: .planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/surface-map.json
  sha256: db936e0bf054eb3545490c5edab052264b795f3586c569281f539406a728f3aa
- path: .planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/skeptic-review-surface-map.md
  sha256: 0ec18b269a1cfb8cc8c1609995c78164d1b8318d9b3535da64fa2a66a7c7736d
- path: .planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/source-h1s2c-handoff.md
  sha256: e325edea2c38f7778923e9200e3c4d7bc77df30976a8820928efee0a4b273b3d
- path: .planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/evidence-ledger.jsonl
  sha256: 7bcf6543af80ec3f4f60303c4136788bd7506ca821607a048bca84ab5278cc34
status: validated
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
  - Baseline extractor coverage saw every in-scope file; the runtime Surface Mapper directly examined only the files needed for interpretive claims.
  - No CI workflow files were present in scope, so CI gating could not be mapped.
mode: lightweight
user_goal: prepare H1 minimum-useful CBM handoff for MCP git server surfaces
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
    entry_count: 37
  staleness_check:
    fresh: 5
    stale_artifacts: []
  skeptic_review:
    artifacts_reviewed: 1
    challenges_logged: 1
    challenges_resolved: 1
contestation_summary:
  claims_by_register:
    factual: 11
    inferential: 2
    interpretive: 2
  claims_by_status:
    active: 14
    challenged: 0
    contested: 1
    contradicted: 0
    superseded: 0
    retired: 0
  open_challenges: 0
  contested_claims:
  - claim_artifact: .planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/surface-map.json
    claim_id: auth-001
    challenge_count: 1
    summary: auth-001 preserves the shared-command-implementation reading and carries chl-10001 as an accepted alternative distributed-routing reading.
  contradicted_claims: []
artifacts:
- path: .planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/surface-map.json
  artifact_type: surface_map
  status: validated
  summary: Final H1 surface state after H1.S1 mapper output, H1.S2b Skeptic challenge, and H1.S2c disposition.
- path: .planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/skeptic-review-surface-map.md
  artifact_type: skeptic_review
  status: validated
  summary: Real isolated skeptic@1.2 review over the H1.S1 runtime Surface Mapper artifact.
- path: .planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/source-h1s2c-handoff.md
  artifact_type: handoff
  status: validated
  summary: Source H1.S2c handoff carrying open_challenges 0 and contested auth-001.
- path: .planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/evidence-ledger.jsonl
  artifact_type: evidence_ledger
  status: validated
  summary: Preserved ledger including challenge_resolved for chl-10001 and documented historical caveats.
open_questions_count: 1
coverage_caveats:
- Runtime Surface Mapper direct examination covered 7 of 12 in-scope files; extractor coverage saw all 12 in-scope files.
- No CI workflow files were present in target scope, so CI gating remains unmapped.
- MCP runtime dispatch through the external library remains partially opaque even though the in-repo registry is clear.
recommended_next_action_kind: prepare_pass_claim_review
recommended_next_action: Run the non-current-model checkpoint review of the H1 pass claim; do not move to H2 or Phase B until accepted.
---
# H1 Minimum-Useful CBM Handoff

## Target

- Repository: `https://github.com/modelcontextprotocol/servers`
- Subtree: `src/git`
- Pinned SHA: `4503e2d12b799448cd05f789dd40f9643a8d1a6c`
- Local verification checkout: `/var/tmp/cbm-h1-mcp-servers-4503e2d/src/git`

## Evidence Chain

Final H1 surface state = H1.S1 runtime Surface Mapper artifact + H1.S2b runtime Skeptic review + H1.S2c mapper response/disposition.

- H1.S1 produced a real `surface-mapper@1.2` `surface-map.json` through backend `codex-cli`.
- H1.S2b produced a real isolated `skeptic@1.2` review over the H1.S1 map through backend `codex-cli`.
- H1.S2c accepted `chl-10001` as an alternative reading and carried the result into `surface-map.json` and the source H1.S2c handoff.

This handoff is the reviewable H1.S3 packet. It is not itself a new runtime reading and does not claim that H1 is complete before checkpoint acceptance.

## Producer Honesty

Runtime-produced evidence:

- `surface-mapper@1.2`: original H1.S1 map of the MCP git server.
- `skeptic@1.2`: isolated H1.S2b review that raised `chl-10001`.
- `surface-mapper@1.2`: H1.S2c mapper response accepting the challenge as an alternative.

Deterministic or baseline artifacts in the packet remain deterministic support material only. They are not promoted as runtime-agent understanding, and no `cbm-baseline-*` or `dev-fixture-*` artifact is used as a substitute for the real Surface Mapper or Skeptic evidence.

## Coverage

The final surface map reports 12 files in scope, 7 files examined directly, 12 files inspected via extractor, and 0 unread files in scope. The direct-examination count is limited to the files needed for interpretive claims; extractor coverage is not treated as direct reading.

Limitations:

- No CI workflow files were present, so CI gating could not be mapped.
- MCP runtime dispatch through the external library remains partially opaque even though in-repo registry surfaces are clear.
- This is one pinned external target only; repeatability on a second target is not claimed.

## Contestation

`auth-001` is contested. The original reading treats `src/mcp_server_git/__init__.py` as the shared command implementation because the console script and module runner route into the same callable. The accepted alternative, `chl-10001`, reads launch/routing authority as distributed across packaging metadata and the module shim.

The accepted alternative is grounded in:

- `pyproject.toml:25-26@4503e2d12b79`
- `src/mcp_server_git/__main__.py:1-5@4503e2d12b79`
- `src/mcp_server_git/__init__.py:7-24@4503e2d12b79`

Current contestation state:

- `auth-001.claim_status = contested`
- `chl-10001.status = accepted_as_alternative`
- `open_challenges = 0`
- `claims_by_status.contested = 1`

## Unknowns

The final surface map still records unknown edges. The live unknown summary is that no CI workflow files were present in scope and MCP runtime dispatch through the external library remains partially opaque. This packet does not imply full codebase understanding.

## Boundary

Prepared claim: H1 has a reviewable minimum-useful-CBM packet for one pinned external target.

Unaccepted claims:

- H1 is not complete until a non-current-model checkpoint disposition accepts the pass claim.
- Minimum-useful CBM is not complete until that checkpoint accepts.
- Phase B or later is not passed.
- Standard mode, repeatability, beta readiness, mature CBM, cross-platform parity, and broad product maturity are not claimed.

## Recommended Next Action

Run the non-current-model checkpoint review using `.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/PROMPT.md`. The current dev-agent must not fill in reviewer identity, confidence, or disposition.
