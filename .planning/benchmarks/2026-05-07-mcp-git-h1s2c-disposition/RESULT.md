# H1.S2c MCP Git Challenge Disposition

Status: passed for H1.S2c challenge disposition

## Input

- Input benchmark: `.planning/benchmarks/2026-05-07-mcp-git-h1s2b-skeptic/`
- Input run id: `run-mcp-git-h1s2b-skeptic-1`
- H1.S2c run id: `run-mcp-git-h1s2c-disposition-1`
- Target checkout: `/var/tmp/cbm-h1-mcp-servers-4503e2d/src/git`
- Input challenge id: `chl-10001`
- Challenged claim: `auth-001`

## Decision

- Decision: `accepted_as_alternative`
- Final `auth-001.claim_status`: `contested`
- Final `chl-10001.status`: `accepted_as_alternative`

Mapper response:

`auth-001` keeps the original reading that `src/mcp_server_git/__init__.py` is the shared command implementation, and accepts `chl-10001` as a live alternative reading that launch/routing authority is also distributed across `pyproject.toml` and `src/mcp_server_git/__main__.py`.

## Citation Support

The accepted alternative remains grounded in:

- `pyproject.toml:25-26@4503e2d12b79`
- `src/mcp_server_git/__main__.py:1-5@4503e2d12b79`
- `src/mcp_server_git/__init__.py:7-24@4503e2d12b79`

The original `auth-001` citations also remain on the claim, so this is contestation rather than contradiction or replacement.

## Preserved Packet

```text
.planning/benchmarks/2026-05-07-mcp-git-h1s2c-disposition/
  RESULT.md
  surface-map.json
  handoff.md
  evidence-ledger.jsonl
  .research/run-mcp-git-h1s2c-disposition-1/
    surface-map.json
    skeptic-review/surface-map.md
    handoff.md
    handoff.json
    evidence-ledger.jsonl
    evidence-ledger.jsonl.integrity.json
    producer-registry.json
    logs/
    codex_outputs/
```

## Validation Commands Run

```bash
TMPDIR=/var/tmp pytest -q tests/test_cli.py::test_run_backend_codex_cli_skill_mode_loads_skeptic_skill tests/test_cli.py::test_run_backend_codex_cli_skill_skeptic_reviews_existing_surface_artifact tests/test_cli.py::test_respond_challenge_accepts_alternative_marks_claim_contested tests/test_cli.py::test_handoff_counts_accepted_alternative_as_contested_not_open
TMPDIR=/var/tmp python3 -m cbm.cli respond-challenge .research/run-mcp-git-h1s2c-disposition-1/surface-map.json --repo /private/var/tmp/cbm-h1-mcp-servers-4503e2d/src/git --challenge-id chl-10001 --decision accepted_as_alternative --resolution "accepted_as_alternative: preserved original auth-001 reading and accepted distributed-routing reading as a live alternative" --response-note "accept chl-10001 as an alternative reading. __init__.py remains the shared command implementation, while launch/routing authority is also distributed across pyproject.toml and __main__.py." --resolved-by surface-mapper@1.2
TMPDIR=/var/tmp python3 -m cbm.cli handoff --repo /private/var/tmp/cbm-h1-mcp-servers-4503e2d/src/git --run-id run-mcp-git-h1s2c-disposition-1
```

Additional final verification after artifact and planning updates:

```bash
TMPDIR=/var/tmp python3 -m cbm.cli validate /Users/rookslog/Development/cbm/.planning/benchmarks/2026-05-07-mcp-git-h1s2c-disposition/surface-map.json --repo /private/var/tmp/cbm-h1-mcp-servers-4503e2d/src/git
TMPDIR=/var/tmp python3 -m cbm.cli verify-citations /Users/rookslog/Development/cbm/.planning/benchmarks/2026-05-07-mcp-git-h1s2c-disposition/surface-map.json --repo /private/var/tmp/cbm-h1-mcp-servers-4503e2d/src/git
TMPDIR=/var/tmp python3 -m cbm.cli check-evidence /Users/rookslog/Development/cbm/.planning/benchmarks/2026-05-07-mcp-git-h1s2c-disposition/surface-map.json --repo /private/var/tmp/cbm-h1-mcp-servers-4503e2d/src/git
TMPDIR=/var/tmp python3 -m cbm.cli validate /Users/rookslog/Development/cbm/.planning/benchmarks/2026-05-07-mcp-git-h1s2c-disposition/handoff.md --repo /private/var/tmp/cbm-h1-mcp-servers-4503e2d/src/git
TMPDIR=/var/tmp python3 -m cbm.cli verify-citations /Users/rookslog/Development/cbm/.planning/benchmarks/2026-05-07-mcp-git-h1s2c-disposition/handoff.md --repo /private/var/tmp/cbm-h1-mcp-servers-4503e2d/src/git
TMPDIR=/var/tmp pytest -q
```

All exited 0. Full suite reported 116 passed and 2 existing `jsonschema.RefResolver` deprecation warnings.

## Boundary

This satisfies H1.S2c only. It does not claim H1 complete, minimum-useful CBM complete, or Phase B+. H1.S3 remains next.
