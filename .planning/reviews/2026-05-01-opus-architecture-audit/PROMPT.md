# Prompt: Opus Architecture Audit

Status: aborted - biased framing
Superseded by: `.planning/reviews/2026-05-01-strategy-workflow-vision-audit/`

Do not run this prompt. It over-specifies the current agent's suspected diagnosis and is preserved only as an audit trace of the aborted review attempt.

Original prompt follows.

---

You are reviewing the CBM repository as an external architecture auditor.

Be adversarial and specific. Do not assume the current implementation is on track just because it has tests or a long build log. Identify design drift, bad planning decisions, misleading documentation, and weak verification.

## Context

CBM is intended to become an epistemic instrument for mapping unfamiliar codebases. The mature system should produce evidence-bound artifacts, preserve contestation, avoid false understanding, and eventually use runtime agents for nuanced interpretive work.

The current implementation appears to have:

- a deterministic CLI/kernel with schemas, citations, ledgers, maps, cards, gates, refresh/consult pieces, and smoke artifacts;
- live Codex hook dogfooding in the implementation repo;
- many later-phase deterministic pieces implemented before the runtime agent architecture is settled;
- no true runtime Surface Mapper/Skeptic/Synthesizer/Planner orchestration yet.

The project now needs a hard architecture review before more implementation.

## Files to Read First

1. `VISION.md`
2. `RUNTIME-CONSTITUTION.md`
3. `.planning/STATE.md`
4. `.planning/CURRENT-PLAN.md`
5. `.planning/reviews/2026-05-01-opus-architecture-audit/REVIEW-SPEC.md`
6. `AGENTS.md`
7. `docs/roadmap.md`
8. `docs/architecture.md`
9. `docs/contracts.md`
10. `BUILD-LOG.md`

Then inspect:

- `pyproject.toml`
- `cbm/cli.py`
- `tests/test_cli.py`
- `platform/PORTABILITY.md`
- `platform/codex/`
- `platform/claude-code/README.md`

## Review Tasks

Answer the questions in `REVIEW-SPEC.md`.

Pay special attention to:

- whether the current hook work is architecturally justified;
- whether hooks should be kept only for CBM-launched Codex agents;
- whether `cbm run` should be renamed/framed as a deterministic pipeline until runtime agents exist;
- whether a Codex CLI backend is the right first runtime agent mechanism;
- whether `.planning/STATE.md` and `.planning/CURRENT-PLAN.md` are sufficient to recover auditability;
- whether `docs/roadmap.md` needs rewriting or demotion;
- whether existing deterministic work should be preserved, refactored, or reverted;
- what benchmark repository should be used before claiming mapping adequacy.

## Output

Write your review to:

`.planning/reviews/2026-05-01-opus-architecture-audit/OUTPUT.md`

Use the structure requested in `REVIEW-SPEC.md`.

Do not edit source files other than `OUTPUT.md`.
