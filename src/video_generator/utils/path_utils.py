"""
Path and executable utility functions.
"""

import os
from pathlib import Path
from typing import Optional, List, Union

def get_tool_path(tool_name: str, settings=None) -> Path:
    """Get the path for a specific tool."""
    if settings is None:
        from ..config import settings

    tool_paths = {
        "ffmpeg": settings.ffmpeg_exe,
        "ffprobe": settings.ffprobe_exe,
        "yt-dlp": settings.ytdlp_exe,
    }

    if tool_name in tool_paths:
        return tool_paths[tool_name]

    return settings.tools_dir / tool_name

def find_executable(name: str, paths: Optional[List[Union[str, Path]]] = None) -> Optional[Path]:
    """
    Find an executable in PATH or specified paths.

    Args:
        name: Executable name
        paths: Optional list of paths to search

    Returns:
        Path to executable or None if not found
    """
    if paths:
        for path in paths:
            candidate = Path(path) / name
            if candidate.exists() and candidate.stat().st_size > 0:
                return candidate

    return which(name)

def which(name: str) -> Optional[Path]:
    """
    Find executable in system PATH.

    Args:
        name: Executable name

    Returns:
        Path to executable or None if not found
    """
    if os.name == "nt":
        name = name + ".exe"

    if Path(name).is_absolute() and Path(name).exists():
        return Path(name)

    path_env = os.environ.get("PATH", "")
    for path in path_env.split(os.pathsep):
        candidate = Path(path) / name
        if candidate.exists():
            return candidate

    return None
