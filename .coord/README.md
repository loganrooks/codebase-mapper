# `.coord/` — escalation protocol for Codex↔Claude

This directory holds the **dev-workflow coordination layer** between the agents building CBM (Codex executor + Claude supervisor). It is *not* part of the CBM product. End users of CBM never see `.coord/`; `cbm` the CLI does not read or write to it.

## Why it exists

When Codex runs `/goal` in its own session, it has no live channel back to a Claude session running elsewhere. If Codex hits a planned stop-and-surface gate (per the "When to stop and surface" rules in `AGENTS.md`) or an unplanned blocker, the parent supervisor cannot be notified. Pasting paths by hand works but is fragile. `.coord/` is the smallest possible file-based IPC that fixes this:

- Codex opens a structured escalation file, blocks on a pure shell wait (zero LLM tokens), and resumes when the file's `status` flips.
- Claude monitors the directory, answers asynchronously, and the conversation lives in one append-only markdown file per escalation.
- The `coord` CLI enforces the schema so neither agent can produce malformed escalations.

## Layout

```text
.coord/
  coord                                        # the CLI (chmod +x)
  README.md                                    # this file
  escalations/
    INDEX.md                                   # one row per escalation, status-keyed
    20260517-171243-h2s1-target-pick/
      escalation.md                            # the conversation file
      attachments/                             # optional: logs, snippets, repros
```

## Lifecycle

```text
              coord open                coord answer                coord resolve
   (codex) --------------> open ----- (claude) -----> answered --- (codex) ---> resolved
                              \                                     /
                               '------------ coord resolve ---------'   (if codex resolves directly without explicit answer)

                              abandoned   (set manually in frontmatter if escalation became moot)
```

1. **Open.** Codex runs `COORD_AGENT=codex .coord/coord open --kind {gate|block} --slice <slug> --title <text> [--body <text> | --body-file <path|->] ...`. The CLI generates an id (`YYYYMMDD-HHMMSS-<slug>`), writes the frontmatter and first turn, appends a row to `INDEX.md`, and prints the id.
2. **Wait.** Codex runs `.coord/coord wait <id>`. This is a blocking shell loop: `until grep -q '^status: answered\|^status: resolved' …; do sleep 10; done`. The LLM is suspended during the sleep; no tokens are consumed while blocked.
3. **Surface to Claude.** Either (a) Claude's `Monitor` (armed at session start, watching `.coord/escalations/`) fires on the new file, (b) Claude's session-start scan of `INDEX.md` picks up the open row, or (c) the user pastes the path.
4. **Answer.** Claude runs `.coord/coord answer <id> --body-file response.md` (or `--body "<text>"` for a one-liner, or `--body-file -` to read from stdin). The CLI appends a `## claude <ts> (answered)` section to the file and flips `status: open → answered` in both the file and `INDEX.md`.
5. **Resume + resolve.** Codex's wait loop exits; Codex reads the response, acts, and runs `.coord/coord resolve <id> --body-file ack.md` to close. Status → `resolved`.

## Kinds

| Kind    | Use case                                                                    | Required fields |
|---------|-----------------------------------------------------------------------------|-----------------|
| `gate`  | Planned stop-and-surface (named in `.planning/` or expected by the plan).   | `answer_shape`; `options` if `pick-one`. |
| `block` | Unplanned blocker — error, contradiction, ambiguity, plan-revision request. | none beyond the base set. |

Two kinds is the minimum viable taxonomy. A third (`proposal`, for deviation-from-plan requests) may be added later if it recurs often enough to warrant separate filtering.

## Frontmatter schema

```yaml
---
id: 20260517-171243-h2s1-target-pick
kind: gate                       # gate | block
status: open                     # open | answered | resolved | abandoned
opened_by: codex                 # codex | claude
opened_at: 2026-05-17T17:12:43Z  # UTC ISO 8601
slice: H2.S1
plan_ref: .planning/phases/02-runtime-producer-repeatability/GOAL-H2S1-REPEATABILITY-PLAN.md   # optional
answer_shape: pick-one           # pick-one | free-form | approve-reject (gates only)
options: [h11, mcp-filesystem, conc]   # pick-one gates only
---
```

`status` is the single coordination primitive both agents read. The `coord` CLI is the only thing that should flip `status` — direct edits risk leaving `INDEX.md` and the file out of sync.

## Body convention

Append-only. Each turn is a new section:

```markdown
## <agent> <ISO-timestamp> (<status>)

<turn content>
```

The CLI writes the headers; agents write the prose under their own header. Don't edit prior turns — they're the audit trail.

## Setup

Add to PATH or alias:

```bash
alias coord='./.coord/coord'
# or:
export PATH=".coord:$PATH"
```

Codex sessions should set `COORD_AGENT=codex` (so the CLI stamps `opened_by: codex` etc.); Claude sessions inherit the default `claude`.

## CLI reference

`coord help` lists all subcommands. The full surface:

| Verb       | Purpose                                                              |
|------------|----------------------------------------------------------------------|
| `open`     | Create a new escalation. Validates kind/answer-shape, generates id, writes frontmatter, appends to INDEX. |
| `answer`   | Append a response and flip `open → answered`. Errors if status ≠ `open`. |
| `resolve`  | Append a closing note and flip `→ resolved`. Allowed from `open` or `answered`. |
| `wait`     | Block until status is `answered` or `resolved`. Pure shell sleep loop. |
| `list`     | Print the INDEX (or just open rows with `--open`).                   |
| `show`     | Print one escalation file.                                           |

Per-file writes are atomic (tempfile + `mv`). `INDEX.md` and the per-escalation file are updated *sequentially*, not transactionally — an interruption between the two writes can leave them briefly out of sync. For dev-workflow use between two trusted agents this is acceptable; if it ever happens, the per-escalation file is the source of truth, and INDEX.md can be hand-edited to match.

## Cross-platform

Designed for **POSIX shell + standard Unix tools** (bash 3.2+, grep, sed, awk, date, mktemp). Smoke-tested on macOS (BSD coreutils); should work on Linux (GNU coreutils) and WSL but not independently verified. Native Windows is out of scope.

The `Monitor` tool on Claude's side branches on `fswatch` (macOS) vs `inotifywait` (Linux); both are fine to install.

## Why not `cbm gates`?

`.coord/` is dev-workflow infrastructure for the team building CBM. CBM the product is a codebase mapper; its CLI surface should not grow to handle inter-agent coordination unrelated to mapping codebases. Keeping `coord` as a separate one-file shell tool prevents scope creep into the product.

## When to use this vs `BUILD-LOG.md`

| Situation | Mechanism |
|-----------|-----------|
| Decision needed before continuing | `coord open --kind gate` (or `block`). Blocks Codex. |
| Decision logged after the fact | `BUILD-LOG.md` entry. Does not block. |
| Discovery worth surfacing but not blocking | `BUILD-LOG.md` entry with `surface:` prefix. |
| Stop-and-surface bullet from `AGENTS.md` triggered | `coord open` (escalation) — and a BUILD-LOG entry referencing the escalation id. |

Escalations are *blocking*. The BUILD-LOG is non-blocking audit. Use both: the escalation drives the live decision; the BUILD-LOG entry preserves the why-and-what for future review.
