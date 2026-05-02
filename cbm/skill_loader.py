from __future__ import annotations

import os
import re
import hashlib
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

SKILL_NAME_RE = re.compile(r"^[a-z0-9-]+$")


@dataclass(frozen=True)
class LoadedSkill:
    name: str
    path: str
    sha256: str
    body: str


def load_skill(name: str, repo: Path | None = None) -> LoadedSkill:
    if not SKILL_NAME_RE.fullmatch(name):
        raise ValueError(f"invalid skill name: {name}")
    filename = f"{name}.md"
    search_dirs: list[Path] = []
    if os.environ.get("CBM_SKILL_DIR"):
        search_dirs.append(Path(os.environ["CBM_SKILL_DIR"]))
    if repo is not None:
        search_dirs.append(repo / "skills")
    source_root = Path(__file__).resolve().parents[1]
    search_dirs.append(source_root / "skills")
    for directory in search_dirs:
        path = directory / filename
        if path.exists():
            body = path.read_text(encoding="utf-8")
            return LoadedSkill(name=name, path=str(path), sha256=hashlib.sha256(body.encode("utf-8")).hexdigest(), body=body)
    package_path = resources.files("cbm").joinpath("runtime_skills", filename)
    if package_path.is_file():
        body = package_path.read_text(encoding="utf-8")
        return LoadedSkill(name=name, path=f"package://cbm/runtime_skills/{filename}", sha256=hashlib.sha256(body.encode("utf-8")).hexdigest(), body=body)
    raise FileNotFoundError(f"skill not found: {name}")
