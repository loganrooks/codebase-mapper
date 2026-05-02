# Concrete Interventions — Ready to Formalize

Status: proposal
Last updated: 2026-05-02
Source: derived from `OUTPUT-CLAUDE-OPUS.md` in this directory

This document translates the audit's findings into a ranked, classifiable intervention list. Each intervention has a stable ID, severity, recovery-allowance classification, effort estimate, and acceptance criterion. The user can pick a subset and formalize them as the next phase plan (or a follow-up milestone after recovery closes).

Classification key:
- **R-OK**: allowed under current recovery rules (`AGENTS.md:30-34`) — directly supports runtime producers, benchmark evidence, producer provenance, run manifests, or recovery governance.
- **R-DEFER**: kernel-only or expansion work; defer until the first real agent-produced benchmark artifact lands.
- **R-AFTER**: depends on a `R-OK` intervention to land first; valid once recovery closes.
- **POST-MS**: belongs to the next milestone or a calibration milestone; out of current recovery scope.

Severity inherited from `OUTPUT-CLAUDE-OPUS.md`. Effort is a rough order, not a commitment.

---

## Tier 1 — Recovery-allowed, do next

| ID | Intervention | Severity | Effort | Class | Acceptance |
|---|---|---|---|---|---|
| **I-S1** | Live Codex CLI isolation probe | high (verifies A3 assumption) | 0.5-1 day | R-OK | Spike artifact at `.planning/spikes/2026-05-02-codex-isolation-live.md` records a transcript proving spawned context cannot see parent-only information; outcome `verified | breached | inconclusive`. |
| **I-S3** | `cbm-loop-status` review-completion + checkpoint gates (closes B1, codifies W1, W2, W6) | blocking | 1-2 days | R-OK | Empty `OUTPUT*.md` blocks `--scope broad-goal`; same-model-only checkpoint blocks pass-claim scope; repeated-rework heuristic warns. Three regressions added. |
| **I-S4a** | Codex CLI adapter timeout + `run_id` validation (closes B2, B3) | blocking | 0.5 day | R-OK | `subprocess.run(..., timeout=600)`; `run_id` rejected unless `^[A-Za-z0-9._-]{1,64}$`; manifest records `interrupted` status on timeout; two regressions added. |
| **I-S4b** | Codex CLI adapter output-path enforcement + stderr tee (closes N7) | medium | 0.5 day | R-OK | Smoke step writes JSON only to `--output-path`; stderr to `.research/<run_id>/logs/<step>.stderr`; manifest records both file SHAs. |
| **I-S2** | Skill loader + first real Skeptic artifact on MCP `src/git` (closes N3, A2) | high (unblocks runtime track) | 3-5 days | R-OK | `cbm/skills.py::load_skill(name)` exists; `--backend codex-cli` injects `skills/skeptic.md` as system prompt; live run on existing surface map produces an artifact with ≥1 factual citation spot-check (resolves at SHA, supports the claim) and ≥1 attempted interpretive challenge (with `competing_reading`, `competing_evidence`, `interpretive_axis`, `relation_to_original`); parent-side gates pass; result lands at `.planning/benchmarks/<date>-mcp-git-skeptic-real/`. **This is the minimum-useful-CBM floor (`VISION.md:41-43`).** |
| **I-S5** | ADR ledger seed (codifies W3) | medium | 0.5 day | R-OK | `.planning/decisions/ADR-001-cbm-owns-run-lifecycle.md`, `ADR-002-hooks-are-adapter-glue.md`, `ADR-003-producer-registry-over-outer-orchestrator.md`, `ADR-004-deterministic-baseline-is-not-runtime-evidence.md`, `ADR-005-cross-model-checkpoint-mandatory-for-pass-claims.md` written; STATE.md / CURRENT-PLAN.md cross-link them by slug. |
| **I-S6** | Codex CLI failure-mode regressions (closes N14) | medium | 0.5 day | R-OK | Five `tests/test_cli.py` cases: timeout, invalid-JSON output, missing-output-file, schema-rejection of model output, stderr noise with valid JSON in file. Use existing fake-executable pattern. |
| **I-S7** | Honest-baseline banner on cards/handoff (closes A6) | medium | 0.25 day | R-OK | Handoff and every intervention card with `produced_by: cbm-baseline-*` carry a prominent "deterministic baseline output, not a runtime-agent reading; cards from this run inherit baseline guarantees only" banner. Schema unchanged; presentation only. |

**Tier 1 total: ~6-9 days.** Sequencing: I-S1 → I-S3 || I-S4a/b || I-S5 → I-S2 → I-S6 → I-S7.

---

## Tier 2 — Recovery-allowed governance / gap-closures

| ID | Intervention | Severity | Effort | Class | Acceptance |
|---|---|---|---|---|---|
| **I-N1** | BUILD-LOG.md retroactive disposition annotation (closes O1) | medium | 0.5 day | R-OK | Each historical "Phase X disposition: pass" entry gets a footnote citing `f98605d` and `STATE.md:39`. |
| **I-N2** | `consult` auto-validate-fresh (closes N10) | medium | 0.25 day | R-OK | `command_consult` calls `command_validate_fresh` on inputs; refuses with stale-input error if any input is stale. One regression. |
| **I-N3** | Pack-load failure surfacing (closes N12) | low | 0.25 day | R-OK | Malformed goal/project packs raise `ValueError` on load (or log to stderr with pack id and validation error if best-effort is preserved). |
| **I-N4** | Architecture/roadmap "see STATE.md" header (closes O2) | low | 0.25 day | R-OK | `docs/architecture.md` and `docs/roadmap.md` open with a current-status header linking to `STATE.md`. |
| **I-N5** | STATE.md split: dispatch evidence vs. minimum-useful (closes O4) | medium | 0.25 day | R-OK | Benchmark State section distinguishes "first runtime-producer dispatch evidence" (cleared) from "minimum-useful CBM" (still pending I-S2). |
| **I-N6** | Self-critique audit script (codifies W5) | low | 0.5 day | R-OK | `cbm-self-critique-audit` (or a one-off script) counts pass/fail rate across BUILD-LOG self-critique blocks; threshold for "review broken" alarm. Output reviewed at next phase boundary. |
| **I-N7** | Schema duplication wheel-install integration test (closes N6) | medium | 0.5 day | R-OK | Test builds wheel into temp venv, imports `cbm.cli` with `CBM_SCHEMA_DIR` unset and target-local `schemas/` absent, asserts `schema_store()` resolves all 19 schemas from package data. Counter-regression: an unmirrored root schema fails CI. |

**Tier 2 total: ~2-3 days.** Can interleave with Tier 1 or run in a follow-up slice.

---

## Tier 3 — Architectural uplifts after recovery closes

| ID | Intervention | Severity | Effort | Class | Acceptance |
|---|---|---|---|---|---|
| **I-A1** | Producer registry as data (closes N5, A1) | medium | 2-3 days | R-AFTER | `ProducerManifest` dataclass; `cbm/producers/<id>.json|yaml`; one source of truth for dispatch; new producer added without editing dispatcher. |
| **I-A2** | `cli.py` first split: `git_ops`, `schema_loading`, `ledger` extraction (closes N4 partial) | medium | 3-5 days | R-AFTER | Three modules extracted; `cli.py` ~3500 lines; full pytest passes; behavior unchanged. |
| **I-A3** | `cli.py` second split: `claim_evidence`, `artifact_builders` (parallel) | medium | 3-5 days | R-AFTER | `cli.py` ~2200 lines; full pytest passes; behavior unchanged. |
| **I-A4** | `cli.py` third split: `codex_cli_adapter`, `gate_executor`, `producer_registry` | medium | 3-5 days | R-AFTER | `cli.py` ~600 lines (entry-point + glue only); full pytest passes; behavior unchanged. |
| **I-B4** | `RefResolver` → `referencing.Registry` migration (closes B4) | blocking-on-jsonschema-5 | 1-2 days | R-AFTER | All `RefResolver` usages migrated; deprecation warnings disappear from `pytest -q`; full suite passes against jsonschema 4.18+. |
| **I-N9** | Ledger HMAC tamper-evidence (closes N9 — only if downstream consumer requires it) | medium | 1-2 days | POST-MS | Per-repo HMAC key stored outside `.research/`; ledger entries HMAC-signed; threat model documented in `RUNTIME-CONSTITUTION.md §13`. |
| **I-N13** | Subprocess heartbeat + `--resume` (closes N13 — only when first agent run >2 min produces UX problem) | medium | 2-3 days | POST-MS | Heartbeat lines via newline-delimited JSON; checkpoint per N seconds; `--resume` flag re-runs only failed steps. |

**Tier 3 total (excluding POST-MS): ~12-20 days.** All gated on recovery closing (i.e., I-S2 lands).

---

## Tier 4 — Cross-platform parity (post-recovery, before graduation criterion 8)

| ID | Intervention | Severity | Effort | Class | Acceptance |
|---|---|---|---|---|---|
| **I-CP1** | Claude Code adapter `--backend claude-code` | high (graduation crit 8) | 5-7 days | R-AFTER | Claude Code subprocess dispatch + isolation probe (mirror of I-S1) + skill loading; smoke artifact on MCP `src/git` matches Codex output structure; `platform/PORTABILITY.md` updated. |
| **I-CP2** | Cross-platform parity test in CI | medium | 1-2 days | R-AFTER | Same input + same skill + both backends produce structurally equivalent artifacts (per `platform/PORTABILITY.md`); regression added. |

**Tier 4 total: ~7-9 days.**

---

## Tier 5 — GSDR adoption (post-recovery; PARTIAL_FIT verdict)

GSDR adoption is a developer-workflow change that does not modify CBM's runtime. It addresses W2 (cross-model checkpoint as a primitive), W4 (BUILD-LOG slicing benefit), and reduces ongoing planning friction. Migration is **not** authorized during the active recovery intervention. Run after I-S2 lands.

| ID | Intervention | Severity | Effort | Class | Acceptance |
|---|---|---|---|---|---|
| **I-G1** | Rename CBM "Phase A-F" to "Maturity Bands" or "Capability Phases" | medium | 0.5 day | R-AFTER | `VISION.md`, `STATE.md`, `CURRENT-PLAN.md`, `AGENTS.md`, `docs/roadmap.md`, `docs/architecture.md` updated; "Phase" reserved for GSDR work units; single-commit rename. |
| **I-G2** | Run `/gsdr:upgrade-project` on this repo, set `commit_docs: false` initially | medium | 0.25 day | R-AFTER | `.planning/config.json` exists; GSDR does not auto-commit `.planning/` artifacts. |
| **I-G3** | Disable `gsdr:map-codebase` and `gsdr-codebase-mapper` for this repo | high (epistemic conflict) | 0.5 day | R-AFTER | Local override in `~/.claude/gsdr-local-patches/` (the patches directory exists); refusal documented in `AGENTS.md`. |
| **I-G4** | Wire `gsdr-auditor` to CBM checkpoint reviews (codifies W2 mechanically) | high | 1 day | R-AFTER | CBM-specific task-spec template loads `RUNTIME-CONSTITUTION.md`, `STATE.md`, `CURRENT-PLAN.md`, recent diff/commits, and the maturity-band acceptance criteria being claimed. Saved under `.planning/audits/<date>/checkpoint-task-spec.md`. `audit_delegation: cross_model:gpt-5.4` (or chosen cross-model) used for pass-claim checkpoints. |
| **I-G5** | Map current recovery sequence to a closed GSDR phase | medium | 0.5 day | R-AFTER | `.planning/phases/00-recovery-intervention/{PLAN.md=current CURRENT-PLAN content, VERIFICATION.md=accepted CHECKPOINT.md, SUMMARY.md=this audit's verdict + I-S1 through I-S7 ship status}`. Closed via `gsdr:audit-milestone`. |
| **I-G6** | Open next phase via `gsdr:plan-phase` for first runtime-producer evidence track | medium | 0.5 day | R-AFTER | `.planning/phases/01-first-runtime-producer-evidence/PLAN.md` lists I-S1 through I-S2; acceptance criterion = minimum-useful-CBM floor cleared. |
| **I-G7** | AGENTS.md amendment: GSDR governs implementation cadence; CBM runtime + RUNTIME-CONSTITUTION govern artifact epistemics; `gsdr:map-codebase` is disabled | medium | 0.25 day | R-AFTER | New AGENTS.md section; no behavior change to CBM runtime. |

**Tier 5 total: ~3-4 days.** Optional; the user may also choose to keep CBM's planning system as-is and just adopt selected GSDR primitives (e.g., `gsdr:audit` for cross-model checkpoints, `gsdr:health-check`) without the full migration.

**Do not pursue GSD-2.** Architectural conflict: GSD-2 wants to own the run lifecycle via Pi SDK + SQLite state + worktree isolation; CBM's accepted recovery decision is that CBM owns the run lifecycle through a producer registry. Two run-lifecycle owners is one too many.

---

## Tier 6 — Uplift program (calibration milestone, beyond gap-closure)

These belong to a separate milestone with its own acceptance criteria. They are listed here so they are not forgotten when the runtime-agent floor is cleared.

| ID | Intervention | Severity | Effort | Class | Acceptance |
|---|---|---|---|---|---|
| **I-U1** | Adversarial benchmark suite — 5-10 mid-size codebases with known traps | high (anchors graduation crits 3, 4, 10) | 2-4 weeks | POST-MS | Curated repos at fixed SHAs; CBM run on each; Skeptic catch-rate measured against expert review for ≥30 runs; graduation criteria 3 + 4 measurable. |
| **I-U2** | Interpretive-challenge corpus (public, opt-in from owners) | medium | ongoing | POST-MS | Curated `chl-*` references usable in writing; demonstrates `VISION.md:50-51` claim. |
| **I-U3** | Pedagogical track — solo-day-test (graduation crit 9) | high | 1-2 weeks per attempt | POST-MS | Careful reader new to CBM produces a valid surface map and intervention card on a small repo from `RUNTIME-CONSTITUTION.md` alone within a working day, with feedback collected. |
| **I-U4** | Cross-domain spike — legal corpus or scientific paper pilot | medium | 2-3 days | POST-MS | Schemas applied to a non-code corpus; baked-in domain assumptions named explicitly; spike artifact at `.planning/spikes/<date>-cross-domain.md`. |
| **I-U5** | Multi-perspective adversarial Skeptic (post-MVP design) | low | TBD | POST-MS | Skeptic panel with named frames (security, performance, accessibility, maintainability, sustainability); challenges come from articulated positions; structured challenge graph emerges. |

---

## Recommended formalization shape

If the user authorizes, the natural plan structure is:

1. **Now (recovery slice)**: Tier 1 — sequence I-S1 → I-S3 || I-S4a/b || I-S5 → I-S2 → I-S6 → I-S7. Total ~6-9 days. Updates `CURRENT-PLAN.md`'s "Next `/goal` Track".
2. **Recovery-close slice**: Tier 2 — interleave with Tier 1 or run after. Updates BUILD-LOG and STATE so the recovery closes honestly.
3. **Next milestone open**: Tier 3 (cleanup) + Tier 4 (cross-platform) + Tier 5 (GSDR adoption — optional). New milestone "Capability Phase B — Standard mode + portability" begins.
4. **Calibration milestone (parallel research program)**: Tier 6. Funded and resourced separately; not on the build agent's loop.

The recovery officially closes when I-S2 ships and the minimum-useful-CBM floor (`VISION.md:41-43`) is cleared with a real Skeptic artifact.
