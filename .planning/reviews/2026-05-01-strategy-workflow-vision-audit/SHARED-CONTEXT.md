# Shared Context for Reviewers

Status: active
Last updated: 2026-05-01

## Project

CBM is intended to become an epistemic instrument for mapping unfamiliar codebases. Its stated destination is in `VISION.md`; runtime-agent discipline is in `RUNTIME-CONSTITUTION.md`.

The project has a deterministic Python CLI implementation, schemas, validation gates, smoke artifacts, platform adapter notes, and a long `BUILD-LOG.md`. It also has planning concerns: implementation moved across roadmap phases opportunistically, and some live docs may no longer match implementation reality.

The user wants to operate the project through a mostly automated Codex `/goal` loop that steadily moves the repository closer to the ideal vision. That means the development workflow itself is part of the product problem: `AGENTS.md`, `.planning/`, roadmap/state/plan protocols, review gates, and verification expectations must make autonomous progress safer, more auditable, and more likely to produce a robust codebase mapper rather than a pile of plausible-looking artifacts.

## Important Caution

Do not assume the current agent's diagnosis is correct.

Candidate interpretations include, but are not limited to:

- the implementation is mostly on track and only planning docs lag;
- deterministic kernel work was useful but overextended before runtime-agent design;
- hooks were useful dogfooding but over-framed as architecture;
- hooks are a legitimate part of the eventual runtime if CBM launches Codex agents;
- the roadmap was under-specified for the current build style;
- `VISION.md` itself may be unclear, overbroad, or insufficiently operational;
- the main issue may be workflow/governance rather than product architecture.
- the main issue may be that the agent operating instructions and planning protocol are not strong enough for long autonomous `/goal` execution.

Your job is to diagnose, not to ratify any one of these.

## Suggested Files

Read enough to ground your review. Prioritize:

- `VISION.md`
- `RUNTIME-CONSTITUTION.md`
- `AGENTS.md`
- `.planning/STATE.md`
- `.planning/CURRENT-PLAN.md`
- `docs/roadmap.md`
- `docs/architecture.md`
- `docs/contracts.md`
- `BUILD-LOG.md`
- `pyproject.toml`
- `cbm/cli.py`
- `tests/test_cli.py`
- `platform/PORTABILITY.md`
- `platform/codex/`
- `platform/claude-code/README.md`

You may inspect git history and `.research/` smoke artifacts if useful.

## Current Known Facts

- Recent committed checkpoint: `5a2ceb5 docs: add live planning and review surface`.
- Recent implementation checkpoints include `504fbba`, `f08722e`, `b480b0b`, `108ab3a`, and `7963479`.
- Last known full test result before the planning reset was `pytest -q`: `51 passed, 2 warnings`.
- `.planning/STATE.md` says the project is in a mixed kernel build beyond Phase A, before a settled runtime-agent architecture.
- The previous review packet at `.planning/reviews/2026-05-01-opus-architecture-audit/` was aborted because its prompt was too leading.

## Output Norms

- Be specific and cite files/lines or concrete repo evidence where possible.
- Separate observed facts from interpretations.
- Identify alternative interpretations when evidence is ambiguous.
- Prefer actionable recommendations with verification implications.
