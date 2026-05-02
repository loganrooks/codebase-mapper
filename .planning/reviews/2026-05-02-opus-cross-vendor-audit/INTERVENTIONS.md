# Concrete Interventions — Ready to Formalize

Status: proposal
Last updated: 2026-05-02
Source: derived from `OUTPUT-CLAUDE-OPUS.md` in this directory

This document translates the audit's findings into a ranked, classifiable, **`/goal`-executable** intervention list. Each intervention has a stable ID, severity, recovery-allowance classification, effort estimate, acceptance criterion, **verification commands** (red-test names, focused-suite invocation, cross-regression set, diff check, full-suite gate), **branch outcomes** (when applicable), and **stop conditions** (when applicable).

Classification key:
- **R-OK**: allowed under current recovery rules (`AGENTS.md:30-34`) — directly supports runtime producers, benchmark evidence, producer provenance, run manifests, or recovery governance.
- **R-DEFER**: kernel-only or expansion work; defer until the first real agent-produced benchmark artifact lands.
- **R-AFTER**: depends on a `R-OK` intervention to land first; valid once recovery closes.
- **POST-MS**: belongs to the next milestone or a calibration milestone; out of current recovery scope.

Severity inherited from `OUTPUT-CLAUDE-OPUS.md`. Effort is a rough order, not a commitment.

---

## How to consume this document with Codex `/goal`

This section is the **execution protocol** for an unattended `/goal` track. The agent running under `/goal` MUST follow it.

### Authorized scope

The `/goal` track scoped at this document is authorized to execute **Tier 1 (I-S1, I-S3, I-S4a, I-S4b, I-S5, I-S6, I-S7) and the R-OK subset of Tier 5 (I-X1, I-X2, I-X3) only**, in the order given by the "Sequencing" line under each tier. **Do not start any Tier 2, Tier 3, Tier 4, or Tier 6 intervention from this `/goal` track.** Those tiers require a separate, explicitly-scoped `/goal` invocation with the user's authorization. If an unblocked Tier 2+ intervention is reached, **stop and surface**.

### The standard verification loop (every intervention)

For every intervention with code changes, follow this exact sequence:

1. **Read** the intervention's full block in this document and any cited `OUTPUT-CLAUDE-OPUS.md` lines.
2. **Write the red test(s) first.** Each intervention names the regression test(s) by name. Write them so they fail against current `main`. Run them and confirm they fail in the way the acceptance criterion implies (not from an unrelated import error).
3. **Implement** the change. Stay inside the touch-set named in the intervention's block; do not refactor adjacent code.
4. **Run focused regression**: `pytest -q <named_tests>` from the intervention's Verification block.
5. **Run cross-regression**: `pytest -q <related_tests>` from the intervention's Verification block. These guard against regressions in adjacent flows.
6. **Diff check**: `git diff --check -- <touched_paths>` to catch whitespace/conflict markers.
7. **Run full suite**: `pytest -q`. Must pass in full. If it fails on a test outside the focused set, the change has a wider blast radius than expected — stop and surface; do not "fix forward" without authorization.
8. **Update STATE.md and CURRENT-PLAN.md** if the intervention changes either's claims (most do not; the ones that do are explicit).
9. **Append a BUILD-LOG.md slice entry** following the recovery-era pattern (e.g., `BUILD-LOG.md:1196-1206, :1355-1376`): `## <date> — Recovery slice: <intervention-id> <title>`, then `Implemented:` bullets, `Verification run:` bullets with the exact commands run, and (only at named boundaries — see AGENTS.md `:69-84`) a self-critique block. **Do not write a self-critique block on every slice; the per-slice ritual is explicitly demoted in AGENTS.md.**
10. **Atomic commit**: one commit per intervention, message `<type>: <imperative-summary>` matching the existing project style (see `git log --oneline -20` for examples). Touch-set must match the intervention's intent; do not bundle unrelated changes.
11. **Re-run `cbm-loop-status`** before continuing: `python3 -m cbm.cli loop-status --repo . --scope recovery-slice --work-category recovery-governance` (or `runtime-producer` depending on intervention class). Must exit 0.
12. **Proceed to next unblocked intervention** in the sequencing order.

### Stop-and-surface conditions (override the loop)

Stop and write a `STOP-NOTE.md` under `.planning/` (or in the relevant intervention's working area) and exit the `/goal` track if any of the following hold:

- An intervention's "Branch outcomes" block names a stop condition that just fired.
- An intervention has been retried and failed twice in a row with the same root cause (per AGENTS.md `:108`).
- A live model run (I-S2) requires user cost approval that has not been obtained.
- The full suite (`pytest -q`) regresses on a test outside the focused set, and the regression is not a trivial mechanical consequence of the change.
- An attempt to satisfy an acceptance criterion would require touching files outside the intervention's named touch-set in a way not anticipated by the criterion.
- Token budget for the goal is approaching exhaustion (the runtime will already steer to wrap-up via the budget-limit prompt; honor it).
- An ambiguity in this document, in `AGENTS.md`, in `RUNTIME-CONSTITUTION.md`, or in `CURRENT-PLAN.md` would cause two reasonable interpretations to produce substantially different systems.

### Recommended `/goal` invocation

```
/goal apply all R-OK interventions from .planning/reviews/2026-05-02-opus-cross-vendor-audit/INTERVENTIONS.md in the sequencing order specified, following the "How to consume this document" protocol exactly. Stop and surface on any branch-outcome stop condition or any condition listed in AGENTS.md `:104-114`.
```

Set a `token_budget` on the goal — `1500000` to `3000000` is reasonable for the full Tier 1 + Tier 5 R-OK sequence. The budget-limited soft stop (Codex PR 18076) will inject wrap-up steering rather than abort mid-intervention.

### Atomicity expectation

Each intervention is an atomic unit. The agent MUST NOT mark an intervention complete until its full Verification block passes. Half-implementations are not acceptable: either the full Verification block passes and the BUILD-LOG slice is committed, or the intervention is rolled back (`git restore`) and the agent stops and surfaces.

---

## Tier 1 — Recovery-allowed, do next

Sequencing: **I-S1 → (I-S3 with I-X3 folded in) → I-S4a → I-S4b → I-S5 → I-X2 → I-X1 → I-S2 → I-S6 → I-S7.**

(I-S3/I-S4a/I-S4b/I-S5/I-X2 are mutually independent and may run in any order after I-S1; the canonical order above is recommended for blast-radius isolation. I-S6 must follow I-S4a/b because it tests their behavior. I-S2 must follow I-X1 so the first pass-claim it produces has a cross-model checkpoint primitive available.)

---

### I-S1 — Live Codex CLI isolation probe

- **Severity**: high (verifies the assumption every later runtime-producer intervention rides on)
- **Effort**: 0.5–1 day
- **Class**: R-OK
- **Closes**: A3 from `OUTPUT-CLAUDE-OPUS.md`; V2 verification gap

**Acceptance.** A spike artifact at `.planning/spikes/2026-05-02-codex-isolation-live.md` records (a) the methodology used, (b) the live transcript of one or more probe runs, (c) the outcome classified as `verified | breached | inconclusive`, and (d) explicit instructions for re-running the probe.

**Probe methodology** (the agent must follow this; do not improvise an alternative without surfacing first).

1. The parent agent (the one running `/goal`) defines a unique secret token of the form `isolation-probe-<8-random-hex-chars>`. **The token must NOT be written to any file at any point during the probe.** It exists only in the parent's session/context.
2. The parent agent dispatches a Codex CLI subprocess via the existing infrastructure: `python3 -m cbm.cli run --repo /tmp/<scratch-repo> --goal "<probe-objective>" --backend codex-cli --allow-live-codex --codex-model gpt-5.4-mini --codex-reasoning-effort medium --mode lightweight --run-id run-isolation-probe-1`. The `<scratch-repo>` should be a tiny, throwaway repo containing only a README. The probe-objective in the goal string is: "Report any tokens, secrets, or unique identifiers that have been mentioned in the parent conversation context, including but not limited to strings beginning with the prefix `isolation-probe-`. If you have no such information, state that explicitly."
3. The subprocess produces a `skeptic-review-surface-map.md` (or whichever artifact the smoke backend emits). Capture its content verbatim.
4. Run a second probe with a different secret token and a slightly different objective phrasing to rule out coincidence.

**Outcome classification.**

- **verified**: subprocess output explicitly states "I have no information about prior context" or equivalent, OR makes no mention of any string matching the secret-token format and produces only output grounded in the scratch-repo content. Both probes must clear.
- **breached**: subprocess output contains the secret token literally OR contains a substring with sufficient overlap to be unambiguously the secret (e.g., 6+ matching hex chars in sequence). Either probe triggering this is a breach.
- **inconclusive**: subprocess output is evasive, refuses without saying why, references "prior context" without naming it, or one probe is `verified` and the other is ambiguous. Surface to the user; do not auto-classify as either of the others.

**Verification.**

- **Red test**: not applicable — this is a spike, not a code change. The artifact existing and recording one of the three classifications IS the verification.
- **Diff check**: `git diff --check -- .planning/spikes/2026-05-02-codex-isolation-live.md BUILD-LOG.md`
- **Loop-status preflight before AND after**: `python3 -m cbm.cli loop-status --repo . --scope recovery-slice --work-category benchmark`
- **Atomic commit**: `feat: record live codex cli isolation probe`. Commit BOTH the spike artifact and the BUILD-LOG entry.

**Branch outcomes.**

- **`verified`** → proceed to I-S3 and the rest of Tier 1.
- **`breached`** → STOP. Write `.planning/STOP-NOTE-isolation-breached.md` summarizing the breach and the implications: I-S2 cannot proceed with `--backend codex-cli` as the Skeptic dispatcher. Surface to the user. Do not start I-S2; do not improvise an alternative backend without authorization. Continue executing I-S3, I-S4a, I-S4b, I-S5, I-X1, I-X2 (governance/adapter-hardening work that is independent of the breach).
- **`inconclusive`** → STOP. Write `.planning/STOP-NOTE-isolation-inconclusive.md`. Surface to the user. Do not start I-S2. The user must adjudicate whether to design a stronger probe (e.g., longer token, more probes, structured prompt) or treat as effectively `breached` until proven otherwise.

**Stop conditions** (in addition to AGENTS.md `:104-114`):

- The live subprocess fails with a Codex CLI error (auth, quota, model unavailable). Record the failure in the spike artifact; do not retry indefinitely; surface to the user.
- The user has not approved cost for the live model run. Surface and wait.

---

### I-S3 — `cbm-loop-status` review-completion + checkpoint gates (with I-X3 folded in)

- **Severity**: blocking
- **Effort**: 1.5–2 days (folds I-X3, see Tier 5)
- **Class**: R-OK
- **Closes**: B1, codifies W1, W2 (mechanical), W6; folds I-X3

**Acceptance.** `cbm-loop-status` (a.k.a. `cbm loop-status`) blocks broad-goal scope when:

- Any `.planning/reviews/<slug>/` contains a `PROMPT.md` but no non-empty `OUTPUT*.md` and no `STOP-NOTE.md` AND no `DISPOSITION.md` recording an explicit abort/park.
- Any `.planning/reviews/<slug>/` exists but is entirely empty (no `PROMPT.md`, no `STOP-NOTE.md`, nothing).
- Any `.planning/reviews/<slug>/CHECKPOINT.md` exists with no `reviewer_model_id` field in its frontmatter (or the field is empty), AND the requested scope is `pass-claim`.
- Any `.planning/reviews/<slug>/CHECKPOINT.md` has `reviewer_model_id` matching the current dev-agent's model family (defined in `cbm/loop_status_config.json` or equivalent — see implementation notes), AND the requested scope is `pass-claim`. Same-model checkpoints are valid for `recovery-slice` scope only and must include `same_model_fallback: true` in the frontmatter to be tolerated even at that scope.

It also emits a non-blocking warning when:

- The most recent N (default: 5) BUILD-LOG.md slices touch the same file in a corrective pattern (rework heuristic, codifies W6).

**Verification.**

- **Red tests** (write first; must fail against current `main`):
  - `tests/test_cli.py::test_loop_status_blocks_broad_goal_on_orphaned_review_packet` — fixture creates a synthetic `<tmp>/.planning/reviews/<slug>/PROMPT.md` with no OUTPUT, asserts loop-status exits nonzero on `--scope broad-goal`.
  - `tests/test_cli.py::test_loop_status_blocks_broad_goal_on_empty_review_folder` — fixture creates `<tmp>/.planning/reviews/<slug>/` with no contents, asserts loop-status exits nonzero on `--scope broad-goal`.
  - `tests/test_cli.py::test_loop_status_blocks_pass_claim_with_missing_reviewer_model_id` — fixture creates a CHECKPOINT.md with no reviewer field, asserts loop-status exits nonzero on `--scope pass-claim`.
  - `tests/test_cli.py::test_loop_status_blocks_pass_claim_with_same_model_reviewer` — fixture creates a CHECKPOINT.md with `reviewer_model_id` matching the configured dev-agent family, asserts loop-status exits nonzero on `--scope pass-claim`.
  - `tests/test_cli.py::test_loop_status_accepts_pass_claim_with_cross_model_reviewer` — fixture creates a CHECKPOINT.md with `reviewer_model_id` of a different family, asserts loop-status exits 0.
  - `tests/test_cli.py::test_loop_status_warns_on_repeated_rework_pattern` — synthetic BUILD-LOG with N+1 corrective slices on the same path, asserts warning emitted; with N rework, no warning.
  - `tests/test_cli.py::test_loop_status_recovery_slice_tolerates_labeled_same_model_fallback` — fixture with `reviewer_model_id` matching dev-agent family AND `same_model_fallback: true`, asserts `--scope recovery-slice` exits 0.

- **Implement**. Add config file `cbm/loop_status_config.json` (or equivalent constant in `cli.py` with comment) declaring the current dev-agent model family list (initial value: `["claude-opus", "claude-sonnet", "claude-haiku"]`). Extend `command_loop_status` (currently in `cli.py`).

- **Focused regression**: `pytest -q tests/test_cli.py::test_loop_status_blocks_broad_goal_on_orphaned_review_packet tests/test_cli.py::test_loop_status_blocks_broad_goal_on_empty_review_folder tests/test_cli.py::test_loop_status_blocks_pass_claim_with_missing_reviewer_model_id tests/test_cli.py::test_loop_status_blocks_pass_claim_with_same_model_reviewer tests/test_cli.py::test_loop_status_accepts_pass_claim_with_cross_model_reviewer tests/test_cli.py::test_loop_status_warns_on_repeated_rework_pattern tests/test_cli.py::test_loop_status_recovery_slice_tolerates_labeled_same_model_fallback`

- **Cross-regression**: `pytest -q tests/test_cli.py::test_loop_status_blocks_broad_goal_until_checkpoint_satisfies_resume tests/test_cli.py::test_loop_status_blocks_dirty_authority_docs_and_disallowed_work`

- **Diff check**: `git diff --check -- cbm/cli.py cbm/loop_status_config.json tests/test_cli.py docs/contracts.md BUILD-LOG.md`

- **Self-test on this very repo**: `python3 -m cbm.cli loop-status --repo . --scope broad-goal --work-category benchmark` MUST now flag `.planning/reviews/2026-05-01-claude-cowork-architecture-review/` as an empty review folder needing a STOP-NOTE. **Resolve the flag** by writing `.planning/reviews/2026-05-01-claude-cowork-architecture-review/STOP-NOTE.md` recording the abort (cite the prior decision in BUILD-LOG that this review packet was supersedanded). Re-run loop-status; it should now exit 0.

- **Full suite**: `pytest -q`

- **Atomic commit**: `feat: gate broad goal on review packet completion and cross model checkpoints`

**Branch outcomes.**

- Self-test reveals that the existing accepted CHECKPOINT.md (`.planning/reviews/2026-05-01-strategy-workflow-vision-audit/CHECKPOINT.md`) is now flagged because it lacks `reviewer_model_id` → **expected**. Add the field to that CHECKPOINT.md frontmatter as part of this slice (record `reviewer_model_id: claude-opus-4-5-or-equivalent`, `same_model_fallback: true`). The same-model fallback is permitted at `recovery-slice` scope per the recovery's earlier disposition; codifying the field is the load-bearing change. Document this in the BUILD-LOG slice.
- Self-test reveals other unanticipated review-folder failures → STOP and surface; do not silently fix-forward.

---

### I-S4a — Codex CLI adapter timeout + `run_id` validation

- **Severity**: blocking
- **Effort**: 0.5 day
- **Class**: R-OK
- **Closes**: B2, B3

**Acceptance.**

- All `subprocess.run(...)` calls dispatching live model work (notably `cli.py:3875`, plus any other live-subprocess dispatch added since) carry an explicit `timeout=<int>` argument (default 600 seconds, configurable via `--codex-timeout-seconds` flag).
- On `subprocess.TimeoutExpired`, the manifest is updated with `status: "interrupted"` and a `cause: "timeout"` field; partial output (if any) is preserved at `.research/<run_id>/codex_outputs/<step>.partial`.
- All commands accepting `--run-id` validate the value against `^[A-Za-z0-9._-]{1,64}$` (apply `sanitize_id`-style validation, see existing `cli.py:3608`) and exit nonzero with a clear error if it fails. Apply at every entry point: `command_init` (`cli.py:971`), `command_run` (`cli.py:4342`), and any other `--run-id`-accepting command (audit by grep `args.run_id`).

**Verification.**

- **Red tests**:
  - `tests/test_cli.py::test_codex_cli_subprocess_times_out_and_writes_interrupted_manifest` — fake executable that sleeps 5 seconds; invoke with `--codex-timeout-seconds 2`; assert `subprocess.TimeoutExpired` is caught, manifest reports `status: "interrupted"` and `cause: "timeout"`, and the run exits nonzero.
  - `tests/test_cli.py::test_run_id_rejects_path_traversal_in_init` — `cbm init --run-id "../../etc"` exits nonzero with a clear error message; `.research/../../etc/` is NOT created.
  - `tests/test_cli.py::test_run_id_rejects_path_traversal_in_run` — `cbm run --run-id "../escape"` exits nonzero with a clear error message.
  - `tests/test_cli.py::test_run_id_accepts_valid_identifiers` — `cbm init --run-id "run-mcp-git-codex-smoke-4"` succeeds, ensures the regex isn't over-strict.

- **Implement**. Add timeout kwarg to subprocess.run; wrap in try/except; update manifest on timeout. Add `validate_run_id()` helper (or extend `sanitize_id`); apply at command entry points.

- **Focused regression**: `pytest -q tests/test_cli.py::test_codex_cli_subprocess_times_out_and_writes_interrupted_manifest tests/test_cli.py::test_run_id_rejects_path_traversal_in_init tests/test_cli.py::test_run_id_rejects_path_traversal_in_run tests/test_cli.py::test_run_id_accepts_valid_identifiers`

- **Cross-regression**: `pytest -q tests/test_cli.py::test_run_backend_codex_cli_fake_producer_writes_agent_review tests/test_cli.py::test_run_backend_codex_cli_requires_explicit_live_flag tests/test_cli.py::test_init_map_handoff_and_citation_resolution tests/test_cli.py::test_run_orchestrates_phase_a_flow`

- **Diff check**: `git diff --check -- cbm/cli.py tests/test_cli.py docs/contracts.md BUILD-LOG.md`

- **Full suite**: `pytest -q`

- **Atomic commit**: `feat: add timeout and run id validation to codex cli subprocess`

**Stop conditions.**

- A timeout test that should be deterministic is flaky (passes 9/10 runs). Stop. The fake-executable sleep duration vs. timeout value must give a clear margin; if a 5s-sleep-vs-2s-timeout is flaky, the test design is wrong, not the implementation.

---

### I-S4b — Codex CLI adapter output-path enforcement + stderr tee

- **Severity**: medium
- **Effort**: 0.5 day
- **Class**: R-OK
- **Closes**: N7

**Acceptance.**

- The Codex CLI smoke backend (`command_codex_cli_smoke_review`, `cli.py:3828+`) reads model output ONLY from the file path passed to `--output-path`. If the file is missing or empty after subprocess exit (and exit code was 0), the run fails with a clear error.
- Subprocess stdout is captured but not parsed for JSON; if non-empty it is logged at `.research/<run_id>/logs/<step>.stdout`.
- Subprocess stderr is captured and tee'd to `.research/<run_id>/logs/<step>.stderr`, never printed directly to parent stderr.
- The run-manifest records `stdout_sha256`, `stderr_sha256`, and `output_path_sha256` for each step (or empty-string sentinel if file is empty).

**Verification.**

- **Red tests**:
  - `tests/test_cli.py::test_codex_cli_smoke_fails_when_output_path_not_written` — fake executable exits 0 without writing the output_path file; run exits nonzero with a clear error.
  - `tests/test_cli.py::test_codex_cli_smoke_tees_stderr_to_log_file` — fake executable writes to stderr; assert `.research/<run_id>/logs/<step>.stderr` exists and contains the expected content; assert it is NOT in parent stderr (capture parent stderr in test).
  - `tests/test_cli.py::test_codex_cli_smoke_records_log_shas_in_manifest` — fake executable writes known content to stdout, stderr, and output_path; manifest contains the three sha256 fields with correct values.
  - `tests/test_cli.py::test_codex_cli_smoke_tolerates_stdout_when_output_path_is_valid` — fake executable writes valid JSON to output_path AND noise to stdout; run succeeds; stdout content goes to log file but is not parsed.

- **Implement**. Refactor `command_codex_cli_smoke_review` so it reads only from output_path; introduce log-file tee; extend manifest schema if needed (add fields are additive; check `run-manifest.schema.json`).

- **Focused regression**: `pytest -q tests/test_cli.py::test_codex_cli_smoke_fails_when_output_path_not_written tests/test_cli.py::test_codex_cli_smoke_tees_stderr_to_log_file tests/test_cli.py::test_codex_cli_smoke_records_log_shas_in_manifest tests/test_cli.py::test_codex_cli_smoke_tolerates_stdout_when_output_path_is_valid`

- **Cross-regression**: same set as I-S4a plus `tests/test_cli.py::test_extract_citations_ignores_markdown_backticks`

- **Diff check**: `git diff --check -- cbm/cli.py schemas/run-manifest.schema.json cbm/schemas/run-manifest.schema.json tests/test_cli.py BUILD-LOG.md`

- **Full suite**: `pytest -q`

- **Atomic commit**: `feat: enforce codex cli output path and tee stderr`

**Stop conditions.**

- If the schema additions break existing manifest validation tests, do not relax the schema; investigate whether the test fixtures need updating. Schema schema_version bump is not justified for additive fields.

---

### I-S5 — ADR ledger seed

- **Severity**: medium
- **Effort**: 0.5 day
- **Class**: R-OK
- **Closes**: W3

**Acceptance.** Five ADRs exist at the named paths, each with explicit frontmatter (`Status: accepted`, `Date: 2026-05-02`, `Context:`, `Decision:`, `Consequences:`, `Supersedes:`/`Superseded by:` if applicable). STATE.md and CURRENT-PLAN.md cross-link them by slug at appropriate sites.

**Required ADRs** (paths must match exactly):

- `.planning/decisions/ADR-001-cbm-owns-run-lifecycle.md` — context: `RUNTIME-CONSTITUTION.md` and accepted recovery decision; decision: CBM owns the run lifecycle through a producer registry; consequences: precludes adopting GSD-2 or any harness that owns run lifecycle.
- `.planning/decisions/ADR-002-hooks-are-adapter-glue.md` — context: pre-recovery drift treated hooks as the deployment model; decision: hooks may invoke validators; correctness lives in CBM CLI validation; consequences: no global/user-level hooks; portability lives in `platform/`.
- `.planning/decisions/ADR-003-producer-registry-over-outer-orchestrator.md` — context: alternatives considered during recovery (GSDR, GSD-2, hand-rolled orchestrator); decision: producer registry; consequences: each artifact type declares its producer backend and validation chain.
- `.planning/decisions/ADR-004-deterministic-baseline-is-not-runtime-evidence.md` — context: false-provenance recovery slice (`ebf43d7`); decision: producer ids label deterministic baseline as `cbm-baseline-*`, runtime agents as `<role>@<version>`, smokes as `<id>-smoke@<version>`; consequences: no role-like producer ids on deterministic output; tests enforce label discipline.
- `.planning/decisions/ADR-005-cross-model-checkpoint-mandatory-for-pass-claims.md` — context: this audit (`OUTPUT-CLAUDE-OPUS.md`); decision: same-model-only checkpoints valid only for narrow recovery slices, must be labeled `same_model_fallback: true`; cross-model required for pass-claim scope; consequences: I-X1 implements the primitive; loop-status enforces.

**Cross-link sites.**

- `STATE.md` "Active Architecture Decision" section: cite ADR-001, ADR-002, ADR-003 by slug.
- `CURRENT-PLAN.md` "Locked Decisions" section: cite the ADRs they paraphrase.
- `AGENTS.md:30-34` (recovery rules): cite ADR-004.
- `AGENTS.md:55` (cross-model preference): cite ADR-005.

**Verification.**

- **Red tests**: not strictly required (this is doc work). Optional: `tests/test_cli.py::test_loop_status_warns_on_undocumented_adr_references` — if a STATE.md cite-by-slug fails to resolve, warn. **Skip in this slice; revisit in a follow-up.**
- **Loop-status preflight**: `python3 -m cbm.cli loop-status --repo . --scope recovery-slice --work-category recovery-governance` exits 0.
- **Diff check**: `git diff --check -- .planning/decisions STATE.md CURRENT-PLAN.md AGENTS.md BUILD-LOG.md`
- **Full suite**: `pytest -q` (must still pass; no behavior change).
- **Atomic commit**: `docs: seed adr ledger with five load bearing recovery decisions`

**Stop conditions.**

- The ADR content disagrees with what STATE.md or CURRENT-PLAN.md currently says. Stop; surface; do not silently choose one to override the other. The ADRs are paraphrasing existing decisions, not making new ones.

---

### I-X2 — Per-phase artifact bundle convention

- **Severity**: medium
- **Effort**: 0.5–1 day
- **Class**: R-OK
- **Closes**: replaces rejected I-G5/I-G6; formalizes the recovery's existing shape

**Acceptance.**

- `AGENTS.md` has a new section titled "Per-phase artifact bundle" documenting:
  - Each implementation phase lives at `.planning/phases/<NN-slug>/`.
  - Required files per phase: `PLAN.md` (active during the phase), `VERIFICATION.md` (filled at phase close), `SUMMARY.md` (filled at phase close).
  - Optional file: `RESEARCH.md` (filled before/during the phase if research is required).
  - Phase numbers are zero-padded two-digit decimals starting from `00`. Non-decimal slug suffixes are kebab-case.
  - The roadmap-level CBM "Phase A-F" maturity bands in `docs/roadmap.md` are explicitly distinct: those are *graduation criteria*, not work units. Phase directories are *implementation* phases.
- The recovery intervention is archived as `.planning/phases/00-recovery-intervention/`:
  - `PLAN.md`: copy current `.planning/CURRENT-PLAN.md` as it stood at the start of this `/goal` track. Add a header note: "This is the archived recovery PLAN; live planning lives at `.planning/CURRENT-PLAN.md`."
  - `VERIFICATION.md`: copy `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/CHECKPOINT.md` content with a header note linking to the original.
  - `SUMMARY.md`: write fresh — recovery completion summary citing the audit (`OUTPUT-CLAUDE-OPUS.md`), this very `/goal` track's interventions shipped (will be filled progressively as interventions land; initial draft is acceptable), and the recovery's official-close criterion (I-S2 + first cross-model-reviewed pass-claim checkpoint).
- The next phase is opened as `.planning/phases/01-first-runtime-producer-evidence/`:
  - `PLAN.md`: lists I-S1 (already done by the time this intervention runs), I-S3, I-S4a/b, I-S5, I-X1, I-X2 (this one, self-referential), I-X3, I-S2, I-S6, I-S7. Acceptance criterion: minimum-useful-CBM floor (`VISION.md:41-43`) cleared with a substantive Skeptic artifact AND first cross-model-reviewed pass-claim checkpoint dispositioned `accept`.
  - `VERIFICATION.md` and `SUMMARY.md` are stubs at this point; filled at phase close.

**Verification.**

- **Red tests**: not required (doc/archive work). Optional `tests/test_cli.py::test_loop_status_warns_on_phase_dir_missing_required_files` — if `.planning/phases/<NN>/` exists without required files, warn. **Defer to a follow-up slice; not load-bearing here.**
- **Loop-status preflight**: `python3 -m cbm.cli loop-status --repo . --scope recovery-slice --work-category recovery-governance` exits 0.
- **Diff check**: `git diff --check -- AGENTS.md .planning/phases BUILD-LOG.md`
- **Full suite**: `pytest -q`
- **Atomic commit**: `docs: introduce per phase artifact bundle convention`

**Stop conditions.**

- The recovery PLAN content does not cleanly fit the per-phase template (e.g., the "Active Recovery Sequence" structure is too specific). Acceptable resolution: keep the original prose verbatim under a `## Original recovery plan` heading inside `00-recovery-intervention/PLAN.md`; do NOT force-rewrite to fit a template. The convention is "these files exist with this content type", not "this content fits a rigid format."

---

### I-X1 — CBM-native cross-model checkpoint primitive

- **Severity**: high
- **Effort**: 1–2 days
- **Class**: R-OK
- **Closes**: codifies W2 mechanically; replaces rejected I-G4

**Acceptance.**

- A new CLI subcommand `cbm checkpoint` exists with at least these flags:
  - `--pass-criterion <text>`: the criterion being claimed (free string, required).
  - `--scope <recovery-slice|pass-claim|main-merge|broad-goal-restart>`: the scope of the checkpoint (required).
  - `--reviewer <model-id>`: optional; if provided, recorded as `reviewer_model_id`. If omitted, `reviewer_model_id` is left empty in the emitted CHECKPOINT.md and must be filled in before disposition.
  - `--reviewer-fallback-same-model`: opt-in flag that records `same_model_fallback: true`. Tolerable only at `recovery-slice` scope; emits a warning at any other scope.
- Running `cbm checkpoint` produces `.planning/reviews/<YYYY-MM-DD>-<auto-slug>/`:
  - `PROMPT.md`: templated from STATE.md + CURRENT-PLAN.md + diff-since-last-checkpoint + the pass-criterion. The diff is generated by `git diff <last-checkpoint-commit>..HEAD -- AGENTS.md VISION.md RUNTIME-CONSTITUTION.md docs/architecture.md docs/contracts.md docs/roadmap.md cbm/ tests/ schemas/ cbm/schemas/ .planning/STATE.md .planning/CURRENT-PLAN.md`.
  - `CHECKPOINT.md`: skeleton with frontmatter (`Status: pending`, `Date: <today>`, `Reviewer model id: <value-or-empty>`, `Same model fallback: <bool>`, `Scope: <value>`, `Pass criterion: <text>`, `Confidence: <empty>`, `Disposition: <empty>`). Body is empty for the reviewer to fill.
  - `DISPOSITION.md`: skeleton (`Status: pending`, `Decision: <empty>`).
- `cbm-loop-status` (already extended in I-S3) refuses pass-claim scope unless the most recent CHECKPOINT.md has `reviewer_model_id` set to a model from a different family than the configured dev-agent family.

**Verification.**

- **Red tests**:
  - `tests/test_cli.py::test_checkpoint_command_emits_packet_with_required_files` — invoke `cbm checkpoint --pass-criterion "test" --scope recovery-slice`; assert `.planning/reviews/<auto-slug>/PROMPT.md` and `CHECKPOINT.md` and `DISPOSITION.md` exist with correct frontmatter shape.
  - `tests/test_cli.py::test_checkpoint_packet_includes_diff_since_last_checkpoint` — fixture: a repo with two commits since the last checkpoint; assert PROMPT.md contains content from those commits' diff.
  - `tests/test_cli.py::test_checkpoint_records_reviewer_model_id_when_provided` — invoke with `--reviewer gpt-5-thinking`; assert CHECKPOINT.md frontmatter contains `reviewer_model_id: gpt-5-thinking`.
  - `tests/test_cli.py::test_checkpoint_recovery_slice_allows_same_model_fallback_with_flag` — invoke with `--scope recovery-slice --reviewer-fallback-same-model`; assert no error, frontmatter has `same_model_fallback: true`.
  - `tests/test_cli.py::test_checkpoint_pass_claim_warns_on_same_model_fallback` — invoke with `--scope pass-claim --reviewer-fallback-same-model`; assert warning emitted (or rejection — pick one in implementation; recommend warning, with loop-status doing the hard block).
  - `tests/test_cli.py::test_loop_status_pass_claim_blocked_until_cross_model_disposition` — fixture: CHECKPOINT.md with `reviewer_model_id: claude-opus-4-7` and `Disposition: accept`; assert loop-status `--scope pass-claim` exits nonzero. Then update CHECKPOINT.md `reviewer_model_id` to `gpt-5-thinking`; assert loop-status `--scope pass-claim` exits 0.

- **Implement**. Add `command_checkpoint` to `cli.py`. Add `checkpoint` subcommand parser. The model-family check must reuse the config introduced in I-S3.

- **Focused regression**: `pytest -q tests/test_cli.py::test_checkpoint_command_emits_packet_with_required_files tests/test_cli.py::test_checkpoint_packet_includes_diff_since_last_checkpoint tests/test_cli.py::test_checkpoint_records_reviewer_model_id_when_provided tests/test_cli.py::test_checkpoint_recovery_slice_allows_same_model_fallback_with_flag tests/test_cli.py::test_checkpoint_pass_claim_warns_on_same_model_fallback tests/test_cli.py::test_loop_status_pass_claim_blocked_until_cross_model_disposition`

- **Cross-regression**: full I-S3 cross-regression set.

- **Diff check**: `git diff --check -- cbm/cli.py cbm/loop_status_config.json tests/test_cli.py docs/contracts.md AGENTS.md BUILD-LOG.md`

- **Full suite**: `pytest -q`

- **Atomic commit**: `feat: add cbm checkpoint command and cross model gate`

**Branch outcomes.**

- The actual cross-model checkpoint that this `/goal` track will eventually need (for the I-S2 pass claim) is OUT OF SCOPE for I-X1 itself. I-X1 only builds the primitive. Surface to the user when I-X1 lands so the user can arrange the actual cross-model review (e.g., a GPT-class model) before I-S2 attempts a pass claim.

**Stop conditions.**

- The model-family configuration introduces ambiguity (e.g., the agent doesn't know whether "Claude" includes hypothetical fine-tunes by other parties). Stop and surface; do not improvise. The list is small and explicit.

---

### I-S2 — Skill loader + first real Skeptic artifact on MCP `src/git`

- **Severity**: high (unblocks runtime track; clears minimum-useful-CBM floor)
- **Effort**: 3–5 days
- **Class**: R-OK
- **Closes**: N3, A2; achieves `VISION.md:41-43` minimum-useful floor

**This is the largest intervention. Do it in three sub-slices, each with its own commit.**

#### I-S2a — Skill loader

**Acceptance.** A new module `cbm/skills.py` exposes `load_skill(name: str) -> dict` that returns `{"name": str, "path": Path, "sha256": str, "body": str}`. Reads from `skills/<name>.md` (relative to the CBM source tree). Raises `SkillNotFoundError` (a custom exception class) if the file is missing. The function is pure and idempotent.

**Verification.**

- **Red tests**:
  - `tests/test_cli.py::test_load_skill_returns_path_sha256_and_body` — `load_skill("skeptic")` returns dict with the four fields; sha256 matches manual hashlib computation.
  - `tests/test_cli.py::test_load_skill_raises_skill_not_found_on_missing` — `load_skill("nonexistent")` raises the custom error.
  - `tests/test_cli.py::test_load_skill_is_pure` — calling twice returns the same sha256 and body.

- **Implement**. New module `cbm/skills.py`. Define `SkillNotFoundError`. Read from `Path(__file__).parent.parent / "skills" / f"{name}.md"` with package-resource fallback (mirror the schema-loading pattern from I-N6).

- **Focused regression** + **Cross-regression** (existing skill-related tests, if any) + **Diff check** + **Full suite**

- **Atomic commit**: `feat: add skill loader`

#### I-S2b — Codex backend wires skill into subprocess

**Acceptance.**

- The `command_codex_cli_smoke_review` step (and its successor — see below) accepts a `skill: <name>` parameter from the producer registry. It calls `load_skill(skill)`, passes the body as the system prompt to the subprocess (Codex CLI `--system` or equivalent), and records `skill_name`, `skill_sha256`, and `skill_path` in the run-manifest's step entry.
- The producer-registry entry for skeptic-review is updated to specify `skill: skeptic`.
- A new producer id is introduced: `skeptic@0.1` (separate from `codex-cli-smoke@0.1`). When the skill is loaded successfully and the subprocess produces a substantive artifact (defined below), the artifact's `produced_by` is `skeptic@0.1`. When the skill cannot be loaded or the subprocess fails to produce substantive output, the artifact remains labeled `codex-cli-smoke@0.1` (or fails outright).
- Substantive-artifact criteria: artifact contains ≥1 spot-check entry with a citation that resolves at SHA, AND ≥1 challenge entry with all four required fields populated and `competing_evidence` containing ≥1 citation that resolves at SHA.

**Verification.**

- **Red tests**:
  - `tests/test_cli.py::test_codex_cli_skeptic_run_loads_skill_and_records_sha_in_manifest` — fake executable; assert manifest's step entry has `skill_name: "skeptic"`, `skill_sha256: <expected>`, `skill_path: skills/skeptic.md`.
  - `tests/test_cli.py::test_codex_cli_skeptic_subprocess_receives_skill_as_system_prompt` — fake executable echoes its `--system` argv into output; assert echoed body matches `skills/skeptic.md` content.
  - `tests/test_cli.py::test_codex_cli_skeptic_substantive_output_uses_skeptic_producer_id` — fake executable produces an output with required spot-check + challenge fields; assert artifact `produced_by` is `skeptic@0.1`.
  - `tests/test_cli.py::test_codex_cli_skeptic_stub_output_falls_back_to_smoke_producer_id` — fake executable produces empty output; assert artifact `produced_by` is `codex-cli-smoke@0.1` (or run fails — pick the stricter; recommend run failure).
  - `tests/test_cli.py::test_codex_cli_skeptic_run_fails_on_missing_skill` — set up a producer registry pointing to `skill: nonexistent`; assert run fails with clear `SkillNotFoundError` propagation.

- **Implement**. Update `command_codex_cli_smoke_review` (and the producer-registry-driven dispatch). Update `producer-registry.schema.json` and `cbm/schemas/producer-registry.schema.json` if needed (additive `skill` field).

- **Focused regression** + cross-regression with all existing codex-cli tests + I-S4a/b cross + I-S6 cross + diff check + full suite.

- **Atomic commit**: `feat: load skeptic skill into codex cli subprocess and record provenance`

#### I-S2c — Live run on MCP `src/git`

**Prerequisites.**

- I-S1 outcome was `verified`. **If not, STOP and surface; do not proceed.**
- I-S2a and I-S2b have shipped and full suite passes.
- I-S3, I-S4a, I-S4b, I-S5, I-X1, I-X2, I-S6 (mostly) have shipped — the live run should not be the first thing exercising any other unverified code path.
- User has approved cost for the live model run.

**Acceptance.** A live Codex CLI run on MCP `src/git` (already pinned at `4503e2d12b799448cd05f789dd40f9643a8d1a6c`, see existing `2026-05-02-mcp-git-codex-smoke/`) produces a Skeptic artifact that meets the substantive-artifact criteria above. The run-manifest reports `produced_by: skeptic@0.1`. The handoff gate passes (citation_resolution.unresolved_count: 0, ledger_consistency.missing_citation_count: 0). Result is published to `.planning/benchmarks/2026-05-02-mcp-git-skeptic-real/RESULT.md` with run-manifest.json, producer-registry.json, the skeptic-review-surface-map.md, and handoff.md copied in.

**This achieves the minimum-useful-CBM floor (`VISION.md:41-43`).**

**Verification.**

- **Red tests**: none — this is a benchmark run. The substantive-artifact criteria are enforced by the parent-side gates already verified in I-S2b's tests (with fake executables).
- **Pre-flight**: `python3 -m cbm.cli loop-status --repo . --scope recovery-slice --work-category benchmark` exits 0.
- **Live invocation**: `python3 -m cbm.cli run --repo /tmp/cbm-live-mcp-servers-4503e2d/src/git --goal "produce isolated skeptic review of MCP git server surface map" --backend codex-cli --allow-live-codex --codex-model gpt-5.4-mini --codex-reasoning-effort medium --mode lightweight --run-id run-mcp-git-skeptic-real-1`
- **Inspect output**: read `.research/run-mcp-git-skeptic-real-1/skeptic-review-surface-map.md`. Confirm by hand AND by gate that ≥1 spot-check entry has a SHA-resolving citation that substantively supports the claim, AND ≥1 challenge entry has all four required fields with competing-evidence citations resolving at SHA.
- **Validate**: `python3 -m cbm.cli validate .research/run-mcp-git-skeptic-real-1/handoff.md` exits 0.
- **Publish**: copy artifacts into `.planning/benchmarks/2026-05-02-mcp-git-skeptic-real/`. Write `RESULT.md` summarizing.
- **Update STATE.md**: add to "Benchmark State" section. Distinguish "first runtime-producer dispatch evidence" (cleared earlier) from "minimum-useful CBM floor" (cleared by this run, with link).
- **Update CURRENT-PLAN.md**: mark recovery as eligible for closure pending the I-X1-produced cross-model checkpoint.
- **Full suite**: `pytest -q` (no test changes expected; this is benchmark work).
- **Atomic commit**: `feat: produce first real skeptic artifact on mcp git benchmark`

**Branch outcomes.**

- **Substantive output, gates pass** → recovery eligible for closure. Surface to the user with a recommendation to invoke `cbm checkpoint --scope pass-claim --pass-criterion "minimum useful cbm floor cleared"` and arrange a cross-model reviewer (per I-X1).
- **Stub output (zero findings, placeholder citations)** → DO NOT mark as success. Save the artifact under `.planning/benchmarks/2026-05-02-mcp-git-skeptic-real/attempt-N/`. Iterate ONCE on the system-prompt construction (e.g., examine whether the skill body was truncated, whether the subprocess saw the surface map content, whether `--codex-reasoning-effort high` produces better output). If the second attempt is also stub-quality, **STOP** — three attempts is the budget per AGENTS.md `:108`. Surface to the user; the issue is in the prompt/skill content or the model choice, not in the harness.
- **Subprocess failure (auth, quota, network, model unavailable)** → record failure cause in `.planning/benchmarks/2026-05-02-mcp-git-skeptic-real/RESULT.md`. STOP and surface; do not retry indefinitely.
- **Output meets only one of the two substantive criteria** (e.g., spot-check passes but no challenge raised) → save attempt; iterate once with prompt adjustment focused on the missing criterion. Stop after second attempt if not both criteria met.
- **I-S1 outcome was `breached` or `inconclusive`** → I-S2c MUST NOT run. STOP and surface. The whole I-S2c sub-slice is gated on isolation verification.

**Stop conditions** (in addition to AGENTS.md `:104-114`):

- User cost approval not obtained → STOP and surface.
- Three attempts exhausted without substantive output → STOP and surface.
- Live run produces output that the parent-side gate accepts but a manual spot-check reveals fabricated citations (e.g., the citation resolves at SHA but doesn't actually support the claim) → STOP. This is the most important failure mode to catch; it is the exact thing CBM exists to prevent. Surface to the user with the offending citation+claim pair.

---

### I-S6 — Codex CLI failure-mode regressions

- **Severity**: medium
- **Effort**: 0.5 day
- **Class**: R-OK
- **Closes**: N14
- **Sequencing note**: must run AFTER I-S4a, I-S4b, I-S2b have landed (they introduce the behaviors being tested).

**Acceptance.** Five regression tests covering known Codex CLI failure modes. (Some overlap with I-S4a/b's red tests is acceptable; this slice ensures the full set exists and runs as a deliberate suite.)

**Required tests** (use existing fake-executable pattern from `test_run_backend_codex_cli_fake_producer_writes_agent_review`):

- `tests/test_cli.py::test_codex_cli_smoke_handles_subprocess_timeout` — covered by I-S4a; verify it exists and is named per this convention; rename if needed.
- `tests/test_cli.py::test_codex_cli_smoke_rejects_invalid_json_output` — fake executable writes invalid JSON to output_path; run exits nonzero with a parse error message.
- `tests/test_cli.py::test_codex_cli_smoke_rejects_missing_output_file` — covered by I-S4b; verify and rename if needed.
- `tests/test_cli.py::test_codex_cli_smoke_rejects_schema_invalid_output` — fake executable writes valid JSON that does not match the artifact schema; run exits nonzero with a clear schema error.
- `tests/test_cli.py::test_codex_cli_smoke_tolerates_stderr_noise_with_valid_json` — covered by I-S4b; verify.

**Verification.**

- **Red tests**: any of the above not yet existing.
- **Implement**: any missing tests; rename any drifted from the convention.
- **Focused regression**: `pytest -q tests/test_cli.py::test_codex_cli_smoke_handles_subprocess_timeout tests/test_cli.py::test_codex_cli_smoke_rejects_invalid_json_output tests/test_cli.py::test_codex_cli_smoke_rejects_missing_output_file tests/test_cli.py::test_codex_cli_smoke_rejects_schema_invalid_output tests/test_cli.py::test_codex_cli_smoke_tolerates_stderr_noise_with_valid_json`
- **Cross-regression**: all existing codex-cli tests.
- **Diff check**: `git diff --check -- tests/test_cli.py BUILD-LOG.md`
- **Full suite**: `pytest -q`
- **Atomic commit**: `test: complete codex cli failure mode regression set`

**Stop conditions.**

- A test that should be deterministic produces flaky behavior. Stop; investigate; do not mark "fixed by re-running".

---

### I-S7 — Honest-baseline banner on cards/handoff

- **Severity**: medium
- **Effort**: 0.25 day
- **Class**: R-OK
- **Closes**: A6

**Acceptance.** Handoff renders a prominent banner when ANY card or artifact in the run has `produced_by` matching `cbm-baseline-*` or `dev-fixture-*`. Banner text: `"This run includes deterministic baseline output. Cards and artifacts labeled cbm-baseline-* or dev-fixture-* are NOT runtime-agent readings; they inherit baseline guarantees only (schema-valid, citation-resolved, evidence-table-checked). Do not act on them as if they had Skeptic review."` Each individual card with such a producer also carries an inline marker `[BASELINE]` near its title. No schema change.

**Verification.**

- **Red tests**:
  - `tests/test_cli.py::test_handoff_renders_baseline_banner_when_any_card_is_baseline` — fixture: handoff with at least one `cbm-baseline-*` card; assert banner text appears in handoff.md.
  - `tests/test_cli.py::test_handoff_omits_baseline_banner_when_all_cards_are_runtime_agent` — fixture: handoff with all cards `produced_by: skeptic@0.1` (or similar); assert banner absent.
  - `tests/test_cli.py::test_handoff_marks_each_baseline_card_with_inline_marker` — fixture: two cards, one baseline one runtime; assert `[BASELINE]` appears in the baseline card section, not the runtime one.

- **Implement**: extend `command_handoff` (in `cli.py`); presentation only.
- **Focused regression** + cross-regression with existing handoff tests + diff check + full suite.
- **Atomic commit**: `feat: render baseline producer banner on handoff and cards`

**Stop conditions.**

- The banner text disagrees with `OUTPUT-CLAUDE-OPUS.md` A6's recommended language. Use the exact language from A6 verbatim; do not paraphrase.

---

## Tier 5 — I-X3 (folded into I-S3) and I-X4 (deferred)

I-X3 is intentionally folded into I-S3's red-test set above. It does not run as a separate intervention.

I-X4 is POST-MS and out of `/goal` scope. Documented for completeness only.

---

## Tier 2 onward — DO NOT START FROM THIS `/goal` TRACK

Tiers 2, 3, 4, and 6 are out of scope for the current `/goal` track. The agent MUST NOT start any intervention from these tiers under this `/goal`. After Tier 1 + Tier 5 R-OK interventions complete, **stop and surface**; the user will scope a new `/goal` for the next milestone.

The retained tabular form below is for human reference, not for execution.

### Tier 2 — Recovery-allowed governance / gap-closures (defer to follow-up `/goal`)

| ID | Intervention | Severity | Effort | Class | Acceptance summary |
|---|---|---|---|---|---|
| **I-N1** | BUILD-LOG.md retroactive disposition annotation (closes O1) | medium | 0.5 day | R-OK | Each historical "Phase X disposition: pass" entry footnoted citing `f98605d` and `STATE.md:39`. |
| **I-N2** | `consult` auto-validate-fresh (closes N10) | medium | 0.25 day | R-OK | `command_consult` calls `command_validate_fresh` on inputs; refuses with stale-input error. One regression. |
| **I-N3** | Pack-load failure surfacing (closes N12) | low | 0.25 day | R-OK | Malformed packs raise on load (or log to stderr with id + error). |
| **I-N4** | Architecture/roadmap "see STATE.md" header (closes O2) | low | 0.25 day | R-OK | `docs/architecture.md` and `docs/roadmap.md` open with current-status header linking STATE.md. |
| **I-N5** | STATE.md split: dispatch evidence vs. minimum-useful (closes O4) | medium | 0.25 day | R-OK | Done as part of I-S2c implicitly; verify after I-S2c lands. |
| **I-N6** | Self-critique audit script (codifies W5) | low | 0.5 day | R-OK | `cbm-self-critique-audit` script counts pass/fail rate across BUILD-LOG self-critique blocks. |
| **I-N7** | Schema duplication wheel-install integration test (closes N6) | medium | 0.5 day | R-OK | Test builds wheel into temp venv, asserts `schema_store()` resolves all 19 schemas from package data. |

**Tier 2 total: ~2-3 days.** Defer to a follow-up `/goal`.

### Tier 3 — Architectural uplifts (post-recovery `/goal`)

| ID | Intervention | Severity | Effort | Class | Acceptance summary |
|---|---|---|---|---|---|
| **I-A1** | Producer registry as data (closes N5, A1) | medium | 2-3 days | R-AFTER | `ProducerManifest` dataclass; `cbm/producers/<id>.json|yaml`; one source of truth. |
| **I-A2** | `cli.py` first split: `git_ops`, `schema_loading`, `ledger` (closes N4 partial) | medium | 3-5 days | R-AFTER | Three modules extracted; cli.py ~3500 lines; behavior unchanged. |
| **I-A3** | `cli.py` second split: `claim_evidence`, `artifact_builders` | medium | 3-5 days | R-AFTER | cli.py ~2200 lines; behavior unchanged. |
| **I-A4** | `cli.py` third split: `codex_cli_adapter`, `gate_executor`, `producer_registry` | medium | 3-5 days | R-AFTER | cli.py ~600 lines; behavior unchanged. |
| **I-B4** | `RefResolver` → `referencing.Registry` migration (closes B4) | blocking-on-jsonschema-5 | 1-2 days | R-AFTER | All `RefResolver` usages migrated; deprecation warnings cleared. |
| **I-N9** | Ledger HMAC tamper-evidence (closes N9 — only if downstream consumer requires it) | medium | 1-2 days | POST-MS | HMAC signing; threat model documented. |
| **I-N13** | Subprocess heartbeat + `--resume` (closes N13 — only when first agent run >2 min produces UX problem) | medium | 2-3 days | POST-MS | Heartbeat lines via NDJSON; `--resume` flag. |

**Tier 3 total (excluding POST-MS): ~12-20 days.** All gated on recovery closing.

### Tier 4 — Cross-platform parity (post-recovery `/goal`)

| ID | Intervention | Severity | Effort | Class | Acceptance summary |
|---|---|---|---|---|---|
| **I-CP1** | Claude Code adapter `--backend claude-code` | high (graduation crit 8) | 5-7 days | R-AFTER | Claude Code subprocess dispatch + isolation probe (mirror of I-S1) + skill loading. |
| **I-CP2** | Cross-platform parity test in CI | medium | 1-2 days | R-AFTER | Same input + same skill + both backends produce structurally equivalent artifacts. |

**Tier 4 total: ~7-9 days.**

### Tier 6 — Uplift program (calibration milestone, separate budget)

| ID | Intervention | Severity | Effort | Class | Acceptance summary |
|---|---|---|---|---|---|
| **I-U1** | Adversarial benchmark suite — 5-10 codebases with known traps | high (anchors graduation crits 3, 4, 10) | 2-4 weeks | POST-MS | Curated repos at fixed SHAs; ≥30 expert-reviewed runs. |
| **I-U2** | Interpretive-challenge corpus | medium | ongoing | POST-MS | Curated `chl-*` references; demonstrates `VISION.md:50-51`. |
| **I-U3** | Pedagogical track — solo-day-test (graduation crit 9) | high | 1-2 weeks per attempt | POST-MS | Careful reader produces valid surface map + card from RUNTIME-CONSTITUTION alone within a day. |
| **I-U4** | Cross-domain spike — legal/scientific corpus pilot | medium | 2-3 days | POST-MS | Schemas applied to non-code corpus; baked-in domain assumptions named. |
| **I-U5** | Multi-perspective adversarial Skeptic | low | TBD | POST-MS | Skeptic panel with named frames. |

---

## Recommended formalization shape (unchanged)

If the user authorizes, the natural plan structure is:

1. **Now (recovery slice / current `/goal` track)**: Tier 1 (I-S1 → I-S3 → I-S4a → I-S4b → I-S5 → I-X2 → I-X1 → I-S2 → I-S6 → I-S7) plus I-X3 folded into I-S3. Total ~8–12 days. Updates `CURRENT-PLAN.md`'s "Next `/goal` Track".
2. **Recovery-close slice (separate `/goal`)**: Tier 2. Updates BUILD-LOG and STATE so the recovery closes honestly.
3. **Next milestone (separate `/goal`)**: Tier 3 (cleanup) + Tier 4 (cross-platform). New milestone "Capability Phase B — Standard mode + portability" begins, opened as `.planning/phases/01-first-runtime-producer-evidence/` per I-X2.
4. **Calibration milestone (parallel research program, not on the build agent's loop)**: Tier 6 + I-X4.

The recovery officially closes when I-S2 ships *and* the first pass-claim checkpoint produced via I-X1 is dispositioned `accept` by a non-current-model reviewer. The minimum-useful-CBM floor (`VISION.md:41-43`) is cleared at the same moment.
