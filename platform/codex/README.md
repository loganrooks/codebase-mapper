# Codex Adapter

This adapter documents the current Codex-specific glue for CBM.

## Hook Boundary

The repository currently uses `.codex/hooks.json` to run:

```sh
PYTHONPATH="$(git rev-parse --show-toplevel)" python3 -m cbm hook-stop
```

The hook validates the latest `.research/<run_id>/handoff.md` when present. It does not replace artifact validation during the run; it is a final stop-gate check.

## Artifact Gate Boundary

Use `platform/codex/gate-artifact.sh <artifact-path> [repo]` for post-artifact-write hooks. The script resolves the repo root, sets `PYTHONPATH`, and runs:

```sh
python3 -m cbm gate-artifact <artifact-path> --repo <repo>
```

This single command performs schema validation, citation resolution, and claim-evidence checks.

## Subagent Boundary

Runtime subagent behavior is represented by durable skill files in `skills/*.md` and artifacts in `.research/<run_id>/`. The current CLI implementation uses deterministic commands for mapper, skeptic, tracer, planner, and approval-plan boundaries. Actual Codex subagent spawning remains platform glue and must preserve the artifact contract.

## Portability Contract

When porting away from Codex, preserve the `cbm` CLI and artifact schemas. Replace only hook syntax, subagent spawn syntax, and orchestrator entry points.
