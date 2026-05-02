# Skill: Surface Mapping

**Skill version**: 1.2
**Loaded by**: Surface Mapper subagent.
**Reads**: `RUNTIME-CONSTITUTION.md`, `schemas/surface-map.schema.json`, `extractor-registry.json`, this skill. In refresh mode, additionally reads the prior surface map and the codebase-map refresh delta.

## Purpose

Turn the deterministic baseline (`codebase-map.json`) into typed interpretive maps. In MVP, produces a single `surface-map.json` covering authorities, dependency edges, and verification.

This skill does not produce structural facts. Structural facts come from CLI tools. This skill *interprets* what the CLI tools produced — and labels each claim with its register so the Skeptic protocol applies correctly.

## Inputs

- `./.research/<run_id>/codebase-map.json` (validated, fresh)
- `./.research/<run_id>/intake.json`
- `./.research/<run_id>/state.json`
- `./.research/<run_id>/extractor-registry.json` (the extractors available for this run)
- The repository at `state.source_sha`

## Outputs

- `./.research/<run_id>/surface-map.json`
- Append entries to `evidence-ledger.jsonl`
- Append entries to `uncertainty-register.jsonl` (zero or more)

## Method

### Step 1 — Read the baseline and registry

Read `codebase-map.json` in full. Read `extractor-registry.json` to know which extractors produced which evidence kinds. Note `extraction_warnings` — these belong in the uncertainty register, not silently absorbed.

### Step 2 — Plan coverage honestly

Decide which files you will *examine directly* (open and read) versus *inspect via extractor only*. This decision constrains what claims you can make:

- Files only inspected via extractor: you can emit edges of kinds `import`, `call`, `public_api` (with extractor_id), and structural authorities. You **cannot** make interpretive claims about these files.
- Files examined directly: you can do everything plus interpretive claims about role, centrality, etc.

For the MVP and standard mode, examine directly any file you intend to make interpretive claims about. Record this in `coverage.result.files_examined_directly`.

### Step 3 — Identify candidate authorities

Walk the file list. For each candidate, classify:

- **Routing/entry-point** (`urls.py`, `routes.rb`, `main.go`, MCP tool registries).
- **Config** (verify by finding the read site; cite both files; corroboration ≥ 2).
- **Schema** (verify by finding the validator).
- **Policy** (security/access; cite enforcement site).
- **Registry** (plugin/hook/dispatch tables).
- **Build/CI gates**.
- **Test suite**.
- **Doc contract** (`authority_source: doc`; advisory).

For each authority, write:

```yaml
id: auth-NNN
kind: routing | config | schema | ...
path: <file>
citations: [<≥1 citations>]
authority_source: code | config | schema | test | doc
claim_register: factual | inferential | interpretive
claim_status: active  # default
evidence_kinds: [<from list>]
corroboration_count: <int>
rationale: "<≥10 chars; references citations>"
confidence: high | medium | low
```

**On claim_register for authorities:**
- "File X is the routing config" with cited read site → **factual**.
- "X is *the* central routing authority" → **interpretive** (the centrality claim is the interpretive move).
- "X probably governs routing because it matches the convention `urls.py`" → **inferential** (depends on the inference rule "Django apps put routing in urls.py").

When in doubt, use the more interpretive register. The system handles interpretive claims well; it does not handle interpretive claims smuggled in as factual.

**Anti-pattern**: classifying a config file as authoritative without finding the read site (corroboration_count = 1). The schema/Skeptic require ≥2 corroboration for `authority.config`.

### Step 4 — Extract dependency edges

For each non-vendored, non-generated file, extract edges. Each edge requires:

```yaml
id: edge-NNNN
kind: import | call | public_api | config_contract | ... | unknown
from: { path: <p>, symbol: <s>? }
to: { path: <p>, symbol: <s>? }
citations: [<...>]
extractor_id: ext-treesitter-python-v1  # required for import/call/public_api/generated_from
claim_register: factual | inferential | interpretive
claim_status: active
evidence_kinds: [<from list>]
corroboration_count: <int>
confidence: high | medium | low
rationale: "<required for medium/low confidence and certain kinds>"
```

**Mapping kind → claim_register:**
- `import`, `call`, `public_api` (extractor-derived): `factual`. Bytes settle it.
- `config_contract`, `schema_contract`: `factual` if you cite both the contract and its read site; `inferential` if you reason from convention.
- `test_exercises`: usually `inferential` (you infer from imports/naming what a test exercises). `factual` only if the test framework's introspection confirms.
- `generated_from`: `factual` if you cite generator + generated file; `unknown` if the build is custom.
- `runtime_workflow`: `inferential` at best; often `interpretive` if the workflow is named or characterized. Usually `low` confidence with rationale required.
- `doc_contract`: `interpretive` (docs frame behavior; that framing is a reading). Always advisory.
- `implicit_social_contract`: `interpretive`. Always advisory.
- `unknown`: no register required (the schema relaxes for unknown kind).

**Mapping kind → evidence_kinds (per RUNTIME-CONSTITUTION.md §7 table):**
- `import`: `[static_relation]`.
- `call`: `[static_relation]`.
- `runtime_workflow`: must include `runtime_trace` OR `command_output`; `static_structure` alone forbidden.
- `config_contract`: `[static_relation]` with corroboration ≥ 2.

The Skeptic enforces this table. Mismatches fail the gate.

**Anti-pattern**: emitting `runtime_workflow` with only `static_structure` evidence. The schema and RUNTIME-CONSTITUTION.md §7 forbid this.

**Anti-pattern**: zero `unknown` edges on a non-trivial codebase. Re-examine; either find them or write the gap to the uncertainty register.

### Step 5 — Verification subsection

For each test in `codebase-map.tests`:
- Resolve framework or mark unknown.
- For each test target, cite test code AND exercised code.
- The `exercises` entries are typically `claim_register: inferential` with `evidence_kinds: [static_relation]`.

For each CI file:
- Identify gates and cite the workflow file.
- Optionally declare a `command` block with `safety_envelope` for `cbm-run-gate` to use later (standard+ mode).

Coverage summary as raw counts. Never as percentage. `coverage_unknown` is real on metaprogramming-heavy codebases.

### Step 6 — Unknowns block

Required schema fields: `edge_unknowns_present` (boolean) and `summary` (≥10 chars). State which categories of edges or surfaces could not be determined and why. Specific examples are better than generic disclaimers.

### Step 7 — Append to evidence ledger

For every citation introduced, append `citation_introduced` to `evidence-ledger.jsonl` with `claim_register` field (so the Skeptic knows what protocol applies to that claim).

### Step 8 — Log uncertainties

For every claim you would have liked to make but couldn't ground, append to `uncertainty-register.jsonl`. Mark `blocking: true` only if downstream cannot proceed.

### Step 9 — Coverage report

Fill the `coverage` block of the artifact:
- `scope.included_globs` / `excluded_globs`: what you intended to look at.
- `result.files_examined_directly`: count of files you actually opened.
- `result.files_inspected_via_extractor`: count of files extractors processed without you reading them.
- `result.files_unread_in_scope`: in-scope files neither read nor extracted (red flag if non-zero with claims about them).
- `limitations`: what you couldn't look at and why.

## Differential refresh mode (v1.2)

When the orchestrator invokes the Surface Mapper with `refresh_mode: interpretive` and a prior surface map as input, the protocol changes. The goal is **not** to re-do the whole map — it's to address what the codebase change broke and carry forward what survives.

### Inputs (refresh mode adds)

- The prior `surface-map.json` at its `source_sha`.
- The current `codebase-map.json` refreshed to HEAD (with its own `refreshed_from` block).
- A pending `refresh-delta.json` for the codebase map (lists added/removed/changed files).

### Method (refresh mode)

**Step R1 — Per-claim evidence-resolution pass.** For every claim in the prior surface map, resolve its citations at HEAD:
- All cited bytes unchanged → claim is a candidate for `carried_forward`.
- Some cited bytes changed → claim is a candidate for `updated` or `retracted`; producer must address.
- Cited file removed or lines no longer exist → claim is a candidate for `retracted`.

The resolution pass is mechanical; the producer's interpretive work begins after.

**Step R2 — Carry-forward decisions.** For each candidate-for-carried-forward claim: confirm the surrounding code context still supports the claim's reading. A factual claim about an import survives almost automatically. An interpretive claim about centrality may need re-reading even if the cited bytes are unchanged — the *surroundings* may have shifted enough that the centrality reading no longer holds. When in doubt, move the claim to `updated` and re-examine.

**Step R3 — Address affected claims.** For each claim with shifted evidence, the producer makes an explicit decision:
- **Update**: the claim's interpretive content survives; re-cite the new bytes; possibly adjust evidence_kinds.
- **Retract**: the claim is no longer defensible; record rationale.
- **Supersede**: a different but related claim now holds; create the successor and link via refresh-delta.
- **Mark as needs-review**: defer the decision, write the claim to the successor with `claim_status: challenged` and a self-challenge naming the unresolved evidence shift.

**Step R4 — New claims from the delta.** The codebase delta may have introduced new files, new authorities, new edges. Treat these as fresh-mode claims (Steps 3–4 of the standard method). They appear in `newly_added` of the refresh-delta.

**Step R5 — Carry challenges forward.** Each prior challenge is classified by what the refresh did to it:
- `still_active`: the challenge's target survived as-is or was updated; the challenge still bites. Carry the challenge into the successor verbatim.
- `resolved_by_refresh`: the codebase change adjudicated the challenge (e.g., the alternative reading is now the only defensible reading). Move challenge to `withdrawn` or `accepted_as_replacement` as appropriate.
- `obsolete_target_retracted`: the challenged claim was retracted; the challenge has nothing to bite into.
- `now_contradicted`: the codebase change actually contradicted the original claim, escalating challenge to contradiction.

**Step R6 — Newly contested claims.** Sometimes the codebase change surfaces a competing reading that wasn't visible in the prior. These go in `newly_contested` of the refresh-delta. The successor claim's `claim_status` moves to `challenged` with the new challenge attached.

**Step R7 — Open question reconciliation.** Each open question from the prior gets a status: `still_open`, `resolved`, `obsolete`, or `transformed` (the question morphed into a different question).

**Step R8 — Write successor + delta.** The successor `surface-map.json` is a normal artifact, with `refreshed_from` populated and a `refresh_delta_path` reference. The refresh delta records the trajectory.

### Anti-patterns (refresh mode)

- **Re-mapping from scratch under the guise of refresh.** If you find yourself ignoring the prior map and producing fresh claims, you're doing Mode 5, not Mode 4. Either commit to a fresh run or actually carry forward what survives.
- **Carrying forward without re-resolving citations.** A claim whose citations point at deleted lines and gets carried forward verbatim is silent corruption. Run R1 first, always.
- **Treating challenges as obsolete just because the codebase changed.** Most challenges survive most refreshes; they're about readings, not bytes. Default to `still_active` and explicitly justify other classifications.
- **Producing a successor without a refresh delta.** The delta is what makes the trajectory legible. A successor surface map without its delta is a dropped chain of custody.
- **Promoting the successor before the delta is written.** Hooks gate this; do not bypass.

## Quality bar

A surface map of acceptable quality:

- Has at least one authority for each major subsystem.
- Has `unknowns.edge_unknowns_present: true` for non-trivial codebases.
- Citations on every authority and non-`unknown` edge.
- Rationales on `medium`/`low` confidence and advisory edges.
- `claim_register` correctly assigned (interpretive claims marked as such).
- `evidence_kinds` matches the RUNTIME-CONSTITUTION.md §7 requirements per claim type.
- `extractor_id` present on extractor-derived edges.
- `corroboration_count` ≥ 2 where required.
- Coverage report honestly distinguishes direct examination from extractor inspection.
- Ledger entries match artifact citations.

A surface map you should not write:

- Zero unknowns on a 50k-LOC codebase with a plugin system.
- "Central authority" claims labeled `claim_register: factual`.
- Edges of kind `runtime_workflow` with `evidence_kinds: [static_structure]` only.
- Coverage as a percentage.
- Authorities classified as `code` whose `path` points to a doc file.
- Interpretive claims about files in `files_inspected_via_extractor` but not `files_examined_directly`.

## On disagreement with the kernel

The kernel's outputs are authoritative for structural facts. Disagree → file in uncertainty register and proceed treating kernel output as ground truth. Do not silently override.

## When to stop and surface

- `codebase-map.json` is missing or fails validation.
- Repo at `source_sha` is no longer accessible.
- Universal heuristics produce zero authorities (likely needs a project-type pack).

## Output: final response

When invoked as a subagent: pointer to the artifact, pointer to uncertainty register entries, one-line note on whether the unknowns partition is non-empty.

Do not summarize the artifact. The orchestrator reads the artifact, not your summary.
