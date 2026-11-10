"""
Video Generator 4.0 - Modern AI-Powered Video Creation Tool

A complete rebuild with clean architecture, async patterns, and modern Python practices.
"""

__version__ = "4.0.0"
__author__ = "khomyak75roman-dotcom"

from .config import settings
from .models import VideoConfig, Scene, ProjectState, GenerationMode
from .pipeline import VideoPipeline
from .core import VideoGenerator

__all__ = [
    "__version__",
    "settings",
    "VideoConfig",
    "Scene",
    "ProjectState",
    "GenerationMode",
    "VideoPipeline",
    "VideoGenerator",
]
