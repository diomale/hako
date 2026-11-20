"""Path helpers that do not depend on other HAKO packages."""

from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """Return the repository/project root.

    This file lives at ``<root>/src/hako/utils/paths.py``.
    """
    return Path(__file__).resolve().parents[3]


def resolve_path(value: str | Path, base: Path) -> Path:
    """Resolve a configured path against ``base`` when it is relative."""
    path = Path(value).expanduser()
    return path if path.is_absolute() else base / path


def ensure_parent_dir(path: Path) -> None:
    """Create the parent directory of ``path`` if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
