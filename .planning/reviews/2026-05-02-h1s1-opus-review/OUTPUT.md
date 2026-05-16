Now I'll write the review.

# H1.S1 External Reviewer Audit

## Verdict

**ACCEPT_WITH_BLOCKERS_FOR_NEXT_STAGE.**

The Surface Mapper artifact itself plausibly clears H1.S1's stated acceptance criteria, and the parent-side runtime path produces a non-trivial, citation-resolved map on a pinned external target. But the run's *handoff* — and the fixture/test substrate around it — describe the run dishonestly: they label the runtime map as "deterministic", silently include a dev-fixture skeptic stub as a real `skeptic_review` artifact, and bake a hard-coded `edge-unknown-001` id into both producer prompts and downstream gates. Those should be cleared before H1.S2 spawns a live Skeptic against this artifact.

## Executive Summary

- The runtime Surface Mapper subprocess (`surface-mapper@1.2` over `codex-cli`) does produce the artifact: 8 authorities, 7 edges + 1 unknown edge, 25 resolving citations, two interpretive claims, coverage that distinguishes 7 directly-examined files from 12 extractor-inspected files. Schema/citation/evidence gates pass. Producer and skill hash are recorded in `run-manifest.json`.
- The surrounding pipeline still treats the surface map as Phase A baseline output. The `handoff.md` for the same run reports `coverage.result.files_examined_directly: 1`, `files_unread_in_scope: 11`, with `summary: Draft deterministic surface map ...` and a recommended next action that says "Implement call and runtime workflow extraction" — even though the surface map already has call edges from a runtime agent. A reviewer reading only the handoff would not understand that a runtime mapper ran.
- The handoff also auto-writes a `skeptic-review/surface-map.md` from a dev-fixture template (because `--codex-skeptic-mode none`), then ingests it into `gate_summary.skeptic_review.artifacts_reviewed: 1` with the inline summary `Lightweight Skeptic finding against unknown dependency closure`. Only the producer-registry, not the artifact itself, distinguishes this stub from a real Skeptic.
- The parent validator depends on the agent producing a literal id `edge-unknown-001` (cli.py:4183-4184 and cli.py:4708) so the deterministic handoff fallback can attach `chl-00001` to it. This is a leaky implementation detail that the runtime mapper now must scaffold around.
- Several validations are present but too permissive (substring SHA match, no re-hashing of declared `inputs[].sha256`, ledger entries hard-code `skill_version: "0.1"` for `surface-mapper@1.2`).
- Test coverage for the new path is two cases (happy + baseline-rejection); rejection paths around coverage, SHA, citation resolution, missing unknown edge, and the repair-loop are uncovered.
- Planning docs (`HORIZONS.md`, `STATE.md`, `CURRENT-PLAN.md`, phase 01 `VERIFICATION.md`, `RESULT.md`) are mostly accurate and explicit about the H1.S1-only boundary, including that the skeptic stub is dev-fixture. The benchmark dir, however, omits the `findings/`, `skeptic-review/`, `logs/`, and `codex_outputs/` subtrees that the handoff frontmatter cites with sha256s, so the preserved evidence is incomplete relative to its own claims.

## Findings (by severity)

### F1 — HIGH — Handoff misrepresents runtime mapper output as deterministic Phase A

- Evidence: `.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/handoff.md:32-39` reports `files_examined_directly: 1` and limitation "Phase A kernel records structure only; interpretive review remains a runtime-agent task."; `:91` says `summary: Draft deterministic surface map with explicit unknown dependency edge.`; `:106-113` declares `Phase A surface mapping is deterministic and has not performed language-level import/call extraction.` and `recommended_next_action: Implement call and runtime workflow extraction ...`. The actual surface map at `surface-map.json:42-47` reports `files_examined_directly: 7, files_unread_in_scope: 0`, includes call edges (`edge-0002`, `edge-0003`, `edge-0005`), and is produced by `surface-mapper@1.2`.
- Source of the bug: `cbm/cli.py:4862` (artifact summary string), `cbm/cli.py:4911` (`coverage_block(... examined=1)`), `cbm/cli.py:386` (hardcoded coverage limitation text), `cbm/cli.py:4946-4947` (handoff caveat + `recommended_next_action`).
- Why this matters: this is exactly the property `VISION.md:33-34` calls out — the system "is honest about what it didn't do". A runtime-produced map being labeled "deterministic" with `examined=1` is the same failure mode `ADR-004` and the recovery interventions were meant to close. The honest-baseline banner work (`91f1f95`) covered the top-level banner string but not the per-artifact summary, the coverage block, or the next-action recommendation.
- Recommended action: when the producer-registry's `surface_map.producer_id` is not in the baseline set, the handoff must (a) read coverage from the actual `surface-map.json` instead of fabricating it, (b) update the artifact summary string, (c) drop or rewrite the "Phase A kernel" caveats and the "Implement call extraction" next-action. Add a regression that runs the fake-codex skill surface and asserts the handoff `coverage.result.files_examined_directly` matches the surface map (currently no test asserts this).

### F2 — HIGH — Dev-fixture skeptic-review is silently included in the H1.S1 handoff

- Evidence: with `--codex-skeptic-mode none`, `cbm/cli.py:4724-4750` writes `skeptic-review/surface-map.md` with `produced_by: dev-fixture-skeptic@0.1`, then `cbm/cli.py:4864` adds it to `artifacts` with `summary: Lightweight Skeptic finding against unknown dependency closure.`, and `cbm/cli.py:4940` counts it in `gate_summary.skeptic_review.artifacts_reviewed: 1`. The benchmark handoff confirms `artifacts_reviewed: 1, challenges_logged: 0` at lines 60-63, with the artifact present at `:100-103`. RESULT.md is honest about the boundary (`Boundary: ... skeptic-review/surface-map.md in the live run remains a dev-fixture review produced by handoff fallback behavior.`), but the artifact text itself is not.
- Why this matters: H1.S1 explicitly skipped Skeptic. A handoff that still claims "1 artifact reviewed" with a generic-looking summary makes the next-stage reviewer (H1.S2 Skeptic) operate against a misleading description. The producer-registry is the only out-of-band signal; the handoff's `artifact_type: skeptic_review` line gives a casual reader the wrong impression.
- Recommended action: when `--codex-skeptic-mode none`, either (a) do not emit the dev-fixture skeptic stub at all and report `artifacts_reviewed: 0`, or (b) make the in-artifact summary unmistakable (e.g., `[BASELINE] No real Skeptic ran for this run.`) and wrap the gate count in a `dev_fixture_count` field. The current banner-only signal is not enough.

### F3 — HIGH — `edge-unknown-001` is a hard-coded scaffolding requirement for downstream gates

- Evidence: `cbm/cli.py:4183-4184` makes the parent validator reject any runtime surface map that lacks an edge with literal id `edge-unknown-001`, with the rationale "for the handoff gate"; `cbm/cli.py:4708-4711` then uses that exact id in the deterministic handoff to attach `chl-00001`; the runtime prompt also instructs the agent to produce that id (`cbm/cli.py:4096`). The actual MCP map dutifully writes `edge-unknown-001` with rationale about MCP runtime dispatch.
- Why this matters: this is two layers of leak. The Surface Mapper subagent now has a CBM-internal stable id baked into its contract because the deterministic handoff template can't find unknown edges by `kind: "unknown"`. The contract also forces the agent to label one specific unknown that way, even if its honest reading would be that there are several or none. On any codebase with no real unknown surface, the producer would have to fabricate one to clear the gate.
- Recommended action: change the gate to "at least one edge with `kind == unknown`" (which the schema already permits). Update the deterministic handoff to look up the first such edge by kind, not by id. Drop the prompt's instruction that prescribes the literal id.

### F4 — MEDIUM — `source_sha` validation accepts trivial prefix matches

- Evidence: `cbm/cli.py:4158-4160`: `surface_sha.startswith(sha) or sha.startswith(surface_sha)` over `sha = source_sha(repo)` (12-char short SHA from `git rev-parse --short=12`, `cbm/cli.py:166`). With current `sha = "4503e2d12b79"`, an agent submitting `source_sha: "4"` passes (`sha.startswith("4")` is True). The same logic re-applies for citation SHAs at `cbm/cli.py:4192-4194`, where the schema does enforce 7-40 hex chars.
- Why this matters: the parent validator is the only thing standing between the agent and the rest of the gate chain on this field. The schema's `^[0-9a-f]{7,40}$` clamps the citation case to ≥7 chars but `source_sha` itself has no minimum-length floor in the parent check.
- Recommended action: require an exact match against the resolved short SHA (or a minimum prefix length of 7). One-line fix.

### F5 — MEDIUM — Declared `inputs[].sha256` is never re-hashed by the parent

- Evidence: `surface_map_parent_validation_errors` (`cbm/cli.py:4151-4200`) checks artifact_type, run_id, source_sha, producer, coverage, claim presence, citations, and the unknown-edge gate, but does not re-compute sha256 of the four files in `surface["inputs"]` against the declared values. The Codex prompt at `cbm/cli.py:4108-4111` actually feeds the agent `sha256=<hash>` for each input, so a non-reading agent could echo them verbatim and pass.
- Why this matters: the schema says `staleness.stale_if_input_hash_changes: true` and the input list is the staleness chain of custody. If the agent hadn't actually consulted those inputs, the artifact still claims it did.
- Recommended action: in the parent validator, recompute `sha256_file(repo / item["path"])` for each declared input and reject mismatches. Two reasons: integrity, and a small structural check that the agent did at least skim the input set.

### F6 — MEDIUM — Ledger `skill_version: "0.1"` is hardcoded for `surface-mapper@1.2`

- Evidence: `cbm/cli.py:897` writes `"skill_version": "0.1"` for every citation entry from `append_citation_entries`, including the runtime Surface Mapper case at `cbm/cli.py:4350-4358`. The benchmark `evidence-ledger.jsonl:4-28` shows 25 entries with `agent: surface-mapper@1.2, skill_version: "0.1"`, while `skills/surface-mapping.md:3` declares `Skill version: 1.2`.
- Why this matters: ledger entries are the chain-of-custody record. Anchoring the skill version to a baseline-era literal makes it impossible for a downstream consumer to ask "what version of the skill produced this evidence?"
- Recommended action: thread the skill version through `append_citation_entries` (it's already in `LoadedSkill`), or derive it from the `produced_by` string. Add a regression that asserts the ledger `skill_version` for the surface mapper path matches `1.2`.

### F7 — MEDIUM — `cbm validate`/`cbm verify-citations`/`cbm check-evidence` do not enforce runtime producer identity

- Evidence: `cbm/cli.py:2352` (validate), `:2386` (check-evidence), `:2402` (verify-citations) operate on schema and resolution only. The H1.S1 RESULT.md's quoted validation commands are these standalone invocations. Producer-id rejection lives only inside `command_codex_cli_surface_map`.
- Why this matters: a third party who later re-runs `cbm validate surface-map.json` against a baseline-faked surface map would get a passing exit. The recovery slice's stated guarantee is that runtime evidence is structurally distinguishable; this guarantee is currently coupled to one code path.
- Recommended action: add a `cbm validate` post-hook (or a separate `cbm validate --producer-strict`) that, when given a surface map, refuses baseline/dev-fixture producers. At minimum, document in `RESULT.md` and/or `BUILD-LOG.md` that the standalone validation does not enforce producer identity, so the validation chain in `RESULT.md` is not over-read.

### F8 — MEDIUM — One repair pass is implemented but untested

- Evidence: `cbm/cli.py:4302-4346` retries the codex subprocess once with a repair prompt that contains the rejected output and the parent error list. There is no regression test covering the failure → repair-success path or the failure → repair-failure path. The two surface-mapper tests (`tests/test_cli.py:535`, `:670`) cover only the success-on-first-try and the baseline-producer rejection.
- Why this matters: the repair loop is a control-flow surface, not a one-liner. A repair attempt that itself times out, returns garbage, or returns the same baseline producer is exercised only by the live benchmark, and the benchmark dir does not preserve `codex_outputs/` or `logs/`, so we cannot verify whether the live run hit the repair path.
- Recommended action: add two regressions using a stateful fake codex (output v1 invalid, output v2 valid → success; output v1 invalid, output v2 invalid → exit 1). Also preserve `codex_outputs/` and `logs/` in the benchmark dir for future audit.

### F9 — MEDIUM — Benchmark evidence is incomplete relative to its own handoff

- Evidence: the handoff frontmatter at `handoff.md:9-18` declares input sha256s for `findings/int-0001.md` and `skeptic-review/surface-map.md`. The benchmark directory (`.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/`) does not contain `findings/`, `skeptic-review/`, `logs/`, or `codex_outputs/`. RESULT.md states it preserves "the map, manifest, registry, handoff, goal binding, Codex output, ledger, codebase map, and extractor registry" — i.e., the curated subset, not the full run.
- Why this matters: a checkpoint reviewer or an H1.S2 reviewer cannot independently verify the integrity chain (sha256 in handoff → bytes on disk) because the bytes weren't preserved. This is the kind of unverifiable-self-claim that the recovery interventions were meant to discourage.
- Recommended action: either preserve the full `.research/<run_id>/` tree in the benchmark dir, or strip handoff input entries that point at non-preserved files. The current state is the worst of both — claims integrity, doesn't preserve evidence.

### F10 — LOW — Surface map remains `status: draft`

- Evidence: `surface-map.json:459` has `"status": "draft"`. There is no promotion step to `validated` or `reviewed` after parent validation passes; the runtime command writes the artifact and exits.
- Why this matters: the H1.S1 HORIZONS criterion "Surface map validates against the schema" is met, but `status: draft` semantically signals "not yet validated", which is at odds with the run being claimed as passing. A consumer following the constitution's lifecycle will not promote anything that's still `draft`.
- Recommended action: after the full handoff gate succeeds, either bump the surface map to `validated` (with an audit note) or document explicitly that `status: draft` is intentional until H1.S2 closes contestation. Either is fine; mute ambiguity is the thing to avoid.

### F11 — LOW — Coverage `files_examined_directly: 7` is unverifiable but plausible

- Evidence: the schema and parent validator both only require `files_examined_directly >= 1` for runtime output (`cbm/cli.py:4171-4172`). The MCP map's claim of 7 examined out of 12 in scope is consistent with the scope of authorities/edges (which span `__init__.py`, `__main__.py`, `server.py`, `tests/test_server.py`, `pyproject.toml`, `Dockerfile`, `README.md` — exactly 7 distinct paths).
- Why this matters: the parent has no way to confirm the agent actually opened those files, only that they were cited. The lower bound of `>= 1` is the right floor for now; raising it would force agent-specific decisions out of CBM.
- Recommended action: leave the floor at 1; consider adding a sanity check that `files_examined_directly` is no greater than the count of distinct paths cited in `authorities[].path + edges[].from.path + edges[].to.path` (the agent's coverage cannot exceed the surfaces it claims).

### F12 — LOW — Producer-registry shape is misleading for a partial-runtime run

- Evidence: `producer-registry.json:5-96` lists 15 producers; only `surface_map: surface-mapper@1.2` (codex-cli) is genuinely runtime. `skeptic_review: dev-fixture-skeptic@0.1`, `findings_card: dev-fixture-planner@0.1`, etc., are dev-fixture defaults that the handoff still uses. There is no in-band annotation that the run was a deliberately partial-runtime configuration.
- Why this matters: producer-registry is the canonical answer to "who produced what". A reader cannot tell from this file that `--codex-skeptic-mode none` was used, only that the skeptic producer is dev-fixture. The CLI flag is logged in the manifest's command field but not in the producer-registry.
- Recommended action: add a `run_configuration` block (or `notes` per producer) that records the user-selected modes for each runtime artifact type. Cheap to do; closes a real auditability gap.

### F13 — LOW — `BUILD-LOG.md` H1.S1 entry is short relative to the implementation

- Evidence: `BUILD-LOG.md:1603-1620` covers the H1.S1 slice in 18 lines. It lists what was implemented and the live benchmark command, but does not record the alternatives weighed (e.g., why `surface_map_json` is a stringified-JSON field inside an outer object, why a single repair pass not zero/two, why `edge-unknown-001` is required, why `--codex-skeptic-mode none` was selected over running a real skeptic). `AGENTS.md:29` says BUILD-LOG entries should record decisions and alternatives.
- Recommended action: add a follow-up BUILD-LOG entry capturing the design choices behind the parent-side validator and the prompt's checklist, so the next implementer of H1.S2 can see why the boundaries are where they are.

## Acceptance Criteria Audit

| H1.S1 acceptance criterion (HORIZONS.md:78-86) | Status | Evidence |
|---|---|---|
| Target repository and SHA are pinned | **PASS** | `RESULT.md:7-9`; `STATE.md:117-122` |
| Surface Mapper producer identity and backend recorded in `run-manifest.json` | **PASS** | `run-manifest.json:39-56` records `producer_id: surface-mapper@1.2`, `backend: codex-cli`, skill name + path + sha256 |
| Surface map validates against the schema | **PASS** | `surface-map.json` validates; gates passed per `RESULT.md:46-56`. *Caveat:* `status: draft` (F10) |
| Every cited claim resolves to source bytes at the pinned SHA | **PASS** | `RESULT.md:36-37` (25 source citations resolved); ledger entries lg-00004..lg-00028 carry resolving citations |
| Coverage distinguishes direct examination from extractor-only inspection | **PARTIAL** | Distinguished correctly *in `surface-map.json`* (7 vs 12). Misrepresented in `handoff.md` (1 vs 12) — see F1. The criterion is about the produced artifact, so this passes narrowly, but the run as a whole fails the spirit of it |
| At least one substantive factual, inferential, or interpretive claim grounded in citations | **PASS** | `auth-001` (interpretive: console-script and module runner share the click main entrypoint, 3 citations); `auth-008` (interpretive: doc surface, 2 citations); inferential edges and verification subsection both grounded |
| Output is not labeled or structured as `cbm-baseline-*` or `dev-fixture-*` | **PASS for surface-map.json**; **FAIL for handoff bundle** | Surface map's `produced_by: surface-mapper@1.2` is correct. But the *handoff bundle* still includes a dev-fixture skeptic-review and a dev-fixture findings card; the artifact summary calls the surface map "deterministic" (F1, F2). The criterion text targets the surface map specifically, so technically passes |

Net: every criterion targeting the *surface map* artifact passes. The surrounding handoff carries the integration debts described in F1/F2.

## H1.S2 Readiness Risks

1. **Skeptic context contamination via misleading handoff.** If H1.S2 spawns the Skeptic with the handoff in scope, the Skeptic will read a description of the run that contradicts the artifact under review. The skeptic.md skill instructs the Skeptic to challenge inconsistent coverage claims; it may correctly flag the handoff as inconsistent rather than the surface map. (R1 mitigation: per `RUNTIME-CONSTITUTION.md:226-232`, the Skeptic should read only the artifact under review, ledger, uncertainty register, source repo, and registry. If the H1.S2 implementation is faithful to that, this risk is contained.)

2. **Stale skeptic-review fallback.** When the runtime Skeptic runs and writes `skeptic-review/surface-map.md`, it will overwrite the dev-fixture stub. If the implementation does not delete the dev-fixture *first*, ledger lineage will record the dev-fixture skeptic as the prior agent for the same artifact. Plan H1.S2 to either skip the fallback when `--codex-skeptic-mode skill` is selected (already true per `cbm/cli.py:4724-4750`'s "if skeptic_path.exists()" branch — fine) or explicitly mark the supersession.

3. **`edge-unknown-001` is now load-bearing for challenge ingestion.** The current Skeptic skill-loaded path attaches challenges by `claim_id`. If the H1.S1 contract continues forcing literal `edge-unknown-001`, the Skeptic's competing-reading-and-evidence object can attach trivially to an id everyone agrees is "the unknown one", even when the real challenge belongs to a different surface. Loosening F3 also reduces this risk.

4. **No way to verify the Skeptic actually has isolated context until run.** The isolation probe at `.planning/spikes/2026-05-02-codex-isolation-live` ran in 2026-05-02, before the runtime Surface Mapper produced its artifact. The H1.S2 Skeptic invocation reuses the same `--ephemeral --ignore-user-config --ignore-rules -s read-only` flags, but the prompt body now includes `<runtime_skill>` content that the Skeptic must not see (its own version, not the mapper's). Confirm H1.S2 prompt does not embed the mapper's prompt or its `<runtime_skill>` body — the current `codex_cli_skill_prompt` (`cbm/cli.py:4130-4148`) looks correct.

5. **Test fixture is too small to exercise interesting Skeptic behavior.** `tests/fixtures/sample_repo` is 3 files. The H1.S2 fake-codex regression cannot meaningfully exercise interpretive challenge attachment at that size. Consider a richer fixture where authority-on-authority disputes are plausible.

6. **Repair-pass coupling.** If H1.S2 follows H1.S1's pattern (single repair pass on parent-validation failure), and the Skeptic's repair prompt feeds back its own prior output, there's a real risk of the model laundering a non-substantive challenge through the repair pass. Add a regression where the Skeptic's first attempt is "no challenge", repair prompt asks for grounding — and confirm the parent rejects synthesizing a challenge to satisfy the gate.

7. **Benchmark evidence preservation discipline.** F9 will compound at H1.S2; the Skeptic's outputs, logs, and any repair-pass artifacts should be preserved in `.planning/benchmarks/<date>-<slug>/` so a checkpoint reviewer can audit.

## Suggested Disposition

| Recommendation | Disposition |
|---|---|
| F1 — fix handoff to read coverage/summary/next-action from runtime surface map when present | **revise before H1.S2** |
| F2 — drop or unmistakably label the dev-fixture skeptic stub when `--codex-skeptic-mode none` | **revise before H1.S2** |
| F3 — replace `edge-unknown-001` literal-id requirement with `kind == unknown` | **revise before H1.S2** (or accept and document the leak) |
| F4 — tighten `source_sha` parent check (exact match or ≥7 chars) | **accept** in the H1.S2 slice |
| F5 — re-hash `inputs[].sha256` in parent validator | **accept** in the H1.S2 slice |
| F6 — thread real skill_version into ledger entries | **accept** in the H1.S2 slice |
| F7 — `cbm validate`/`verify-citations` cannot enforce producer identity | **park** with documentation, address when producer-registry consumers expand |
| F8 — add repair-pass regressions and preserve `codex_outputs/`+`logs/` | **revise before H1.S2** (preservation), **accept** (regressions) |
| F9 — preserve full `.research/<run_id>/` in benchmark dir | **revise before H1.S2** |
| F10 — clarify or change `status: draft` semantics for runtime output | **park**; document and revisit at H1.S3 |
| F11 — sanity-check `files_examined_directly` against cited paths | **park**; nice-to-have |
| F12 — record `run_configuration` in producer-registry | **accept** in H1.S2 |
| F13 — backfill BUILD-LOG with design-choice rationale | **accept** as documentation cleanup |

The four `revise before H1.S2` items (F1, F2, F3, F9, and the F8 preservation half) are the ones that, if left alone, will either (a) feed the H1.S2 Skeptic an artifact bundle that misrepresents what was produced, or (b) leave the H1 evidence trail unable to support a future cross-model checkpoint at H1.S3. Everything else can ride along with H1.S2 work or be parked.
