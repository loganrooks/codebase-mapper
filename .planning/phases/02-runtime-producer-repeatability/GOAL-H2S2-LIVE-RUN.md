# Agent Execution Brief — H2.S2 Live Producer Run

Status: proposed
Date: 2026-05-29
Last updated: 2026-05-29
Supersedes: none
Superseded by: none
Audience: AI agent executing the work, and human reviewer auditing the result
Primary horizon: H2 — Runtime Producer Repeatability
Current stage: H2.S2
Goal type: live producer dispatch
Input baseline: `.planning/phases/02-runtime-producer-repeatability/H2-PLAN.md` (locked H2 target + acceptance)
Expected result: a schema-valid H2.S2 benchmark packet at `.planning/benchmarks/<run-date>-h11-h2s2/` produced by a real `surface-mapper@1.2` + `skeptic@1.2` run on `codex-cli` against `python-hyper/h11` at SHA `62c5068c971579d61fa1b55373390e12f25fd856`, with the `.research/` tree preserved and authority docs updated; **without** requesting the cross-vendor pass-claim checkpoint (that is H2.S3).

## One-Sentence Mission

Dispatch a single real `cbm run` that produces both the H2.S2 surface map and Skeptic review against h11, validate the packet at absolute paths, preserve the `.research/` tree, and update the planning docs — without claiming H2 complete and without requesting the H2.S3 cross-vendor pass-claim checkpoint.

## Non-Negotiable Scope

This goal is **H2.S2 live producer dispatch only**.

Do **not** request a cross-vendor pass-claim checkpoint. H2.S3 produces the pass-claim packet; H2.S2 does not. The `cross-vendor-review` skill is not invoked at scope `pass-claim` in this goal.
Do **not** claim H2 complete or repeatability proven. H2 completion requires the H2.S3 packet and a non-current-model checkpoint disposition per ADR-005.
Do **not** claim Phase B+ or beta readiness.
Do **not** rewrite `VISION.md` or `RUNTIME-CONSTITUTION.md`.
Do **not** broaden kernel validators, project packs, or hook policy beyond what H2.S2 requires.
Do **not** revise the accepted H1 packet, the H1 checkpoint disposition, or the locked H2-PLAN.md.
Do **not** re-pick the H2 target. The target is locked: `python-hyper/h11@62c5068c971579d61fa1b55373390e12f25fd856`, scope `h11/` (excluding `h11/tests/`).
Do **not** raise the `--codex-timeout` envelope above 600 seconds without a stop-and-surface to the user. H2-PREFLIGHT Concern 2 prescribes the abort discipline; blind-retry-with-larger-budget is rejected.
Do **not** promote a dev-fixture, baseline, or smoke-anchor artifact. H1 LINEAGE caveat 2 documents the failure mode; H2.S2 promotes only the final Skeptic markdown and only a non-baseline surface map (`produced_by: surface-mapper@1.2`).
Do **not** publish the H2.S2 packet without the `.research/run-h11-h2s2-1/` subtree preserved. H2-PREFLIGHT Concern 9 makes preservation a publication-completeness gate.

The output of this goal makes the H2.S3 handoff packet dispatchable, not the pass-claim disposition itself.

## Required Reading

Read these before editing:

- `VISION.md`
- `RUNTIME-CONSTITUTION.md` (especially §2 evidence ledger, §10 unknowns, §13 artifacts-on-disk, §17 Skeptic three modes, §22 recovery, §25 reuse and refresh discipline)
- `.planning/HORIZONS.md` (H2 / H2.S2 sections)
- `.planning/CURRENT-PLAN.md`
- `.planning/STATE.md`
- `.planning/phases/02-runtime-producer-repeatability/GOAL-H2S1-REPEATABILITY-PLAN.md` (the prior `/goal` that locked the target)
- `.planning/phases/02-runtime-producer-repeatability/H2-PLAN.md` — **the binding plan; H2.S2 implements this**
- `.planning/phases/02-runtime-producer-repeatability/H2-TARGET-SELECTION.md`
- `.planning/phases/02-runtime-producer-repeatability/H2-PREFLIGHT.md` — concerns 1–9 mitigations
- `.planning/phases/02-runtime-producer-repeatability/H2-BENCHMARK-PACKET-SKELETON.md` — the H2.S2 artifact contracts table
- `.planning/phases/02-runtime-producer-repeatability/PLAN.md`, `SUMMARY.md`, `VERIFICATION.md`
- H1 packet for shape reference: `.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/RESULT.md` and `.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/RESULT.md`
- `.planning/decisions/ADR-001-cbm-owns-run-lifecycle.md`
- `.planning/decisions/ADR-003-producer-registry-over-outer-orchestrator.md`
- `.planning/decisions/ADR-004-deterministic-baseline-is-not-runtime-evidence.md`
- `.planning/decisions/ADR-005-cross-model-checkpoint-mandatory-for-pass-claims.md` (informs why H2.S2 does **not** request a checkpoint)
- `schemas/surface-map.schema.json`, `schemas/handoff.schema.json`, `schemas/evidence-ledger.schema.json`, `schemas/run-manifest.schema.json`, `schemas/skeptic-review.schema.json`, `schemas/producer-registry.schema.json`
- `cbm/runtime_skills/surface-mapping.md` and `cbm/runtime_skills/skeptic.md`
- Failure-mode citation for relative-path artifact validation: `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/VERIFY.md:15`

Interpretation order:

1. `H2-PLAN.md` is the binding plan; this brief implements it.
2. `H2-PREFLIGHT.md` is the resolved set of concerns; it tells H2.S2 what is allowed and what triggers stop-and-surface.
3. `H2-BENCHMARK-PACKET-SKELETON.md` is the artifact-contracts table; H2.S2 produces those artifacts exactly.
4. RUNTIME-CONSTITUTION sections govern artifact discipline at the per-claim level.
5. ADR-005 governs the H2.S3 pass-claim checkpoint, which is NOT in H2.S2 scope but the cross-vendor review skill's repeatability is downstream-dependent on H2.S2's output shape.

## Current Facts To Preserve

H2 target (locked on 2026-05-22 via the H2.S1 stop-and-surface gate, recorded in `H2-PLAN.md` and `H2-TARGET-SELECTION.md`):

- Repository: `https://github.com/python-hyper/h11`
- Pinned SHA: `62c5068c971579d61fa1b55373390e12f25fd856`
- Scope: `h11/` package source, excluding `h11/tests/`
- License: MIT
- Approximate LOC: 2,568 across 11 source files
- Target slug: `h11`

Schemas (verified unchanged since H1 merge `76db3bc` per H2-PREFLIGHT Concern 4): `surface-map.schema.json`, `handoff.schema.json`, `evidence-ledger.schema.json`, `run-manifest.schema.json`, `skeptic-review.schema.json`, `producer-registry.schema.json`.

H2.S2 must preserve all of:

- H1 acceptance at `76db3bc` (PR #1).
- The H2.S1 plan-only deliverables (`H2-PLAN.md`, `H2-PREFLIGHT.md`, `H2-BENCHMARK-PACKET-SKELETON.md`, `H2-TARGET-SELECTION.md`) without rewriting them.
- The `H2-PLAN.md` "Variant slice structure — no H2.S2a evidence-bundle-repair pre-step planned" sign-off. H2.S2 is a single `cbm run`; no pre-emptive S2a slice.
- The H2-PREFLIGHT Concern 5 / Concern 8 / Concern 9 obligations (caveat carryover, H2.A4 diff capture, `.research/` preservation).

What is **not** yet proven and must remain open until H2.S3:

- H2 cross-vendor pass-claim checkpoint (ADR-005 gate at `loop-status --scope pass-claim`).
- That `surface-mapper@1.2` / `skeptic@1.2` survive a second packet validation across a different target-shape.
- Repeatability of the `cross-vendor-review` skill at scope `pass-claim` (its second use; first was H1.S3).

## H2.S2 Deliverables

Produce a complete H2.S2 benchmark packet matching `H2-BENCHMARK-PACKET-SKELETON.md` exactly:

```text
.planning/benchmarks/<run-date>-h11-h2s2/
  RESULT.md
  surface-map.json
  skeptic-review-surface-map.md
  evidence-ledger.jsonl
  run-manifest.json
  producer-registry.json
  handoff.md
  .research/run-h11-h2s2-1/
    logs/
    codex_outputs/
    surface-map.json
    skeptic-review/surface-map.md
    evidence-ledger.jsonl
    evidence-ledger.jsonl.integrity.json
    producer-registry.json
    run-manifest.json
    handoff.md
    handoff.json
```

`<run-date>` is the actual date the packet directory is created (the date of this `/goal` invocation, not 2026-05-29 from this brief's "Date" header).

Update these existing authority docs as part of the H2.S2 commit:

```text
.planning/CURRENT-PLAN.md
.planning/HORIZONS.md
.planning/STATE.md
.planning/phases/02-runtime-producer-repeatability/PLAN.md
.planning/phases/02-runtime-producer-repeatability/SUMMARY.md
.planning/phases/02-runtime-producer-repeatability/VERIFICATION.md
BUILD-LOG.md
```

`HORIZONS.md` may move H2.S1 to `complete` (post-loop-status pass) and H2.S2 to `current; live evidence produced` (not `complete` — H2.S2 is complete only when its loop-status pass and a downstream H2.S3 packet have produced the pass-claim checkpoint). Do **not** mark H2 complete.

Do **not** create H2.S3 artifacts. The H2.S3 packet, the cross-vendor review packet, and the pass-claim disposition are H2.S3 deliverables, not H2.S2.

## Dispatch Plan

### Phase 1 — Probe re-verification (read-only)

Re-run the H2-PLAN.md probe (no `cbm run`, no Surface Mapper, no Skeptic):

```bash
git ls-remote https://github.com/python-hyper/h11.git | grep 62c5068c971579d61fa1b55373390e12f25fd856
# expect: 62c5068c971579d61fa1b55373390e12f25fd856	HEAD
# expect: 62c5068c971579d61fa1b55373390e12f25fd856	refs/heads/master
```

If the SHA is no longer present at HEAD or the LOC count drifts, stop-and-surface to the user. Do **not** silently re-pick.

Clone the target into the H2.S2 dispatch workspace, distinct from the H2.S1 re-verification probe workspace. The H2.S1 probe used `/var/tmp/cbm-h2-target-probes-20260522/h11`; **do not reuse that path** — it was a date-stamped read-only re-verification workspace and reusing it risks mixing probe state with live producer dispatch. The H2.S2 dispatch workspace uses a SHA-stamped path so the same path resolves across re-invocations:

```bash
PROBE_DIR=/var/tmp/cbm-h2-h11-62c5068
mkdir -p "$PROBE_DIR"
git clone --filter=blob:none --no-checkout https://github.com/python-hyper/h11.git "$PROBE_DIR/h11"
git -C "$PROBE_DIR/h11" checkout 62c5068c971579d61fa1b55373390e12f25fd856
git -C "$PROBE_DIR/h11" rev-parse HEAD
# expect: 62c5068c971579d61fa1b55373390e12f25fd856
```

### Phase 2 — Live producer dispatch

**Dispatch shape — two `cbm run` invocations (matches H1 precedent).** H1 acceptance was produced by **two** separate `cbm run` invocations: H1.S1 (`run-mcp-git-surface-mapper-h1s1-6`, Surface at `medium`, no Skeptic) and H1.S2b (`run-mcp-git-h1s2b-skeptic-1`, Skeptic at `high` against an imported surface). H2.S2 mirrors that shape under a single `/goal` because the H2-PREFLIGHT Concern 2 envelope (Surface=`medium`, Skeptic=`high`) cannot be satisfied in a single `cbm run` against the current CLI (`cbm/cli.py:6395`'s single global `--codex-reasoning-effort` is applied to both the Surface step at `cli.py:5264-5279` and the Skeptic step at `cli.py:5309-5324`). The two-run shape is therefore the **precedent-matching** shape, not a deviation. Issue #23 tracks ADR-006 (per-producer reasoning-effort + backend-agnostic effort-mapping abstraction) as a steady-state improvement that would unlock a future single-`cbm run` form. That single-run form is documented at the bottom of this Phase 2 as the post-ADR-006 target, not as a constraint H2.S2 must match today.

**Planning-doc tension to surface.** `H2-PLAN.md:144-145` reads "Single `cbm run` invocation producing both `surface-map.json` and `skeptic-review-surface-map.md` in one packet." That language was authored assuming a CLI that could carry the medium/high envelope in one run; given the current CLI, it is internally inconsistent with the H2-PREFLIGHT Concern 2 envelope at `H2-PREFLIGHT.md:43-44`. H1 never had that single-run shape either. The H2.S2 dispatcher should flag this `H2-PLAN.md ⇄ H2-PREFLIGHT.md` tension to the user as a one-line correction on `H2-PLAN.md` before or during dispatch (e.g., revise L144-145 to "Two-run dispatch matching H1.S1 + H1.S2b until ADR-006 lands; see `GOAL-H2S2-LIVE-RUN.md` Phase 2 for the canonical invocation").

**Ledger and run-id provenance under the two-run shape.** Run 2's `--codex-surface-mode existing` invokes `command_import_surface_artifact` (`cli.py:4492-4500`), which calls `append_citation_entries` with `run_id = run-h11-h2s2-2`. Run 2's `evidence-ledger.jsonl` therefore already carries every Run 1 surface citation **re-attributed** to Run 2's run-id (alongside the new `claim_challenged` entries from Skeptic). This is the H1 LINEAGE caveat 3 pattern by construction. The H2.S2 packet's promoted `evidence-ledger.jsonl` is Run 2's ledger directly (not a concatenation — concatenating Run 1's ledger with Run 2's would duplicate the same surface citations under two run-ids and break `cbm check-evidence`'s dedup expectations). Run 1's ledger is preserved under `.research/run-h11-h2s2-1/` as source-stage audit evidence so the original-attribution-history is recoverable. The mixed-run-id-by-import-construction story replaces the prior "merged into a single ledger" instruction and is documented in H2.S2 RESULT.md and inherited by H2.S3 LINEAGE.md per the H2-PLAN.md:172-173 expectation.

Codex envelope (from H2-PREFLIGHT Concern 2):

- Backend: `codex-cli` (`--backend codex-cli`)
- Model: `gpt-5.4-mini` (`--codex-model gpt-5.4-mini`)
- Surface Mapper reasoning effort: `medium`
- Skeptic reasoning effort: `high`
- Timeout: `600` (`--codex-timeout 600`)
- Live-codex authorization: `--allow-live-codex`
- Surface mode (Run 1): `skill` (`--codex-surface-mode skill`) — invokes the real `surface-mapper@1.2` skill, not the deterministic baseline.
- Skeptic mode (Run 1): `none` (`--codex-skeptic-mode none`) — defer Skeptic to Run 2 because Run 2 uses Skeptic-effort=`high`.
- Surface mode (Run 2): `existing` (`--codex-surface-mode existing --surface-artifact <Run-1 surface-map.json>`) — consumes the Run 1 surface map, does not re-invoke the Surface Mapper.
- Skeptic mode (Run 2): `skill` (`--codex-skeptic-mode skill`) — invokes the real `skeptic@1.2` skill against the imported surface.
- Isolation flags (set by `cbm` at the Codex subprocess level, not by the brief): `--ephemeral --ignore-user-config --ignore-rules -s read-only`

Run IDs: `run-h11-h2s2-1` (Surface), `run-h11-h2s2-2` (Skeptic). Both runs write into the same packet directory `.planning/benchmarks/<run-date>-h11-h2s2/` so the H2.A4 diff record and `.research/` preservation operate on the combined packet. The packet's `.research/` subtree therefore preserves both `run-h11-h2s2-1/` and `run-h11-h2s2-2/`.

**Spatial model.** `cbm run` resolves the run directory via `run_paths(repo, run_id)` (`cli.py:909-919`), which is literally `Path(args.repo).resolve() / ".research" / run_id`. Because both runs pass `--repo "$TARGET"`, the per-run `.research/` subtrees land **inside the h11 target checkout** (`$TARGET/.research/run-h11-h2s2-1/` and `$TARGET/.research/run-h11-h2s2-2/`), **not** inside `$CBM_REPO`. The H2.S2 packet directory (`$PACKET = $CBM_REPO/.planning/benchmarks/<run-date>-h11-h2s2/`) is the packet's eventual home, but `cbm run` writes nothing there directly — the packet is assembled by copying from `$TARGET/.research/` to `$PACKET/` in the post-Run-2 assembly step below. H1's accepted precedent is the same shape: H1.S1's surface map landed at `/var/tmp/cbm-h1-mcp-servers-4503e2d/src/git/.research/run-mcp-git-surface-mapper-h1s1-6/surface-map.json` (target checkout, not CBM repo).

Run 1 — Surface Mapper at reasoning-effort=`medium`:

```bash
# Substitute /Users/<you>/Development/cbm with the absolute CBM repo path on the executing host.
CBM_REPO=/Users/rookslog/Development/cbm
PACKET=$CBM_REPO/.planning/benchmarks/<run-date>-h11-h2s2
TARGET=/var/tmp/cbm-h2-h11-62c5068/h11

cd "$CBM_REPO"
python3 -m cbm.cli run \
  --repo "$TARGET" \
  --goal "H2.S2 live producer: surface-mapper@1.2 against python-hyper/h11@62c5068c, scope h11/ excl tests" \
  --mode lightweight \
  --backend codex-cli \
  --allow-live-codex \
  --codex-model gpt-5.4-mini \
  --codex-reasoning-effort medium \
  --codex-surface-mode skill \
  --codex-skeptic-mode none \
  --codex-timeout 600 \
  --run-id run-h11-h2s2-1
```

Confirm Run 1 produced a non-baseline `surface-map.json` (`produced_by` field starts with `surface-mapper@1.2`, not `cbm-baseline-*` or `dev-fixture-*`) **before** launching Run 2 — Run 2's `--codex-surface-mode existing` would otherwise import a baseline-shaped artifact and `existing_surface_producer` (`cli.py:5235`) would propagate the baseline label into the packet's producer-registry. Concrete check:

```bash
# Positive assertion (fails closed): the produced_by field must START WITH
# "surface-mapper@". Any other producer-id — including future bug channels like
# cbm-fallback-surface@*, *-stub@*, etc. that don't match the listed baseline
# prefixes — also stops the dispatch. This is stricter than negating
# cbm-baseline-* / dev-fixture- prefixes alone, which would let an unknown
# producer-id channel slip through.
PRODUCED_BY=$(jq -er '.produced_by' "$TARGET/.research/run-h11-h2s2-1/surface-map.json")
case "$PRODUCED_BY" in
  surface-mapper@*)
    echo "Run 1 produced_by=$PRODUCED_BY — OK, real skill output"
    ;;
  *)
    echo "Run 1 produced_by=$PRODUCED_BY — STOP. Not a real surface-mapper output."
    echo "Do NOT launch Run 2 against a non-skill surface."
    exit 1
    ;;
esac
```

Run 2 — Skeptic at reasoning-effort=`high` against the Run 1 surface:

```bash
# Surface artifact lives in the TARGET checkout's .research/, not in CBM_REPO/.research/.
# cbm run's run_paths() resolves to Path(args.repo) / ".research" / run_id (cli.py:909-919),
# and Run 1 was --repo "$TARGET", so Run 1's surface is at $TARGET/.research/...
RUN1_SURFACE="$TARGET/.research/run-h11-h2s2-1/surface-map.json"

cd "$CBM_REPO"
python3 -m cbm.cli run \
  --repo "$TARGET" \
  --goal "H2.S2 live producer: skeptic@1.2 over imported surface from run-h11-h2s2-1, target python-hyper/h11@62c5068c" \
  --mode lightweight \
  --backend codex-cli \
  --allow-live-codex \
  --codex-model gpt-5.4-mini \
  --codex-reasoning-effort high \
  --codex-surface-mode existing \
  --surface-artifact "$RUN1_SURFACE" \
  --codex-skeptic-mode skill \
  --codex-timeout 600 \
  --run-id run-h11-h2s2-2
```

After Run 2 completes, assemble the H2.S2 packet in three steps. Source paths under `$TARGET/.research/` (NOT `$CBM_REPO/.research/`) per the Spatial model note above:

1. **Create the packet directory and copy the promoted artifacts into the packet root.** Defer `mkdir -p "$PACKET"` to this step so the executing agent's mental model stays clean — `cbm run` does not write into `$PACKET` and creating it ahead of time would invite the misreading that "the packet dir is the run output dir":

```bash
mkdir -p "$PACKET"

cp "$TARGET/.research/run-h11-h2s2-1/surface-map.json"               "$PACKET/surface-map.json"
cp "$TARGET/.research/run-h11-h2s2-2/skeptic-review/surface-map.md"  "$PACKET/skeptic-review-surface-map.md"
cp "$TARGET/.research/run-h11-h2s2-2/handoff.md"                     "$PACKET/handoff.md"
cp "$TARGET/.research/run-h11-h2s2-2/handoff.json"                   "$PACKET/handoff.json"
cp "$TARGET/.research/run-h11-h2s2-2/producer-registry.json"         "$PACKET/producer-registry.json"
# Promote Run 2's run-manifest as the packet's primary (it carries the Skeptic step
# whose effort=high satisfies Concern 2 and whose handoff is the promoted one);
# Run 1's manifest is preserved under .research/run-h11-h2s2-1/.
cp "$TARGET/.research/run-h11-h2s2-2/run-manifest.json"              "$PACKET/run-manifest.json"
```

2. **Preserve both `.research/` subtrees** under `$PACKET/.research/` per H2-PREFLIGHT Concern 9 — Run 1's subtree gives the original-attribution audit trail for the mixed-run-id ledger documentation:

```bash
mkdir -p "$PACKET/.research"
cp -R "$TARGET/.research/run-h11-h2s2-1" "$PACKET/.research/run-h11-h2s2-1"
cp -R "$TARGET/.research/run-h11-h2s2-2" "$PACKET/.research/run-h11-h2s2-2"
```

3. **Promote Run 2's evidence-ledger as the packet's canonical ledger** (do **not** concatenate Run 1's ledger). `command_import_surface_artifact` (`cli.py:4492-4500`) already re-introduces every Run 1 surface citation into Run 2's ledger with `run_id = run-h11-h2s2-2`. Concatenating the two ledgers would produce duplicate `citation_introduced` entries under different run-ids for the same surface lines and break the dedup that `ledger_citations` (`cli.py:857-863`) enforces inside `append_citation_entries` (`cli.py:884+`). Run 1's ledger is preserved under `.research/run-h11-h2s2-1/` as source-stage audit evidence.

**Timestamp caveat (mixed-run-id pattern, by construction):** the promoted canonical ledger's `ts` field for every imported Run 1 citation is the Run 2 wall-clock (the moment `command_import_surface_artifact` re-introduced it), not the original first-emission moment from Run 1. RUNTIME-CONSTITUTION §2's append-only-with-chronological-ordering invariant continues to hold within the canonical ledger (Run 2's writes are chronological), but a reviewer auditing "when was this citation first proposed?" must consult `.research/run-h11-h2s2-1/evidence-ledger.jsonl` (the source-stage ledger preserved above) for the actual first-emission timestamps. The H2.S2 RESULT.md "Mixed-run-id documentation" block (Phase 5 below) MUST name this caveat explicitly so the H2.S3 reviewer does not misattribute first-emission chronology to Run 2.

```bash
cp "$TARGET/.research/run-h11-h2s2-2/evidence-ledger.jsonl" "$PACKET/evidence-ledger.jsonl"

# Sanity-check: every line is valid JSONL.
python3 -c "
import json
with open('$PACKET/evidence-ledger.jsonl') as f:
    lines = [json.loads(l) for l in f if l.strip()]
print(f'{len(lines)} ledger entries')
"
```

Under the future single-`cbm run` shape (post-ADR-006), Run 1 and Run 2 collapse into one run with one ledger; the promote step becomes a direct copy from `$TARGET/.research/run-h11-h2s2-1/` and no `.research/run-h11-h2s2-2/` subtree exists.

**Note on `--mode lightweight` (matches H1 exactly).** Both runs above set `--mode lightweight`. This matches H1 acceptance exactly: `.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/RESULT.md` records `--mode lightweight` for H1.S1, and `.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/.research/run-mcp-git-h1s2b-skeptic-1/run-manifest.json` records `mode: lightweight` for H1.S2b. The codex-cli Surface Mapper step (`cli.py:5260-5282`) and codex-cli Skeptic step (`cli.py:5305-5328`) are wired **outside** the mode-conditional block at `cli.py:5330` (`if args.mode in {"standard", "deep"}:`); `--mode lightweight` does **not** skip them. The standard-mode block only adds deterministic-baseline `authority-map`, `dependency-graph`, `verification-map`, `synthesis-index` and four `dev-fixture-skeptic@0.1` reviews — none of which are listed in the H2.S2 packet skeleton (`H2-BENCHMARK-PACKET-SKELETON.md` H2.S2 Packet block). Choosing `--mode standard` would (a) produce dev-fixture-skeptic artifacts that conflict with the brief's "Do not promote a dev-fixture, baseline, or smoke-anchor artifact" non-negotiable scope (line 31) via `.research/` preservation by construction, (b) deviate from H1 precedent, and (c) introduce artifacts the skeleton does not contract. Use `lightweight`.

When ADR-006 lands (issue #23), H2.S2 should re-converge to a single `cbm run` with per-producer reasoning-effort flags — the split documented here is interim, not the desired steady state.

**Future-form (single-cbm-run, gated on ADR-006 / issue #23 closing).** When the CLI exposes per-producer reasoning-effort flags (working name `--surface-reasoning-effort medium --skeptic-reasoning-effort high`), the single-run invocation will look like:

```bash
# DO NOT RUN UNTIL ADR-006 LANDS. Listed only so the brief documents the steady state.
python3 -m cbm.cli run \
  --repo "$TARGET" \
  --goal "H2.S2 live producer ..." \
  --mode lightweight \
  --backend codex-cli \
  --allow-live-codex \
  --codex-model gpt-5.4-mini \
  --surface-reasoning-effort medium \
  --skeptic-reasoning-effort high \
  --codex-surface-mode skill \
  --codex-skeptic-mode skill \
  --codex-timeout 600 \
  --run-id run-h11-h2s2-1
```

That single-run shape avoids the mixed-run-id caveat and matches `H2-PLAN.md:144-146` ("Single `cbm run` invocation producing both `surface-map.json` and `skeptic-review-surface-map.md`"). The interim split above is a temporary deviation that must be removed once ADR-006 lands.

Stop-and-surface mid-dispatch if any of the following fires:

- Codex subprocess hits the timeout (`run-manifest.json` records `status: interrupted` + `cause: timeout`). Hard abort per H2-PREFLIGHT Concern 2. Root-cause before any retry.
- Surface Mapper produces a baseline-shaped artifact (`produced_by` starts with `cbm-baseline-*` or `dev-fixture-*`). H2-BENCHMARK-PACKET-SKELETON H2.S2 stop-and-surface row 1. Stop.
- Skeptic output cites prohibited parent-session context, is generic without competing evidence, or relies on hidden mapper reasoning. H1 LINEAGE caveat patterns — stop and either re-prompt or surface to the user.
- Citation resolution fails at the pinned SHA (any cited `path:lines@sha` does not resolve). Stop; document an `uncertainty-register.jsonl` entry per RUNTIME-CONSTITUTION §10 only after user confirms the response shape.
- Wall clock exceeds 8 minutes per producer for two consecutive retries (H2-PREFLIGHT Concern 2 soft abort).

### Phase 3 — Validate the packet at absolute paths

All artifact paths in validation commands MUST be absolute (re H1.S3 VERIFY.md:15 failure mode). Substitute `/Users/rookslog/Development/cbm` with the absolute CBM-repo path on the executing host:

```bash
PACKET=/Users/rookslog/Development/cbm/.planning/benchmarks/<run-date>-h11-h2s2
TARGET=/var/tmp/cbm-h2-h11-62c5068/h11

python3 -m cbm.cli validate           "$PACKET/surface-map.json"                --repo "$TARGET"
python3 -m cbm.cli verify-citations   "$PACKET/surface-map.json"                --repo "$TARGET"
python3 -m cbm.cli check-evidence     "$PACKET/surface-map.json"                --repo "$TARGET"
python3 -m cbm.cli validate           "$PACKET/skeptic-review-surface-map.md"   --repo "$TARGET"
python3 -m cbm.cli verify-citations   "$PACKET/skeptic-review-surface-map.md"   --repo "$TARGET"
python3 -m cbm.cli validate           "$PACKET/run-manifest.json"               --repo "$TARGET"
python3 -m cbm.cli validate           "$PACKET/producer-registry.json"          --repo "$TARGET"
python3 -m cbm.cli validate           "$PACKET/handoff.md"                      --repo "$TARGET"
python3 -m cbm.cli verify-citations   "$PACKET/handoff.md"                      --repo "$TARGET"
```

Under the interim split shape, the packet may carry two `run-manifest.json` files (one per run). Validate each:

```bash
python3 -m cbm.cli validate           "$PACKET/.research/run-h11-h2s2-1/run-manifest.json" --repo "$TARGET"
python3 -m cbm.cli validate           "$PACKET/.research/run-h11-h2s2-2/run-manifest.json" --repo "$TARGET"
```

Each command must exit 0. Record exit codes, surface counts, and citation counts in `RESULT.md` and `VERIFICATION.md`.

### Phase 4 — Preserve `.research/` tree

Under the interim two-run split, confirm `$PACKET/.research/` contains **both** `run-h11-h2s2-1/` and `run-h11-h2s2-2/` subtrees, each with its own `logs/`, `codex_outputs/`, per-step ledgers, and manifests as listed in H2-BENCHMARK-PACKET-SKELETON. If the runtime wrote `.research/` outside the packet, copy both subtrees in. The packet is **not complete** until both trees are preserved (H2-PREFLIGHT Concern 9).

Under the future single-cbm-run shape (post-ADR-006), only `.research/run-h11-h2s2-1/` would exist; the skeleton's expected-path block at `H2-BENCHMARK-PACKET-SKELETON.md:26` describes that shape and is the steady state.

### Phase 5 — Write `RESULT.md` and `handoff.md`

`RESULT.md` mirrors the shape of `.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/RESULT.md` and `.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/RESULT.md` combined (since H2.S2 produces both producers' artifacts in one packet, even if the dispatch shape is two `cbm run`s). It records:

- Target (`python-hyper/h11@62c5068c`, scope, LOC, license).
- Commands and run-ids (`run-h11-h2s2-1` for Surface, `run-h11-h2s2-2` for Skeptic under the interim split; collapsed to a single id under the post-ADR-006 single-run shape).
- Dispatch shape declaration: explicitly state whether this run used the **interim split** (issue #23) or the **single-run** form, with a one-line citation of which CLI flags were used. Future H2.S3 reviewers must be able to read this from `RESULT.md` without re-deriving from manifests.
- Surface summary (authority count, edge count, register mix, unknown-edge count per §10).
- Skeptic outcome (challenge IDs and titles, or schema-carried no-challenge note).
- Validation command outputs (exit codes, citation counts).
- H2.A4 diff fields from H2-PREFLIGHT Concern 8 (skill SHAs, backend version, target shape, surface depth, claim/challenge density, citation success rate, runtime cost).
- **Mixed-run-id documentation** (when the interim split is used) — record the H1 LINEAGE caveat 3 re-emergence per `H2-PLAN.md:172-173`. State which ledger entries carry which run-id, why the split was used (issue #23), and the expected re-convergence path.
- Boundary: H2.S2 evidence only; no H2 completion claim; no pass-claim checkpoint requested.

`handoff.md` is the per-run handoff produced by `cbm-handoff@0.1`. Under the interim split, each run produces its own per-run handoff; the H2.S2 packet's promoted `handoff.md` is the Run 2 (Skeptic) handoff because it consumes the Run 1 surface and carries the final claim contestation state. The Run 1 (Surface) handoff is preserved at `$PACKET/.research/run-h11-h2s2-1/handoff.md` as source-stage evidence. Both handoffs validate against `schemas/handoff.schema.json`. The promoted `handoff.md` declares `recommended_next_action_kind: prepare_pass_claim_review` (the cross-vendor reviewer is dispatched in H2.S3, not H2.S2).

### Phase 6 — H2.A4 diff record discipline

Record the H2-vs-H1 diff fields in `.planning/STATE.md` per H2-PREFLIGHT Concern 8 (skill SHAs vs H1 `356cda1f...` and `1d676f7d...`, backend, target shape, surface depth, claim/challenge density, citation success rate, runtime cost). Read these from the H2.S2 `run-manifest.json` directly — do not rely on H2.S3 to re-derive them.

## Authority-Doc Updates

After the packet is complete and validated.

**Vocabulary**: the two status words `live evidence produced` and `completed` reference **different things** in this brief, and the authority docs must use them consistently:

- **work-slice status** (used in Phase 02 `PLAN.md`): tracks whether this `/goal`'s deliverables exist. H2.S2's work-slice is **completed** the moment the H2.S2 packet validates and `cbm loop-status --scope broad-goal --work-category runtime-producer` returns `status: ok`.
- **horizon-stage status** (used in `HORIZONS.md`): tracks whether the horizon's acceptance criteria are met. H2.S2 advances the horizon to `live evidence produced` once this `/goal` completes, but the horizon-stage cannot itself reach `complete` until H2.S3 lands its pass-claim checkpoint (per H2.A5 / ADR-005). The H2 horizon is **not** complete until H2.S3.

The same fact (this `/goal`'s outcome) gets two different status verbs in two different documents because they track different things. Apply the verb that matches each doc's role; do not back-propagate one doc's verb into the other.

### `.planning/CURRENT-PLAN.md`

- Update the Active Recovery Sequence item that references H2.S2 (item 27 today per `.planning/CURRENT-PLAN.md:61` — confirm before editing; the item number may have shifted if the brief is dispatched after later /goals reorganize the sequence) to "completed: H2.S2 packet at `<commit-hash>` and packet path `<absolute path>`". This is **work-slice status**.
- Add a new item for the next /goal: "Author `GOAL-H2S3-HANDOFF-AND-CHECKPOINT.md` against H2.S2 evidence."
- Update `Next /goal Track` to reference H2.S3 (validated handoff + cross-vendor pass-claim checkpoint).
- Keep `Current horizon: H2` and `Current stage: H2.S2` until completion; then advance `Current stage` to H2.S3.

### `.planning/HORIZONS.md`

- H2.S1 may now be marked `complete` (post-H2.S2 loop-status pass on `broad-goal` satisfies the H2.S1 brief's completion condition that was outstanding).
- H2.S2 horizon-stage status becomes `live evidence produced; horizon-completion pending H2.S3`. Do **not** mark the H2.S2 horizon-stage `complete` until H2.S3 lands the pass-claim checkpoint per H2.A5 / ADR-005.
- Do **not** mark the H2 horizon complete.

### `.planning/STATE.md`

- Add a Phase 02 Recent Checkpoints entry for the H2.S2 commit hash.
- Replace the H2.S1 verification footer's "expected status" templated placeholders with the actual H2.S2 post-commit `loop-status` JSON shape per the H2.S1 brief's two-commit pattern.
- Append the H2.A4 diff fields from H2-PREFLIGHT Concern 8.
- Update `pending next work` to reference H2.S3.
- If the interim split shape was used (issue #23), append a short note documenting the dispatch deviation from `H2-PLAN.md:144-146` and the H1 caveat 3 re-emergence.

### Phase 02 files (`PLAN.md`, `SUMMARY.md`, `VERIFICATION.md`)

- `PLAN.md`: bump `Last updated`. Move the H2.S2 track to **work-slice status** `completed` with the packet pointer. **Do not** add a horizon-completion claim here; that is `HORIZONS.md`'s scope.
- `SUMMARY.md`: orienting paragraph + factual state list updated to reflect H2.S2 evidence produced. Never overclaim. Bump `Last updated`.
- `VERIFICATION.md`: append the H2.S2 verification record (commands run, exit codes, test counts, loop-status outcomes). Bump `Last updated`.

### `BUILD-LOG.md`

Add a slice entry for H2.S2. Shape: H2.S1 slice entry but with H2.S2-specific Context / Implemented / Tests / Verification / Boundary fields.

## H2.S2 Verification Commands

Follows H2-PLAN.md's H2 Verification Commands template, with concrete absolute paths.

Pre-dispatch:

```bash
TMPDIR=/var/tmp pytest -q
git diff --check -- .planning BUILD-LOG.md cbm tests schemas
python3 -m cbm.cli loop-status --repo . --scope broad-goal --work-category runtime-producer --json
python3 -m cbm.cli loop-status --repo . --scope recovery-slice --work-category runtime-producer --json
```

Pre-dispatch loop-status outputs are recorded into `RESULT.md` and the H2.S1 verification footer in `STATE.md` (the templated placeholders from the H2.S1 commit are now resolved against the H2.S2 commit's post-state).

Post-dispatch (after the packet is written and authority docs are staged):

```bash
PACKET=/Users/rookslog/Development/cbm/.planning/benchmarks/<run-date>-h11-h2s2
TARGET=/var/tmp/cbm-h2-h11-62c5068/h11

python3 -m cbm.cli validate           "$PACKET/surface-map.json"                --repo "$TARGET"
python3 -m cbm.cli verify-citations   "$PACKET/surface-map.json"                --repo "$TARGET"
python3 -m cbm.cli check-evidence     "$PACKET/surface-map.json"                --repo "$TARGET"
python3 -m cbm.cli validate           "$PACKET/skeptic-review-surface-map.md"   --repo "$TARGET"
python3 -m cbm.cli verify-citations   "$PACKET/skeptic-review-surface-map.md"   --repo "$TARGET"
python3 -m cbm.cli validate           "$PACKET/run-manifest.json"               --repo "$TARGET"
python3 -m cbm.cli validate           "$PACKET/producer-registry.json"          --repo "$TARGET"
python3 -m cbm.cli validate           "$PACKET/handoff.md"                      --repo "$TARGET"
python3 -m cbm.cli verify-citations   "$PACKET/handoff.md"                      --repo "$TARGET"

TMPDIR=/var/tmp pytest -q
git diff --check -- .planning BUILD-LOG.md cbm tests schemas
```

Post-commit (after the H2.S2 commit lands):

```bash
python3 -m cbm.cli loop-status --repo . --scope broad-goal      --work-category runtime-producer --json
python3 -m cbm.cli loop-status --repo . --scope recovery-slice  --work-category runtime-producer --json
```

Expected behavior at the H2.S2 post-commit state:

- `broad-goal` must pass with `status: ok`, no issues, no warnings.
- `recovery-slice` must pass.
- `pass-claim` is **not** in the H2.S2 verification command list. It continues to pass on the accepted H1 minimum-useful checkpoint at `.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/`, which is correct for H1 and is not H2 evidence. H2.A5 is satisfied only when H2.S3 produces a non-current-model pass-claim checkpoint that becomes the most-recent accepted pass-claim checkpoint per `checkpoint_for_loop_scope` (`cbm/cli.py:5430-5452`).

## Two-Commit Verification Pattern

Same shape as the H2.S1 brief (Commit 1 = H2.S2 work with templated placeholders; Commit 2 = post-commit loop-status record only if the placeholders diverged from actuals). The dirty-authority-docs gate makes a single pre-commit `loop-status` deterministically fail on the H2.S2 commit boundary; that is the gate firing correctly, not an H2 regression.

**Commit 1 — H2.S2 work** (substantive slice):

```bash
TMPDIR=/var/tmp pytest -q
git diff --check -- .planning BUILD-LOG.md cbm tests schemas
git add <H2.S2 packet directory + authority-doc edits + BUILD-LOG.md entry>
git commit -m "<scoped subject>"
```

`STATE.md` and `BUILD-LOG.md` in Commit 1 carry templated placeholders for the post-commit loop-status JSON (e.g., `status: ok`, `issues: []`, `warnings: []`). The H2.S1 commit's templated placeholders are also resolved in this commit if H2.S2 advances H2.S1's status.

**Post-Commit-1 verification**:

```bash
python3 -m cbm.cli loop-status --repo . --scope broad-goal      --work-category runtime-producer --json
python3 -m cbm.cli loop-status --repo . --scope recovery-slice  --work-category runtime-producer --json
```

**Commit 2 — audit-only verification record** (only if the templated placeholders diverged from the actuals):

```bash
git add .planning/STATE.md BUILD-LOG.md
git commit -m "docs: record H2.S2 post-commit loop-status output"
```

Break the recursion at Commit 2: do **not** re-run `loop-status` after Commit 2 unless verifying an external claim about repo state.

## Suggested Tests If Code Changes Are Needed

Only add code tests if H2.S2 surfaces a tooling gap that must close before H2.S3 (e.g., a citation-resolver bug, a packet-validator bug, a Codex-subprocess-isolation regression). Most of H2.S2 is producer-output, not code. Possible tests:

```text
test_h2s2_packet_paths_match_skeleton
test_run_manifest_records_h2_envelope
test_evidence_ledger_integrity_round_trips
```

Do **not** add tests just to increase test count.

## Completion Criteria

H2.S2 is complete when:

- The H2.S2 packet at `.planning/benchmarks/<run-date>-h11-h2s2/` matches the artifact-contracts table in `H2-BENCHMARK-PACKET-SKELETON.md`. Under the interim split shape (issue #23) the packet's `.research/` carries `run-h11-h2s2-1/` and `run-h11-h2s2-2/`; under the future single-cbm-run shape the `.research/` carries `run-h11-h2s2-1/` only.
- Every artifact validates: `cbm validate`, `cbm verify-citations`, `cbm check-evidence` exit 0 at absolute paths against the h11 target checkout.
- Under the interim split shape, both per-run `run-manifest.json` files validate; under the single-cbm-run shape, the one `run-manifest.json` validates.
- The `.research/` subtree(s) for the run(s) used are preserved in the packet (H2-PREFLIGHT Concern 9 gate).
- `surface-map.json` is non-baseline (`produced_by: surface-mapper@1.2`).
- `skeptic-review-surface-map.md` is the promoted final Skeptic markdown (not a smoke-anchor exploratory version).
- The H2.A4 diff fields per H2-PREFLIGHT Concern 8 are captured in `.planning/STATE.md` from the H2.S2 `run-manifest.json`.
- `TMPDIR=/var/tmp pytest -q` passes.
- `cbm loop-status --scope broad-goal --work-category runtime-producer` passes post-commit with `status: ok`, no issues, no warnings.
- `cbm loop-status --scope recovery-slice --work-category runtime-producer` passes post-commit.
- No `--scope pass-claim` invocation occurs against H2 evidence in H2.S2 (that is H2.S3 work).
- No cross-vendor reviewer is launched against the H2.S2 packet in this `/goal`. The `cross-vendor-review` skill is dispatched in H2.S3.
- Authority docs (`CURRENT-PLAN.md`, `HORIZONS.md`, `STATE.md`, phase 02 `PLAN.md` / `SUMMARY.md` / `VERIFICATION.md`, `BUILD-LOG.md`) reflect H2.S2 status without overclaiming H2 complete.

## Stop And Surface Conditions

Stop and surface to the user if:

- The h11 target SHA `62c5068c971579d61fa1b55373390e12f25fd856` does not resolve on the public remote at probe time.
- The Codex subprocess hits `--codex-timeout 600` (`run-manifest.json` records `interrupted`/`timeout`) — H2-PREFLIGHT Concern 2 hard abort.
- The Surface Mapper produces a baseline / dev-fixture / smoke-anchor artifact instead of a real `surface-mapper@1.2` output.
- The Skeptic output cites parent-session context, hidden mapper reasoning, or is generic without competing evidence.
- A schema between this brief and dispatch changes (re-verify `git log 76db3bc..HEAD -- schemas cbm/schemas` before dispatch; H2-PREFLIGHT Concern 4 mitigation).
- The `.research/` subtree cannot be located or preserved.
- Citation resolution fails at the pinned SHA for any promoted claim (do not auto-promote to `uncertainty-register.jsonl` without user confirmation).
- The agent is tempted to request a cross-vendor pass-claim checkpoint in this `/goal` (that is H2.S3).
- The agent is tempted to mark H2 complete, claim repeatability proven, or claim Phase B+.
- The agent is tempted to bypass `--codex-timeout 600` by raising it without root-causing the abort.
- The agent is tempted to "fix" the interim two-cbm-run split inline by adding per-producer reasoning-effort flags to `cbm/cli.py` directly without an ADR. That code change is tracked at issue #23 / ADR-006 and is **out of H2.S2 scope**; landing it inside this `/goal` would conflate H2.S2 with architectural redesign and break the per-slice horizon discipline.
- `cbm loop-status --scope broad-goal` fails post-commit.
- The full test suite fails outside the H2.S2 blast radius.
- The agent thinks `VISION.md` or `RUNTIME-CONSTITUTION.md` should be rewritten.

## Expected Commit

Suggested commit message:

```text
feat(h2): h2.s2 live producer run — surface-mapper + skeptic vs h11@62c5068c
```

If small tooling fixes are needed in the same commit (only if H2.S2 surfaced a gap that blocked dispatch):

```text
feat(h2): h2.s2 live run + <single-line-tooling-fix-scope>
```

Do **not** bundle unrelated cleanup. Do **not** bundle H2.S3 work. Do **not** bundle the H2.S3 brief (that is its own follow-up commit, parallel to how H2.S1 produced H2-PLAN.md without an H2.S2 brief in the same commit).

## Post-Goal Follow-Up

After this `/goal` completes, the next action is **not** a single H2 pass-claim bundle.

The next action is:

```text
Open a fresh /goal for H2.S3 using a new GOAL-H2S3-HANDOFF-AND-CHECKPOINT.md
authored against the H2.S2 packet and against H2-PLAN.md's H2.S3 slice.
H2.S3 produces the validated handoff packet at
.planning/benchmarks/<run-date>-h11-h2s3-handoff/ and dispatches the
cross-vendor pass-claim checkpoint review at
.planning/reviews/<run-date>-h2-repeatability-checkpoint/ via the
cross-vendor-review skill. Only H2.S3 makes the H2 pass claim.
```

Per-slice `/goal` invocations remain deliberate: H2.S3 carries the ADR-005 cross-model pass-claim checkpoint mandate; H2.S2 does not, and bundling the slices would conflate the boundaries.
