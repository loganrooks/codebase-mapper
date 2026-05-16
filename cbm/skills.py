from __future__ import annotations

from pathlib import Path

from cbm import skill_loader


class SkillNotFoundError(FileNotFoundError):
    pass


def load_skill(name: str, repo: Path | None = None) -> dict[str, str | Path]:
    # Verify-gates S12 fix: previously this wrapper dropped the `repo`
    # argument and called skill_loader.load_skill(name) without it.
    # skill_loader's resolution order is CBM_SKILL_DIR -> repo/skills ->
    # source_root/skills -> package, so external callers via
    # cbm.skills.load_skill could never resolve a repo-local skill
    # override even though internal cli.py callers (which pass repo
    # directly to skill_loader.load_skill) could. The two public entry
    # points are now consistent.
    try:
        loaded = skill_loader.load_skill(name, repo=repo)
    except FileNotFoundError as exc:
        raise SkillNotFoundError(str(exc)) from exc
    return {
        "name": loaded.name,
        "path": Path(loaded.path) if not loaded.path.startswith("package://") else loaded.path,
        "sha256": loaded.sha256,
        "body": loaded.body,
    }
