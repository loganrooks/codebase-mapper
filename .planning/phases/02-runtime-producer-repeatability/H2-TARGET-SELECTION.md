# H2 Target Selection

Status: stop-and-surface; user target pick required
Last updated: 2026-05-16
Scope: H2.S1 planning only

## Boundary

This artifact proposes candidate targets for H2 runtime-producer repeatability. It does not lock the H2 target, does not dispatch Surface Mapper or Skeptic, does not claim H2 complete, and does not claim repeatability or Phase B+ readiness.

User: please confirm the H2 target.

## Selection Summary

Recommended target: Candidate 2, `python-hyper/h11` scoped to the `h11/` package.

Reasoning: `h11` is the best H2 target if the immediate goal is repeatability rather than language-generalization. It is outside the MCP repository, stays in Python so the first H2 live run does not combine repeatability risk with a new-language risk, and is materially different from H1's MCP `src/git` target: protocol state-machine library rather than MCP server, no git wrapper domain, no I/O by design, and an obvious non-trivial interpretive surface around connection state, event flow, and error handling. Candidate 1 gives useful TypeScript/filesystem coverage but stays inside the MCP monorepo. Candidate 3 gives the strongest language-generalization signal, but Go quality is a separate preflight risk for a producer skill only proven on Python so far.

## Probe Command Ledger

Probe workspace: `/var/tmp/cbm-h2-target-probes-20260516`.

No `cbm run`, Surface Mapper, Skeptic, or live producer command was invoked against any candidate. Probes were limited to clone/checkout, `git rev-parse`, LOC counting, and LICENSE/metadata inspection.

### Rejected Probe - `pallets/click`

`pallets/click` was evaluated as a possible different-repo same-language target, then rejected for size. Its `src/click` package alone counted 11,823 LOC, which exceeds the H2.S1 bounded-size criterion.

```bash
git clone --depth 1 https://github.com/pallets/click.git /var/tmp/cbm-h2-target-probes-20260516/click
git -C /var/tmp/cbm-h2-target-probes-20260516/click rev-parse HEAD
# e3e69e3bf8d749ac1a632f2ece4d38ec7f6588f5

# From /var/tmp/cbm-h2-target-probes-20260516/click:
git ls-files src/click | rg '\.(py|pyi|toml|md)$' | xargs -r wc -l | tail -n 1
# 11823 total
```

## Candidate 1 - `mcp-filesystem`

- Repo: `https://github.com/modelcontextprotocol/servers`
- Pinned SHA: `4503e2d12b799448cd05f789dd40f9643a8d1a6c`
- Subtree: `src/filesystem`
- Approximate LOC under examination: 4,498 lines. Count includes tracked TypeScript, tests, README, package metadata, and local config under `src/filesystem`; it excludes Dockerfile because the final count filter was source/config/doc extensions only.
- Language(s) and project shape: TypeScript MCP server, package-style server subtree with CLI entrypoint, filesystem tools, path validation, roots handling, and Vitest tests.
- License: Apache-2.0 / MIT transition at repository root; package metadata says `SEE LICENSE IN LICENSE`. This is permissive enough for automated reading and public packet quotation, but H2.S2 should record the transition note rather than flatten it to one SPDX id.
- Domain: Filesystem access and directory access control for an MCP server.
- Materially different from H1 in which dimensions: language family (TypeScript instead of Python), domain (filesystem access instead of git wrapping), dependency surface (Node/TypeScript/Vitest stack), security/safety surface (path validation and allowed-directory roots), and larger source/test shape.
- Plausible non-trivial claim or challenge a Skeptic could raise: a Skeptic could challenge whether path validation or roots handling is the central authority for filesystem safety, especially if tool handlers also enforce or bypass directory constraints.
- Risk factors for the run: Still inside the same MCP monorepo and protocol ecosystem as H1, so a positive result is a weaker independence signal than a separate repo; TypeScript is unproven for `surface-mapper@1.2`; LOC is close to the H2 bound; license has a transition note that should be cited carefully.
- Why this candidate over the others: This is the lowest integration-risk way to exercise a substantially different language and domain while preserving the known MCP benchmark SHA and repository shape. It is useful if the user wants H2 to stress language/domain variance while avoiding a brand-new repository. It is weaker than Candidate 2 for proving "not MCP-specific."

Probe commands and outcomes:

```bash
git clone --filter=blob:none --no-checkout https://github.com/modelcontextprotocol/servers.git /var/tmp/cbm-h2-target-probes-20260516/mcp-servers
git -C /var/tmp/cbm-h2-target-probes-20260516/mcp-servers checkout 4503e2d12b799448cd05f789dd40f9643a8d1a6c
git -C /var/tmp/cbm-h2-target-probes-20260516/mcp-servers rev-parse HEAD
# 4503e2d12b799448cd05f789dd40f9643a8d1a6c

# From /var/tmp/cbm-h2-target-probes-20260516/mcp-servers:
git ls-files src/filesystem | rg '\.(py|ts|tsx|js|json|toml|ya?ml|md)$' | xargs -r wc -l | tail -n 1
# 4498 total

sed -n '1,60p' LICENSE
# Root LICENSE begins with a transition notice from MIT to Apache-2.0, then Apache-2.0 terms.

sed -n '1,80p' src/filesystem/package.json
# package license field: "SEE LICENSE IN LICENSE"
```

## Candidate 2 - `python-hyper-h11`

- Repo: `https://github.com/python-hyper/h11`
- Pinned SHA: `62c5068c971579d61fa1b55373390e12f25fd856`
- Subtree: `h11` package source. Root `LICENSE.txt`, `README.rst`, and `pyproject.toml` were inspected for license/context, but the primary mapper scope should be the package source.
- Approximate LOC under examination: 2,568 lines for tracked Python package source under `h11/`, excluding `h11/tests/`.
- Language(s) and project shape: Python protocol library, bring-your-own-I/O HTTP/1.1 state machine.
- License: MIT.
- Domain: HTTP/1.1 message/event/state handling.
- Materially different from H1 in which dimensions: different repository, protocol library rather than MCP server, HTTP state machine rather than git command wrapper, no I/O by design, dependency surface close to standard-library-only, mature test-heavy project conventions.
- Plausible non-trivial claim or challenge a Skeptic could raise: a Skeptic could challenge whether `Connection` is the central authority or whether the actual authority is distributed between the connection object, state machine, and event classes.
- Risk factors for the run: Same language as H1 reduces language-generalization signal; scoped package source omits tests from the primary LOC count unless H2.S2 deliberately includes them as verification context; protocol state machines may require careful citation density to avoid interpretive overreach.
- Why this candidate over the others: This is the strongest pragmatic repeatability target. It proves the pipeline is not MCP- or git-subtree-specific while keeping the runtime producer on a language it has already handled once. The state-machine domain is interpretively rich without forcing H2.S2 to debug TypeScript or Go language-fit at the same time as repeatability.

Probe commands and outcomes:

```bash
git clone --depth 1 https://github.com/python-hyper/h11.git /var/tmp/cbm-h2-target-probes-20260516/h11
git -C /var/tmp/cbm-h2-target-probes-20260516/h11 rev-parse HEAD
# 62c5068c971579d61fa1b55373390e12f25fd856

# From /var/tmp/cbm-h2-target-probes-20260516/h11:
git ls-files h11 | rg '\.(py|pyi)$' | rg -v '^h11/tests/' | xargs -r wc -l | tail -n 1
# 2568 total

sed -n '1,80p' LICENSE.txt
# LICENSE.txt is MIT.

sed -n '1,120p' README.rst
# README describes h11 as a Python HTTP/1.1 library with no I/O code, centered on Connection/event flow.
```

## Candidate 3 - `sourcegraph-conc`

- Repo: `https://github.com/sourcegraph/conc`
- Pinned SHA: `5f936abd7ae87036af1f75c95fb9d0daaf00116b`
- Subtree: whole repo
- Approximate LOC under examination: 3,631 lines across tracked Go source, Go tests, `go.mod`, `go.sum`, and `README.md`.
- Language(s) and project shape: Go structured-concurrency library with packages for wait groups, pools, panic handling, iteration, and streams.
- License: MIT.
- Domain: Structured concurrency and safer goroutine ownership in Go.
- Materially different from H1 in which dimensions: different repository, different language family, library rather than MCP server, concurrency/panic/error domain rather than git command wrapper, small multi-package Go module with tests.
- Plausible non-trivial claim or challenge a Skeptic could raise: a Skeptic could challenge whether `WaitGroup` is the central ownership authority or whether panic/error/context propagation in `pool` and `panics` forms separate co-equal authority surfaces.
- Risk factors for the run: Highest language-fit risk because `surface-mapper@1.2` has not been proven on Go; concurrency semantics may produce confident-sounding but under-grounded interpretations if the mapper does not cite tests and panic paths carefully; the target may need an H2.S2 dry-run quality check before spending the full run budget.
- Why this candidate over the others: This is the highest-signal target for proving the producer is not Python-overfit. It stays under the size bound and has a clear interpretive surface, but it combines repeatability with new-language generalization. It is a better H3/H4 language-generalization target unless the user explicitly wants H2 to absorb that risk now.

Probe commands and outcomes:

```bash
git clone --depth 1 https://github.com/sourcegraph/conc.git /var/tmp/cbm-h2-target-probes-20260516/conc
git -C /var/tmp/cbm-h2-target-probes-20260516/conc rev-parse HEAD
# 5f936abd7ae87036af1f75c95fb9d0daaf00116b

# From /var/tmp/cbm-h2-target-probes-20260516/conc:
git ls-files | rg '(^|/)(.*\.go|go\.mod|go\.sum|README\.md)$' | xargs -r wc -l | tail -n 1
# 3631 total

sed -n '1,60p' LICENSE
# LICENSE is MIT.

sed -n '1,140p' README.md
# README describes structured concurrency goals, WaitGroup ownership, pool variants, panic handling, and stream/iter helpers.
```

## Recommendation

Pick Candidate 2, `python-hyper/h11`, unless the user wants H2 to explicitly test language generalization.

Candidate 2 best matches the H2.S1 objective: it is materially different from MCP `src/git`, has a small and bounded scope, has a permissive license, offers obvious non-trivial interpretive claims, and avoids making H2 simultaneously answer "can the pipeline repeat?" and "can the mapper handle a new language family?" Candidate 1 is acceptable if the priority is staying in a known benchmark repo while varying language/domain. Candidate 3 is acceptable if the priority is stronger generalization evidence and the user is willing to carry the Go-language preflight risk into H2.S2.

## Pending User Decision

User: please confirm the H2 target.

After the target is confirmed, H2.S1 can proceed to fill:

- `H2-PLAN.md`
- `H2-BENCHMARK-PACKET-SKELETON.md`
- `H2-PREFLIGHT.md`
- `PLAN.md`
- `SUMMARY.md`
- `VERIFICATION.md`

Until then, H2 target remains unlocked and H2.S2 live producer dispatch remains blocked.
