# Codex CLI Isolation Spike

Status: completed local capability check
Date: 2026-05-01
Scope: recovery step 11, Codex CLI subprocess viability for CBM runtime producers

## Question

Can CBM plausibly launch isolated Codex CLI producer processes for interpretive mapping work without relying on the parent Codex session lifecycle?

## Local Evidence

Commands run:

- `command -v codex`
- `codex --version`
- `codex --help`
- `codex exec --help`
- `codex exec review --help`
- `codex debug --help`
- `codex debug prompt-input --help`

Observed local version:

- `codex-cli 0.128.0`

Relevant local CLI capabilities observed from help output:

- `codex exec` runs non-interactively.
- `codex exec --ephemeral` runs without persisting session files to disk.
- `codex exec --ignore-user-config` avoids loading `$CODEX_HOME/config.toml`; auth still uses `CODEX_HOME`.
- `codex exec --ignore-rules` avoids user/project execpolicy `.rules` files.
- `codex exec --output-schema <FILE>` constrains the final response shape.
- `codex exec --json` emits JSONL events.
- `codex exec -C <DIR>` sets the working root.
- `codex exec --add-dir <DIR>` grants additional writable directories.
- `codex exec -s read-only|workspace-write|danger-full-access` selects sandbox policy.
- `codex exec -a never|on-request|untrusted|on-failure` selects approval policy.
- `codex exec -m <MODEL>`, `--profile <CONFIG_PROFILE>`, and `-c key=value` allow model/profile/config override.

## Conclusion

Codex CLI is a plausible subprocess backend for CBM producer experiments. It can be invoked independently of the parent session, with a chosen working directory, sandbox mode, approval policy, config overrides, JSONL output, output schema, and optional ephemeral/no-user-config/no-rules settings.

This does not yet prove that a launched Skeptic satisfies `RUNTIME-CONSTITUTION.md` isolation. The local help surface shows isolation controls exist; it does not prove model-visible context boundaries, hook behavior under alternate config, or cost/runtime behavior.

## Recommended Backend Shape

Add a future `codex_cli` backend distinct from both current values:

- `deterministic`: current baseline/dev-fixture producers.
- `external`: declared but refused until a generic external runner exists.
- `codex_cli`: concrete subprocess runner using `codex exec`.

Recommended Skeptic subprocess defaults for first live test:

```sh
codex exec \
  --ephemeral \
  --ignore-user-config \
  --ignore-rules \
  -C <scratch-run-workspace> \
  -s read-only \
  -a never \
  --json \
  --output-schema <skeptic-output.schema.json> \
  -m <chosen-model> \
  -
```

Use a scratch run workspace containing only:

- the target artifact to review;
- required schemas;
- cited source excerpts or a bounded read-only target repo path;
- `RUNTIME-CONSTITUTION.md`;
- the specific producer prompt.

The parent CBM process should validate the returned artifact after the subprocess exits. The subprocess must not be trusted to mark its own output accepted.

## Open Checks Before Enabling Skeptic

- Run a paid/live `codex exec` smoke on a tiny fixture and record whether model-visible context excludes parent-chat history.
- Confirm whether custom hook behavior can be supplied without using the user-level config, or decide that CBM subprocesses should run with `--ignore-user-config` and no hooks.
- Verify JSONL event parsing and final-response extraction.
- Verify `--output-schema` failure behavior.
- Verify that read-only sandbox plus a scratch workspace allows artifact reading but prevents writes outside the intended output path.
- Decide whether subprocess auth should use the user's `CODEX_HOME` or an isolated `CODEX_HOME` with copied auth only.

## Decision

Do not wire `codex_cli` into `cbm run` yet.

Next implementation should be a narrow live smoke command or fixture-gated backend spike that produces one schema-valid artifact from a tiny repo and records the subprocess invocation in `run-manifest.json`.
