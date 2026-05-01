# Current Plan

Status: active
Last updated: 2026-05-01
Supersedes: direct use of `docs/roadmap.md` as current execution plan
Superseded by: none

## Objective

Continue building toward `VISION.md`, but pause feature work long enough to correct the execution architecture and planning workflow.

The immediate goal is not another gate hardening slice. The immediate goal is to make the project auditable, reviewable, and clear about the boundary between:

- deterministic CBM kernel;
- runtime agent producers;
- validation gates;
- optional platform hooks/adapters.

## Current Understanding

The implementation has drifted beyond Phase A in useful but confusing ways. Many later-phase deterministic artifacts and gates exist, but the actual nuanced codebase-reading layer is still missing.

The main correction:

- `cbm run` is currently a deterministic pipeline runner, not a true agent orchestrator.
- Codex hooks should not be treated as the general artifact guarantee.
- The core product guarantee should come from explicit CLI validation and run-level validation.
- Hooks may be useful only as optional Codex adapter glue, especially for CBM-launched Codex agent subprocesses.

## Candidate Architecture Direction

This is a candidate direction, not an accepted conclusion. It must be reviewed before further implementation.

1. Keep the deterministic kernel.
   - It provides file inventory, static edges, schemas, citations, ledgers, gates, freshness, reuse, and baseline artifacts.

2. Add an explicit runtime agent backend.
   - Preferred first backend: Codex CLI subprocesses launched by CBM.
   - Candidate command family: `codex exec --cd <target> --profile <cbm-profile> --output-schema <schema> ...`.
   - Parent CBM process controls run directory, prompt/spec files, output paths, and validation.

3. Make validation explicit and backend-independent.
   - Add or center a full-run validation command, likely `cbm validate-run --repo ... --run-id ...`.
   - `cbm run` should call validation directly after each stage.
   - Hooks should call the same validators, not contain unique policy.

4. Demote hooks in the architecture.
   - No global/user-level CBM hooks.
   - Repo-local hooks only for explicit dogfooding or target repo opt-in.
   - Per-agent hooks only if CBM intentionally launches Codex agent sessions and can control their config/profile.

5. Add a real benchmark target.
   - The existing fixture is too small for nuanced mapping.
   - Add or document a pinned small real-world repo fixture, preferably an MCP server, before claiming mapping adequacy.

## Next Concrete Actions

1. Create `.planning/` state/plan surface. Status: completed in `5a2ceb5`.
2. Mark the first Opus review packet as aborted because its prompt overdetermined the diagnosis. Status: in progress.
3. Create a neutral multi-track review packet for architecture, workflow/governance, and vision quality. Status: in progress.
4. Launch Track A and Track B as independent reviews. Status: pending.
5. Launch Track C either immediately after A/B or after A/B if they identify vision ambiguity as a significant cause. Status: pending.
6. Synthesize and disposition review outputs. Status: pending.
7. Update `docs/roadmap.md`, `docs/architecture.md`, and `docs/contracts.md` only after review disposition or explicit user direction. Status: pending.
8. Implement the next code slice only after the architecture/workflow correction is accepted or revised. Status: pending.

## Expected Verification

For this planning/workflow slice:

- `git diff --check -- AGENTS.md BUILD-LOG.md .planning`
- optional markdown inspection by external audit

For the next code slice:

- focused regression test for the behavior;
- `pytest -q`;
- generated artifact validation if artifact shape changes;
- update `BUILD-LOG.md`, `.planning/STATE.md`, and this plan if status or direction changes.

## Open Questions for Audit

- Should CBM launch Codex CLI subprocesses directly, or should an outer agent orchestrate runtime subagents?
- Can Codex CLI config/profile controls support per-role agent sessions cleanly enough without global hooks?
- Are hooks worth keeping in this repo as dogfood, or should live `.codex/` be removed in favor of template-only adapters?
- Is `docs/roadmap.md` salvageable as a phase roadmap, or should it be rewritten after the architecture correction?
- Which artifact should be the source of truth for deployment shape: `docs/architecture.md`, `docs/contracts.md`, or a new deployment document?
- What minimum benchmark repo proves CBM is more than a schema/gate demo?
- What protocol governs `CURRENT-PLAN.md` completion, stale-state detection, supersession, and archival?
- Should phase/slice completion require independent reviewer/checkpoint agents?
- Is `VISION.md` itself clear and operational enough, or should it be revised to better guide implementation and verification?
- What should the automated `/goal` loop do when it drifts, hits repeated failures, discovers the plan is wrong, or encounters ambiguous architecture choices?

## Non-Goals Right Now

- Do not add more deterministic feature surface before resolving the runtime agent plan.
- Do not claim `VISION.md` maturity.
- Do not treat smoke `.research/` runs against this repo as proof of nuanced mapping.
- Do not install CBM hooks globally.
