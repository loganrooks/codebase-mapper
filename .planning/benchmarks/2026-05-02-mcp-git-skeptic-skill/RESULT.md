# MCP Git Skill-Loaded Skeptic Result

Status: passed as skill-loaded dispatch evidence; minimum-useful CBM not met
Date: 2026-05-02

## Target

- Repository: `https://github.com/modelcontextprotocol/servers`
- Pinned SHA: `4503e2d12b799448cd05f789dd40f9643a8d1a6c`
- Target subtree: `src/git`
- Local checkout: `/tmp/cbm-live-mcp-servers-4503e2d/src/git`
- Successful run id: `run-mcp-git-codex-skeptic-skill-2`

## Command

```bash
TMPDIR=/var/tmp python3 -m cbm.cli run \
  --repo /tmp/cbm-live-mcp-servers-4503e2d/src/git \
  --goal "understand MCP git server surfaces" \
  --backend codex-cli \
  --allow-live-codex \
  --codex-skeptic-mode skill \
  --codex-model gpt-5.4-mini \
  --codex-reasoning-effort medium \
  --mode lightweight \
  --run-id run-mcp-git-codex-skeptic-skill-2
```

## Outcome

The run succeeded. It produced:

- `run-manifest.json` with `status: succeeded`;
- `producer-registry.json` with `skeptic_review` produced by `skeptic@1.2`;
- manifest skill metadata for `skills/skeptic.md` with SHA-256 `1d676f7d1a23660b00b150dcf4cb9441e4a00e6d02c46fe126999f1bc570de39`;
- `skeptic-review/surface-map.md` with `produced_by: skeptic@1.2`;
- `handoff.md` with schema validation passing for 6 artifacts and citation resolution reporting `unresolved_count: 0`.

The skill-loaded Skeptic reported one substantive finding:

- `CH-001: interpretive_claim_without_direct_examination` against `/authorities/0`.

## Failed Attempt Preserved As Context

- `run-mcp-git-codex-skeptic-skill-1` reached the skill-loaded Skeptic step but failed under disk pressure. The parent process later hit `OSError: [Errno 28] No space left on device` while updating `run-manifest.json`. This was treated as an infrastructure failure, not a model-quality result.

## Interpretation

This proves more than the smoke run:

- runtime skill loading from disk works;
- the manifest records the loaded skill hash;
- the Codex CLI subprocess can produce a schema-valid Skeptic review under `skeptic@1.2`;
- the review contains a concrete, citation-grounded defect finding rather than an empty smoke acknowledgment.

It does not yet meet the `VISION.md` minimum-useful CBM floor:

- the model did not produce a non-trivial interpretive challenge;
- the reported `challenge_ids` are not yet integrated into the evidence ledger or contestation summary;
- `handoff.md` reports `skeptic_review.challenges_logged: 0` and `open_challenges: 0` even though the review body names `CH-001`.

## Next Gap

The next implementation slice should make runtime Skeptic output structurally consumable:

- require structured challenge objects in the Codex output schema;
- append corresponding challenge entries to `evidence-ledger.jsonl`;
- update challenged claim status or contestation summaries when a runtime Skeptic challenge is accepted by the parent-side parser;
- add regressions proving `handoff.md` counts runtime Skeptic challenges.
