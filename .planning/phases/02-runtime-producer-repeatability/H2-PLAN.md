# H2 Plan

Status: locked
Date: 2026-05-22
Last updated: 2026-05-22
Supersedes: none
Superseded by: none
Audience: AI agent executing H2.S2 / H2.S3, and human reviewer auditing H2 evidence

## Boundary

This file is the binding plan for H2 — Runtime Producer Repeatability — once the H2 target is user-confirmed. It does not by itself produce H2 evidence and does not claim H2 complete. H2.S1's deliverable is this plan, not a run. H2.S2 produces the live evidence; H2.S3 produces the validated handoff and cross-vendor pass-claim checkpoint.

The H1 acceptance at PR #1 (`76db3bc`, 2026-05-16) is preserved exactly. Nothing in this file revises H1.

## H2 Target

User-confirmed on 2026-05-22 via the H2.S1 `/goal` stop-and-surface gate.

- Repository: `https://github.com/python-hyper/h11`
- Pinned SHA: `62c5068c971579d61fa1b55373390e12f25fd856`
- Scope: `h11/` package source (excluding `h11/tests/`)
- License: MIT (root `LICENSE.txt`, header: "The MIT License (MIT)" copyright Nathaniel J. Smith and contributors)
- Approximate LOC under examination: 2,568 across 11 tracked `.py` files in `h11/` (`__init__.py`, `_abnf.py`, `_connection.py`, `_events.py`, `_headers.py`, `_readers.py`, `_receivebuffer.py`, `_state.py`, `_util.py`, `_version.py`, `_writers.py`).
- Domain: HTTP/1.1 protocol state-machine library, bring-your-own-I/O.
- Target slug for packet/run-id use: `h11`.
- Rationale for the pick: candidate 2 in `H2-TARGET-SELECTION.md`. Materially different from H1's MCP `src/git` along repository, project shape (protocol library vs MCP server), domain (HTTP state machine vs git wrapper), and dependency surface (near-stdlib-only). Stays in Python so H2 does not combine repeatability risk with a brand-new-language risk for `surface-mapper@1.2`; that combined risk is deferred to H3+.

### Probe re-verification on 2026-05-22

Probe workspace: `/var/tmp/cbm-h2-target-probes-20260522/h11`. No `cbm run`, Surface Mapper, or Skeptic was invoked.

```bash
git ls-remote https://github.com/python-hyper/h11.git | grep 62c5068c971579d61fa1b55373390e12f25fd856
# 62c5068c971579d61fa1b55373390e12f25fd856	HEAD
# 62c5068c971579d61fa1b55373390e12f25fd856	refs/heads/master

git clone --filter=blob:none --no-checkout https://github.com/python-hyper/h11.git /var/tmp/cbm-h2-target-probes-20260522/h11
git -C /var/tmp/cbm-h2-target-probes-20260522/h11 checkout 62c5068c971579d61fa1b55373390e12f25fd856
git -C /var/tmp/cbm-h2-target-probes-20260522/h11 rev-parse HEAD
# 62c5068c971579d61fa1b55373390e12f25fd856

git -C /var/tmp/cbm-h2-target-probes-20260522/h11 ls-files h11 | grep -E '\.(py|pyi)$' | grep -v '^h11/tests/' | xargs wc -l | tail -1
# 2568 total

head -4 /var/tmp/cbm-h2-target-probes-20260522/h11/LICENSE.txt
# The MIT License (MIT)
# Copyright (c) 2016 Nathaniel J. Smith <njs@pobox.com> and other contributors
```

Probe outcome: SHA resolvable on the public remote; LOC and file inventory match the pre-built selection probe at `H2-TARGET-SELECTION.md`; license confirmed MIT.

## H2 Acceptance (concrete)

```text
H2.A1: A real runtime Surface Mapper producer (surface-mapper@1.2 on backend
       codex-cli, identity recorded in run-manifest.json) ran against
       python-hyper/h11 at SHA 62c5068c971579d61fa1b55373390e12f25fd856
       (scope h11/ package, excluding h11/tests/) and produced a schema-valid,
       non-baseline surface map with cited claims that resolve to source bytes
       at 62c5068c.

H2.A2: A real isolated Skeptic producer (skeptic@1.2 on backend codex-cli)
       ran against the H2 surface map without parent session context or
       hidden mapper reasoning, and produced a schema-carried challenge OR a
       schema-carried "no-challenge" disposition whose result is structurally
       ingested into surface-map.json / skeptic-review and the handoff.
       Either outcome satisfies A2; H2 does not require a manufactured
       challenge.

H2.A3: At least one non-trivial cited interpretive claim (e.g., centrality
       of Connection vs distributed authority across _state.py / _events.py
       / _readers.py / _writers.py) OR at least one non-trivial Skeptic
       challenge survives citation resolution against
       python-hyper/h11@62c5068c and survives cross-vendor pass-claim review.

H2.A4: Differences between the H1 run and the H2 run are recorded in
       .planning/STATE.md, with at minimum: skill versions
       (surface-mapper@1.2 / skeptic@1.2 expected to be unchanged from H1),
       backend (codex-cli), Codex model + reasoning-effort settings, target
       shape (Python protocol library vs MCP server git wrapper), surface
       depth (authority + edge counts, register mix), claim/challenge density,
       citation resolution success rate, and runtime cost (wall clock,
       timeout-fraction used).

H2.A5: A non-current-model cross-vendor checkpoint accepts the H2 pass claim
       using the cross-vendor-review skill at scope pass-claim. Same-model
       fallback is disallowed by ADR-005.

       Pre-acceptance failure window (load-bearing for H2.S3):
       checkpoint_for_loop_scope at cbm/cli.py:5430-5452 is the SELECTOR
       and returns the most-recent checkpoint whose scope label equals
       pass-claim, REGARDLESS of disposition. checkpoint_pass_claim_issues
       at cbm/cli.py:5795-5832 is the separate GATE that then evaluates
       reviewer_model_id and disposition.

       Consequence for H2.S3 dispatch: today the only pass-claim-scoped
       checkpoint is the accepted H1 minimum-useful checkpoint at
       .planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/, so
       the selector returns it and the gate is green. The moment H2.S3
       writes its own CHECKPOINT.md with scope: pass-claim (which
       `cbm checkpoint --scope pass-claim` does as part of packet
       creation), the selector immediately switches to the H2.S3 file
       because it has a newer mtime — the H1 fallback is no longer
       reachable via the selector. The gate then fails with
       missing_reviewer_model_id (cli.py:5795-5801) and
       checkpoint_disposition_not_accepted (cli.py:5828-5848) UNTIL
       the non-current-model reviewer writes reviewer_model_id +
       disposition: accept (via the cross-vendor-review runner).

       The H2.S3 author MUST expect `loop-status --scope pass-claim`
       to be RED between H2.S3 packet commit and reviewer acceptance.
       That red is the gate working as designed, NOT an H2 regression
       and NOT a signal to delete the H2.S3 CHECKPOINT.md or write a
       disposition prematurely; doing either would break ADR-005's
       cross-model invariant. The H1 checkpoint's green status is
       recoverable only by reverting the H2.S3 packet commit.

       H2.A5 is satisfied when the reviewer's accept-disposition lands
       and `loop-status --scope pass-claim --work-category
       runtime-producer` returns to green ON the H2.S3 checkpoint
       (not on the H1 fallback).
```

## H2 Verification Commands

Run after the H2.S2 / H2.S3 packets land. The slug `<run-date>` is the actual date the H2.S2 (or H2.S3) packet directory is created on; the planning placeholders below name the H2.S2 packet as `.planning/benchmarks/<run-date>-h11-h2s2/` and the H2.S3 packet as `.planning/benchmarks/<run-date>-h11-h2s3-handoff/`.

Artifact arguments MUST be ABSOLUTE paths to the CBM-repo packet path (e.g. `/Users/rookslog/Development/cbm/.planning/benchmarks/<run-date>-h11-h2s2/surface-map.json`). `command_validate` (`cbm/cli.py:2391-2404`) resolves a relative artifact under `--repo` via `path = repo / path` when `path.is_absolute()` is false; a relative artifact combined with `--repo /var/tmp/...h11/` would look for the artifact inside the h11 target checkout and raise `FileNotFoundError`. This is the exact failure mode H1.S3 hit; the resolution is recorded at `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/VERIFY.md:15`.

**Workspace path note for H2.S2 dispatch.** The `--repo` argument below names `/var/tmp/cbm-h2-h11-62c5068/h11` — this is the dispatch workspace, which H2.S2 must create fresh. Do **not** reuse the H2.S1 re-verification probe workspace at `/var/tmp/cbm-h2-target-probes-20260522/h11`; that path was used only for read-only re-verification on 2026-05-22 and reusing it risks mixing read-only probe state with live producer dispatch state. The H2.S2 brief (`GOAL-H2S2-LIVE-RUN.md`, **to be authored as the H2.S2 `/goal`'s deliverable** — not yet present at this PR head) will carry the canonical dispatch invocation. Until that brief exists, the canonical clone-and-checkout sequence for the H2.S2 dispatch workspace is:

```bash
PROBE_DIR=/var/tmp/cbm-h2-h11-62c5068
mkdir -p "$PROBE_DIR"
git clone --filter=blob:none --no-checkout https://github.com/python-hyper/h11.git "$PROBE_DIR/h11"
git -C "$PROBE_DIR/h11" checkout 62c5068c971579d61fa1b55373390e12f25fd856
git -C "$PROBE_DIR/h11" rev-parse HEAD
# expect: 62c5068c971579d61fa1b55373390e12f25fd856
```

The probe sequence at `H2-PLAN.md:33-49` above is structurally identical but writes to the probe path; for H2.S2 dispatch substitute the dispatch path above.

```bash
# H2.S2 packet validation:
python3 -m cbm.cli validate \
  /Users/rookslog/Development/cbm/.planning/benchmarks/<run-date>-h11-h2s2/surface-map.json \
  --repo /var/tmp/cbm-h2-h11-62c5068/h11
python3 -m cbm.cli verify-citations \
  /Users/rookslog/Development/cbm/.planning/benchmarks/<run-date>-h11-h2s2/surface-map.json \
  --repo /var/tmp/cbm-h2-h11-62c5068/h11
python3 -m cbm.cli check-evidence \
  /Users/rookslog/Development/cbm/.planning/benchmarks/<run-date>-h11-h2s2/surface-map.json \
  --repo /var/tmp/cbm-h2-h11-62c5068/h11
python3 -m cbm.cli validate \
  /Users/rookslog/Development/cbm/.planning/benchmarks/<run-date>-h11-h2s2/run-manifest.json \
  --repo /var/tmp/cbm-h2-h11-62c5068/h11
python3 -m cbm.cli validate \
  /Users/rookslog/Development/cbm/.planning/benchmarks/<run-date>-h11-h2s2/skeptic-review-surface-map.md \
  --repo /var/tmp/cbm-h2-h11-62c5068/h11
python3 -m cbm.cli verify-citations \
  /Users/rookslog/Development/cbm/.planning/benchmarks/<run-date>-h11-h2s2/skeptic-review-surface-map.md \
  --repo /var/tmp/cbm-h2-h11-62c5068/h11

# H2.S3 handoff packet validation:
python3 -m cbm.cli validate \
  /Users/rookslog/Development/cbm/.planning/benchmarks/<run-date>-h11-h2s3-handoff/HANDOFF.md \
  --repo /var/tmp/cbm-h2-h11-62c5068/h11
python3 -m cbm.cli verify-citations \
  /Users/rookslog/Development/cbm/.planning/benchmarks/<run-date>-h11-h2s3-handoff/HANDOFF.md \
  --repo /var/tmp/cbm-h2-h11-62c5068/h11

# Test suite + diff check + cross-scope gates:
TMPDIR=/var/tmp pytest -q
git diff --check -- .planning BUILD-LOG.md cbm tests schemas
python3 -m cbm.cli loop-status --repo . --scope broad-goal --work-category runtime-producer --json
python3 -m cbm.cli loop-status --repo . --scope pass-claim --work-category runtime-producer --json
```

Note on `loop-status --scope pass-claim`: the gate currently passes on the accepted H1 minimum-useful checkpoint at `.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/` because `checkpoint_for_loop_scope` selects the most-recent accepted pass-claim checkpoint regardless of horizon. That green result is correct for H1 and is not H2 evidence. H2.A5 is satisfied only when an H2.S3 checkpoint with `scope: pass-claim` and a non-current-model reviewer disposition becomes the most-recent accepted pass-claim checkpoint.

## H2 Sub-Slice Structure

- **H2.S2** — Live Surface Mapper + Skeptic run against h11.
  - Single `cbm run` invocation producing both `surface-map.json` and `skeptic-review-surface-map.md` in one packet. Isolation is enforced at the Codex subprocess level (`--ephemeral --ignore-user-config --ignore-rules -s read-only`), not at the `cbm run` level; the Skeptic subprocess still reads only its declared inputs per RUNTIME-CONSTITUTION §17.
  - Packet path: `.planning/benchmarks/<run-date>-h11-h2s2/`. Contents enumerated in `H2-BENCHMARK-PACKET-SKELETON.md`.
  - Boundary: produces H2 evidence. Does not by itself claim H2 complete and does not request the cross-vendor pass-claim checkpoint.

- **H2.S3** — Validated handoff + cross-vendor pass-claim checkpoint.
  - Packet path: `.planning/benchmarks/<run-date>-h11-h2s3-handoff/`. Contents enumerated in `H2-BENCHMARK-PACKET-SKELETON.md`.
  - Cross-vendor review path: `.planning/reviews/<run-date>-h2-repeatability-checkpoint/` with `PROMPT.md`, `REVIEW-SPEC.md`, `CHECKPOINT.md`, `DISPOSITION.md`, `DISPOSITION.json`, `EVIDENCE-MANIFEST.md` per the `.codex/skills/cross-vendor-review/` contract.
  - Boundary: H2.S3 makes the H2 pass claim and is the ADR-005 cross-model checkpoint slice. Only this slice fires the `SCOPES_REQUIRING_CROSS_MODEL` gate at `pass-claim` scope. H2.S1 and H2.S2 follow the standing per-slice cross-vendor review practice (see `docs/review-playbook.md`); those reviews are not ADR-005 pass-claim checkpoints and do not gate `loop-status --scope pass-claim`.

### Variant slice structure — no H2.S2a evidence-bundle-repair pre-step planned

H1 needed an H1.S2a evidence-bundle-repair slice because the original H1.S1 publication promoted dev-fixture Skeptic fallback as real review, hardcoded `edge-unknown-001`, and omitted repair-pass evidence preservation. Those code-level issues were dispositioned at PR #1 (and earlier intervention commits) and remain fixed on `main`.

For H2, the runtime Surface Mapper and Skeptic pipeline has now run cleanly once on MCP `src/git`. H2 is using the same `surface-mapper@1.2` skill, the same `skeptic@1.2` skill, the same `codex-cli` backend, and the same packet conventions. Pre-emptively planning an H2.S2a repair slice would be speculative work. If H2.S2 surfaces a new evidence-bundle-honesty class of issue, that becomes a stop-and-surface decision at H2.S2 time (with an H2.S2a inserted by intervention) — not a pre-emptive slice.

## H1 Caveat Carryover (Concern 5 from the brief)

H1's `LINEAGE.md` flagged three caveats. Classification for H2 follows.

1. **Final-surface-state provenance drift** (H1.S3 promoted `surface-map.json` carries H1.S1-era `produced_at` and `inputs` while holding H1.S2c disposition).
   - Classification: **(b) generic pipeline issue likely to re-encounter in H2.S3**.
   - Mitigation: H2.S3 follows the same external-lineage-commentary pattern (write provenance into `LINEAGE.md`, don't mutate the validated successor artifact). An artifact-production-path that produces a true H2.S3-era surface artifact is a follow-up work item, not in H2.S1 scope.

2. **Historical smoke-anchor ledger entry `lg-00030`** (`.gitignore:1@4503e2d12b79` smoke citation in H1.S2b Skeptic markdown).
   - Classification: **(a) H1-specific and resolved**.
   - The promoted H1.S2b Skeptic markdown no longer contains the smoke anchor; the ledger entry is preserved as historical evidence. h11 has its own SHA; a similar Skeptic smoke-anchor would have a different cite. The general pattern (Skeptic producing exploratory citations before promotion) is addressed by promoting only the final Skeptic output, which H2.S2 must continue to do.

3. **Mixed run-id provenance on `lg-00029`** (`claim_challenged` ledger entry's `run_id` is the H1.S1 run while `artifact_path` points at H1.S2b's imported surface map).
   - Classification: **(b) generic pipeline issue likely to re-encounter** if H2.S2 had been split into S2a (surface) and S2b (skeptic over imported surface). H2.S2 here is a single `cbm run` producing both artifacts, so the mixed-run-id pattern is structurally avoided. If H2.S2 dispatch needs to be re-split (e.g., because budget overrun forces re-running just the Skeptic against an imported surface), this caveat re-emerges and H2's `LINEAGE.md` must document the same way H1.S3 did.

H2.S3's `LINEAGE.md` must address (1) and (3) as expected re-occurrences; (2) is recorded as resolved.

## Cross-Reference

- Candidate selection and reasoning: `H2-TARGET-SELECTION.md`.
- Packet artifact contracts: `H2-BENCHMARK-PACKET-SKELETON.md`.
- Preflight concerns: `H2-PREFLIGHT.md`.
- H2.S1 verification record: `VERIFICATION.md` in this directory.
- H2.S1 brief: `GOAL-H2S1-REPEATABILITY-PLAN.md`.
- H1 packet shape this plan mirrors: `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/`.
- ADR-005 cross-model gate: `.planning/decisions/ADR-005-cross-model-checkpoint-mandatory-for-pass-claims.md`.
- Cross-vendor review skill: `.codex/skills/cross-vendor-review/SKILL.md`.
