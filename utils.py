import os
import shutil
from typing import Callable

# items that need to be copied from the local files directory
ITEMS = [
    "dxgi.dll",
    "ReShade.ini",
    "ReShadePreset.ini",
    "reshade-shaders",
    "SpectrumB Bodycam",
]


def get_files_dir() -> str:
    """Return the absolute path to the bundled files directory."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "files")


def install_mod(
    target_dir: str,
    backup: bool,
    log: Callable[[str], None],
    progress: Callable[[float], None],
    files_dir: str | None = None,
) -> None:
    """Copy mod files to ``target_dir`` and optionally backup existing ones.

    Parameters
    ----------
    target_dir: str
        Destination directory selected by the user.
    backup: bool
        Whether to move existing ReShade files to ``reshade_backup``.
    log: Callable[[str], None]
        Callback used to log status messages.
    progress: Callable[[float], None]
        Callback used to update progress (0..1).
    files_dir: str | None
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
                except Exception as exc:
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
        except Exception as exc:
            log(f"Failed to copy {item}: {exc}")
        progress(idx * step)

    # ensure the bar reaches 100%
    progress(1)
