# MCP Git Codex CLI Smoke Result

Status: passed with limitations
Date: 2026-05-02

## Target

- Repository: `https://github.com/modelcontextprotocol/servers`
- Pinned SHA: `4503e2d12b799448cd05f789dd40f9643a8d1a6c`
- Target subtree: `src/git`
- Local checkout used for smoke: `/tmp/cbm-live-mcp-servers-4503e2d/src/git`
- Run id: `run-mcp-git-codex-smoke-4`

## Command

```bash
python3 -m cbm.cli run \
  --repo /tmp/cbm-live-mcp-servers-4503e2d/src/git \
  --goal "understand MCP git server surfaces" \
  --backend codex-cli \
  --allow-live-codex \
  --codex-model gpt-5.4-mini \
  --codex-reasoning-effort medium \
  --mode lightweight \
  --run-id run-mcp-git-codex-smoke-4
```

## Outcome

The live run succeeded. It produced:

- `run-manifest.json` with `status: succeeded`;
- `skeptic-review/surface-map.md` with `produced_by: codex-cli-smoke@0.1`;
- `handoff.md` with schema validation passing for 6 artifacts;
- handoff citation gate summary with `unresolved_count: 0`;
- handoff ledger consistency with `missing_citation_count: 0`;
- no copied `schemas/` directory in the target checkout.

Durable evidence copied into this directory:

- `run-manifest.json`
- `producer-registry.json`
- `skeptic-review-surface-map.md`
- `handoff.md`

## Failed Attempts Preserved As Evidence

- `run-mcp-git-codex-smoke-1`: failed because `codex exec` does not accept `-a never`. Fix: pass approval policy through `-c approval_policy="never"`.
- `run-mcp-git-codex-smoke-2`: live Codex step succeeded, but handoff failed because the smoke review citation was not added to the evidence ledger. Fix: Codex smoke producer appends citation ledger entries for its review body.
- `run-mcp-git-codex-smoke-3`: live Codex step succeeded, but handoff failed because a Markdown-backticked citation was parsed with a leading backtick in the path. Fix: citation regex excludes backticks from path characters.

## Interpretation

This is the first live Codex CLI-produced CBM artifact on the pinned external benchmark. It proves subprocess dispatch, cheap-model selection, output-schema use, parent-side validation, ledger integration, and handoff preservation for one smoke artifact.

This is not a Phase B+ pass claim and not the `VISION.md` minimum useful CBM floor. The surface map is still deterministic baseline output, not a real Surface Mapper artifact, and the live Codex artifact is a bounded smoke review rather than a full isolated Skeptic review.
