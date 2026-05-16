---
status: complete
date: 2026-05-07
scope: pass-claim
pass_criterion: H1 minimum-useful CBM floor
reviewer_model_id: claude-opus-4-7
same_model_fallback: false
confidence: high
disposition: accept
---
# H1 Minimum-Useful Checkpoint

## Reviewer

- Reviewer model: `claude-opus-4-7` (Anthropic Claude Opus 4.7).
- Reviewer family: `claude` (not in the disallowed `gpt-5` or `codex` families).
- Reviewer role: cross-vendor pass-claim checkpoint; not the dev-agent that prepared the H1.S3 packet.
- Inputs read directly: the artifacts named in `EVIDENCE-MANIFEST.md` plus the H1.S2b `run-manifest.json` and three spans from the local target checkout for citation spot-check.

## Pass Criterion Reminder

H1 minimum-useful CBM floor: one pinned external target has a real runtime Surface Mapper output, a real isolated Skeptic review over that output, a structurally carried challenge/no-challenge result, a validated handoff with contestation and coverage honesty, and no deterministic-baseline overclaim.

## Findings By Question

### 1. Did H1.S1 use a real runtime Surface Mapper producer?

Yes. `.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/RESULT.md` records run id `run-mcp-git-surface-mapper-h1s1-6` produced by `surface-mapper@1.2` through backend `codex-cli` with `--codex-surface-mode skill --codex-skeptic-mode none --codex-model gpt-5.4-mini --codex-reasoning-effort medium --codex-timeout 600`. The surface map validates, 25 source citations resolved at SHA `4503e2d12b79`, and `check-evidence` passed. Output is not labeled `cbm-baseline-*` or `dev-fixture-*`. The resulting `surface-map.json` carries 8 authorities, 7 edges, and 1 unknown edge (`edge-unknown-001`) with rationale that runtime dispatch is data-dependent and only observable when the server runs — i.e., unknowns are not zero, which `RUNTIME-CONSTITUTION.md` §10 calls suspect when zero. H1.S1 acceptance criteria are met.

### 2. Did H1.S2b use a real isolated Skeptic producer?

Yes. The H1.S2b run-manifest at `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/.research/run-mcp-git-h1s2b-skeptic-1/run-manifest.json` records the Skeptic step `codex-cli-skill-skeptic-review` with `producer_id: skeptic@1.2`, `backend: codex-cli`, `model: gpt-5.4-mini`, `model_reasoning_effort: high`, the recorded skill path/SHA `1d676f7d1a23...`, and the launch flags `--ephemeral --ignore-user-config --ignore-rules -C <target> -s read-only`. The `run_id` is distinct from the H1.S1 run id, the input H1.S1 surface map was imported by absolute path with its SHA-256 captured, and the H1.S2b RESULT records that an output search for parent-session/prohibited-context terms returned no substantive leak signal. Together with the earlier live isolation probe at `.planning/spikes/2026-05-02-codex-isolation-live/`, this is genuine subprocess isolation rather than a re-prompted parent role.

### 3. Was the H1.S2b challenge grounded in citations?

Yes. `chl-10001` cites three competing-evidence spans:

- `pyproject.toml:25-26@4503e2d12b79` (`[project.scripts]` declaration of `mcp-server-git = "mcp_server_git:main"`).
- `src/mcp_server_git/__main__.py:1-5@4503e2d12b79` (the module shim that imports and calls `main`).
- `src/mcp_server_git/__init__.py:7-24@4503e2d12b79` (the click `main` callable that invokes `serve(repository)`).

Reviewer spot-check of the local checkout at the pinned SHA confirmed all three byte ranges resolve to lines that materially support both the original `auth-001` reading (console script and module runner share the same callable) and the alternative reading (launch authority is in packaging metadata and the module shim, while `__init__.py` defines the implementation). The challenge meets the §5 RUNTIME-CONSTITUTION discipline: ≥20-char `competing_reading`, ≥1 `competing_evidence`, `interpretive_axis: centrality`, `relation_to_original: scope_dispute`. It is specific, not generic, and the alternative is non-trivially defensible — exactly the kind of centrality-vs-implementation distinction `VISION.md` says interpretive register should expose.

### 4. Was the H1.S2c disposition structurally carried into the surface/handoff path?

Yes. The promoted `surface-map.json` records:

- `auth-001.claim_register: interpretive`
- `auth-001.claim_status: contested`
- `auth-001.challenges[0].challenge_id: chl-10001`
- `chl-10001.status: accepted_as_alternative`
- The mapper response is recorded inline in `auth-001.rationale` ("Mapper response: accept chl-10001 as an alternative reading...") and as `relation_to_original: scope_dispute`.

Original `auth-001` citations are preserved alongside the alternative — this is contestation, not contradiction or supersession, consistent with §4-§5 of `RUNTIME-CONSTITUTION.md`. The handoff `gate_summary.skeptic_review` reports `challenges_logged: 1, challenges_resolved: 1`, `contestation_summary.claims_by_status.contested: 1`, and `open_challenges: 0`. The evidence ledger `lg-00035` is a `challenge_resolved` entry citing `chl-10001` with resolution `accepted_as_alternative` and `agent: surface-mapper@1.2`. Carry-through is structural, not narrative.

### 5. Does the final handoff preserve coverage honesty and unknowns?

Yes. The H1.S3 `HANDOFF.md` reports `files_in_scope: 12, files_examined_directly: 7, files_inspected_via_extractor: 12, files_unread_in_scope: 0`. Limitations distinguish baseline extractor coverage (every in-scope file) from runtime mapper direct examination (only the files needed for interpretive claims). Coverage caveats name (a) the 7-of-12 direct-examination gap, (b) absence of CI workflow files in scope, and (c) MCP runtime dispatch through the external library remaining partially opaque. The surface map's `unknowns.edge_unknowns_present: true` and the explicit `edge-unknown-001` unknown edge survive into the final state, and `open_questions_count: 1` is preserved on the handoff. No 100%-coverage figure is produced.

### 6. Does the final handoff distinguish runtime evidence from deterministic/dev-fixture evidence?

Yes. The H1.S3 `HANDOFF.md` "Producer Honesty" section explicitly names `surface-mapper@1.2` and `skeptic@1.2` as the runtime-produced evidence and states that any deterministic or baseline artifacts in the packet remain support material only and that no `cbm-baseline-*` or `dev-fixture-*` artifact is used as a substitute for the real Surface Mapper or Skeptic evidence. The H1.S3 handoff itself is `produced_by: cbm-handoff@0.1` (not the baseline handoff renderer). The included `source-h1s2c-handoff.md` is correctly labeled with its `cbm-baseline-handoff@0.1` producer in its own frontmatter and is referenced as a preserved source-stage handoff, not promoted as runtime understanding. `LINEAGE.md` further records that the H1.S3 packet does not promote the historical `.gitignore:1@4503e2d12b79` ledger anchor (`lg-00030`) as supporting evidence for the H1 pass claim. There is no deterministic-baseline overclaim.

### 7. Are artifact lineage and ledger caveats clear enough to audit?

Yes, with one acknowledged residual that does not block the pass claim. `LINEAGE.md` documents:

- the final surface state as H1.S1 + H1.S2b + H1.S2c, with the promoted `surface-map.json` inheriting H1.S1-era `produced_at` and `inputs` while carrying an H1.S2c-era `run_id` and disposition. The author explicitly chose not to add a `refreshed_from` block because mutating the validated successor would require a new artifact-production path, and chose external lineage commentary instead;
- the historical smoke-anchor ledger entry `lg-00030` (a `.gitignore:1@4503e2d12b79` citation introduced by `codex-cli-skeptic` against the original Skeptic markdown), and the fact that the rendered/promoted Skeptic review no longer contains that anchor;
- the mixed run-id provenance on `lg-00029` (`claim_challenged` carries `run_id: run-mcp-git-surface-mapper-h1s1-6` while `artifact_path` points at `.research/run-mcp-git-h1s2b-skeptic-1/surface-map.json`), interpreted as a challenge raised during H1.S2b against an imported H1.S1 artifact, with the durable challenge id `chl-10001` and the H1.S2c successor carrying the disposition.

Residual: the promoted `surface-map.json` frontmatter is internally inconsistent in `produced_at` vs. `run_id` vs. `inputs[]`. The author's reasoning for preserving the validated artifact rather than rewriting it is sound, the inconsistency is documented externally rather than hidden, and no claim or citation is corrupted. This is auditable as-is and is a candidate for a follow-up artifact-production-path improvement, not a checkpoint blocker.

### 8. Is the H1 pass claim scoped correctly?

Yes. The H1.S3 `HANDOFF.md` "Boundary" section explicitly disclaims (i) H1 completion before checkpoint acceptance, (ii) minimum-useful CBM completion before checkpoint acceptance, (iii) Phase B or later, (iv) repeatability, (v) standard mode, (vi) beta readiness, (vii) mature CBM, (viii) cross-platform parity, (ix) broad product maturity. This matches the explicit non-claims in `PROMPT.md` one for one. `STATE.md`, `CURRENT-PLAN.md`, `HORIZONS.md`, and `phases/01-first-runtime-producer-evidence/SUMMARY.md` consistently describe the packet as "prepared, checkpoint pending" rather than as accepted. Deterministic-baseline-is-not-runtime-evidence (ADR-004) and same-model-fallback prohibition for pass-claim scope (ADR-005) are honored. `cbm-loop-status --scope pass-claim` is currently expected to fail with `missing_reviewer_model_id` until this checkpoint is accepted, which is recorded in `VERIFY.md`.

### 9. Disposition

`accept`. See `DISPOSITION.md` for decision text and any optional improvements.

## Limitations Of This Review

- The reviewer did not re-execute the H1.S1 Surface Mapper or the H1.S2b Skeptic; isolation evidence comes from the recorded run-manifest, packet RESULTs, and the earlier `.planning/spikes/2026-05-02-codex-isolation-live/` probe rather than a fresh isolation run.
- Citation resolution at the pinned SHA was confirmed by the packet's `cbm verify-citations` records and by reviewer spot-check of the three competing-evidence spans cited in `chl-10001`. The remaining 25 surface-map source citations were not individually re-checked.
- This review is a pass-claim checkpoint over the H1 minimum-useful floor only. It does not opine on H2 repeatability, Phase B+, or beta-graduation criteria.
