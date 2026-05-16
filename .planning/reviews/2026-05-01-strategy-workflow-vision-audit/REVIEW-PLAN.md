# Review Plan: Strategy, Workflow, and Vision Audit

Status: ready for reviewer launch
Last updated: 2026-05-01
Supersedes: `.planning/reviews/2026-05-01-opus-architecture-audit/`
Superseded by: none

## Purpose

Run independent reviews of the CBM project state without anchoring reviewers to the current agent's latest diagnosis.

The review should answer three separable questions:

1. What is the right product/execution architecture for CBM?
2. What development workflow and planning protocol would keep this project auditable and on track?
3. Is `VISION.md` itself clear, useful, and strong enough to guide implementation, or should it be improved?

## Review Tracks

### Track A: Architecture and Product Shape

Output: `OUTPUT-ARCHITECTURE.md`

Focus:

- actual product boundary;
- CLI, artifact, runtime-agent, and platform-adapter relationships;
- plausible execution models;
- role of deterministic artifacts;
- role of hooks, if any;
- deployment/interface story for another project using CBM.

### Track B: Development Workflow and Governance

Output: `OUTPUT-WORKFLOW.md`

Focus:

- relationship between roadmap, current plan, state, build log, and review packets;
- how to know when a plan is stale, complete, superseded, or archived;
- phase gates and verification evidence;
- use of reviewer/checkpoint agents;
- practices to prevent future drift or unreviewed phase jumping.

### Track C: Vision Quality

Output: `OUTPUT-VISION.md`

Focus:

- whether `VISION.md` is clear, operationally useful, and well written;
- whether ambiguity in the vision may have contributed to implementation drift;
- whether the vision creates good development pressure or vague aspiration;
- how the vision could be improved to better shape code quality, roadmap quality, and verification discipline.

## Independence Rules

- Each reviewer should read `SHARED-CONTEXT.md` and only its own prompt.
- Reviewers should not read other reviewers' outputs before writing their own.
- Prompts must not presume that hooks are the problem, that Codex CLI subprocesses are the solution, or that `VISION.md` is either good or bad.
- Reviewers should critique the framing of their own prompt if it seems incomplete or biased.

## After Reviews

1. Create `SYNTHESIS.md` comparing agreements, conflicts, and missing questions across outputs.
2. Create or update `DISPOSITION.md` with accepted, modified, deferred, and rejected recommendations.
3. Update `.planning/STATE.md` and `.planning/CURRENT-PLAN.md`.
4. Only then update `docs/roadmap.md`, `docs/architecture.md`, `docs/contracts.md`, or implementation code.

## Launch Recommendation

Launch at least Track A and Track B before changing architecture docs or implementation.

Track C can run immediately after, or after A/B if the first two reviews identify vision ambiguity as a significant source of drift.
