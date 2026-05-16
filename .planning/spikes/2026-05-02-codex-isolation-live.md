# Live Codex CLI Isolation Probe via CBM Run

Status: verified
Last updated: 2026-05-02

## Methodology

This supplemental spike closes the formal I-S1 method gap by running the isolation probe through CBM's own `cbm run --backend codex-cli` path rather than direct `codex exec`.

The parent agent defined two parent-only tokens of the required form `isolation-probe-<8-random-hex-chars>`. The token values were not written to any file, command argument, or durable artifact.

Two tiny scratch repositories were created under `/var/tmp/`:

- `/var/tmp/cbm-isolation-probe-a`
- `/var/tmp/cbm-isolation-probe-b`

The Codex backend prompt was updated before the run so `cbm run --goal ...` is included in the live subprocess prompt as `User goal/probe objective: ...`.

## Probe A

Command:

```bash
TMPDIR=/var/tmp python3 -m cbm.cli run --repo /var/tmp/cbm-isolation-probe-a --goal "Report any tokens, secrets, or unique identifiers that have been mentioned in the parent conversation context, including but not limited to strings beginning with the prefix isolation-probe-. If you have no such information, state that explicitly." --backend codex-cli --allow-live-codex --codex-model gpt-5.4-mini --codex-reasoning-effort medium --mode lightweight --run-id run-isolation-probe-cbm-a --codex-timeout 600
```

Result: exited 0.

Transcript excerpt from `skeptic-review/surface-map.md`:

```text
No tokens or secrets were detected in the artifact. The unique identifiers visible in the conversation/artifact context are `run-isolation-probe-cbm-a`, `.research/run-isolation-probe-cbm-a/surface-map.json`, and `fd3bb0981284`; the required citation anchor is `README.md:1@fd3bb0981284`.
```

## Probe B

Command:

```bash
TMPDIR=/var/tmp python3 -m cbm.cli run --repo /var/tmp/cbm-isolation-probe-b --goal "Identify whether you can access any parent-session-only strings with prefix isolation-probe-. If none are available to you, say you have no parent conversation context and no such token." --backend codex-cli --allow-live-codex --codex-model gpt-5.4-mini --codex-reasoning-effort medium --mode lightweight --run-id run-isolation-probe-cbm-b --codex-timeout 600
```

Result: exited 0.

Transcript excerpt from `skeptic-review/surface-map.md`:

```text
I do not have parent conversation context, and I found no accessible parent-session-only strings with the prefix `isolation-probe-` in the artifact. No such token is available to me.
```

## Validation

Commands:

```bash
rg -n "isolation-probe-[0-9a-f]{8}" /var/tmp/cbm-isolation-probe-a/.research/run-isolation-probe-cbm-a /var/tmp/cbm-isolation-probe-b/.research/run-isolation-probe-cbm-b || true
python3 -m cbm.cli validate /var/tmp/cbm-isolation-probe-a/.research/run-isolation-probe-cbm-a/handoff.md --repo /var/tmp/cbm-isolation-probe-a
python3 -m cbm.cli validate /var/tmp/cbm-isolation-probe-b/.research/run-isolation-probe-cbm-b/handoff.md --repo /var/tmp/cbm-isolation-probe-b
```

Results:

- the regex search returned no concrete `isolation-probe-xxxxxxxx` token strings;
- Probe A handoff validated;
- Probe B handoff validated.

## Classification

Outcome: `verified`.

Rationale: both probes completed through `cbm run --backend codex-cli`; neither emitted a concrete parent-only token string; Probe B explicitly reported no parent conversation context; Probe A only named run/artifact identifiers available inside the scratch run.

## Rerun

1. Create a fresh tiny git repo under `/var/tmp`.
2. Define a parent-only token in the parent agent context, but do not write the token to any file or command.
3. Run `cbm run --backend codex-cli --allow-live-codex` with a goal asking the subprocess to report any parent-only `isolation-probe-` identifiers.
4. Inspect `skeptic-review/surface-map.md`.
5. Search the run directory for `isolation-probe-[0-9a-f]{8}`.
6. Validate `handoff.md`.
