---
Status: accepted
Date: 2026-05-02
Context: Pre-recovery drift treated hooks as if they were the deployment and correctness model.
Decision: Hooks are optional adapter glue. Correctness lives in CBM CLI validation and run-level gates.
Consequences: Do not install global/user-level hooks for CBM behavior. Hook configuration, when used, must be explicit, repo-local, or created for CBM-launched agent sessions with a documented purpose.
Supersedes: none
Superseded by: none
---

# ADR-002: Hooks Are Adapter Glue

Hooks may invoke validators or help integrate with a host agent session, but they are not the source of truth. A terminal user running `cbm run` must get the same correctness guarantees from CBM commands and artifacts without ambient Codex or Claude hooks.

Portability belongs in explicit platform adapters and validation commands, not in user-level hook configuration.
