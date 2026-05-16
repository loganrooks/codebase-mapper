#!/usr/bin/env sh
set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: gate-artifact.sh <artifact-path> [repo]" >&2
  exit 2
fi

ARTIFACT="$1"
# W5 fix (verify-gates review): capture the git rev-parse output
# separately and check it is non-empty. `set -eu` does NOT trip on
# command-substitution failure inside parameter-expansion default,
# so a bare host (no git tree, no `[repo]` arg passed) silently left
# REPO empty and the cbm invocation ran with PYTHONPATH= and
# --repo "" which resolves to cwd. Fail loudly instead.
if [ "$#" -ge 2 ]; then
  REPO="$2"
else
  REPO=$(git rev-parse --show-toplevel 2>/dev/null || true)
  if [ -z "$REPO" ]; then
    echo "gate-artifact.sh: not in a git tree and no [repo] arg passed; cannot resolve repo root" >&2
    exit 2
  fi
fi

PYTHONPATH="$REPO" python3 -m cbm gate-artifact "$ARTIFACT" --repo "$REPO"
