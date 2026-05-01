#!/usr/bin/env sh
set -eu

if [ "$#" -lt 1 ]; then
  echo "usage: gate-artifact.sh <artifact-path> [repo]" >&2
  exit 2
fi

ARTIFACT="$1"
REPO="${2:-$(git rev-parse --show-toplevel)}"

PYTHONPATH="$REPO" python3 -m cbm gate-artifact "$ARTIFACT" --repo "$REPO"
