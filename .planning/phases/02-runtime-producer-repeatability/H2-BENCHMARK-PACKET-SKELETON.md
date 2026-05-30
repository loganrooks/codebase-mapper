# H2 Benchmark Packet Skeleton

Status: locked
Date: 2026-05-22
Last updated: 2026-05-22
Supersedes: none
Superseded by: none

## Boundary

This file lists the expected paths and artifact contracts for H2.S2, H2.S3, and the H2.S3 cross-vendor checkpoint review. It does not produce the artifacts themselves. H2.S2 writes the H2.S2 packet; H2.S3 writes the H2.S3 handoff packet and the cross-vendor review packet.

Target slug: `h11`. The `<run-date>` placeholder is the date each packet directory is created (one date for H2.S2, a separate date for H2.S3, since they are separate `/goal`s).

## H2.S2 Packet

```text
.planning/benchmarks/<run-date>-h11-h2s2/
  RESULT.md
  surface-map.json
  skeptic-review-surface-map.md
  evidence-ledger.jsonl
  run-manifest.json
  producer-registry.json
  handoff.md
  .research/run-h11-h2s2-<n>/        # one subtree per `cbm run` invocation; see note below.
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

The `<n>` suffix is whatever the dispatching `/goal` author chose for `--run-id run-h11-h2s2-<n>` (the integer is conventional, not enforced by `cbm run`). Under the H2.S2 brief's **interim two-`cbm run` split** (tracked at issue #23 / forthcoming ADR-006; the brief `GOAL-H2S2-LIVE-RUN.md` will carry the dispatch shape once authored as the H2.S2 `/goal`'s deliverable) the packet preserves **both** `.research/run-h11-h2s2-1/` (Surface, `--codex-skeptic-mode none`, effort=medium) and `.research/run-h11-h2s2-2/` (Skeptic, `--codex-surface-mode existing`, effort=high). Under the future single-`cbm run` shape (post-ADR-006 lands) only `.research/run-h11-h2s2-1/` exists. Either shape is valid as long as the H2.S2 `RESULT.md` declares which shape was used and the `.research/` subtrees match. If H2.S2's first attempt fails and a retry uses a different suffix (`-3`, etc.), the skeleton's `<n>` covers that case too.

### H2.S2 artifact contracts

| Artifact | Producer | Consumer | Schema / contract | Validation command |
|---|---|---|---|---|
| `RESULT.md` | H2.S2 `/goal` agent (this `/goal`'s successor, not H2.S1) | H2.S3, human reviewers | Free-form markdown. Records target, command, evidence, surface summary, validation commands, boundary. Same shape as `.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/RESULT.md` and `.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/RESULT.md`. | Human read; no schema validation. |
| `surface-map.json` | `surface-mapper@1.2` on backend `codex-cli`, runtime skill `surface-mapping` | H2.S3 handoff packet, `skeptic@1.2` (within H2.S2), human reviewers | `schemas/surface-map.schema.json` (version `1.2`). Must be non-baseline (`produced_by: surface-mapper@1.2`, not `cbm-baseline-*` or `dev-fixture-*`), schema-valid, with every cited claim resolving to source bytes at `62c5068c`. RUNTIME-CONSTITUTION §10: ≥1 unknown edge expected on a non-trivial codebase. | `python3 -m cbm.cli validate <abs-path-to-surface-map.json> --repo <h11-target-checkout>` and `python3 -m cbm.cli verify-citations <abs-path> --repo <h11-target-checkout>` and `python3 -m cbm.cli check-evidence <abs-path> --repo <h11-target-checkout>`. |
| `skeptic-review-surface-map.md` | `skeptic@1.2` on backend `codex-cli`, runtime skill `skeptic` | H2.S3 handoff packet, human reviewers | `schemas/skeptic-review.schema.json` (artifact frontmatter); body free-form. The Skeptic markdown that gets promoted is the final rendered version, not a smoke-anchor exploratory version (H1.S3 LINEAGE caveat 2). | `python3 -m cbm.cli validate <abs-path> --repo <h11-target-checkout>` and `python3 -m cbm.cli verify-citations <abs-path> --repo <h11-target-checkout>`. |
| `evidence-ledger.jsonl` | The `cbm run` runtime (append-only writes from `surface-mapper@1.2` and `skeptic@1.2` producer steps) | `cbm check-evidence`, H2.S3 handoff packet, human reviewers | `schemas/evidence-ledger.schema.json`. Append-only; entry kinds include `citation_introduced`, `claim_challenged`, `challenge_resolved`. RUNTIME-CONSTITUTION §2: every artifact write preceded by ledger entries for citations introduced. | `python3 -m cbm.cli check-evidence <abs-path-to-surface-map.json> --repo <h11-target-checkout>` reads the ledger transitively. |
| `run-manifest.json` | The `cbm run` runtime | H2.S3, human reviewers, H2.A4 diff record | `schemas/run-manifest.schema.json` (version `1.2`). Records `backend: codex-cli`, every producer step's `producer_id` (`surface-mapper@1.2` and `skeptic@1.2`), the runtime skill name + path + sha256, model + reasoning-effort, started_at / completed_at, stdout/stderr/output sha256 hashes, exit codes, final manifest `status` (`succeeded` or `interrupted`). | `python3 -m cbm.cli validate <abs-path> --repo <h11-target-checkout>`. |
| `producer-registry.json` | `cbm run` setup | The `cbm run` runtime, audit | `schemas/producer-registry.schema.json`. Records the chosen backend per artifact type. For H2.S2: `surface_map` → `surface-mapper@1.2` on `codex-cli`; `skeptic_review` → `skeptic@1.2` on `codex-cli`. | `python3 -m cbm.cli validate <abs-path> --repo <h11-target-checkout>`. |
| `handoff.md` | `cbm-handoff@0.1` (CBM handoff renderer) | H2.S3 handoff packet (as a source-stage handoff, not promoted as the H2.S3 deliverable) | `schemas/handoff.schema.json` (version `1.2`). Carries `gate_summary`, `contestation_summary`, `coverage_caveats`, etc. The H2.S2 `handoff.md` is the per-run handoff; the H2.S3 packet produces its own `HANDOFF.md` that is the H2 pass-claim handoff. | `python3 -m cbm.cli validate <abs-path> --repo <h11-target-checkout>` and `python3 -m cbm.cli verify-citations <abs-path> --repo <h11-target-checkout>`. |
| `.research/run-h11-h2s2-<n>/` subtree(s) (logs, codex_outputs, ledgers, etc.) — **one per `cbm run` invocation** (1 under the future single-run shape; 2 under the interim split, suffix `-1` for Surface and `-2` for Skeptic; more on retry) | The `cbm run` subprocess + ledger writes | Audit | RUNTIME-CONSTITUTION §13 ("Artifacts on disk, always") and §22 ("Recovery"). H1 LINEAGE explicitly recorded that the H1.S1 publication did NOT preserve this tree, which limited retrospective auditability. H2.S2 publication MUST preserve `logs/` and `codex_outputs/` for every run-id in the dispatch. | No schema validation; presence/preservation is the audit criterion. |

H2.S2 stop-and-surface conditions (in addition to the brief's standing ones):

- Surface Mapper produces a baseline-shaped artifact (`produced_by` starts with `cbm-baseline-*` or `dev-fixture-*`). Same class as H1.S2a's blocker; stop.
- Skeptic output is generic, lacks competing evidence, or cites prohibited parent-session context. Stop and either re-prompt with skill or pick a different backend with user authorization.
- Citation resolution fails at the pinned SHA. Stop and either re-prompt or document an `uncertainty-register.jsonl` entry per RUNTIME-CONSTITUTION §10.
- The Codex subprocess hits the timeout (default `--codex-timeout 600`). `run-manifest.json` records `status: interrupted` with `cause: timeout`. H2.S2 stops and the `/goal` author root-causes whether the timeout is a target-size issue (re-pick scope), a reasoning-effort issue (re-tune), or a backend issue (escalate). Do not blindly re-run with a higher timeout.
- The `.research/` subtree is not preserved in the published packet. Re-publish before announcing H2.S2 complete.

## H2.S3 Handoff Packet

```text
.planning/benchmarks/<run-date>-h11-h2s3-handoff/
  RESULT.md
  HANDOFF.md
  VERIFY.md
  LINEAGE.md
  INCLUDED-ARTIFACTS.md
  CHECKPOINT-PACKET.md
  CHECKPOINT-PROMPT.md
  surface-map.json                       # final state copied from H2.S2 + any H2.S3 mapper response
  skeptic-review-surface-map.md          # promoted Skeptic markdown from H2.S2
  source-h2s2-handoff.md                 # per-run handoff from H2.S2 (preserved as source)
  evidence-ledger.jsonl
  .research/run-h11-h2s2-<n>/            # all H2.S2 run subtrees preserved (1 or 2 depending on shape)
    logs/
    codex_outputs/
    ...
  .research/run-h11-h2s3-handoff-1/      # only if H2.S3 has its own preserved-inputs run
    ...
```

### H2.S3 artifact contracts

| Artifact | Producer | Consumer | Schema / contract | Validation command |
|---|---|---|---|---|
| `RESULT.md` | H2.S3 `/goal` agent | Cross-vendor checkpoint reviewer, human auditors | Free-form markdown. Records target, evidence chain, preflight concerns, verification summary, boundary. Same shape as `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/RESULT.md`. | Human read. |
| `HANDOFF.md` | `cbm-handoff@0.1` (rendered for the H2 pass-claim packet, not the H2.S2 per-run handoff) | Cross-vendor reviewer, downstream H3 work | `schemas/handoff.schema.json` (version `1.2`). Must validate, resolve all promoted citations, distinguish baseline vs runtime vs Skeptic evidence (ADR-004), name unresolved unknowns + live disputes, carry no deterministic-baseline overclaim, declare `recommended_next_action_kind: prepare_pass_claim_review` until accepted then progress per slice. | `python3 -m cbm.cli validate <abs-path> --repo <h11-target-checkout>` and `python3 -m cbm.cli verify-citations <abs-path> --repo <h11-target-checkout>`. |
| `VERIFY.md` | H2.S3 `/goal` agent | Cross-vendor reviewer, human auditors | Free-form markdown. Records the exact local verification commands run (with absolute artifact paths per H1.S3 VERIFY.md:15), exit codes, citation counts, test counts, and loop-status outcomes. | Human read. |
| `LINEAGE.md` | H2.S3 `/goal` agent | Cross-vendor reviewer, human auditors | Free-form markdown. Records final surface state lineage (H2.S2 surface + any H2.S3 mapper response), any provenance drift on the promoted `surface-map.json` (H1 caveat 1 carryover — see `H2-PLAN.md` "H1 Caveat Carryover"), any mixed-run-id ledger lines (H1 caveat 3 carryover), and source-stage preserved evidence. | Human read. |
| `INCLUDED-ARTIFACTS.md` | H2.S3 `/goal` agent | Cross-vendor reviewer | Free-form markdown listing each preserved artifact, what it is, where it came from, and why it is in the packet. Same shape as H1.S3's. | Human read. |
| `CHECKPOINT-PACKET.md` | H2.S3 `/goal` agent | Cross-vendor reviewer | The reviewer-facing pack-of-pointers — names the H2 pass criterion, the evidence files to read, and what the reviewer is being asked to disposition. Same shape as H1.S3's. | Human read. |
| `CHECKPOINT-PROMPT.md` | H2.S3 `/goal` agent | Cross-vendor reviewer (via `cross-vendor-review` skill runner) | Prompt body that gets paired with `REVIEW-SPEC.md` under `.planning/reviews/<run-date>-h2-repeatability-checkpoint/`. Reviewer-launch contract is `.codex/skills/cross-vendor-review/SKILL.md`. | Cross-vendor-review skill runner consumes it. |
| `surface-map.json` | Copied from H2.S2 final state (after H2.S3 mapper response, if any) | Cross-vendor reviewer, H2.A1 / H2.A3 evidence | `schemas/surface-map.schema.json`. Must validate, citations resolve, evidence check passes. Carries claim contestation if a Skeptic challenge was accepted as alternative. | `python3 -m cbm.cli validate / verify-citations / check-evidence`. |
| `skeptic-review-surface-map.md` | Copied from H2.S2 promoted Skeptic markdown | Cross-vendor reviewer, H2.A2 evidence | `schemas/skeptic-review.schema.json`. Must validate, citations resolve. | `python3 -m cbm.cli validate / verify-citations`. |
| `source-h2s2-handoff.md` | Copied from H2.S2 `handoff.md` (per-run handoff, preserved as source-stage) | Cross-vendor reviewer, H2.A4 diff record | `schemas/handoff.schema.json`. Distinct from the H2.S3 `HANDOFF.md` — labeled as `cbm-baseline-handoff@0.1` or whatever H2.S2 produced; not promoted as the H2 pass-claim handoff. | `python3 -m cbm.cli validate / verify-citations`. |
| `evidence-ledger.jsonl` | Copied from H2.S2 final state | Cross-vendor reviewer, audit | `schemas/evidence-ledger.schema.json`. Append-only; any mixed-run-id lines documented in `LINEAGE.md`. | Read by `check-evidence`. |
| `.research/run-h11-h2s2-<n>/` subtree(s) | Copied from H2.S2 packet (every `.research/run-h11-h2s2-<n>/` subtree H2.S2 preserved) | Audit | Preserved per H1 caveat — H1.S1 publication originally dropped this. H2.S3 publication MUST preserve every subtree H2.S2 preserved (1 under the single-run shape, 2 under the interim split). | No schema; presence is the criterion. |

## H2.S3 Cross-Vendor Pass-Claim Checkpoint

```text
.planning/reviews/<run-date>-h2-repeatability-checkpoint/
  PROMPT.md
  REVIEW-SPEC.md
  CHECKPOINT.md
  DISPOSITION.md
  DISPOSITION.json
  EVIDENCE-MANIFEST.md
```

### Checkpoint artifact contracts

| Artifact | Producer | Consumer | Schema / contract | Validation command |
|---|---|---|---|---|
| `PROMPT.md` | H2.S3 `/goal` agent | Cross-vendor reviewer (non-current-model) | Reviewer prompt; pairs with `REVIEW-SPEC.md` per `cross-vendor-review` skill contract. Describes H2 pass criterion concretely, lists evidence files, names the reviewer's required outputs. Same shape as `.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/PROMPT.md`. | Human read; `cross-vendor-review` runner picks it up. |
| `REVIEW-SPEC.md` | H2.S3 `/goal` agent | `cross-vendor-review` skill runner | Per `.codex/skills/cross-vendor-review/docs/REVIEW-SPEC-CONTRACT.md`. Declares `review_type: pass_claim_checkpoint` (matches H1 precedent `.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/REVIEW-SPEC.md:2` and the contract's own decision-review example at REVIEW-SPEC-CONTRACT.md:88), declared output paths, write roots, retain-on-success flag. | `cross-vendor-review` runner preflight; `preflight.sh`. |
| `CHECKPOINT.md` | Non-current-model reviewer (writes directly via `cross-vendor-review` runner; NOT the dev agent that produced the H2.S3 packet) | `cbm-loop-status --scope pass-claim`, H2.A5 evidence | Markdown with YAML frontmatter: `status: complete`, `scope: pass-claim`, `pass_criterion: H2 minimum-useful-repeatability` (or equivalent), `reviewer_model_id: <model family NOT in cbm/loop_status_config.json's current_dev_agent_model_families = ["gpt", "openai", "codex"]>` — for H2.S3 with `--backend codex-cli`, a Claude family reviewer (e.g., `claude-opus-4-7`) is **valid** and matches the H1 precedent (`.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/DISPOSITION.json`); a `gpt-5`, `o1`, or `codex-*` reviewer would fail the gate via substring match in `model_matches_family`. The check is against the runtime-producer backend's family, not the `/goal`-orchestrator's family. `same_model_fallback: false`, `confidence: ...`, `disposition: accept|revise|park|reject`. The dev agent that produced the H2.S3 packet does NOT fill reviewer identity, confidence, or disposition. | `cbm-loop-status --scope pass-claim --work-category runtime-producer` checks via `checkpoint_for_loop_scope` (`cbm/cli.py:5430-5452`); the family check fires in `checkpoint_pass_claim_issues` (`cbm/cli.py:5795-5810`). |
| `DISPOSITION.md` | Non-current-model reviewer | Audit | Free-form markdown explaining the disposition decision. | Human read. |
| `DISPOSITION.json` | Non-current-model reviewer | Audit, machine-readable acceptance record | Structured JSON: `schema_version: 1`, `review_id: <run-date>-h2-repeatability-checkpoint`, `status: complete`, `reviewer_model_id: <model id>`, `same_model_fallback: false`, `disposition: accept|revise|park|reject`, `decided_at: <ISO 8601 UTC>`. Same shape as `.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/DISPOSITION.json`. | Parsed by `cbm/cli.py` loop-status path. |
| `EVIDENCE-MANIFEST.md` | H2.S3 `/goal` agent | Cross-vendor reviewer | Free-form markdown enumerating every input artifact the reviewer is supposed to read, with absolute paths. Same shape as H1.S3's. | Human read. |

### ADR-005 cross-model requirement

`SCOPES_REQUIRING_CROSS_MODEL = {"pass-claim", "main-merge", "broad-goal-restart"}` is a constant set declared at `cbm/cli.py:5464`. The H2.S3 checkpoint is scope `pass-claim`. **The "current dev-agent model family" the gate enforces against is the RUNTIME-PRODUCER family** — the model used by the `cbm run` backend, not the `/goal`-orchestrator. For H2.S3 with backend `codex-cli`, the runtime-producer family is sourced from `cbm/loop_status_config.json` (`current_dev_agent_model_families = ["gpt", "openai", "codex"]`); `model_matches_family` (`cbm/cli.py:5564-5566`) is a substring `in` test, so a Claude family reviewer (`claude-opus-4-7`) clears the gate, a `gpt-5` reviewer fails it, and `codex-*` IDs would also fail. The H1 precedent at `.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/DISPOSITION.json` carries `reviewer_model_id: claude-opus-4-7` with `disposition: accept` and the gate is currently green on it.

Same-model fallback is invalid for pass-claim scope per ADR-005. Two distinct mechanisms enforce the cross-family discipline: (1) the **selector** `checkpoint_for_loop_scope` (`cbm/cli.py:5430-5452`) filters candidate checkpoints by declared `scope` label only — it does not itself read the reviewer model family; (2) the **family-rejection gate** lives in `checkpoint_pass_claim_issues` (`cbm/cli.py:5795-5810`), which emits `same_model_checkpoint` when `model_matches_family()` substring-matches `reviewer_model_id` against the configured family list for a scope present in `SCOPES_REQUIRING_CROSS_MODEL`. The selector and the gate are independent: the selector enforces scope-label match so a newer non-matching checkpoint cannot shadow a valid one; the gate separately rejects current-runtime-producer-family reviewers.

A future Claude Code backend (per ADR-006 / issue #23) will require adding `"claude"`/`"anthropic"` to `current_dev_agent_model_families` and recording the decision in BUILD-LOG.md per `cbm/loop_status_config.json`'s own `_documentation` guidance. Until that happens, "reviewer ∉ {gpt, openai, codex}" is the operative rule and Claude family reviewers are the natural choice that matches H1.

## Cross-Reference

- H2 binding plan and acceptance: `H2-PLAN.md`.
- Target selection ledger: `H2-TARGET-SELECTION.md`.
- Preflight concerns to resolve before H2.S2 dispatch: `H2-PREFLIGHT.md`.
- H1 packet shapes this skeleton mirrors: `.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/`, `.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/`, `.planning/benchmarks/2026-05-07-mcp-git-h1s2c-disposition/`, `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/`, `.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/`.
- Cross-vendor review skill: `.codex/skills/cross-vendor-review/SKILL.md`; runbook `.codex/skills/cross-vendor-review/docs/CLAUDE-CODE-RUNBOOK.md`; spec contract `.codex/skills/cross-vendor-review/docs/REVIEW-SPEC-CONTRACT.md`.
