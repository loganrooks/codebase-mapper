# MCP Git Skill-Loaded Skeptic Result

Status: passed as minimum-useful CBM evidence
Date: 2026-05-02

## Target

- Repository: `https://github.com/modelcontextprotocol/servers`
- Pinned SHA: `4503e2d12b799448cd05f789dd40f9643a8d1a6c`
- Target subtree: `src/git`
- Local checkout: `/tmp/cbm-live-mcp-servers-4503e2d/src/git`
- Successful run id: `run-mcp-git-codex-skeptic-skill-4`

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
  --run-id run-mcp-git-codex-skeptic-skill-4
```

## Outcome

The run succeeded. It produced:

- `run-manifest.json` with `status: succeeded`;
- `producer-registry.json` with `skeptic_review` produced by `skeptic@1.2`;
- manifest skill metadata for `skills/skeptic.md` with SHA-256 `1d676f7d1a23660b00b150dcf4cb9441e4a00e6d02c46fe126999f1bc570de39`;
- `skeptic-review/surface-map.md` with `produced_by: skeptic@1.2`;
- `handoff.md` with schema validation passing for 6 artifacts, citation resolution reporting `unresolved_count: 0`, `skeptic_review.challenges_logged: 1`, and `contestation_summary.open_challenges: 1`.

The skill-loaded Skeptic reported one structurally ingested interpretive challenge:

- `CHL-001: classification / reframing` against `auth-001`.
- Competing reading: `pyproject.toml` is better understood as a broader packaging/configuration authority surface than a narrow build surface.
- Competing evidence: `pyproject.toml:25-30@4503e2d12b79` and `pyproject.toml:32-39@4503e2d12b79`.

## Failed Attempt Preserved As Context

- `run-mcp-git-codex-skeptic-skill-1` reached the skill-loaded Skeptic step but failed under disk pressure. The parent process later hit `OSError: [Errno 28] No space left on device` while updating `run-manifest.json`. This was treated as an infrastructure failure, not a model-quality result.
- `run-mcp-git-codex-skeptic-skill-2` passed as skill-loaded dispatch evidence but did not meet the minimum-useful floor because its challenge was not structurally integrated and no interpretive challenge was produced.
- `run-mcp-git-codex-skeptic-skill-3` produced an interpretive challenge but failed parent-side ingestion because `competing_evidence` included artifact JSON pointers and a source citation collapsed into one invalid citation string. This drove the citation-pattern and prompt tightening before `run-mcp-git-codex-skeptic-skill-4`.

## Interpretation

This proves more than the smoke run:

- runtime skill loading from disk works;
- the manifest records the loaded skill hash;
- the Codex CLI subprocess can produce a schema-valid Skeptic review under `skeptic@1.2`;
- parent-side CBM can ingest structured runtime Skeptic challenges into the reviewed artifact and evidence ledger;
- handoff contestation summaries reflect the runtime challenge.

This meets the narrow `VISION.md` minimum-useful CBM floor:

- one runtime-agent-produced run on a pinned external codebase;
- at least one non-trivial interpretive challenge;
- challenge grounded in source citations that resolve at the pinned SHA;
- parent-side validation and handoff gates passed.

## Next Gap

The next implementation slice should not claim Phase B+ yet. The next gap is quality and breadth:

- repeat the minimum-useful run on at least one additional small external target;
- add stricter runtime-output failure-mode tests for malformed challenge objects;
- decide whether this closes the recovery intervention and opens the next roadmap/maturity-band work.
