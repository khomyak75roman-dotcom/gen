"""
File utility functions.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Any, List, Optional, Union

import requests

def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure a directory exists, create if necessary."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def download_file(
    url: str,
    destination: Union[str, Path],
    timeout: int = 300,
    headers: Optional[dict] = None,
    chunk_size: int = 1 << 18,
    progress_callback=None,
) -> Path:
    """
    Download a file from URL with progress tracking.
    """
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    temp_path = Path(str(destination) + ".part")

    headers = headers or {}
    headers.setdefault("User-Agent", "VideoGenerator/4.0")

    with requests.get(url, stream=True, timeout=timeout, headers=headers) as response:
        response.raise_for_status()
        total_size = int(response.headers.get("Content-Length", 0))

        with open(temp_path, "wb") as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback and total_size:
                        progress_callback(downloaded, total_size)

        os.replace(temp_path, destination)

    return destination

def get_file_size(path: Union[str, Path]) -> int:
    """Get file size in bytes."""
    path = Path(path)
    if not path.exists():
        return 0
    return path.stat().st_size

def remove_file(path: Union[str, Path]) -> bool:
    """Remove a file, return True if successful."""
    path = Path(path)
    try:
        if path.exists():
            path.unlink()
        return True
    except OSError:
        return False

def list_files(
    directory: Union[str, Path],
    pattern: str = "*",
    recursive: bool = False,
) -> List[Path]:
    """List files in a directory matching a pattern."""
    directory = Path(directory)
    if not directory.exists():
        return []

    if recursive:
        return list(directory.rglob(pattern))
    return list(directory.glob(pattern))

def write_json(path: Union[str, Path], data: Any, indent: int = 2) -> None:
    """Write data as JSON to a file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
