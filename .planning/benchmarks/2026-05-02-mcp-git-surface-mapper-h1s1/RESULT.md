# H1.S1 MCP Git Surface Mapper Benchmark

Status: passed

## Target

- Repository: `https://github.com/modelcontextprotocol/servers`
- Subtree: `src/git`
- Pinned SHA: `4503e2d12b799448cd05f789dd40f9643a8d1a6c`
- Local checkout used: `/var/tmp/cbm-h1-mcp-servers-4503e2d/src/git`
- Run id: `run-mcp-git-surface-mapper-h1s1-6`

## Command

```bash
TMPDIR=/var/tmp python3 -m cbm.cli run \
  --repo /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git \
  --goal "produce real Surface Mapper map for MCP git server surfaces" \
  --backend codex-cli \
  --allow-live-codex \
  --codex-surface-mode skill \
  --codex-skeptic-mode none \
  --codex-model gpt-5.4-mini \
  --codex-reasoning-effort medium \
  --mode lightweight \
  --run-id run-mcp-git-surface-mapper-h1s1-6 \
  --codex-timeout 600
```

## Evidence

- `surface-map.json` validates and is produced by `surface-mapper@1.2`.
- `run-manifest.json` records `codex-cli-skill-surface-map` with backend `codex-cli`, producer `surface-mapper@1.2`, and runtime skill `surface-mapping`.
- `producer-registry.json` records `surface_map` as `surface-mapper@1.2` on backend `codex-cli`.
- `handoff.md` was repaired during H1.S2a to describe the promoted runtime Surface Mapper output honestly, derive coverage from `surface-map.json`, and avoid counting the dev-fixture Skeptic fallback as real review.
- `verify-citations surface-map.json` resolved 25 source citations at `4503e2d12b79`.
- `check-evidence surface-map.json` passed.

## Surface Summary

- Coverage: 12 files in scope, 7 directly examined, 12 inspected via extractor, 0 unread.
- Claim registers: factual, inferential, interpretive.
- Artifact size: 8 authorities, 7 edges.
- Unknown edges present: at least one edge has `kind: unknown`; the checked-in map's current id is `edge-unknown-001`, but H1.S2a acceptance must not depend on that literal id.

## H1.S2a Evidence Bundle Repair Note

The original benchmark publication copied selected root artifacts but did not preserve the full `.research/run-mcp-git-surface-mapper-h1s1-6/` tree, including `logs/` and `codex_outputs/`. That limits retrospective auditability for files that were not copied. Future benchmark publication for runtime producers must preserve the run tree, including `logs/` and `codex_outputs/`, or avoid references to non-preserved `.research/` files.

The repaired convenience `handoff.md` therefore references only files present in this benchmark packet and omits the dev-fixture Skeptic fallback from promoted inputs/artifacts. H1.S1 remains narrowly accepted as Surface Mapper evidence only; H1.S2 still requires a real isolated Skeptic run.

## Validation Commands Run

```bash
TMPDIR=/var/tmp python3 -m cbm.cli validate /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git/.research/run-mcp-git-surface-mapper-h1s1-6/surface-map.json --repo /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git
TMPDIR=/var/tmp python3 -m cbm.cli verify-citations /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git/.research/run-mcp-git-surface-mapper-h1s1-6/surface-map.json --repo /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git
TMPDIR=/var/tmp python3 -m cbm.cli check-evidence /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git/.research/run-mcp-git-surface-mapper-h1s1-6/surface-map.json --repo /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git
TMPDIR=/var/tmp python3 -m cbm.cli validate /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git/.research/run-mcp-git-surface-mapper-h1s1-6/run-manifest.json --repo /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git
TMPDIR=/var/tmp python3 -m cbm.cli validate /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git/.research/run-mcp-git-surface-mapper-h1s1-6/handoff.md --repo /var/tmp/cbm-h1-mcp-servers-4503e2d/src/git
```

All commands exited 0.

## Boundary

This satisfies H1.S1 only. It deliberately skipped a real Skeptic pass with `--codex-skeptic-mode none`; `skeptic-review/surface-map.md` in the live run remains a dev-fixture review produced by handoff fallback behavior. H1.S2 remains pending.
