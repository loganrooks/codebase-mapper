---
Status: accepted
Date: 2026-05-02
Context: Recovery considered GSDR, GSD-2, hand-rolled outer orchestration, and CBM-owned producer dispatch.
Decision: Use a producer registry under CBM run lifecycle instead of an outer orchestrator owning the work.
Consequences: Each artifact type declares its producer backend, producer identity, execution contract, and validation chain. Runtime producers remain replaceable without surrendering CBM's run manifest, evidence ledger, or handoff gates.
Supersedes: none
Superseded by: none
---

# ADR-003: Producer Registry Over Outer Orchestrator

The reversible default is a CBM-owned producer registry. The registry lets the deterministic baseline, Codex CLI backend, future Claude Code backend, and external handoff producers coexist behind the same parent-side validation.

This avoids binding the project to an outer workflow engine before CBM has proven its own minimum useful runtime-agent artifact.
