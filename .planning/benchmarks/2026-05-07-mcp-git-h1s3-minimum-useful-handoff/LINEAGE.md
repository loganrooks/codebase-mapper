# H1.S3 Lineage

Status: prepared
Date: 2026-05-07
Run/packet id: `run-mcp-git-h1s3-minimum-useful-handoff-1`

## Final Surface State

Final H1 surface state = H1.S1 runtime Surface Mapper artifact + H1.S2b runtime Skeptic review + H1.S2c mapper response/disposition.

The final surface artifact for review is:

- `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/surface-map.json`

This file is copied from the H1.S2c disposition packet. Its `produced_by` remains `surface-mapper@1.2`, while some fields such as `produced_at` and imported inputs still reflect H1.S1-era provenance. The H1.S3 packet therefore carries lineage here instead of implying that the H1.S1 map alone already included the H1.S2c disposition.

No `refreshed_from` block was added because changing the copied `surface-map.json` would alter a previously validated successor artifact and would require a new artifact-production path. The safer H1.S3 action is to preserve the exact validated final surface state and explain the lineage externally.

## Source Artifacts

- H1.S1 `surface-map.json`: original runtime Surface Mapper reading from `.planning/benchmarks/2026-05-02-mcp-git-surface-mapper-h1s1/surface-map.json`.
- H1.S2b `skeptic-review/surface-map.md`: real isolated Skeptic review, preserved as `.planning/benchmarks/2026-05-07-mcp-git-h1s3-minimum-useful-handoff/skeptic-review-surface-map.md`.
- H1.S2c `surface-map.json`: successor/disposition state carrying `auth-001.claim_status = contested` and `chl-10001.status = accepted_as_alternative`; preserved as H1.S3 `surface-map.json`.
- H1.S2c `handoff.md`: handoff carrying `open_challenges = 0` and `claims_by_status.contested = 1`; preserved as `source-h1s2c-handoff.md`.
- H1.S2c `evidence-ledger.jsonl`: ledger with `challenge_resolved` for `chl-10001`; preserved as `evidence-ledger.jsonl`.

## Preserved Runtime Logs And Codex Outputs

The `.research/` trees copied into this packet preserve source-stage runtime evidence for audit. They are not newly produced H1.S3 live model output.

- `.research/run-mcp-git-surface-mapper-h1s1-6/logs/` preserves H1.S1 runtime Surface Mapper subprocess evidence.
- `.research/run-mcp-git-h1s2b-skeptic-1/codex_outputs/` and `logs/` preserve H1.S2b runtime Skeptic subprocess evidence.
- `.research/run-mcp-git-h1s2c-disposition-1/` preserves the H1.S2c disposition state. Any copied `codex_outputs/` or `logs/` under that tree are inherited evidence from the imported H1.S2b Skeptic run, not a fresh H1.S2c or H1.S3 live Skeptic call.

## Historical Ledger Caveats

The preserved `evidence-ledger.jsonl` is append-only evidence and was not hand-edited.

Historical smoke anchor:

- Ledger entry `lg-00030` records `.gitignore:1@4503e2d12b79` as a historical `citation_introduced` entry for `.research/run-mcp-git-h1s2b-skeptic-1/skeptic-review/surface-map.md`.
- The rendered H1.S2b Skeptic review promoted in this packet no longer contains that smoke citation anchor.
- The H1.S3 handoff does not promote `.gitignore:1@4503e2d12b79` as supporting evidence for the H1 pass claim.
- The raw Codex output and run tree are preserved for audit under `.research/run-mcp-git-h1s2b-skeptic-1/`.

Mixed run-id provenance:

- Ledger entry `lg-00029` is a `claim_challenged` entry for `auth-001` / `chl-10001`.
- It records `run_id: run-mcp-git-surface-mapper-h1s1-6` while its `artifact_path` points to `.research/run-mcp-git-h1s2b-skeptic-1/surface-map.json`.
- Interpretation: the challenge was raised during H1.S2b against an imported H1.S1 surface map. The durable challenge id is `chl-10001`, and the H1.S2c successor artifact carries the disposition.
- The H1.S3 packet documents this ambiguity rather than rewriting existing ledger lines.

## Boundary

This lineage supports checkpoint review. It does not by itself accept the H1 pass claim.
