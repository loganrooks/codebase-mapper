# Cross-Vendor Audit

Reviewer: Claude Opus 4.7 (1M context), orchestrating four parallel sub-investigations (code-quality, planning/governance, agential-setup, GSDR/GSD-2 research). Read-only inspection. No files outside this review session were modified.

This audit answers the seven questions in `PROMPT.md` and additionally responds to a broader user request issued at the same time: full repo audit, agential-setup readiness, uplift ideas, GSD-2 fit, and a concrete intervention list ready to formalize. Beyond-prompt sections are clearly labeled.

## Verdict

**Mostly sound direction; brittle mechanism; one structural risk that will repeat the original drift if not addressed before the next `/goal` track.**

CBM has a real deterministic kernel, a coherent claim-register thesis, and an honestly labeled producer-registry recovery. The just-completed live Codex CLI smoke is real evidence that subprocess dispatch + parent-side validation works on a pinned external benchmark. That is genuine progress and the team should be credited for the false-provenance correction (`ebf43d7`) and the schema-source/packaging cleanup (`05f0534`, `a1770cc`). State documents now match implementation reality more honestly than two days ago.

The structural risk is unchanged in shape: **the planning system depends on the dev agent reading and obeying its own constitution, with very little mechanical enforcement.** The `2026-05-02-opus-cross-vendor-audit/` folder for which this very document is the missing OUTPUT — created at 22:47 today, never filled — is the canary. A second empty review folder (`2026-05-01-claude-cowork-architecture-review/`) tells the same story. Combined with the BUILD-LOG.md per-slice self-critique blocks that have *never failed in ~140 entries* (a pattern the prior `OUTPUT-WORKFLOW.md` already named at `:27-37`), the operational truth is that review packets are created without being gated to completion, and self-validation continues to look like governance.

The next runtime-producer evidence slice — a real Surface Mapper or full isolated Skeptic — is the *exact* shape of work most likely to produce fluent, plausible, self-passing output. Sending it through the same same-model checkpoint that approved the recovery would re-run the original drift mechanism on smaller scope.

Recommended posture: proceed with the runtime-producer track, but install three mechanical guards (review-completion gate in `cbm-loop-status`, mandatory cross-model checkpoint for any pass claim, ADR ledger) **before** the first real Surface Mapper artifact is produced, so that artifact lands into a system that can falsify it.

## Blocking Findings

### B1. `cbm-loop-status` does not detect orphaned review packets — severity: blocking
- **Evidence**: `.planning/reviews/2026-05-02-opus-cross-vendor-audit/OUTPUT-CLAUDE-OPUS.md` and `STDERR.txt` are both 0 bytes; PROMPT.md timestamp 22:47, OUTPUT/STDERR touched 22:58. Folder was untracked until this audit. `.planning/reviews/2026-05-01-claude-cowork-architecture-review/` is entirely empty (no REVIEW-SPEC, no abort note). `STATE.md:106-110` declares `/goal` readiness while these orphans existed.
- **Recommendation**: extend `cbm-loop-status` so every `.planning/reviews/<slug>/` with a `PROMPT.md` but no non-empty OUTPUT (or a STOP-NOTE) blocks broad `/goal`. Same for `STATE.md` whose last-updated trails HEAD by >N commits, and `CURRENT-PLAN.md` whose Active Recovery Sequence references commits already archived.
- **Disposition suggestion**: accept; implement before the next runtime-producer slice.

### B2. Codex CLI subprocess has no timeout — severity: blocking for live runs
- **Evidence**: `cbm/cli.py:3875` invokes `subprocess.run(...)` with no `timeout=` kwarg. A live model that hangs blocks `/goal` indefinitely with no `SIGTERM/SIGINT` cleanup; `run-manifest.json` is left in `running` state.
- **Recommendation**: add explicit `timeout=600` (configurable per backend), catch `subprocess.TimeoutExpired`, write `manifest.status: "interrupted"` with cause, persist any partial output. Add a regression that asserts a slow fake executable is killed and the manifest reflects it.
- **Disposition suggestion**: accept; bundle with B3.

### B3. `run_id` is used in path construction without validation — severity: blocking (security)
- **Evidence**: `cbm/cli.py:971` and `:4342` accept `args.run_id` directly (`run_id = args.run_id or f"run-..."`) and pass it through to path construction (e.g., `run_dir = repo / ".research" / run_id` at `:3798`); no allowlist regex. A `run_id` like `../../tmp/x` writes outside `.research/`. `cli.py:3608` defines `sanitize_id()` but it is not applied to user-supplied `run_id` values.
- **Recommendation**: validate `run_id` against `^[A-Za-z0-9._-]{1,64}$` at entry; reject otherwise. Apply to every CLI command that accepts `--run-id`. Add a regression with a traversal payload.
- **Disposition suggestion**: accept; cheap to fix and load-bearing for benchmark-harness honesty.

### B4. `jsonschema.RefResolver` deprecation — severity: blocking on jsonschema 5.0
- **Evidence**: `cbm/cli.py:503` (per code-quality agent's report). `RefResolver.from_schema()` is removed in jsonschema 5.0; the suite already emits 2 deprecation warnings on every `pytest -q` (`STATE.md:114`).
- **Recommendation**: migrate to `referencing.Registry` (the supported successor) before jsonschema 5.0 ships. This is not urgent today, but the migration touches every artifact gate and should be planned, not paniced.
- **Disposition suggestion**: accept; schedule as its own slice within the runtime-producer track (the validation chain is on the critical path).

## Nonblocking Findings

### N1. BUILD-LOG.md self-critique blocks have never failed — severity: high
- **Evidence**: ~140 entries with Drift/Contract/Reviewer-eye blocks; sampled spread (`:1-30`, `:653-749`, `:1196-1376`); each block passes its own check. `AGENTS.md:69-84` was rewritten to demote the cadence ("not a per-slice ritual") but practice has not caught up. `OUTPUT-WORKFLOW.md:27-37` already diagnosed this.
- **Recommendation**: enforce the cadence change. Self-critique only at named boundaries (plan completion, phase boundary, before main merge, kit deviation, repeated failure). Add a quarterly audit that counts pass/fail rate; if 0 fails across N slices, declare self-critique broken and require external review for the next phase boundary.

### N2. Codex CLI smoke artifact is ~80% template, ~20% review — severity: high (label honestly is correct; do not let it ratchet)
- **Evidence**: `.planning/benchmarks/2026-05-02-mcp-git-codex-smoke/skeptic-review-surface-map.md` has `findings_logged: 0`, empty `challenge_ids`, citation anchor `.gitignore:1@4503e2d12b79` (placeholder). RESULT.md `:56` is honest about this. Producer label is `codex-cli-smoke@0.1` (not `skeptic@…`), which is correct.
- **Recommendation**: keep the honest labeling. The next slice must produce a real Skeptic artifact with at least one factual citation spot-check and at least one interpretive challenge attempted, not another smoke. Otherwise the producer-id distinction will erode.

### N3. Skill prompts are runtime-loadable in design only; no loader exists — severity: high
- **Evidence**: `skills/{surface-mapping,skeptic,synthesizer,intervention-planner,consult,compaction-recovery,tracer}.md` are mature design documents. No code in `cbm/cli.py` injects them as system prompts to a spawned subprocess. The smoke backend invokes `codex exec ...` with `--output-schema` but does not load `skills/skeptic.md` as the system prompt; what the model actually used to produce the stub is unspecified.
- **Recommendation**: implement a `load_skill(name)` function that reads `skills/<name>.md`, hashes it, and (a) injects via `--system` or equivalent into the subprocess, (b) records hash in `run-manifest.json` for reproducibility, (c) refuses to dispatch the producer if the skill doesn't exist or the hash check fails. ~3 days. This unlocks the rest of the runtime-producer track.

### N4. `cli.py` is a 5012-line monolith with eight clear seams; do not split yet — severity: medium
- **Evidence**: `cbm/cli.py` line count from `wc -l`. Code-quality agent identified eight natural seams: schema-loading, git-ops, ledger, claim-evidence, artifact-builders, codex-cli adapter, gate-executor, producer-registry. `STATE.md:103` already records the deferral.
- **Recommendation**: keep deferring. Extracting now is churn. Extract in this order *after* the first real Skeptic artifact: git-ops → schema-loading → ledger → claim-evidence → artifact-builders (parallel) → codex-cli-adapter → gate-executor → producer-registry. Maintain test coverage at each cut.

### N5. Producer registry is a hardcoded static dict, duplicated in three places — severity: medium
- **Evidence**: `cbm/cli.py:51-67` (DETERMINISTIC_PRODUCERS), `:880-924` (build_producer_registry), `:4358-4434` (command_run dispatch). Adding a new producer requires three edits.
- **Recommendation**: introduce a `ProducerManifest` dataclass with `{schema, subprocess_template, retry_policy, timeout, validation_chain}` fields; index everything off it. This is the natural shape once a real Surface Mapper backend is wired; does not need to land first.

### N6. Schema duplication regression is content-equality only — severity: medium
- **Evidence**: `tests/test_cli.py:40-47` checks `cbm/schemas/*.schema.json` content equals root `schemas/*.schema.json`. It does *not* verify the installed wheel can load schemas without `CBM_SCHEMA_DIR` set, nor that adding a new root schema fails the regression unless it is also added to `cbm/schemas/`.
- **Recommendation**: add an integration test that builds the wheel into a temp venv, imports `cbm.cli` with `CBM_SCHEMA_DIR` unset and target-local `schemas/` absent, calls `schema_store()`, and asserts all 19 schemas resolve from package data. Add a counter-regression that asserts an unmirrored root schema fails CI.

### N7. Codex CLI adapter merges stderr into noise — severity: medium
- **Evidence**: `cbm/cli.py:3875-3878` pipes both stdout and stderr; if the model writes valid JSON to `--output-path` and unrelated logs to stderr, the parent prints stderr to its own stderr and may confuse automation. If the model writes to stdout instead of `--output-path`, the JSON is lost.
- **Recommendation**: enforce that the model writes to `--output-path` only; read stdout only as fallback diagnostics; tee stderr into a per-step log file under `.research/<run_id>/logs/<step>.stderr` so it is auditable but does not pollute the parent.

### N8. Citation regex permits 7-char abbreviated SHAs without verification — severity: medium
- **Evidence**: `cbm/cli.py:24` regex `(?P<sha>[0-9a-f]{7,40})`. Subsequent `git_show_bytes()` (`:677`) trusts the value. An abbreviated SHA could be ambiguous in a busy repo.
- **Recommendation**: keep the regex permissive but call `git rev-parse --verify` on capture, persist the resolved 40-char SHA, and reject ambiguity. Add a regression with an ambiguous-prefix scenario.

### N9. Ledger append-only verification is structurally append-only but not cryptographically tamper-evident — severity: medium
- **Evidence**: `cbm/cli.py:761-774` compares hashes from a manifest co-located with the ledger. An attacker who can write the ledger can also rewrite the manifest. Code-quality agent flagged this; CBM's threat model arguably tolerates it (ledger is a build-side audit, not an externally-trusted record).
- **Recommendation**: defer hardening unless the user has a downstream consumer that requires tamper-evidence. If yes: HMAC entries with a per-repo key stored outside `.research/`. Otherwise document the threat model in `RUNTIME-CONSTITUTION.md §13` and move on.

### N10. `cbm-validate-fresh` is a real command but consult does not auto-call it — severity: medium
- **Evidence**: `cbm/cli.py:2619+` defines `command_validate_fresh`; `command_consult` (`:3526+`) does not call it. `consult.md §1` and `RUNTIME-CONSTITUTION.md §25` ("Validate-fresh before consulting. Never consult an artifact without first running cbm-validate-fresh on its inputs.") both require it.
- **Recommendation**: have `command_consult` call `command_validate_fresh` on the run's input artifacts before reading them; refuse with a stale-input error if any input is stale. This is a forbidden behavior currently relying on agent discipline; promote to a gate.

### N11. Three-mode execution is metadata-only — severity: low
- **Evidence**: `cbm/cli.py:4340+` parses `--mode` and writes to `intake.json`; no conditional logic in current code branches on the mode for Skeptic frequency or producer composition. Modes will be enforced at the orchestrator/skeptic-spawn layer once it exists.
- **Recommendation**: leave this until a real Skeptic and (later) Tracer exist. Document that mode is currently labeling, not behavior; do not let users assume `--mode deep` is doing more validation today than `--mode lightweight`.

### N12. Goal-pack and project-pack validation errors are silently swallowed on load — severity: low
- **Evidence**: `cbm/cli.py:1786,1814-1868`. Validation functions return errors but `load_*_packs` ignores them. Malformed packs disappear without warning.
- **Recommendation**: raise `ValueError` on malformed packs at load time. If you must keep best-effort loading, log to stderr with the pack id and validation error.

### N13. No streaming/heartbeat in subprocess dispatch — severity: low (now), high (when Skeptic runs >5min)
- **Evidence**: `cbm/cli.py:3875` is a blocking `subprocess.run`. There is no progress logging, no cancellation point, no resumption.
- **Recommendation**: defer until first real >2min agent run produces a UX problem. Then introduce heartbeat lines (newline-delimited JSON), a checkpoint write per N seconds, and a `--resume` flag. Premature.

### N14. Test coverage on Codex-CLI failure modes is thin — severity: low
- **Evidence**: 2 codex-cli tests (`test_run_backend_codex_cli_requires_explicit_live_flag`, `test_run_backend_codex_cli_fake_producer_writes_agent_review`). No tests for: timeout, invalid-JSON output, missing-output-file, schema-rejection of model output, stderr noise with valid JSON.
- **Recommendation**: add five regressions before the next live smoke. Each ~15 lines using the existing fake-executable pattern.

## Overclaim Or Drift Risks

### O1. BUILD-LOG carries Phase A-F "disposition: pass" entries that STATE.md now contradicts
- **Evidence**: `BUILD-LOG.md:176` (Phase A pass), `:445` (Phase C), `:504-518` (Phase D), `:542-554` (Phase E), `:568+` (Phase F slice work). `STATE.md:39` says "Phases B-F are not passed." The contradicting entries are not annotated.
- **Recommendation**: amend each historical "Phase X disposition: pass" entry with a footnote pointing to `f98605d` and `STATE.md:39`. Keep the original prose (audit fidelity) but make the supersession visible to a reader scanning top-down.

### O2. `docs/architecture.md` describes the five-role agent suite as if normative; current state has none
- **Evidence**: `docs/architecture.md:38` agent table. `:7-11` adds a current-status disclaimer but the two sections are not cross-linked, and the `architecture.md → STATE.md` direction is one-way.
- **Recommendation**: at the top of every roadmap/architecture doc that describes the runtime, add a "Current implementation status: see STATE.md" header with a hyperlink. Cheap; prevents reader-onboarding overclaim.

### O3. The recovery's checkpoint was a same-model fallback; STATE.md treats it as a cleared gate
- **Evidence**: `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/CHECKPOINT.md:7,45` labels itself "Codex adversarial checkpoint reviewer, same-model fallback" with `Confidence: medium-high`. `STATE.md:106-110` and `CURRENT-PLAN.md:75` declare `/goal` readiness. `AGENTS.md:55` requires same-model reviews to be labeled as such — that requirement was met. But the cross-vendor audit `2026-05-02-opus-cross-vendor-audit/` was set up as the corrective and never filled.
- **Recommendation**: this audit fills the gap. Going forward: codify in `AGENTS.md` that same-model checkpoints are valid only for narrow recovery slices, never for phase-pass or merge-to-main; cross-model checkpoints are mandatory before any pass claim.

### O4. The minimum-useful-CBM bar is one slice closer than it sounds
- **Evidence**: `VISION.md:41-43` defines minimum-useful as "one runtime-agent-produced run on a pinned external codebase, with at least one non-trivial interpretive claim or challenge grounded in citations." Current state: deterministic surface map exists on pinned MCP `src/git`; the live smoke produced a stub Skeptic with zero findings. The minimum-useful floor is not met; the recovery's "first runtime-producer evidence slice" claim (CURRENT-PLAN.md `:46`) is structurally honest but the language elsewhere blurs the distinction.
- **Recommendation**: in `STATE.md` Benchmark State section, separate "first runtime-producer dispatch evidence" (cleared) from "minimum-useful CBM" (not cleared). The next slice's acceptance criterion should name minimum-useful explicitly, not just "first agent-produced artifact."

### O5. VISION graduation criteria 3, 4, 9, 10 are unanchored from current trajectory
- **Evidence**: `VISION.md:101-114`. Criterion 3 (Skeptic catches expert-blind defects ≥30 runs), 4 (interpretive challenge precision ≥75% on ≥30 runs), 9 (pedagogical adequacy: solo-day-test on small repo), 10 (≥5 distinct project types). The repo has 1 deterministic baseline + 1 live smoke + 0 expert reviews. Scaling ratio: ~30×.
- **Recommendation**: the criteria are aspirational and that is fine, but they need a *research program* (paid expert reviewers, multi-project benchmark suite, a graded learning resource) that is currently in nobody's plan. Either add a note to VISION.md acknowledging which criteria are deferred to a research-program milestone, or accept that "graduation" remains beyond the build roadmap.

## Architecture Recommendations

### A1. Producer registry as data, not as branching code
Once the first real Skeptic backend lands, replace `DETERMINISTIC_PRODUCERS` (`cli.py:51-67`) and the duplicated dispatch in `command_run` with a single registry of `ProducerManifest` records loaded from `cbm/producers/<id>.json` (or a YAML). One source of truth; pluggable; new producers don't require dispatcher edits. Defer until immediately after that landing — premature now.

### A2. Skill loader as a first-class function
Add `cbm/skills.py` with `load_skill(name) → (path, sha256, body)`. Every producer manifest names a `skill: <name>`. The dispatcher reads the skill, injects the body as system prompt for the subprocess, and records the SHA in `run-manifest.json`. Refuses dispatch on missing or modified skill (configurable: warn vs. fail). This is the unblocker for real agent runs (~3 days).

### A3. Subagent isolation: live validation before relying on it
The `2026-05-01-codex-cli-isolation.md` spike documents capability (`--ephemeral --ignore-user-config --ignore-rules -s read-only`) but did not run a live model. Before using Codex CLI for a real Skeptic, run a live isolation probe: parent session establishes "X is true" in its context; spawned Skeptic is asked about X with the same Codex CLI flags but no shared session ID. Skeptic must answer "I have no information about X." Capture the transcript in `.planning/spikes/`. ~1 day.

### A4. Codex CLI adapter: tighten contract and observability
- `--output-schema` is set; require `--output-path` writes to a unique file under `.research/<run_id>/codex_outputs/<step>.json`. Parent reads only that file.
- Stderr per step → `.research/<run_id>/logs/<step>.stderr`.
- Manifest records: command argv, stdout sha256, stderr sha256, exit code, duration, model, reasoning-effort, skill SHA.
- Add timeout (B2) and `run_id` validation (B3).

### A5. Cross-platform: Claude Code adapter as a 1-week port behind a feature gate
The Codex backend is one external producer; Claude Code can be another. Implement a `--backend claude-code` analogous to `--backend codex-cli` with the same isolation-validation requirement (A3) before enabling for real Skeptic. This is the structural answer to graduation criterion 8 (cross-platform parity); it does not need to land before the first runtime-producer evidence slice but should be planned alongside.

### A6. Honest map / honest deterministic baseline distinction
The deterministic baseline produces schema-valid intervention cards that look like Skeptic-reviewed cards. The producer-id label is honest (`cbm-baseline-*`) but a downstream consumer reading a card may not notice. Add a prominent banner to handoff and to each card: `Producer: cbm-baseline-* — this is deterministic baseline output, not a runtime-agent reading. Cards from this run inherit baseline guarantees only.` Cheap; prevents the "user acts on a deterministic card thinking it had a Skeptic" failure mode.

## Workflow Recommendations

### W1. Mechanical review-completion gate (closes B1)
`cbm-loop-status` checks: (a) every `<reviews>/<slug>/PROMPT.md` has a non-empty sibling `OUTPUT*.md` or a `STOP-NOTE.md`; (b) every `<reviews>/<slug>/CHECKPOINT.md` has a non-empty `DISPOSITION.md`; (c) every empty review folder is either deleted or has a `STOP-NOTE.md`. Failures block broad `/goal`.

### W2. Cross-model checkpoint mandatory for phase pass / main merge
Codify in `AGENTS.md`. Same-model isolated reviews remain valid for narrow recovery slices and self-critique cadence at boundaries; they cannot clear a pass gate. Cross-model can be GSDR's `audit_delegation: cross_model:gpt-5.4` pattern (see GSDR section below) or a manual handoff to a different vendor.

### W3. ADR ledger
Hoist load-bearing decisions ("hooks are adapter glue", "producer registry over outer orchestrator", "CBM owns the run lifecycle") from BUILD-LOG entries to immutable `.planning/decisions/ADR-NNN-<slug>.md`. ADRs are referenced by slug from STATE/PLAN. The next reset should not have to rediscover decisions.

### W4. BUILD-LOG slicing and per-entry IDs
Slice the log at recovery boundaries; rolling 200-line "current era" file plus indexed `BUILD-LOG-archive/<phase>.md`. Add per-slice IDs (`SLICE-001`...) so cross-references are stable. This is bookkeeping, not gating; do it once after the next runtime-producer slice ships.

### W5. Self-critique audit
Quarterly (or per-50-slice) sweep: count "self-critique surfaced rework" vs. "self-critique passed." If the latter is zero across N slices, declare self-critique broken and require external review for the next phase boundary. Makes the failure mode of self-validation observable.

### W6. Stop-and-surface coverage
`AGENTS.md:104-114` lists seven stop-and-surface conditions; six are mechanically detectable. The seventh ("same mistake twice in a row") relies on agent self-detection. Add a tiny `cbm-loop-status` check: scan recent `BUILD-LOG.md` slices for repeated rework on the same artifact (e.g., two corrective slices touching the same file in N consecutive entries). Imperfect heuristic; better than nothing.

## Verification Gaps

### V1. The recovery's verification chain has no live cross-model checkpoint
This audit is the corrective; future pass claims should not trust same-model checkpoints alone. **Gap close action**: this document.

### V2. Subagent isolation is asserted, not verified
See A3.

### V3. Skill prompt → subprocess injection has no test
See N3, A2.

### V4. Wheel-installed schema loading has no integration test
See N6.

### V5. Codex CLI failure modes are untested
See N14.

### V6. Claim-register misclassification check is not exercised at evidence-gate time for runtime-agent artifacts
The evidence-kinds table (RUNTIME-CONSTITUTION §7) is enforced at `check_claim_evidence` (`cli.py:567-620`) for every claim that a deterministic producer writes. There is no current code path where a runtime agent writes a claim with `claim_register: factual` that *should* be `interpretive`; therefore the misclassification gate has never run on real agential output. The first real Skeptic run is the test.

### V7. Refresh delta and consult-validate-fresh integration is unexercised on a real refresh
Refresh delta is generated by `command_refresh` for deterministic refreshes. There has never been a refresh where prior interpretive claims existed and had to be migrated. The migration protocol (RUNTIME-CONSTITUTION §25) is fully specified but unexercised. Defer until the second real agent run on the same codebase at a different SHA.

## Recommended Next Slice

### Slice S1. Live isolation probe (1 day; allowed under recovery)
Run a live Codex CLI subprocess that establishes whether the spawned context can see information that was only in the parent session. Capture transcript in `.planning/spikes/2026-05-02-codex-isolation-live.md`. Outcome: `isolation_verified | isolation_breached | inconclusive`. If `breached`, the next slice changes shape (find a different backend or a different isolation mechanism).

### Slice S2. Skill loader + first real Skeptic on MCP `src/git` (3-5 days; allowed under recovery)
Implement `cbm/skills.py::load_skill`. Wire `--backend codex-cli` to inject `skills/skeptic.md` as system prompt. Run on the existing pinned `src/git` deterministic surface map. Acceptance: artifact contains at least one factual citation spot-check (resolves at SHA, supports the claim) and at least one interpretive challenge attempted (with `competing_reading`, `competing_evidence`, `interpretive_axis`, `relation_to_original`). Validate with parent-side gates. Land in `.planning/benchmarks/<date>-mcp-git-skeptic-real/`.

### Slice S3. Mechanical review-completion + checkpoint gates in `cbm-loop-status` (1-2 days; allowed under recovery — directly supports governance)
Implements W1, W2 (codification), W6. Tests: a synthetic empty-OUTPUT folder blocks `broad-goal`; a same-model-only checkpoint with no cross-model packet blocks pass-claim scopes.

### Slice S4. Codex CLI adapter hardening: timeout, run_id validation, output-path enforcement, stderr tee (1 day; allowed under recovery)
Implements B2, B3, N7. Five regression tests as part of N14 closure.

### Slice S5. ADR-001 through ADR-005 (~half day; allowed under recovery)
Lift load-bearing recovery decisions out of BUILD-LOG into immutable ADRs. Cross-link from STATE.md/CURRENT-PLAN.md.

These five slices are sequential by risk-reduction value: S1 falsifies the assumption everything else rides on; S3 closes the governance gap that this very audit revealed; S2 unblocks the runtime-producer track; S4 hardens it; S5 stabilizes context for the next reset.

The first **out-of-recovery** work — splitting `cli.py`, RefResolver migration, Claude Code adapter port — should not start until S1 (or its falsifier) lands.

---

## Beyond-Prompt: Where We Are vs. Where We're Going

CBM is one focused slice away from its own minimum-useful definition (`VISION.md:41-43`). The kernel is real; the validation surface is real; the governance has the right shape and one structural hole; the runtime-agent layer is 10% wired (subprocess dispatch ✓, skill loader ✗, isolation verified ✗, real claim-register checks on agent output ✗). Three to five slices, properly sequenced, gets the floor cleared.

After that floor: the work to graduation (`VISION.md:101-114`) is dominated by *measurement*, not *code*. Cross-platform parity (Codex + Claude Code) is a 1-2 week port. Project-type breadth (≥5 types) is a benchmark assembly project. Skeptic catch-rate calibration against expert review (≥30 runs) is a research program with no plan. The build-out and the calibration program need to be named separately, otherwise the second will quietly cannibalize the first or be silently dropped.

The deployment shape ("local CLI producing artifacts on disk", `VISION.md:97`) remains correct. There is no signal that CBM should drift toward a chatbot or a code-mutator; the anti-vision is well-defended.

## Beyond-Prompt: Agential Development Setup

The dev-agent / runtime-agent split is real and clean in the docs. In practice the runtime-agent half is mostly empty: skills exist, no loader; isolation is documented, not verified; three modes are tracked, not enforced. The dev-agent half (governance, planning) is well-elaborated but mechanically unenforced (hence B1 / W1).

Two specific gaps are worth naming:
- **Subagent identity and provenance.** When a real Skeptic runs, its identity is `produced_by: skeptic@<version>` plus the skill SHA. The current run-manifest records the subprocess command but not the skill SHA. Add it (A2).
- **Cross-model dispatch as an actual capability, not a doctrine.** AGENTS.md `:55` prefers cross-model checkpoints. Operationally that means: "the dev agent must remember to route the next checkpoint to a different vendor and produce an OUTPUT and a DISPOSITION." Nothing in the system makes that easy or automatic. GSDR's `gsdr:audit` with `audit_delegation: cross_model:gpt-5.4` is exactly this primitive (see next section).

## Beyond-Prompt: GSDR / GSD-2 Fit and Migration Sketch

(The user has GSDR 1.19.6 installed. They asked specifically about "GSD-2", which has a public GitHub page.)

**GSD-2** (`https://github.com/gsd-build/gsd-2`) is the upstream Pi-SDK rewrite — TypeScript CLI, SQLite state, fresh-session-per-task, automated git worktree isolation, provider-agnostic via Pi SDK. **GSDR** (what's installed) is a community v1-lineage fork descending from `gsd-build/get-shit-done` v1.x with a reflection / signals / knowledge-base layer added.

**Verdict: PARTIAL_FIT — for GSDR. POOR_FIT for GSD-2.**

The split is sharper than the names suggest: GSDR is a Claude-Code-resident workflow tool that runs *above* the project; GSD-2 is a CLI that wants to *own* the run lifecycle. CBM's `RUNTIME-CONSTITUTION.md` and accepted recovery decision say *CBM* owns the run lifecycle through a producer registry. Two run-lifecycle owners is one too many. **GSD-2 conflicts at the architectural foundation; GSDR does not.**

What GSDR *would* add to CBM (the dev-agent layer):
- `.planning/phases/NN-slug/{PLAN,RESEARCH,VERIFICATION,SUMMARY}.md` lifecycle (currently ad hoc).
- 3-axis audit taxonomy with `audit_delegation: cross_model:*` as a first-class field (closes W2 mechanically).
- `gsdr-auditor`, `gsdr:audit-milestone`, `gsdr:validate-phase` (Nyquist gap auditing).
- `gsdr:reflect` cross-run lesson distillation at `~/.gsd/knowledge/`.
- `gsdr:health-check` for `.planning/` integrity.
- `gsdr-spike-runner` + `.planning/spikes/` (directory already matches).

What conflicts:
- `gsdr:map-codebase` produces confident prose-style summary docs without claim register, citation discipline, Skeptic, or contestation. **CBM exists in opposition to that style.** Disable for this repo.
- `gsdr-codebase-mapper` agent has the same epistemological problem; same disposition.
- "Phase" terminology collides: CBM has Phases A-F (maturity bands with acceptance criteria), GSDR has phases NN-slug (work units). Rename CBM's to "Maturity Bands" or "Capability Phases" to free the word.
- GSDR signal/lesson KB at `~/.gsd/knowledge/` is per-developer; CBM evidence ledger is per-run + append-only + citation-bound. Keep separate.

What must coexist:
- CBM's runtime constitution + claim-register schema + evidence ledger stay untouched.
- CBM's producer registry + `cbm run --backend` stays untouched.
- CBM `BUILD-LOG.md` stays (GSDR's per-phase SUMMARY is not a chronological audit substitute).
- Codex CLI parity for runtime agents (CBM-internal); Claude Code parity may use GSDR slash commands for *implementation work*, not for runtime agents.

**Migration recommendation:** **adopt GSDR for the build harness; do not adopt GSD-2.** Rough cost is 2-4 focused sessions. Detailed sequence is in `INTERVENTIONS.md` (interventions I-G1 through I-G7).

**Gating recommendation:** do *not* migrate during the active recovery intervention. The recovery's narrative does not fit GSDR's PLAN.md template, and migration churn would itself violate `AGENTS.md:30-34` ("No kernel-only hardening during recovery"). Migrate after the first real Skeptic artifact lands (S2), which is when the recovery officially closes.

## Beyond-Prompt: Uplift Brainstorm (Best-Possible-Product)

Beyond closing gaps, four ideas with leverage on the *thesis* of CBM (not just on the build):

**U1. Adversarial benchmark suite.** Curate 5-10 mid-size codebases (5k-50k LOC, mixed types: web framework, MCP server, CLI tool, library, monorepo subsystem) with known *traps*: dynamic dispatch the AST extractors miss, plugin registration the static analysis can't trace, doc claims that contradict code, "primary" workflows that are actually one-of-two. Run CBM on each; record `unknown_partition_present` and Skeptic-catch counts. The benchmark answers "does the system catch what it should catch on hard codebases?" rather than "does it produce a schema-valid artifact on an easy one?" This is the work that turns graduation criteria 3, 4, 10 from aspiration into measurement. ~2-4 weeks. High leverage on VISION.

**U2. Interpretive-challenge corpus as a piece of writing.** As real Skeptic runs accumulate, the interesting output is not the artifact but the *challenges*. A challenge with `relation_to_original: scope_dispute` and `interpretive_axis: centrality` is a tiny piece of close reading. Curate the best ones into a public corpus (with opt-in from codebase owners). This is `VISION.md:50-51`'s "challenge ids cited like blog posts" made literal. It is also a powerful demo of the asymmetry the system exists to demonstrate — that *not pretending to understand* is a useful posture.

**U3. Pedagogical track: solo-day-test.** Take a careful reader who has never used CBM, give them `RUNTIME-CONSTITUTION.md` and a small repo, and ask them to produce a valid surface map and intervention card by hand within a working day. This is graduation criterion 9 (`VISION.md:111`). It tests whether the discipline is teachable, not just executable. It also produces excellent feedback on which parts of the constitution are unclear or load-bearing-but-implicit. ~1 week of facilitation per attempt.

**U4. Cross-domain spike: legal-corpus pilot.** `VISION.md:61` names "the schemas and discipline ship successfully to legal corpora, scientific literature reviews." A small spike that runs the schemas (claim-register, citation-resolves-to-bytes, contestation) against, e.g., a single Supreme Court opinion or a single peer-reviewed paper, would test whether the kernel really is domain-portable or whether code-specific assumptions are baked in. This is a small, high-information experiment; one designer, one weekend. Likely outcome: discover three domain assumptions you didn't know you'd made.

These four are not "do them now"; they are "name them so they're not forgotten when the kernel is ready." `INTERVENTIONS.md` ranks them alongside the gap-closure work.

## Evidence Reviewed

### Authority docs
- `VISION.md` (read in full)
- `RUNTIME-CONSTITUTION.md` (read in full)
- `AGENTS.md` (read in full)
- `README.md` (read in full)
- `docs/architecture.md` (read in full)
- `docs/roadmap.md` (read in full)

### Live state
- `.planning/STATE.md` (read in full)
- `.planning/CURRENT-PLAN.md` (read in full)
- `BUILD-LOG.md` (1376 lines; read header, mid-spread `:1100-1376`, sampled by sub-agent)
- `git log --oneline -40`, `git branch -a`, `git status`

### Reviews
- `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/` (referenced via sub-agent)
- `.planning/reviews/2026-05-01-opus-architecture-audit/` (referenced as superseded)
- `.planning/reviews/2026-05-01-claude-cowork-architecture-review/` (empty)
- `.planning/reviews/2026-05-02-opus-cross-vendor-audit/` (this packet; OUTPUT/STDERR were 0-byte)

### Code
- `cbm/cli.py` (5012 lines; sampled by sub-agent across schema-loading, citation, ledger, claim-evidence, codex-cli adapter, gate-executor, producer registry, validate-fresh, consult, refresh, handoff)
- `cbm/__init__.py`, `cbm/__main__.py` (4-6 lines each)
- `cbm/schemas/` (19 schemas confirmed; mirrored from root `schemas/`)
- `cbm/goal_packs/`, `cbm/project_packs/` (scaffolding only, sampled)
- `tests/test_cli.py` (2123 lines, 61 tests; coverage shape sampled)
- `pyproject.toml`
- `platform/codex/`, `platform/claude-code/`, `platform/PORTABILITY.md` (sampled by sub-agent)
- `skills/{surface-mapping,skeptic,synthesizer,intervention-planner,consult,compaction-recovery,tracer}.md` (sampled by sub-agent)

### Benchmarks and spikes
- `.planning/benchmarks/2026-05-02-mcp-git-codex-smoke/` (RESULT.md, run-manifest.json, skeptic-review-surface-map.md, handoff.md — sampled by sub-agent)
- `.planning/spikes/2026-05-01-codex-cli-isolation.md` (sampled by sub-agent)

### External research
- GSDR (Get Shit Done Reflect) 1.19.6: feature manifest, audit conventions, dual-installation, platform-monitoring docs at `~/.claude/get-shit-done-reflect/`
- GSD-2: `https://github.com/gsd-build/gsd-2`
- Original GSD: `https://github.com/gsd-build/get-shit-done`
- Community forks: `jnuyens/gsd-plugin`, `b-r-a-n/gsd-claude`, `itsjwill/gsd-pro`
- Articles: codecentric, The New Stack, CC for Everyone, estebantorr.es

## Uncertainties

- **U-1**: The claim that 7 forbidden behaviors are enforced-hard, 6 enforced-soft, 2 doc-only is based on sub-agent code-trace; I did not re-derive it. If acted on, verify per-behavior before basing policy on the count.
- **U-2**: Sub-agent identified `cbm/cli.py:503` for `RefResolver` deprecation, `:24` for citation regex, `:868` for `run_id` path construction, `:3875-3878` for Codex subprocess. Spot-checked but not exhaustively verified. Path/line numbers should be reconfirmed before patches.
- **U-3**: Whether the live Codex smoke artifact's "stub" character is a Codex-CLI behavior (model produced empty findings) or a CBM-prompt issue (we asked for nothing substantive) is not separable from this audit. The next live run with `skills/skeptic.md` actually loaded will tell.
- **U-4**: Claim that GSD-2 wants to own the run lifecycle is from sub-agent reading of GSD-2 docs (SQLite state, fresh-session-per-task). The conflict claim is high-confidence in shape; the precise integration boundary should be re-checked if migration is pursued.
- **U-5**: Whether the 2026-05-02-opus-cross-vendor-audit OUTPUT was abandoned, in-flight, or technically failed is not determinable from the repo. Filling it (this document) is the right move regardless.
- **U-6**: VISION.md graduation criteria 3 and 4 require ≥30 expert-reviewed runs. There is no plan for funding or sourcing those reviewers. Treating this as motivational rather than design intent is honest; deciding whether to plan it is a strategic question for the user.

End of audit.
