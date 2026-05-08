# Cross-Vendor Review Recovery

Run id: `xvr-20260508T023055Z-10836`
Review id: `2026-05-07-h1-minimum-useful-checkpoint`

## Classification

- `auth_failed`
- `invalid_disposition`
- `model_unavailable`
- `permission_blocked`

## Expected Outputs

- `/Users/rookslog/Development/cbm/.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/CHECKPOINT.md`: exists=True size=10410
- `/Users/rookslog/Development/cbm/.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/DISPOSITION.md`: exists=True size=3807

## Captured Files

- `.xvr-runs/xvr-20260508T023055Z-10836/raw/claude.command.txt`
- `.xvr-runs/xvr-20260508T023055Z-10836/raw/claude.completed-at.txt`
- `.xvr-runs/xvr-20260508T023055Z-10836/raw/claude.exit-code.txt`
- `.xvr-runs/xvr-20260508T023055Z-10836/raw/claude.path.txt`
- `.xvr-runs/xvr-20260508T023055Z-10836/raw/claude.started-at.txt`
- `.xvr-runs/xvr-20260508T023055Z-10836/raw/claude.stderr.log`
- `.xvr-runs/xvr-20260508T023055Z-10836/raw/claude.stdout.stream-json`
- `.xvr-runs/xvr-20260508T023055Z-10836/raw/git-branch-before.txt`
- `.xvr-runs/xvr-20260508T023055Z-10836/raw/git-diff-after.patch`
- `.xvr-runs/xvr-20260508T023055Z-10836/raw/git-sha-before.txt`
- `.xvr-runs/xvr-20260508T023055Z-10836/raw/git-status-after.txt`
- `.xvr-runs/xvr-20260508T023055Z-10836/raw/git-status-before.txt`

## Recovery Command

Explicit resume is available from the captured session envelope:

```bash
claude --resume xvr-xvr-20260508T023055Z-10836 -p 'Resume the cross-vendor review in /Users/rookslog/Development/cbm/.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint. Read REVIEW-SPEC.md and PROMPT.md again. Write only missing or incomplete declared outputs inside allowed roots. Do not use chat output as the durable artifact.' --model opus --permission-mode auto --output-format stream-json --include-partial-messages --verbose --tools Read,Write,Edit,Bash --add-dir /Users/rookslog/Development/cbm/.planning/reviews/2026-05-07-h1-minimum-useful-checkpoint --setting-sources project --add-dir /Users/rookslog/Development/cbm
```

## Boundary

This recovery note does not synthesize reviewer content, reviewer identity, confidence, or disposition from raw logs.
