# Claude Code Adapter

This adapter records the CBM port boundary for Claude Code.

## Status

The kernel, schemas, skills, and CLI commands are platform-neutral and do not change for Claude Code. The current repository does not claim a verified Claude Code hook or subagent syntax. That syntax belongs in this directory once verified against Claude Code's current platform documentation.

## Required Adapter Semantics

A Claude Code adapter must provide equivalents for:

- stop/finalization hook that runs `python3 -m cbm hook-stop`
- post-artifact-write hook that runs `python3 -m cbm gate-artifact <artifact-path> --repo <repo>`
- subagent definitions that load the runtime skills in `skills/*.md`
- orchestrator entry that calls `python3 -m cbm run`
- environment setup so `python3 -m cbm ...` imports the local package

## Portability Deltas From Codex

- Hook syntax is platform-specific.
- Subagent definition/spawn syntax is platform-specific.
- Any permission or approval UI is platform-specific.
- Artifact schemas, skills, CLI behavior, and citation format are unchanged.

Before marking this adapter production-ready, run the checklist in `platform/PORTABILITY.md` and record the exact Claude Code hook/subagent syntax used.
