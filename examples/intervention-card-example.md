---
schema_version: "1.2"
artifact_type: findings_card
run_id: example-run-001
produced_at: "2026-04-30T14:22:11Z"
produced_by: intervention-planner@1.2
source_sha: a3f2c91
inputs:
  - path: ./.research/example-run-001/surface-map.json
    sha256: 7a2c8f1b3e4d5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b
  - path: ./.research/example-run-001/synthesis-notes.md
    sha256: b3e4d5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4
status: validated

coverage:
  scope:
    included_globs: ["src/**/*.py", "tests/**/*.py", "README.md"]
    excluded_globs: ["**/__pycache__/**", ".venv/**", "vendor/**"]
  result:
    files_in_scope: 47
    files_examined_directly: 12
    files_inspected_via_extractor: 47
    files_unread_in_scope: 0
  limitations:
    - "Dynamic plugin-loader path at edge 91 referenced but not directly read (would require resolving config-driven import path)."

staleness:
  stale_if_input_hash_changes: true
  depends_on_paths:
    - "src/registry.py"
    - "src/server.py"
    - "tests/test_registry.py"

claim_status: challenged

id: int-2026-04-30-001
goal: "Help me understand this MCP server's tool registration so I could potentially add new tools."
goal_class: understand_repo
research_only: true

surface_type: explicit
surface_kind: plugin_registry
surface_classification_register: interpretive

primary_files:
  - path: src/registry.py
    lines: [14, 87]
    role: "Defines the ToolRegistry class — one of the registration paths in this MCP server (see dependent_challenges re: centrality)."
    citations:
      - "src/registry.py:14-87@a3f2c91"
  - path: src/server.py
    lines: [42, 58]
    role: "Imports and instantiates ToolRegistry at server startup; the only static registry instance."
    citations:
      - "src/server.py:42-58@a3f2c91"

related_dependencies:
  certain:
    - ".research/example-run-001/surface-map.json#/edges/12"
    - ".research/example-run-001/surface-map.json#/edges/18"
    - ".research/example-run-001/surface-map.json#/edges/19"
    - "src/server.py:42-44@a3f2c91"
  suspected:
    - ".research/example-run-001/surface-map.json#/edges/47"
  advisory:
    - "README.md:102-118@a3f2c91"
  unknown:
    - ".research/example-run-001/surface-map.json#/edges/91"

affected_workflows:
  - name: "MCP tool/list response"
    citation_or_trace: "src/server.py:88-104@a3f2c91"
  - name: "MCP tool/call dispatch"
    citation_or_trace: "src/server.py:107-145@a3f2c91"

expected_leverage:
  rating: medium
  rationale: "Adding a tool through ToolRegistry exposes it to all MCP clients via the cited tool/list and tool/call workflows; the registry pattern at src/registry.py:14-87@a3f2c91 explicitly centralizes static registration. Leverage rated medium rather than high because the existence of a separate dynamic-loading path (unknown edge 91) means tools added only via ToolRegistry would not be reachable through that alternative mechanism, narrowing the leverage of registry-only changes."
  claim_register: interpretive
  claim_status: challenged
  evidence_kinds:
    - static_relation
    - static_structure
  challenges:
    - challenge_id: chl-00012
      challenges_claim_id: leverage
      raised_by: skeptic@1.2
      raised_at: "2026-04-30T14:18:33Z"
      competing_reading: "Leverage of registry-only changes is low, not medium: if the dynamic-loading path at edge 91 is the production-effective registration mechanism (e.g., loaded at request time from configuration), registry-mediated additions may not appear at all under typical deployment, making the registry surface effectively decorative."
      competing_evidence:
        - "src/server.py:42-58@a3f2c91"
        - "README.md:102-118@a3f2c91"
      interpretive_axis: salience
      relation_to_original: scope_dispute
      status: open
      rationale: "Until edge 91 is resolved, the leverage rating is contingent on which registration mechanism actually governs. The rating space is bounded by 'medium if registry is co-equal' and 'low if registry is shadowed by dynamic loading'."

blast_radius:
  hops_evaluated: 2
  certain_count: 4
  suspected_count: 1
  advisory_count: 1
  unknown_count: 1
  unknown_partition_present: true

verification_strategy:
  hard_gates:
    - description: "New tool's registration succeeds at server startup."
      implementation: "New test in tests/test_registry.py asserting ToolRegistry.register() returns the registered tool; existing test pattern at tests/test_registry.py:23-45@a3f2c91 demonstrates."
      citations:
        - "tests/test_registry.py:23-45@a3f2c91"
      command_ref: "ci-pytest"
    - description: "Tool appears in MCP tool/list response."
      implementation: "Integration test invoking the server's tool/list handler; assert new tool name in response. Note: this gate verifies registry-based tools surface; it does NOT verify whether dynamically loaded tools also surface (deferred per dependent_challenges)."
    - description: "Tool/call dispatches to the new tool."
      implementation: "Integration test invoking tool/call with the new tool's name; assert handler executed."
  warning_gates:
    - description: "No existing tool's behavior changed."
      implementation: "Run full existing test suite; no failures."
  advisory_checks:
    - description: "Tool description follows the conventions visible in existing tools at src/tools/*.py."
  manual_review:
    - description: "If the new tool involves I/O or side effects, security review of input validation."
      reviewer_role: "security reviewer"
    - description: "Adjudicate the centrality challenge (chl-00012) before relying on this card for production work."
      reviewer_role: "maintainer"

risks:
  - description: "Edge 91 (unknown) suggests dynamic tool loading from a config path may exist; a new statically registered tool could conflict if that mechanism overlaps, or may be invisible in production if dynamic loading is the effective registration path."
    severity: medium
    mitigation: "Resolve unc-00012 and challenge chl-00012 before registering tools that could collide with config-loaded tools or that need to be live in production."
  - description: "README at lines 102-118 describes a 'plugin protocol' that isn't reflected in the code; following the README description without verifying could produce a registration that doesn't actually work."
    severity: low
    mitigation: "Verify behavior against the registry code, not the README."

confidence: medium
confidence_rationale: "The static registry surface is well-cited (4 certain edges, corroboration ≥ 2 on the routing claim). Confidence is medium rather than high because (a) the unknown edge 91 leaves the dependency closure incomplete and (b) the leverage and surface-classification claims are interpretive and currently challenged (chl-00012). A high-confidence rating would require resolving the centrality challenge by reading the dynamic-loading code path."

open_questions:
  - question: "Does the dynamic loading path at edge 91 also register tools through ToolRegistry, or does it bypass the registry?"
    register_id: unc-00012
  - question: "README references a 'plugin protocol' that doesn't appear in code; is this a planned feature, deprecated feature, or doc drift?"
    register_id: unc-00015

dependent_challenges:
  - claim_artifact: ".research/example-run-001/surface-map.json"
    claim_id: "auth-001"
    challenge_ids: ["chl-00009"]
    impact: "auth-001 (the surface map's claim that ToolRegistry is the central registration authority) is currently challenged on the centrality axis. If the alternative reading prevails — that ToolRegistry is one of two co-equal registration paths — then this card's surface_kind may shift from plugin_registry toward module_boundary, and the verification strategy needs an additional gate covering the dynamic-loading path. Resolving unc-00012 would adjudicate this challenge."

recommended_next_slice: "Read src/registry.py:14-87@a3f2c91 in full, then locate and read the dynamic-loading code site referenced by edge 91 (likely a config-driven import in src/server.py or a sibling module). Goal: resolve whether the dynamic path registers tools through ToolRegistry (centrality claim survives) or bypasses it (centrality claim contradicted; this card moves to status: superseded). This single read also resolves chl-00012 and unc-00012."
---

# Understanding ToolRegistry

## Why

The user's goal is to understand the MCP server enough to potentially add new tools. The surface map identified ToolRegistry at `src/registry.py:14-87@a3f2c91` as a `kind: registry` authority, with `authority_source: code`. Three certain edges connect it to the server's startup, tool/list response, and tool/call dispatch — three workflows a new tool would need to participate in.

The original surface-map claim that ToolRegistry is *the* central authority is currently challenged (chl-00009): the existence of a dynamic-loading path at edge 91 raises a competing reading where ToolRegistry is one of two registration paths rather than the authoritative one. This card propagates that contestation rather than resolving it.

This is a `research_only` finding: the next step is to investigate the dynamic-loading path and adjudicate the centrality challenge, not to add a tool yet.

## How (sketch)

If the user later wants to add a tool, the path through the static registry is:
1. Implement the tool's logic as a callable matching the registry's expected signature (TBD pending the next-slice investigation).
2. Call `ToolRegistry.register()` somewhere that runs before server startup completes.
3. Verify via the three hard gates above.

But this card stops at understanding, not implementation, because the `unknown` edge 91 and the doc-code disagreement at unc-00015 suggest there may be a parallel registration mechanism (dynamic loading) whose interaction with the registry is unclear.

## Contestation

Two readings are currently live:

- **Original (active):** ToolRegistry is the central registration authority; static registration is the dominant or canonical path; dynamic loading (if real) is a secondary mechanism.
- **Competing (chl-00009, status: open):** ToolRegistry is one of two co-equal registration paths; if the dynamic path is the production-effective mechanism, registry-mediated additions may be invisible at runtime.

The recommended next slice is the cheapest experiment that adjudicates between the two: a single read of the dynamic-loading code site. Output is binary — either it routes through `ToolRegistry.register()` (centrality survives, chl-00009 withdrawn) or it does not (centrality contradicted, this card moves to `superseded` and a new card covers the unified registration story).

## What this defers

- The exact signature of the tool callable. Resolved by the recommended next slice.
- Whether the dynamic loading path (unc-00012, chl-00009) is a separate mechanism, a deprecated mechanism, or actually routes through ToolRegistry. The recommended next slice is exactly this question.
- Whether the README's "plugin protocol" (unc-00015) reflects intent that hasn't been implemented or documentation that hasn't been removed. Out of scope for this card; investigate separately if it bears on the user's goal.
- Performance implications of adding many tools. No evidence in the maps suggests this is a concern.
