---
Status: accepted
Date: 2026-05-02
Context: The false-provenance recovery slice corrected deterministic artifacts that looked like runtime-agent output.
Decision: Deterministic baseline artifacts must be labeled as `cbm-baseline-*`; dev fixtures as `dev-fixture-*`; runtime-agent artifacts as role/version producer ids such as `skeptic@1.2`.
Consequences: Deterministic artifacts can satisfy schema, citation, and gate checks, but they do not count as nuanced runtime-agent readings or Phase B+ evidence.
Supersedes: none
Superseded by: none
---

# ADR-004: Deterministic Baseline Is Not Runtime Evidence

The deterministic kernel is valuable infrastructure, but it is not the hermeneutic runtime-agent layer described in `VISION.md` and `RUNTIME-CONSTITUTION.md`.

Producer identity must make that boundary visible in artifacts, manifests, benchmark summaries, and handoffs.
