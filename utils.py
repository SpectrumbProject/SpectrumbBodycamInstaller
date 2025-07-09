"""Utility functions for installing the SpectrumB Bodycam ReShade mod."""

from __future__ import annotations

import os
import shutil
from typing import Callable


# Files and directories bundled with this installer
ITEMS = [
    "dxgi.dll",
    "ReShade.ini",
    "ReShadePreset.ini",
    "reshade-shaders",
    "SpectrumB Bodycam",
]


def get_files_dir() -> str:
    """Return the absolute path to the bundled ``files`` directory."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")


def install_mod(
    target_dir: str,
    backup: bool,
    log: Callable[[str], None],
    progress: Callable[[float], None],
    files_dir: str | None = None,
) -> None:
    """Install the mod to ``target_dir``.

    Parameters
    ----------
    target_dir:
        Destination directory chosen by the user.
    backup:
        If ``True``, existing ReShade files are moved to ``reshade_backup``.
    log:
        Callback used to log status messages.
    progress:
        Callback used to update progress value between 0 and 1.
    files_dir:
        Directory containing the files to copy. Defaults to ``files/`` next to
        this script.
    """

    files_dir = files_dir or get_files_dir()

    total = len(ITEMS)
    step = 1 / total
    progress(0)

    if backup:
        backup_dir = os.path.join(target_dir, "reshade_backup")
        os.makedirs(backup_dir, exist_ok=True)
        for item in ITEMS:
            src = os.path.join(target_dir, item)
            if os.path.exists(src):
                dest = os.path.join(backup_dir, item)
                try:
                    if os.path.isdir(dest):
                        shutil.rmtree(dest)
                    elif os.path.isfile(dest):
                        os.remove(dest)
                except Exception:
                    pass
                try:
                    shutil.move(src, dest)
                    log(f"Backed up {item}")
                except Exception as exc:  # pragma: no cover - runtime feedback
                    log(f"Failed to backup {item}: {exc}")

    for idx, item in enumerate(ITEMS, start=1):
        src = os.path.join(files_dir, item)
        dest = os.path.join(target_dir, item)
        try:
            if os.path.isdir(src):
                shutil.copytree(src, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dest)
            log(f"Copied {item}")
        except Exception as exc:  # pragma: no cover - runtime feedback
            log(f"Failed to copy {item}: {exc}")
        progress(idx * step)

    progress(1)
