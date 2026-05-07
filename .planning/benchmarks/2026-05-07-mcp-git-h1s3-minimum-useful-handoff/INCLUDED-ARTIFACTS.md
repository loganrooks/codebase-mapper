# Included Artifacts

Status: prepared
Date: 2026-05-07

## Packet Root

```text
.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/
  RESULT.md
  HANDOFF.md
  VERIFY.md
  LINEAGE.md
  CHECKPOINT-PACKET.md
  CHECKPOINT-PROMPT.md
  INCLUDED-ARTIFACTS.md
  surface-map.json
  skeptic-review-surface-map.md
  source-h1s2c-handoff.md
  evidence-ledger.jsonl
  .research/run-mcp-git-surface-mapper-h1s1-6/
  .research/run-mcp-git-h1s2b-skeptic-1/
  .research/run-mcp-git-h1s2c-disposition-1/
```

## Preservation Strategy

No new runtime producer command naturally creates an H1.S3 `.research/<run_id>` tree because H1.S3 is handoff/checkpoint preparation over already-produced H1.S1 and H1.S2 artifacts.

The packet therefore preserves:

- the exact final H1.S2c surface map promoted for checkpoint review;
- the exact H1.S2b rendered Skeptic review promoted for checkpoint review;
- the exact H1.S2c handoff and evidence ledger;
- the available full source run trees for H1.S1, H1.S2b, and H1.S2c.

`codex_outputs/` and `logs/` directories inside the preserved run trees are source-stage audit evidence. In particular, the H1.S2b tree contains the real isolated Skeptic model output and logs; the H1.S2c tree may carry copied/imported Skeptic output evidence from H1.S2b. H1.S3 did not launch a new live runtime producer.

The H1.S1 run tree was available locally at `/var/tmp/cbm-h1-mcp-servers-4503e2d/src/git/.research/run-mcp-git-surface-mapper-h1s1-6/` and is now preserved in this H1.S3 packet. This improves retrospective auditability compared with the original H1.S1 convenience benchmark packet, whose `RESULT.md` recorded that the full run tree had not been copied at publication time.

## Review Packet

Non-current-model checkpoint review files are prepared at:

```text
.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/
  PROMPT.md
  CHECKPOINT.md
  DISPOSITION.md
  EVIDENCE-MANIFEST.md
```

The benchmark packet mirrors the checkpoint prompt and packet index for reviewer convenience:

```text
CHECKPOINT-PROMPT.md
CHECKPOINT-PACKET.md
```
