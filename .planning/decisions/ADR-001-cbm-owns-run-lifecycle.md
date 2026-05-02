---
Status: accepted
Date: 2026-05-02
Context: RUNTIME-CONSTITUTION.md defines runtime-agent discipline, and the recovery reset accepted that CBM itself must own run lifecycle.
Decision: CBM owns the run lifecycle through a producer registry.
Consequences: External harnesses may dispatch producers, but they must not become the lifecycle owner. This precludes adopting GSD-2 or any harness that owns CBM run state, orchestration, or validation.
Supersedes: none
Superseded by: none
---

# ADR-001: CBM Owns Run Lifecycle

CBM is the product being built, not only a wrapper around another agent workflow. Runtime producers can be deterministic, external-agent, or CLI-launched backends, but CBM owns the run directory, producer registry, run manifest, artifact validation, and handoff gates.

This keeps the runtime-agent constitution and evidence ledger under CBM control. It also avoids two competing lifecycle owners.
