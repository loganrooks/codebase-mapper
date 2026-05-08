#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover - bare hosts can still write with no spec validation
    yaml = None


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_spec(review_dir: Path) -> dict[str, Any]:
    spec_path = review_dir / "REVIEW-SPEC.md"
    if not spec_path.exists() or yaml is None:
        return {}
    data = yaml.safe_load(spec_path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def parse_bool(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in {"true", "yes", "1"}:
        return True
    if lowered in {"false", "no", "0"}:
        return False
    raise argparse.ArgumentTypeError("must be true or false")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write a structured cross-vendor review disposition.")
    parser.add_argument("review_dir")
    parser.add_argument("--reviewer-model-id", required=True)
    parser.add_argument("--confidence")
    parser.add_argument("--disposition", required=True)
    parser.add_argument("--same-model-fallback", type=parse_bool, default=False)
    parser.add_argument("--status", default="complete")
    args = parser.parse_args(argv)

    review_dir = Path(args.review_dir).resolve()
    if not review_dir.is_dir():
        raise SystemExit(f"review dir not found: {review_dir}")

    spec = load_spec(review_dir)
    allowed = [str(item).lower() for item in spec.get("allowed_dispositions") or []]
    disposition = args.disposition.strip().lower()
    if allowed and disposition not in allowed:
        raise SystemExit(f"invalid disposition '{disposition}'; allowed: {', '.join(allowed)}")

    reviewer_model_id = args.reviewer_model_id.strip()
    confidence = (args.confidence or "").strip()
    if not reviewer_model_id:
        raise SystemExit("--reviewer-model-id must be non-empty")

    payload = {
        "schema_version": 1,
        "review_id": str(spec.get("review_id") or review_dir.name),
        "status": args.status.strip() or "complete",
        "reviewer_model_id": reviewer_model_id,
        "same_model_fallback": bool(args.same_model_fallback),
        "disposition": disposition,
        "decided_at": utc_now(),
    }
    if confidence:
        payload["confidence"] = confidence
    (review_dir / "DISPOSITION.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(review_dir / "DISPOSITION.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
