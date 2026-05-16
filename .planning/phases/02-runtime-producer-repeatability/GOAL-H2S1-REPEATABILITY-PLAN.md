# Agent Execution Brief — H2.S1 Repeatability Plan

Status: proposed
Date: 2026-05-16
Last updated: 2026-05-16
Supersedes: none
Superseded by: none
Audience: AI agent executing the work, and human reviewer auditing the result
Primary horizon: H2 — Runtime Producer Repeatability
Current stage: H2.S1
Goal type: H2 planning slice, not live producer dispatch
Input baseline: `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/` (H1 accepted evidence)
Expected result: binding H2 plan + benchmark packet skeleton + planning-doc updates that make the H2.S2 live run dispatchable and auditable, with the target locked by user confirmation and H2 acceptance commands defined

## One-Sentence Mission

Produce the H2 repeatability plan — pick the second pinned target, justify why it is materially different from H1's MCP `src/git` target, define H2 acceptance and verification commands, and prepare the benchmark packet skeleton — without launching live Surface Mapper or Skeptic against the new target.

## Non-Negotiable Scope

This goal is **H2.S1 planning only**.

Do **not** launch a live Surface Mapper run against the new target.
Do **not** launch a live Skeptic run against the new target.
Do **not** claim H2 complete or repeatability proven.
Do **not** claim Phase B+ or beta readiness.
Do **not** rewrite `VISION.md`.
Do **not** broaden kernel validators, project packs, or hook policy beyond what H2 repeatability requires.
Do **not** revise the accepted H1 packet or H1 checkpoint disposition.
Do **not** pick the H2 target without explicit user confirmation — stop and surface for that decision.
Do **not** burn the live producer budget in H2.S1; the only acceptable backend calls are read-only fixture-style probes of the target repo (clone + git rev-parse + size check), not Surface Mapper / Skeptic invocations.

The output of this goal should make the H2.S2 live run **dispatchable**, not dispatched.

## Required Reading

Read these before editing:

- `VISION.md`
- `RUNTIME-CONSTITUTION.md`
- `.planning/HORIZONS.md` (especially the H2 and H2.S1 sections)
- `.planning/CURRENT-PLAN.md`
- `.planning/STATE.md`
- `.planning/phases/01-first-runtime-producer-evidence/PLAN.md`
- `.planning/phases/01-first-runtime-producer-evidence/SUMMARY.md`
- `.planning/phases/01-first-runtime-producer-evidence/VERIFICATION.md`
- `.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/RESULT.md` (H1.S1 evidence shape)
- `.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/RESULT.md` (H1.S2b Skeptic shape)
- `.planning/benchmarks/2026-05-07-mcp-git-h1s2c-disposition/RESULT.md` (H1.S2c disposition shape)
- `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/RESULT.md` (H1.S3 handoff shape)
- `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/LINEAGE.md` (lineage caveats inherited from H1)
- `.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/CHECKPOINT.md` and `DISPOSITION.json` (accepted H1 pass-claim shape)
- `.planning/decisions/ADR-001-cbm-owns-run-lifecycle.md`
- `.planning/decisions/ADR-003-producer-registry-over-outer-orchestrator.md`
- `.planning/decisions/ADR-004-deterministic-baseline-is-not-runtime-evidence.md`
- `.planning/decisions/ADR-005-cross-model-checkpoint-mandatory-for-pass-claims.md`
- `schemas/surface-map.schema.json`
- `schemas/handoff.schema.json`
- `schemas/run-manifest.schema.json`
- `docs/review-playbook.md` (cross-vendor review skill modes/effort dial)
- `.codex/skills/cross-vendor-review/SKILL.md` (review skill contract for the H2 pass-claim checkpoint)

Interpretation order:

1. `VISION.md` defines the destination and what counts as repeatability evidence.
2. `.planning/HORIZONS.md` H2 section defines acceptance.
3. `.planning/CURRENT-PLAN.md` Allowed Next Code Work defines bounds.
4. H1 packet artifacts define the **shape** the H2 packet must mirror (deltas allowed but justified).
5. ADR-005 governs the H2 pass-claim checkpoint, which is H2.S3 not H2.S1.

## Current Facts To Preserve

H1 is **accepted** for one pinned external target:

- Target: MCP `servers` repo, subtree `src/git`, pinned SHA `4503e2d12b799448cd05f789dd40f9643a8d1a6c`.
- Real `surface-mapper@1.2` produced a non-baseline schema-valid surface map.
- Real isolated `skeptic@1.2` raised `chl-10001` (auth centrality challenge).
- Mapper response accepted `chl-10001` as alternative; `auth-001.claim_status = contested`.
- H1.S3 handoff/checkpoint packet accepted by non-current-model checkpoint review.
- PR #1 merged to main as `76db3bc` on 2026-05-16.

What is **not** proven by H1:

- The Surface Mapper / Skeptic skills generalize beyond Python + a small library-shaped subtree.
- The Codex CLI backend's isolation properties hold for other target shapes.
- The benchmark packet pipeline (citation resolution, evidence ledger, handoff validation) works without target-specific tweaks.
- The cross-vendor-review skill works for a second pass-claim checkpoint (it was first used at H1.S3 — its repeatability is itself an H2 sub-claim).

H2.S1 must preserve all of these as open questions, not assume them resolved.

## H2.S1 Deliverables

Produce (new) or expand (existing) these artifacts:

```text
.planning/phases/02-runtime-producer-repeatability/
  PLAN.md                          (stub exists; expand with concrete H2.S1/S2/S3 detail)
  SUMMARY.md                       (stub exists; expand as H2.S1 advances)
  VERIFICATION.md                  (stub exists; expand with H2.S1 verification record)
  GOAL-H2S1-REPEATABILITY-PLAN.md  (this file — keep "Last updated" current as state changes)
  H2-TARGET-SELECTION.md           (new — candidate targets, reasoning, user-confirmed pick)
  H2-PLAN.md                       (new — binding H2 plan: target, acceptance, verification,
                                    H2.S2/H2.S3 slice structure)
  H2-BENCHMARK-PACKET-SKELETON.md  (new — expected packet paths and artifact contracts for H2.S2+)
  H2-PREFLIGHT.md                  (new — preflight concerns to resolve before H2.S2 dispatch)
```

Update these existing artifacts:

```text
.planning/CURRENT-PLAN.md          (add H2.S1 to Active Recovery Sequence; update Next /goal Track)
.planning/HORIZONS.md              (annotate H2.S1 status; do not mark H2 complete)
.planning/STATE.md                 (record H2.S1 packet state + the H2 target pick + verification footer)
BUILD-LOG.md                       (slice entry for H2.S1 plan production)
```

Do **not** create benchmark artifacts under `.planning/benchmarks/`. Those are H2.S2+ output. H2.S1's evidence is a plan, not a run.

## H2 Target Selection Criteria

The H2 target must satisfy all of:

1. **Pinned SHA reproducibility.** The target repo must be on a public stable SHA, not a moving tip. Capture the SHA in `H2-TARGET-SELECTION.md`.
2. **Bounded size.** Total LOC under examination ≤ ~5000 lines so the Surface Mapper run fits the Codex CLI budget that H1.S1 used. Record the line count.
3. **Permissive license.** OSS license that allows automated reading and quotation in a public packet (MIT/Apache-2/BSD-style preferred; avoid GPL-only or no-license repos).
4. **Materially different from H1's MCP `src/git`.** At least one of these axes must differ in a non-trivial way:
   - language family (e.g., Go, Rust, TypeScript, or a different style of Python),
   - project shape (CLI tool vs library vs service vs single-script utility),
   - domain (git-wrapping vs not git-wrapping),
   - dependency surface (large dep tree vs near-zero),
   - codebase age/conventions (mature & versioned vs recent & loose).
5. **Achievable non-trivial claim.** A reviewer reading the target should be able to imagine at least one non-trivial cited interpretive claim or challenge the Skeptic could plausibly raise — i.e., the target is not so trivial that any claim is a tautology and not so complex that no claim resolves cleanly.

Anti-criteria — reject targets that:

- contain generated code as the bulk of the readable surface (autogenerated SDKs, vendored protobuf stubs, build artifacts);
- depend on private secrets or unobservable network state to be intelligible;
- are so large or polyglot that the producer skill's existing context budget can't reach a substantive map;
- duplicate H1's MCP `src/git` shape closely enough that a positive H2 result wouldn't generalize (e.g., another MCP server subtree that mostly differs in domain wording but shares the same project skeleton).

## Candidate Targets — Stop And Surface

Propose **three** candidates in `H2-TARGET-SELECTION.md` with the following structure per candidate. Then stop and surface for the user pick.

Per-candidate template:

```markdown
### Candidate <N> — <slug>

- Repo: <https URL>
- Pinned SHA: <40-char SHA, must be a current public commit>
- Subtree (if any): <path or "whole repo">
- Approximate LOC under examination: <number, source of count>
- Language(s) and project shape: <e.g., "Go CLI, single binary, ~3000 LOC">
- License: <SPDX id>
- Domain: <short>
- Materially different from H1 in which dimensions: <list of axes>
- Plausible non-trivial claim or challenge a Skeptic could raise: <one sentence>
- Risk factors for the run: <budget, isolation, schema, citation, etc.>
- Why this candidate over the others: <one paragraph>
```

Suggested starting points to evaluate (the agent may swap any of these for better candidates, but must justify the swap):

- **Candidate A — Same-repo different-subtree.** Another MCP server subtree from `modelcontextprotocol/servers` at SHA `4503e2d...` that is meaningfully different from `src/git` (e.g., a subtree with a different language, a network-IO domain, or a substantially different project skeleton). Lowest backend risk; weakest repeatability signal — defensible only if the subtree's shape diverges enough.
- **Candidate B — Different-repo same-language.** A small Python CLI or library outside MCP (~1000–3000 LOC) with a clearly different domain and dependency surface. Medium risk and medium signal.
- **Candidate C — Different-repo different-language.** A small Go or TypeScript project (~1000–3000 LOC) with a CLI or library shape. Highest signal for "the producer skill is not Python-overfit" but exercises the Surface Mapper skill against a language it has not run on; record this as a separate H2 risk.

Stop-and-surface output must include:

- the three candidates filled in,
- a recommended candidate with reasoning,
- explicit ask: "User: please confirm the H2 target."

Do not pick the target unilaterally. The candidate list and the recommendation are inputs to the user's decision, not the decision.

## H2 Acceptance And Verification — Definition Template

Once the user confirms the target, fill `H2-PLAN.md` with concrete values for each field below. Do not advance to H2.S2 until this section is filled and the user is informed.

H2 acceptance (from `.planning/HORIZONS.md`, made concrete for the chosen target):

```text
H2.A1: A real runtime Surface Mapper producer ran against <pinned target> at SHA <SHA>
       and produced a schema-valid, non-baseline surface map with cited claims that
       resolve to source bytes at <SHA>.
H2.A2: A real isolated Skeptic producer ran against the H2 surface map without parent
       session context or hidden mapper reasoning, and produced a schema-carried
       challenge or no-challenge result whose disposition is structurally ingested.
H2.A3: At least one non-trivial cited interpretive claim or Skeptic challenge survives
       citation resolution and review against <pinned target>@<SHA>.
H2.A4: Differences between the H1 run and the H2 run are recorded in
       `.planning/STATE.md` (skill versions, backend version, target shape, surface
       depth, claim/challenge density, citation success rate, runtime cost).
H2.A5: A non-current-model cross-vendor checkpoint accepts the H2 pass claim using
       the cross-vendor-review skill at scope `pass-claim`. Same-model fallback is
       disallowed by ADR-005.
```

H2 verification commands template (fill `<target-repo>`, `<surface-map.json>`, `<handoff.md>` for the chosen target):

```bash
python3 -m cbm.cli validate <H2 surface-map.json> --repo <target-repo>
python3 -m cbm.cli verify-citations <H2 surface-map.json> --repo <target-repo>
python3 -m cbm.cli check-evidence <H2 surface-map.json> --repo <target-repo>
python3 -m cbm.cli validate <H2 handoff.md> --repo <target-repo>
python3 -m cbm.cli verify-citations <H2 handoff.md> --repo <target-repo>
TMPDIR=/var/tmp pytest -q
git diff --check -- .planning BUILD-LOG.md cbm tests schemas
python3 -m cbm.cli loop-status --repo . --scope broad-goal --work-category runtime-producer --json
python3 -m cbm.cli loop-status --repo . --scope pass-claim --work-category runtime-producer --json
```

H2 sub-slice structure (proposed; finalize in `H2-PLAN.md` after target pick):

- **H2.S2** — Live Surface Mapper + Skeptic run against the chosen target. Produces `.planning/benchmarks/<date>-<target-slug>-h2s2/{RESULT.md, surface-map.json, skeptic-review-surface-map.md, evidence-ledger.jsonl, run-manifest.json, ...}`. Boundary: produces evidence; does not yet claim H2.
- **H2.S3** — Validated handoff + cross-vendor checkpoint. Produces `.planning/benchmarks/<date>-<target-slug>-h2s3-handoff/` with `HANDOFF.md`, `LINEAGE.md`, `VERIFY.md`, `INCLUDED-ARTIFACTS.md`, `CHECKPOINT-PACKET.md`, `CHECKPOINT-PROMPT.md`, and `.planning/reviews/<date>-h2-repeatability-checkpoint/`. Boundary: requests pass-claim acceptance from a non-current-model reviewer via the cross-vendor-review skill.

If the target's shape suggests a different slice structure (e.g., the target needs an H2.S2a evidence-bundle-repair pre-step like H1.S2a did), record the variant in `H2-PLAN.md` with reasoning.

## Benchmark Packet Skeleton Plan

In `H2-BENCHMARK-PACKET-SKELETON.md`, list expected paths and artifact contracts for H2.S2 and H2.S3.

Template:

```text
H2.S2 packet:
  .planning/benchmarks/<date>-<target-slug>-h2s2/
    RESULT.md
    surface-map.json
    skeptic-review-surface-map.md     (only if Skeptic runs in S2 rather than separate S2b)
    evidence-ledger.jsonl
    run-manifest.json
    .research/<run_id>/
      logs/
      codex_outputs/
      ...

H2.S3 packet:
  .planning/benchmarks/<date>-<target-slug>-h2s3-handoff/
    RESULT.md
    HANDOFF.md
    VERIFY.md
    LINEAGE.md
    INCLUDED-ARTIFACTS.md
    CHECKPOINT-PACKET.md
    CHECKPOINT-PROMPT.md
    .research/<run_id-or-preserved-inputs>/
      ...

H2 cross-vendor checkpoint review:
  .planning/reviews/<date>-h2-repeatability-checkpoint/
    PROMPT.md
    CHECKPOINT.md
    DISPOSITION.md
    DISPOSITION.json
    EVIDENCE-MANIFEST.md
```

For each artifact list the producer (which slice creates it), the consumer (who reads it next), the schema or contract it must satisfy, and the validation command that confirms it.

Do not write the artifacts themselves in H2.S1 — only the contract.

## H2 Preflight Concerns To Surface

Enumerate, in `H2-PREFLIGHT.md`, the known risks that H2.S2 must resolve or document. At minimum:

### Concern 1 — Producer-Skill Language Generalization

If the chosen target uses a language Surface Mapper has not run on (anything other than Python so far), the surface map quality and citation density are unknown.

Required H2.S1 statement: record the language fit risk explicitly and propose a mitigation:

- run a small dry-run probe in H2.S2 before claiming the full surface,
- or pick a Python target for H2 and defer language-generalization to H3+.

### Concern 2 — Backend Budget And Cost

H1.S1 used a specific Codex CLI budget. H2.S2's cost depends on target size and language verbosity.

Required H2.S1 statement: capture the H1 budget actuals from `run-manifest.json`, propose an H2 budget envelope, and state the abort condition if the H2 run exceeds it.

### Concern 3 — Cross-Vendor Review Skill Repeatability

The cross-vendor-review skill was used for the H1.S3 pass-claim checkpoint. It has not been used twice.

Required H2.S1 statement: list the cross-vendor-review skill modes the H2.S3 checkpoint will use (e.g., `mode: opus` at `effort_level: high` or `max`), the expected outputs, and the failure modes the skill should surface. Reference `docs/review-playbook.md` for the mode × effort matrix.

### Concern 4 — Schema And Validator Drift

H1's packet used the schemas at SHAs frozen in the merged `main`. H2 must use the same schemas unless an explicit migration is documented.

Required H2.S1 statement: confirm that `schemas/surface-map.schema.json`, `schemas/handoff.schema.json`, `schemas/evidence-ledger.schema.json`, and `schemas/run-manifest.schema.json` are unchanged since H1. If they have changed, list the change and whether H2 should target the new or old version.

### Concern 5 — H1-Caveat Carryover

H1's `LINEAGE.md` documented historical ledger caveats (smoke-anchor citation, mixed run-id challenge entries). Some are H1-specific; some hint at producer-pipeline issues that may resurface.

Required H2.S1 statement: classify each H1 caveat as (a) H1-specific and resolved, (b) generic pipeline issue that H2 will likely re-encounter, or (c) generic issue already fixed in code. For (b), document the expected re-occurrence and the mitigation.

Add concerns beyond these five if the chosen target surfaces them.

## Planning Doc Update Requirements

After the H2 target is locked and `H2-PLAN.md` is filled:

### `.planning/CURRENT-PLAN.md`

- Add Active Recovery Sequence item 26: H2.S1 plan production. Status: completed when this goal completes.
- Update `Next /goal Track` to reference H2.S2 (live producer run) as the next slice with the chosen target slug.
- Keep Current horizon: H2 and Current stage: H2.S1 until completion; then advance Current stage to H2.S2 only after this goal completes successfully.

### `.planning/HORIZONS.md`

- H2.S1 status may become `current; plan prepared` or equivalent.
- Do **not** mark H2.S1 complete unless H2-PLAN.md is filled and `cbm-loop-status --scope broad-goal` passes.
- Do **not** mark H2 complete.

### `.planning/STATE.md`

- Add a new Phase 02 entry to Phase Status (Phase 01 closed; Phase 02 active, H2.S1 in progress / completed).
- Add a Recent Checkpoints entry for the H2.S1 plan commit.
- Add a `pending next work` line: H2.S2 live producer run against the chosen target.
- Append a verification footer block with command outputs (same format as the H1.S3 footers).

### `.planning/phases/02-runtime-producer-repeatability/PLAN.md`

The stub created when this brief landed already carries Status / Last updated / Supersedes / Superseded-by metadata and a track skeleton (H2.S1 / H2.S2 / H2.S3). Expand it as H2.S1 advances:

- bump `Last updated:` to the current date;
- update the H2.S1 track entry to "in progress" or "completed" with a reference to the produced deliverables;
- carry forward the H2.S2 and H2.S3 track entries from `H2-PLAN.md` once the target is locked;
- copy the concrete verification command list from `H2-PLAN.md` into the `## Verification` section.

Do not rewrite the phase objective or overwrite the metadata block.

### `.planning/phases/02-runtime-producer-repeatability/SUMMARY.md` and `VERIFICATION.md`

Both stubs exist with metadata + minimal body. Expand them as evidence accrues:

- `SUMMARY.md`: keep one orienting paragraph plus a short factual state list; never let it overclaim. Bump `Last updated:` on every change.
- `VERIFICATION.md`: append the concrete commands run, exit codes, test counts, and loop-status outcomes for each H2.S1 deliverable. Continue appending for H2.S2 and H2.S3 as they produce evidence. Bump `Last updated:` on every change.

Do not overwrite the existing stubs without preserving their metadata fields.

### `BUILD-LOG.md`

Add a slice entry for H2.S1 plan production. Use the same shape as the H1 slice entries.

## Required Verification

Run these before claiming H2.S1 complete:

```bash
TMPDIR=/var/tmp pytest -q
git diff --check -- .planning BUILD-LOG.md
python3 -m cbm.cli loop-status --repo . --scope broad-goal --work-category runtime-producer --json
python3 -m cbm.cli loop-status --repo . --scope recovery-slice --work-category runtime-producer --json
```

Expected loop-status behavior:

- `broad-goal` must pass with `status: ok`, no issues, no warnings.
- `recovery-slice` must pass.
- `pass-claim` is expected to still fail or block until the H2.S3 checkpoint disposition lands. That is correct and should be recorded.

If the chosen target requires a probe (clone + size check + license check), the probe is allowed but must be read-only and recorded in `H2-TARGET-SELECTION.md` with the exact commands and outcomes. The probe must not invoke Surface Mapper or Skeptic.

## Suggested Tests If Code Changes Are Needed

Only add code tests if the H2 plan surfaces a tooling gap that must close before H2.S2.

Possible tests:

```text
test_h2_target_pin_resolves_at_recorded_sha
test_h2_packet_skeleton_paths_match_plan
test_h2_acceptance_template_substitutes_target_fields
```

Do not add tests just to increase test count. Most of H2.S1 is plan prose, not code.

## Completion Criteria

This goal is complete when:

- `H2-TARGET-SELECTION.md` lists at least three candidates, names a recommendation, and records the user-confirmed pick with SHA and rationale.
- `H2-PLAN.md` fills H2 acceptance, verification commands, and slice structure for the chosen target.
- `H2-BENCHMARK-PACKET-SKELETON.md` enumerates expected H2.S2 and H2.S3 packet paths and contracts.
- `H2-PREFLIGHT.md` documents at least concerns 1–5 above plus any target-specific risks.
- Phase 02 directory's `PLAN.md`, `SUMMARY.md`, and `VERIFICATION.md` stubs are expanded with concrete H2.S1 content (metadata bumped; tracks/state/verification fields filled with `H2-PLAN.md`-derived values).
- `.planning/CURRENT-PLAN.md`, `.planning/HORIZONS.md`, `.planning/STATE.md`, and `BUILD-LOG.md` reflect H2.S1 status.
- `TMPDIR=/var/tmp pytest -q` passes.
- `cbm-loop-status --scope broad-goal --work-category runtime-producer` passes.
- No live Surface Mapper or Skeptic invocation occurred against the new target.
- No H2 completion, repeatability, or Phase B+ claim is made.

## Stop And Surface Conditions

Stop and surface to the user if:

- the candidate-target evaluation produces zero candidates meeting the selection criteria;
- the user-confirmed target turns out to violate a selection criterion after closer inspection (e.g., license is incompatible after reading `LICENSE`);
- the chosen target's pinned SHA cannot be resolved on the public remote;
- a preflight concern surfaces that requires code change before H2.S2 can run (the change is allowed only if it stays inside H2.S1's narrow allowed-work list in `.planning/CURRENT-PLAN.md`);
- the H1 schemas have changed since `76db3bc` in a way that requires re-validating H1 before H2 can layer on top;
- the agent is tempted to launch a live Surface Mapper or Skeptic against the new target "just to check";
- the agent is tempted to mark H2 complete, claim repeatability, or claim Phase B+;
- broad `cbm-loop-status` fails;
- the full test suite fails outside the H2.S1 blast radius;
- the agent thinks `VISION.md` should be rewritten.

## Expected Commit

Suggested commit message:

```text
docs: prepare h2s1 repeatability plan
```

If small tooling fixes are needed:

```text
feat: harden h2 preflight before live producer dispatch
```

Do not bundle unrelated cleanup. Do not bundle H2.S2 work.

## Post-Goal Follow-Up

After this goal completes, the next action is **not** the H2 live producer run as a single bundle.

The next action is:

```text
Open a fresh /goal for H2.S2 using a new GOAL-H2S2-LIVE-RUN.md authored against the
locked H2-PLAN.md target. H2.S2 runs the live Surface Mapper + Skeptic and produces
the H2.S2 benchmark packet. H2.S3 then runs the validated-handoff + cross-vendor
checkpoint slice in a separate /goal.
```

Per-slice /goal invocations are deliberate: each slice gets its own `token_budget`, its own stop-and-surface boundary, its own cross-model checkpoint review, and its own recovery boundary if something goes wrong. See the rationale at the bottom of `.planning/CURRENT-PLAN.md` "Next /goal Track" section once it is updated.
