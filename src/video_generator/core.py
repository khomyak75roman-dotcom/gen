"""
Core video generator implementation.
"""

import asyncio
import json
import os
import re
import shutil
import subprocess
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable, Tuple

from .config import settings
from .models import (
    VideoConfig,
    Scene,
    ProjectState,
    GenerationMode,
    VideoGenerationError,
)
from .utils import (
    ensure_directory,
    download_file,
    get_file_size,
    remove_file,
    get_tool_path,
    run_command,
    get_logger,
    split_sentences,
    format_duration,
)
from .tts.edge_tts import EdgeTTSProvider
from .background.gradient import GradientBackgroundProvider

logger = get_logger(__name__)

class VideoGenerator:
    """
    Main video generator class.

    Handles the complete video generation pipeline:
    1. Script parsing/generation
    2. TTS voice generation
    3. Background generation
    4. Subtitle creation
    5. Final rendering
    """

    def __init__(self, config: Optional[VideoConfig] = None):
        """
        Initialize the video generator.

        Args:
            config: Optional video configuration
        """
        self.config = config or VideoConfig()
        self._workdir: Optional[Path] = None
        self._state: Optional[ProjectState] = None
        self._progress_callbacks: List[Callable[[str], None]] = []

    @property
    def workdir(self) -> Path:
        """Get current working directory."""
        if self._workdir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._workdir = settings.gen_base / timestamp
            ensure_directory(self._workdir)
        return self._workdir

    @property
    def state(self) -> ProjectState:
        """Get current project state."""
        if self._state is None:
            self._state = ProjectState(
                mode=self.config.mode,
                theme="",
                voice=self.config.voice_label,
                size=self.config.size,
                subs=self.config.include_subtitles,
                cover=self.config.include_cover,
                workdir=self.workdir,
            )
        return self._state

    def on_progress(self, callback: Callable[[str], None]) -> None:
        """Register a progress callback."""
        self._progress_callbacks.append(callback)

    def _emit_progress(self, message: str) -> None:
        """Emit progress message to all callbacks."""
        logger.info(message)
        for cb in self._progress_callbacks:
            try:
                cb(message)
            except Exception:
                pass

    def parse_script(self, text: str) -> List[Scene]:
        """
        Parse a script into scenes.

        Args:
            text: Script text with scene markers

        Returns:
            List of Scene objects
        """
        scenes = []

        # Split by scene markers (number followed by dot or parenthesis)
        pattern = r"^\s*(\d+)[.)]\s+(.+)$"

        for line in text.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

            match = re.match(pattern, line, re.MULTILINE)
            if match:
                # This is a scene marker
                scenes.append(Scene(text=match.group(2).strip()))
            elif scenes:
                # Continue previous scene
                scenes[-1].text = scenes[-1].text + "\n" + line
            else:
                # Single scene
                scenes.append(Scene(text=line))

        if not scenes:
            scenes.append(Scene(text=text))

        return scenes

    def generate_script_from_theme(self, theme: str) -> Tuple[List[Scene], str]:
        """
        Generate a script from a theme using AI.

        Args:
            theme: Theme/topic for the video

        Returns:
            Tuple of (scenes, source)
        """
        # For now, create a simple script
        # In the future, this will use LLM to generate scenes
        scenes = [
            Scene(
                text=f"Вітаю! Сьогодні ми поговоримо про {theme}.",
                query=theme,
            ),
            Scene(
                text=f"{theme} - це дуже цікава тема. Давайте розберемо її детальніше.",
                query=f"{theme} details",
            ),
            Scene(
                text=f"Ось кілька важливих аспектів про {theme}.",
                query=f"{theme} aspects",
            ),
            Scene(
                text=f"На завершення, хочеться сказати, що {theme} - це те, що варто вивчати.",
                query=f"{theme} conclusion",
            ),
        ]

        return scenes, "AI-generated from theme"
