# MCP Git Baseline

Status: completed deterministic baseline with benchmark-harness limitation
Date: 2026-05-01

## Target

- Repository: `https://github.com/modelcontextprotocol/servers`
- Pinned SHA: `4503e2d12b799448cd05f789dd40f9643a8d1a6c`
- Sparse target: `src/git`
- Local checkout used: `/tmp/cbm-benchmark-mcp-servers-4503e2d/src/git`
- CBM run ID: `run-mcp-git-baseline-2`

## Commands

```sh
git ls-remote https://github.com/modelcontextprotocol/servers.git | rg 4503e2d12b799448cd05f789dd40f9643a8d1a6c
git clone --filter=blob:none --sparse https://github.com/modelcontextprotocol/servers.git /tmp/cbm-benchmark-mcp-servers-4503e2d
git -C /tmp/cbm-benchmark-mcp-servers-4503e2d checkout 4503e2d12b799448cd05f789dd40f9643a8d1a6c
git -C /tmp/cbm-benchmark-mcp-servers-4503e2d sparse-checkout set src/git
cp -R schemas /tmp/cbm-benchmark-mcp-servers-4503e2d/src/git/schemas
python3 -m cbm.cli run --repo /tmp/cbm-benchmark-mcp-servers-4503e2d/src/git --goal "understand MCP git server surfaces" --backend deterministic --mode standard --run-id run-mcp-git-baseline-2
python3 -m cbm.cli validate /tmp/cbm-benchmark-mcp-servers-4503e2d/src/git/.research/run-mcp-git-baseline-2/handoff.md --repo /tmp/cbm-benchmark-mcp-servers-4503e2d/src/git
python3 -m cbm.cli validate /tmp/cbm-benchmark-mcp-servers-4503e2d/src/git/.research/run-mcp-git-baseline-2/run-manifest.json --repo /tmp/cbm-benchmark-mcp-servers-4503e2d/src/git
```

## Results

- `cbm run` exit: 0
- `handoff.md` validation: passed
- `run-manifest.json` validation: passed
- Source files in scope: 31
- Directly examined files reported by surface map: 0
- Surface authorities: 2
- Surface edges: 17
- Dependency partitions: 16 certain, 0 suspected, 0 advisory, 1 unknown
- Verification gates: 1
- Synthesis open challenges: 0
- Handoff citation resolution: 20 resolved, 0 unresolved
- Handoff ledger consistency: append-only verified, 22 entries, 0 missing citations
- Run manifest status: succeeded

Copied benchmark artifacts:

- `artifacts/codebase-map.json`
- `artifacts/surface-map.json`
- `artifacts/dependency-graph.json`
- `artifacts/verification-map.json`
- `artifacts/synthesis-index.json`
- `artifacts/run-manifest.json`
- `artifacts/handoff.md`

## Limitation

This is not a quality benchmark for nuanced codebase understanding. It is a deterministic baseline smoke on an external pinned repo.

The run required copying CBM schemas into the target checkout because the current CLI loads schemas from `<target-repo>/schemas`. Those copied schemas were included in the file scope. Before serious external benchmark comparisons, CBM needs a schema-source option or package-schema fallback so benchmark target scope is not polluted by CBM's own validation schemas.

## Regression Found And Fixed

The first attempt failed at handoff with missing ledger citations for `project-type.json` evidence. The fix records project-type citations in the evidence ledger during `cbm init` and adds a regression test.
