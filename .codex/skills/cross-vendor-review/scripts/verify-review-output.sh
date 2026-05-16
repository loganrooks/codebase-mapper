#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf 'usage: verify-review-output.sh <review-dir> [run-id]\n' >&2
}

if [ "$#" -lt 1 ] || [ "$#" -gt 2 ]; then
  usage
  exit 2
fi

REVIEW_DIR=$(cd "$1" && pwd -P)
if [ "$#" -eq 2 ]; then
  RUN_ID=$2
else
  RUN_ID=$(cat "$REVIEW_DIR/.xvr-runs/.latest-run-id")
fi

MANIFEST="$REVIEW_DIR/.xvr-runs/$RUN_ID/RUN-MANIFEST.json"
if [ ! -f "$MANIFEST" ]; then
  printf 'cross-vendor-review verify: missing run manifest: %s\n' "$MANIFEST" >&2
  exit 2
fi

python3 - "$MANIFEST" <<'PY'
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

manifest_path = Path(sys.argv[1])
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
review_dir = Path(manifest["review_dir"]).resolve()
run_dir = Path(manifest["paths"]["run_dir"]).resolve()
raw_dir = Path(manifest["paths"]["raw_dir"]).resolve()
issues: list[dict[str, str]] = []

def resolve_output(value: str) -> Path:
    p = Path(value)
    if not p.is_absolute():
        p = review_dir / p
    return p.resolve(strict=False)

def under(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except ValueError:
        return False

required = [str(item) for item in manifest.get("required_outputs") or []]
output_status = []
for output in required:
    path = resolve_output(output)
    exists = path.exists()
    size = path.stat().st_size if exists else 0
    output_status.append({"path": str(path), "exists": exists, "size": size})
    if not exists:
        issues.append({"code": "missing_expected_output", "path": str(path)})
    elif size == 0:
        issues.append({"code": "partial_expected_output", "path": str(path), "detail": "file is empty"})

allowed_roots = [Path(item).resolve(strict=False) for item in manifest.get("allowed_write_roots") or [str(review_dir)]]
repo_root = manifest.get("git", {}).get("repo_root") or ""
before_path = raw_dir / "git-status-before.txt"
after_path = raw_dir / "git-status-after.txt"
if repo_root and before_path.exists() and after_path.exists():
    before = {line for line in before_path.read_text(encoding="utf-8").splitlines() if line and not line.startswith("##")}
    after = {line for line in after_path.read_text(encoding="utf-8").splitlines() if line and not line.startswith("##")}
    new_lines = sorted(after - before)
    root = Path(repo_root).resolve(strict=False)

    def status_path(line: str) -> str:
        payload = line[3:] if len(line) > 3 else line
        if " -> " in payload:
            payload = payload.split(" -> ", 1)[1]
        return payload.strip().strip('"')

    for line in new_lines:
        rel = status_path(line)
        if not rel:
            continue
        path = (root / rel).resolve(strict=False)
        if not any(under(path, allowed) for allowed in allowed_roots):
            issues.append({"code": "wrote_outside_allowed_scope", "path": str(path), "status": line})

review_type = str(manifest.get("review_type") or "").lower()
decision_required = bool(manifest.get("decision_required"))
checkpointish = decision_required or "checkpoint" in review_type or "pass_claim" in review_type
if checkpointish:
    disposition_path = review_dir / "DISPOSITION.md"
    disposition_json_path = review_dir / "DISPOSITION.json"
    structured_disposition = {}
    if disposition_json_path.exists() and disposition_json_path.stat().st_size > 0:
        try:
            loaded = json.loads(disposition_json_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                structured_disposition = loaded
            else:
                issues.append({"code": "invalid_disposition", "path": str(disposition_json_path), "detail": "DISPOSITION.json must be an object"})
        except Exception as exc:
            issues.append({"code": "invalid_disposition", "path": str(disposition_json_path), "detail": str(exc)})
    if not disposition_path.exists() or disposition_path.stat().st_size == 0:
        if not structured_disposition:
            issues.append({"code": "missing_expected_output", "path": str(disposition_path), "detail": "checkpoint decision output is required"})
        text = ""
    else:
        text = disposition_path.read_text(encoding="utf-8")
    model_match = re.search(r"(?im)^\s*(reviewer[_ -]?model(?:_id)?|model[_ -]?id)\s*:\s*(.+?)\s*$", text)
    structured_model = str(structured_disposition.get("reviewer_model_id") or "").strip()
    if structured_model:
        reviewer_model = structured_model
    elif not model_match or not model_match.group(2).strip():
        issues.append({"code": "missing_reviewer_identity", "path": str(disposition_json_path if structured_disposition else disposition_path)})
        reviewer_model = ""
    else:
        reviewer_model = model_match.group(2).strip()
    disposition_match = re.search(r"(?im)^\s*disposition\s*:\s*([a-zA-Z0-9_-]+)\s*$", text)
    structured_value = str(structured_disposition.get("disposition") or "").strip().lower()
    if structured_value:
        disposition = structured_value
    elif decision_required and not disposition_match:
        issues.append({"code": "invalid_disposition", "path": str(disposition_json_path if structured_disposition else disposition_path), "detail": "missing disposition field"})
        disposition = ""
    else:
        disposition = disposition_match.group(1).strip().lower() if disposition_match else ""
    allowed = [str(item).lower() for item in manifest.get("allowed_dispositions") or []]
    if disposition and allowed and disposition not in allowed:
        issues.append({"code": "invalid_disposition", "path": str(disposition_json_path if structured_disposition else disposition_path), "detail": disposition})
    disallowed_families = [str(item).lower() for item in manifest.get("disallowed_reviewer_model_families") or []]
    if reviewer_model:
        reviewer_lower = reviewer_model.lower()
        for family in disallowed_families:
            if family and family in reviewer_lower:
                issues.append({"code": "same_model_disallowed", "path": str(disposition_json_path if structured_disposition else disposition_path), "detail": reviewer_model})
    # W4 fix (gates review): the self-reported reviewer_model_id can be
    # mis-stated; cross-check against the live stream-captured
    # observed_model from the runner. Flag (a) observed_model in a
    # disallowed family and (b) observed_model that disagrees with
    # the self-reported reviewer_model_id.
    #
    # Verify-gates Warning 4 refinement: observed_model often carries a
    # date suffix (e.g., claude-opus-4-7-20251031) while reviewer_model_id
    # is typically the bare model id (claude-opus-4-7). Direct equality
    # after lower() would false-positive every time a dated model lands.
    # Treat the two as agreeing when one is a prefix of the other under
    # the canonical hyphen-and-numbers naming convention.
    observed_model = str(manifest.get("claude", {}).get("observed_model") or "").strip()
    if observed_model:
        observed_lower = observed_model.lower()
        for family in disallowed_families:
            if family and family in observed_lower:
                issues.append({
                    "code": "same_model_disallowed_observed",
                    "path": str(manifest_path),
                    "detail": f"observed_model={observed_model}",
                })
                break
        if reviewer_model:
            reviewer_lower_norm = reviewer_model.strip().lower()
            # Allow either ordering; reviewer_lower_norm == observed_lower
            # also passes both startswith checks.
            agrees = (
                observed_lower.startswith(reviewer_lower_norm)
                or reviewer_lower_norm.startswith(observed_lower)
            )
            if not agrees:
                issues.append({
                    "code": "reviewer_observed_model_mismatch",
                    "path": str(manifest_path),
                    "detail": f"reviewer_model_id={reviewer_model} observed_model={observed_model}",
                })

verify = {
    "run_id": manifest.get("run_id"),
    "status": "ok" if not issues else "fail",
    "required_outputs": output_status,
    "allowed_write_roots": [str(path) for path in allowed_roots],
    "issues": issues,
}
(run_dir / "VERIFY.json").write_text(json.dumps(verify, indent=2) + "\n", encoding="utf-8")
raise SystemExit(0 if not issues else 1)
PY
