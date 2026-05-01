# Platform Portability

CBM's kernel is platform-neutral. The following surfaces must remain unchanged across orchestration platforms:

- `cbm` CLI commands and console scripts
- `schemas/*.schema.json`
- `skills/*.md`
- artifact directory layout under `.research/<run_id>/`
- citation format: `path:lines@sha`
- validation, citation-resolution, freshness, and ledger checks

Platform adapters own only:

- hook configuration syntax
- subagent definition and spawn syntax
- orchestrator entry command
- environment variable setup required to import the local `cbm` package

## Verification Checklist

Run these checks after changing a platform adapter:

```sh
pytest -q
python3 -m cbm --help
python3 -m cbm run --repo <fixture-or-repo> --goal "understand this repo" --run-id <id>
python3 -m cbm gate-artifact <repo>/.research/<id>/surface-map.json --repo <repo>
python3 -m cbm validate <repo>/.research/<id>/handoff.md --repo <repo>
python3 -m cbm verify-citations <repo>/.research/<id>/handoff.md --repo <repo>
```

Passing adapter checks do not prove CBM's reading quality. They prove only that the same kernel, schemas, skills, and CLI contracts are reachable from the target platform.
