"""
Video generation pipeline module.

Handles the complete video generation workflow including:
- State management
- Progress tracking
- Resume functionality
"""

import asyncio
import json
import logging
import os
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

from video_generator.config import settings
from video_generator.models.base import GenerationMode, ProjectState, Scene, VideoConfig
from video_generator.models.exceptions import VideoGenerationError
from video_generator.utils.file_utils import ensure_directory, write_json
from video_generator.utils.logging import get_logger

logger = get_logger(__name__)

class VideoPipeline:
    """
    Manages the video generation pipeline state and progress.

    Attributes:
        state: Current project state
        output_dir: Output directory for generated files
    """

    def __init__(self) -> None:
        """Initialize the pipeline with empty state."""
        self.state: Optional[ProjectState] = None
        self.output_dir: Optional[Path] = None
        self._progress_callbacks: list[Callable[[float, str], None]] = []

    def add_progress_callback(self, callback: Callable[[float, str], None]) -> None:
        """Add a progress callback function.

        Args:
            callback: Function to call with (progress, message) updates
        """
        self._progress_callbacks.append(callback)

    def _notify_progress(self, progress: float, message: str) -> None:
        """Notify all registered callbacks of progress.

        Args:
            progress: Progress percentage (0-100)
            message: Status message
        """
        for cb in self._progress_callbacks:
            try:
                cb(progress, message)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")

    def _get_state_path(self) -> Path:
        """Get the path to the state file.

        Returns:
            Path to project.json

        Raises:
            VideoGenerationError: If output directory is not set
        """
        if self.output_dir is None:
            raise VideoGenerationError("Output directory not set")
        return self.output_dir / "project.json"

    def save_state(self) -> None:
        """Save the current state to disk."""
        if self.state is None or self.output_dir is None:
            return
        ensure_directory(self.output_dir)
        state_path = self._get_state_path()
        write_json(state_path, asdict(self.state))

    def load_state(self, state_path: Path) -> None:
        """Load state from a project.json file.

        Args:
            state_path: Path to the state file
        """
        if not state_path.exists():
            return
        try:
            with open(state_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.state = ProjectState(**data)
        except Exception as e:
            logger.warning(f"Failed to load state: {e}")
            self.state = None

    def create_state(self, config: VideoConfig) -> ProjectState:
        """Create a new project state.

        Args:
            config: Video configuration

        Returns:
            New ProjectState instance
        """
        self.state = ProjectState(
            config=config,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            current_step="",
            completed_steps=[],
            total_steps=0,
            scenes_processed=0,
            errors=[],
        )
        return self.state

    async def initialize(
        self,
        config: VideoConfig,
        output_dir: Path,
        resume: bool = True,
    ) -> tuple[VideoConfig, Path]:
        """Initialize the pipeline with configuration.

        Args:
            config: Video configuration
            output_dir: Output directory
            resume: Whether to attempt resuming a previous session

        Returns:
            Tuple of (config, output_dir)
        """
        self.output_dir = output_dir
        ensure_directory(output_dir)

        if resume:
            state_path = output_dir / "project.json"
            if state_path.exists():
                self.load_state(state_path)
                if self.state and self.state.config.title == config.title:
                    logger.info(f"Resuming project: {config.title}")
                    return config, output_dir

        self.create_state(config)
        self.save_state()
        return config, output_dir

    def get_progress(self) -> tuple[float, str]:
        """Get current progress.

        Returns:
            Tuple of (progress as float 0-1, status message)
        """
        if self.state is None:
            return 0.0, "Not started"

        total = self.state.total_steps or 1
        completed = len(self.state.completed_steps)
        progress = (completed / total) * 100

        if self.state.current_step:
            message = f"{self.state.current_step} ({completed}/{total})"
        else:
            message = f"Processing ({completed}/{total})"

        return progress / 100, message

def find_resume_project(output_dir: Path, title: str) -> Optional[Path]:
    """Find a resumable project by title.

    Args:
        output_dir: Directory to search for projects
        title: Project title to match

    Returns:
        Path to project directory if found, None otherwise
    """
    if not output_dir.exists():
        return None

    for project_dir in output_dir.iterdir():
        if project_dir.is_dir():
            state_path = project_dir / "project.json"
            if state_path.exists():
                try:
                    with open(state_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if data.get("config", {}).get("title") == title:
                        return project_dir
                except Exception:
                    continue
    return None
