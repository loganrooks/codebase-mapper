# Claude Code Review Runner Spike Findings Template

Use this template only for future runner behavior spikes. Do not commit raw logs unless they are needed as durable evidence.

```markdown
# Claude Code Review Runner Spike Result

Status:
Observed:
Scope:

## CLI Capability Check

- `command -v claude`:
- `claude --version`:
- Help surfaces observed:

## Runs

| Probe | Command shape | Exit | Result |
| --- | --- | --- | --- |

## Stream JSON Observations

- Session id:
- Model identity:
- Usage/cost:
- Permission denials:
- Partial messages:

## Resume Observations

- Session name:
- Resume command:
- Reused session id:
- Saw prior context:

## Permission Observations

- Permission mode:
- Tools:
- Command execution:
- Write behavior:

## Decisions For Scripts

- Launch shape:
- Recovery shape:
- Caveats:
```
