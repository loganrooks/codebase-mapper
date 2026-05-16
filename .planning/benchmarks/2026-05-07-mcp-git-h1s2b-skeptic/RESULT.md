# H1.S2b MCP Git Skeptic Benchmark

Status: passed for H1.S2b real isolated Skeptic production

## Target

- Repository: `https://github.com/modelcontextprotocol/servers`
- Subtree: `src/git`
- Pinned SHA: `4503e2d12b799448cd05f789dd40f9643a8d1a6c`
- Local checkout used: `/var/tmp/cbm-h1-mcp-servers-4503e2d/src/git`
- Run id: `run-mcp-git-h1s2b-skeptic-1`
- Surface artifact reviewed: `.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/surface-map.json`

## Command

```bash
TMPDIR=/var/tmp python3 -m cbm.cli run \
  --repo /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git \
  --goal "review H1.S1 Surface Mapper map for MCP git server surfaces" \
  --backend codex-cli \
  --allow-live-codex \
  --codex-surface-mode existing \
  --surface-artifact /Users/rookslog/Development/cbm/.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/surface-map.json \
  --codex-skeptic-mode skill \
  --codex-model gpt-5.4-mini \
  --codex-reasoning-effort high \
  --mode lightweight \
  --run-id run-mcp-git-h1s2b-skeptic-1 \
  --codex-timeout 600
```

## Evidence

- `skeptic-review/surface-map.md` validates and is produced by `skeptic@1.2`.
- `run-manifest.json` records the imported H1.S1 surface map input path and SHA-256, the `skeptic@1.2` producer, backend `codex-cli`, Skeptic skill hash, output path, output hash, and final manifest status `succeeded`.
- `producer-registry.json` records `surface_map` as `surface-mapper@1.2` and `skeptic_review` as `skeptic@1.2`, both on backend `codex-cli`.
- `handoff.md` validates.
- `surface-map.json` carries the ingested `skeptic@1.2` challenge on `auth-001`.
- The full run tree is preserved under `.research/run-mcp-git-h1s2b-skeptic-1/`, including `logs/` and `codex_outputs/`.

## Skeptic Summary

- Factual/inferential defects: none substantiated.
- Spot-checks: 5 citations sampled and reported as supporting.
- Interpretive challenge: `auth-001` centrality/scope challenge.
- Competing reading: routing authority is distributed across `pyproject.toml` and `src/mcp_server_git/__main__.py`; `src/mcp_server_git/__init__.py` is the shared command implementation rather than the sole central authority.
- Competing evidence:
  - `pyproject.toml:25-26@4503e2d12b79`
  - `src/mcp_server_git/__main__.py:1-5@4503e2d12b79`
  - `src/mcp_server_git/__init__.py:7-24@4503e2d12b79`

Manual support check: the cited `pyproject.toml` lines declare the console entrypoint, `__main__.py` imports and calls `main`, and `__init__.py` defines the callable that configures logging and calls `serve(repository)`. The challenge is specific, cited, and substantively supported; it is not generic or stub-like. A search of the Skeptic output for parent-session/prohibited-context terms found no substantive leak signal.

## Preserved Packet

```text
.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/
  RESULT.md
  skeptic-review-surface-map.md
  run-manifest.json
  producer-registry.json
  handoff.md
  surface-map.json
  codex-cli-smoke-output.json
  .research/run-mcp-git-h1s2b-skeptic-1/
    logs/
    codex_outputs/
    ...
```

## Validation Commands Run

```bash
python3 -m cbm.cli validate /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git/.research/run-mcp-git-h1s2b-skeptic-1/skeptic-review/surface-map.md --repo /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git
python3 -m cbm.cli verify-citations /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git/.research/run-mcp-git-h1s2b-skeptic-1/skeptic-review/surface-map.md --repo /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git
python3 -m cbm.cli validate /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git/.research/run-mcp-git-h1s2b-skeptic-1/run-manifest.json --repo /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git
python3 -m cbm.cli validate /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git/.research/run-mcp-git-h1s2b-skeptic-1/handoff.md --repo /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git
python3 -m cbm.cli check-evidence /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git/.research/run-mcp-git-h1s2b-skeptic-1/surface-map.json --repo /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git
```

All commands exited 0.

## Boundary

This satisfies H1.S2b only. It does not claim H1 complete, minimum-useful CBM complete, or Phase B+. H1.S2c remains the next stage for challenge ingestion and mapper response disposition.
