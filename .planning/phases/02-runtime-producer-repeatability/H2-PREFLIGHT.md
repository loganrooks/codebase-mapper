# H2 Preflight Concerns

Status: locked
Date: 2026-05-22
Last updated: 2026-05-22
Supersedes: none
Superseded by: none

## Boundary

This file enumerates the preflight concerns H2.S2 must resolve or document before dispatching the live Surface Mapper + Skeptic run against h11. It does not block H2.S1's deliverables. It is the input to the H2.S2 `/goal` brief that the H2.S1 work prepares for.

H2.S1 itself does not invoke Surface Mapper, Skeptic, or any live producer against h11.

## Concern 1 — Producer-Skill Language Generalization

H2's target is `python-hyper/h11`, Python. `surface-mapper@1.2` and `skeptic@1.2` have both run on Python (MCP `src/git`).

- Language fit risk: **none** for this H2 run.
- Mitigation: not required. The choice of h11 was deliberately Python-only to keep H2 focused on repeatability rather than combining repeatability with a new-language risk for the producer skill. Language generalization is deferred to H3+ when a Go or TypeScript target (e.g., `sourcegraph/conc` or the MCP `src/filesystem` subtree from `H2-TARGET-SELECTION.md`) is selected.
- Required H2.S2 action: none. Do not dry-run probe for language fit; this is unnecessary.

## Concern 2 — Backend Budget And Cost

H1 budget actuals (from preserved `run-manifest.json`s):

- **H1.S1 Surface Mapper** (`run-mcp-git-surface-mapper-h1s1-6`, MCP `src/git`):
  - Wall clock for the `codex-cli-skill-surface-map` step: 3m50s (`started_at: 2026-05-02T20:49:51Z`, `completed_at: 2026-05-02T20:53:41Z`).
  - Total `cbm run` wall clock: 3m51s.
  - Codex flags: `gpt-5.4-mini`, `model_reasoning_effort=medium`, `--ephemeral --ignore-user-config --ignore-rules -s read-only`.
  - Timeout: `--codex-timeout 600` (10 minutes). Used ~38% of the timeout envelope.
  - Final manifest status: `succeeded`.
- **H1.S2b isolated Skeptic** (`run-mcp-git-h1s2b-skeptic-1`, MCP `src/git`):
  - Wall clock for the `codex-cli-skill-skeptic-review` step: 3m34s (`started_at: 2026-05-07T12:33:54Z`, `completed_at: 2026-05-07T12:37:28Z`).
  - Total `cbm run` wall clock: 3m34s.
  - Codex flags: `gpt-5.4-mini`, `model_reasoning_effort=high`, same isolation flags.
  - Timeout: `--codex-timeout 600`. Used ~36% of the timeout envelope.
  - Final manifest status: `succeeded`.

Proposed H2.S2 envelope:

- Codex flags for both producers: `gpt-5.4-mini`, isolation flags identical to H1.
- Surface mapper reasoning effort: `medium` (match H1.S1).
- Skeptic reasoning effort: `high` (match H1.S2b).
- `--codex-timeout`: `600` (match H1).
- Target size is comparable to H1: 11 source files / 2,568 LOC for h11/ (excl tests) vs 12 source files for MCP `src/git`. No reason to expect a substantially different wall clock unless the Codex backend behaves differently for protocol-state-machine code.
- Soft cost envelope estimate: ~4–6 minutes wall clock per producer (assume ~50% timeout-fraction margin over H1 actuals).

Abort conditions during H2.S2:

- Hard abort: a Codex subprocess hits `--codex-timeout 600` and `run-manifest.json` records `status: interrupted` with `cause: timeout`. H2.S2 stops. The `/goal` author root-causes whether the cause is target-shape (re-pick scope), reasoning-effort (re-tune), or backend (escalate). **Do not blindly retry with a higher timeout.**
- Soft abort: wall clock exceeds 8 minutes per producer for two consecutive retries. Same root-cause discipline.
- Cost ceiling: there is no hard $-budget gate in the current backend; the timeout is the load-bearing cap. If the user wants a $-budget gate, that is an out-of-band code change beyond H2.S1 scope.

## Concern 3 — Cross-Vendor Review Skill Repeatability

The `.codex/skills/cross-vendor-review/` skill was used for the H1.S3 pass-claim checkpoint, which produced an `accept` disposition by `claude-opus-4-7`. The skill's repeatability is itself an H2 sub-claim — H2.S3 is the second time it is being asked to deliver a pass-claim checkpoint, and we have only one prior data point.

Plan for H2.S3:

- Reviewer launch surface: `.codex/skills/cross-vendor-review/scripts/run-claude-code-review.sh .planning/reviews/<run-date>-h2-repeatability-checkpoint`.
- Reviewer model: a non-current-model family per ADR-005. If the H2.S2/H2.S3 dev agent is `claude-opus-4-7` (Anthropic Claude family), the reviewer must be from a non-claude family (e.g., `gpt-5` or `codex` family). If the dev agent is a `gpt-5`/`codex` family backend, the reviewer is from `claude` family. Same-model fallback is rejected by `SCOPES_REQUIRING_CROSS_MODEL` at `pass-claim` scope.
- Reviewer mode + effort (per `docs/review-playbook.md`'s mode × effort matrix): for a horizon-closeout pass-claim checkpoint, the recommended sequence is `survey` at `max` (architecture/breadth picture) followed by `opus <file>` at `high` for any load-bearing file the survey flags. In practice the H1.S3 reviewer (Opus 4.7) read the EVIDENCE-MANIFEST.md inputs directly without subdividing into modes; H2.S3 may follow the same pattern if the reviewer is reading a single packet rather than auditing a PR diff.
- Expected outputs (per `cross-vendor-review` skill REVIEW-SPEC contract): `CHECKPOINT.md`, `DISPOSITION.md`, `DISPOSITION.json`, all written by the reviewer; `EVIDENCE-MANIFEST.md` prepared by the H2.S3 dev agent ahead of time.
- Failure modes the skill must surface (from `.codex/skills/cross-vendor-review/SKILL.md`):
  - Reviewer exits nonzero → preserve raw logs, write `RECOVERY.md`, do not synthesize content from logs.
  - Reviewer writes partial files / omits required outputs → same recovery path.
  - Reviewer writes outside declared roots → recovery path; treat as a contract violation.
  - Malformed stream JSON → recovery path.
  - Hits a declared hard limit (e.g., `--max-turns`, `--max-budget-usd`) → recovery path.
  - Ambiguous session state → recovery path using captured `--resume <session-name>` command from `RECOVERY.md`.
- Disposition handling: the H2.S3 dev agent does **not** fill `reviewer_model_id`, `confidence`, or `disposition` on `CHECKPOINT.md` / `DISPOSITION.md` / `DISPOSITION.json`. Those fields stay blank until the reviewer writes them, per ADR-005 and `cross-vendor-review` skill boundaries.

Carry-forward risk: if the skill fails on H2.S3 in a way H1.S3 did not surface, the H2 pass claim is blocked until the failure is dispositioned. That is the correct behavior; do not work around it.

## Concern 4 — Schema And Validator Drift

H1's accepted packet validates against the schemas as merged in `76db3bc` (H1 PR #1 merge to `main` on 2026-05-16). H2 must use the same schemas unless a change is documented.

Verified on 2026-05-22:

```bash
git log 76db3bc..HEAD --oneline -- schemas cbm/schemas
# (no output)
git diff --stat 76db3bc..HEAD -- schemas cbm/schemas
# (no output)
```

Both `schemas/` and the packaged `cbm/schemas/` are byte-identical with `main` at `76db3bc`. The schemas H2 will validate against are:

- `schemas/surface-map.schema.json` (version `1.2`) — unchanged since H1.
- `schemas/handoff.schema.json` (version `1.2`) — unchanged since H1.
- `schemas/evidence-ledger.schema.json` — unchanged since H1.
- `schemas/run-manifest.schema.json` (version `1.2`) — unchanged since H1.
- `schemas/skeptic-review.schema.json` — unchanged since H1.
- `schemas/producer-registry.schema.json` — unchanged since H1.

No migration is needed. H2 targets the same schema versions as H1.

If, between this H2.S1 commit and H2.S2 dispatch, any of these schemas change, H2.S2 must either pin to the H1 schema set or document the change and re-validate. The `loop-status --scope broad-goal` gate continues to require the current main schemas, so schema drift will surface as a validation failure rather than a silent regression.

## Concern 5 — H1-Caveat Carryover

Detailed classification is in `H2-PLAN.md` under "H1 Caveat Carryover". Summary:

- **Final-surface-state provenance drift** (H1 caveat 1): classified (b) generic; H2.S3 follows the same external-lineage-commentary pattern.
- **Historical smoke-anchor ledger entry** (H1 caveat 2): classified (a) H1-specific and resolved; the general pattern (promote only the final Skeptic output) is preserved by H2.S2.
- **Mixed run-id provenance** (H1 caveat 3): classified (b) generic; structurally avoided by H2.S2's single-`cbm run` shape (Surface Mapper + Skeptic in the same run share the same `run_id`). If H2 has to re-split into separate runs, the caveat re-emerges and H2.S3 `LINEAGE.md` must document it the same way H1.S3 did.

## Concern 6 (target-specific) — Protocol-State-Machine Authority Surface

h11 is a tightly coupled protocol library: `Connection`, `_state.py`, `_events.py`, `_readers.py`, and `_writers.py` form a single state machine. The Skeptic might find it harder to challenge centrality than in MCP `src/git` because the authority structure is genuinely concentrated in the state machine rather than distributed across the entrypoint shim.

Mitigation:

- H2.A2 allows a schema-carried "no-challenge" disposition; a quiet Skeptic on h11 is acceptable as long as the surface map carries a non-trivial cited interpretive claim (H2.A3) that survives cross-vendor review.
- The Skeptic should be allowed to raise other axes (e.g., classification: "is the state machine in `_state.py` or in `Connection`?", framing: "is h11 better described as a parser library or an event-emitting state machine?", completeness: "are the event classes the public interface or implementation detail?"). The interpretive_axis enum is open enough to support these.
- If the Skeptic raises zero challenges AND the surface map has zero interpretive claims, H2.A3 is at risk. H2.S2 must surface this state and the H2.S2 `/goal` author must decide whether to re-prompt the Surface Mapper for an interpretive pass or to escalate.

## Concern 7 (target-specific) — Public API Boundary And Re-Exports

h11's `__init__.py` re-exports many names from private modules (`_connection`, `_events`, `_util`, `_version`, etc.). Surface Mapper must record this boundary correctly:

- Treat `__init__.py` as the public-API authority but cite the private modules where the actual definitions live.
- Avoid the failure mode where the Surface Mapper treats `_state.py` as a private implementation detail and skips it from interpretive analysis; the state machine IS the substantive authority structure.

This is a Surface Mapper skill-quality concern, not a structural risk. Recording it here so H2.S2's `/goal` author can re-read it before dispatch.

## Concern 8 (cross-cutting) — H2.A4 Diff Record Discipline

H2.A4 requires recording differences between H1 and H2 in `.planning/STATE.md`. The diff includes:

- `surface-mapper@1.2` skill SHA (record at H2.S2 time; compare to H1's `356cda1f18628fa9c8821478577df0bfa4feaeb349792d347ed9bc4ade5b1740`).
- `skeptic@1.2` skill SHA (compare to H1's `1d676f7d1a23660b00b150dcf4cb9441e4a00e6d02c46fe126999f1bc570de39`).
- Backend version: `codex-cli` (same as H1).
- Target shape: Python protocol library / 11 files / 2,568 LOC (vs H1's Python MCP server / 12 files / unrecorded LOC; H2.S2 may want to record LOC in addition to file count to make the comparator quantitative).
- Surface depth: H1 had 8 authorities and 7 edges. H2 numbers depend on the run.
- Claim/challenge density: H1 produced 1 interpretive challenge (`chl-10001`). H2 may produce 0 or 1+ challenges; both satisfy H2.A2.
- Citation resolution success rate: H1 was 25 citations resolved at the pinned SHA.
- Runtime cost: H1 wall clock 3m51s (surface) + 3m34s (skeptic). H2.S2 records its own actuals.

H2.S2 must capture these diff fields at packet-creation time, not at H2.S3 packet-creation time, because some of the H2.S2 manifest data (skill SHAs, manifest status, step timings) is most-cleanly read from the H2.S2 `run-manifest.json`.

## Concern 9 (cross-cutting) — `.research/` Tree Preservation

The single most-cited H1 evidence-bundle-honesty regression was the original H1.S1 publication NOT preserving the `.research/run-mcp-git-surface-mapper-h1s1-6/` tree (including `logs/` and `codex_outputs/`). H1.S2a fixed this for future runtime benchmarks.

H2.S2 publication MUST preserve `.research/run-h11-h2s2-1/` (logs, codex_outputs, ledgers, intermediates) in the packet under `.planning/benchmarks/<run-date>-h11-h2s2/.research/run-h11-h2s2-1/`. Treat this as a publication-completeness gate: the packet is not complete until the tree is preserved.

## Sign-Off

H2.S1 has surfaced no concern that requires code change before H2.S2 dispatch. Schemas are unchanged. Backend tools (`cbm run`, `cross-vendor-review` skill) are operational. The H2 target is user-confirmed, pinned, and probe-verified.

H2.S2 dispatch is unblocked once this H2.S1 commit lands and `cbm-loop-status --scope broad-goal` passes.
