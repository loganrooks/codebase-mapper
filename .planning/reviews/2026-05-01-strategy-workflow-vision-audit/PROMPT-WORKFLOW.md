# Prompt: Development Workflow and Governance Review

You are an independent process/governance reviewer for the CBM project.

Read `SHARED-CONTEXT.md`, then inspect the repo as needed. Do not assume the current planning reset is adequate. Diagnose the workflow failures and propose a better operating system for the project.

## Task

Review the project's development workflow, planning artifacts, verification practices, and auditability.

Address:

- How should the project be governed so a mostly automated Codex `/goal` loop can move it toward `VISION.md` without silent drift?
- What should `AGENTS.md` require of future agents before, during, and after each slice?
- What should live in `docs/roadmap.md` versus `.planning/CURRENT-PLAN.md` versus `.planning/STATE.md` versus `BUILD-LOG.md`?
- How detailed should `CURRENT-PLAN.md` be?
- How far into the future should it project?
- What protocol should run when the current plan is complete?
- What protocol should run when the current plan changes or becomes stale?
- What protocol should run when the automated loop drifts, discovers a bad assumption, hits repeated failures, or finds that the current plan is no longer fit for purpose?
- What escalation thresholds should force pause/review rather than continued autonomous implementation?
- Should old plans be archived? If yes, where and with what metadata?
- How should phase completion be verified?
- What evidence should be required before claiming a phase or slice is done?
- Should reviewer/checkpoint agents be launched at phase boundaries or high-risk changes?
- How should their outputs be stored and dispositioned?
- How can docs indicate freshness, authority, and supersession clearly?
- What friction signals in this repo show workflow breakdown?
- What governance docs, templates, checklists, or review loops should exist so autonomous work produces the best possible codebase mapper?
- How should agents recover elegantly from mistakes while preserving traceability and avoiding defensive patching?

## Output

Write to `OUTPUT-WORKFLOW.md`.

Use this structure:

- Executive verdict
- Observed workflow failures or risks
- Recommended planning artifact model
- Current-plan lifecycle protocol
- Drift/failure recovery protocol
- Phase/slice verification protocol
- Review/checkpoint protocol
- Recommended `AGENTS.md` operating rules
- Documentation freshness protocol
- Concrete next steps
