from __future__ import annotations

from pathlib import Path

from cbm import skill_loader


class SkillNotFoundError(FileNotFoundError):
    pass


def load_skill(name: str) -> dict[str, str | Path]:
    try:
        loaded = skill_loader.load_skill(name)
    except FileNotFoundError as exc:
        raise SkillNotFoundError(str(exc)) from exc
    return {
        "name": loaded.name,
        "path": Path(loaded.path) if not loaded.path.startswith("package://") else loaded.path,
        "sha256": loaded.sha256,
        "body": loaded.body,
    }
