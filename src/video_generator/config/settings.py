"""
Application settings using Pydantic Settings Management.
"""

import os
from pathlib import Path
from typing import Tuple, Dict, List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Video Generator 4.0"
    app_version: str = "4.0.0"
    app_author: str = "khomyak75roman-dotcom"

    # Directories
    app_dir: Path = Field(
        default=Path(os.path.expanduser("~")) / "AppData" / "Local" / "VideoGenerator",
        description="Base application directory"
    )
    tools_dir: Path = Field(
        default=Path(os.path.expanduser("~")) / "AppData" / "Local" / "VideoGenerator" / "tools",
        description="Directory for external tools (ffmpeg, yt-dlp)"
    )
    gen_base: Path = Field(
        default=Path(os.path.expanduser("~")) / "Videos" / "Generated",
        description="Base directory for generated videos"
    )
    ai_cache_dir: Path = Field(
        default=Path(os.path.expanduser("~")) / "AppData" / "Local" / "VideoGenerator" / "aicache",
        description="Cache directory for AI-generated content"
    )
    ai_cache_max_files: int = 60

    # Video sizes
    video_sizes: Dict[str, Tuple[int, int]] = {
        "1080p": (1920, 1080),
        "720p": (1280, 720),
        "Shorts (9:16)": (1080, 1920),
        "4K": (3840, 2160),
        "Square": (1080, 1080),
    }

    # Scene limits
    max_scenes: int = 12

    # TTS Voices
    voices: Dict[str, str] = {
        "Остап": "uk-UA-OstapNeural",
        "Поліна": "uk-UA-PolinaNeural",
        "Christopher (EN)": "en-US-ChristopherNeural",
        "Jenny (EN)": "en-US-JennyNeural",
        "Ryan (UK)": "en-GB-RyanNeural",
        "Sonia (UK)": "en-GB-SoniaNeural",
        "Marek (PL)": "pl-PL-MarekNeural",
        "Katja (DE)": "de-DE-KatjaNeural",
    }

    # External API endpoints
    pollinations_url: str = "https://text.pollinations.ai"
    llm7_url: str = "https://api.llm7.io/v1"
    kilo_url: str = "https://api.kilo.ai/api/gateway"

    hf_spaces: Dict[str, str] = {
        "img": "https://evalstate-flux1-schnell.hf.space",
        "vid": "https://zerogpu-aoti-wan2-2-fp8da-aoti-faster.hf.space",
    }

    cobalt_instances: List[str] = [
        "https://cobalt-api.kwiatekmiki.com",
        "https://cobalt-api.meowing.de",
    ]

    libre_instances: List[str] = [
        "https://translate.cutie.dating",
        "https://translate.fedilab.app",
        "https://libretranslate.de",
        "https://libretranslate.com",
    ]

    # Tool URLs
    ytdlp_url: str = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
    ffmpeg_sources: List[str] = [
        "https://github.com/BtbN/FFmpeg-Builds/releases/latest/download/ffmpeg-master-latest-win64-gpl.zip",
        "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
    ]

    # User Agent strings
    ua_string: str = "VideoGenerator/4.0 (https://github.com/khomyak75roman-dotcom/video-generator)"
    web_ua: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
    )

    # FFmpeg paths
    ffmpeg_exe: Path = Field(
        default=Path(os.path.expanduser("~")) / "AppData" / "Local" / "VideoGenerator" / "ffmpeg.exe",
        description="Path to ffmpeg executable"
    )
    ffprobe_exe: Path = Field(
        default=Path(os.path.expanduser("~")) / "AppData" / "Local" / "VideoGenerator" / "ffprobe.exe",
        description="Path to ffprobe executable"
    )
    ytdlp_exe: Path = Field(
        default=Path(os.path.expanduser("~")) / "AppData" / "Local" / "VideoGenerator" / "yt-dlp.exe",
        description="Path to yt-dlp executable"
    )

    # Subtitle styling
    sub_style: str = (
        "subtitles=sub.srt:force_style='FontName=Arial,FontSize=13,"
        "PrimaryColour=&H00FFFFFF,OutlineColour=&H80000000,BorderStyle=1,"
        "Outline=2,Shadow=1,MarginV=36'"
    )

    # Pipeline stages
    stages: Tuple[str, ...] = (
        "start", "script", "voice", "subtitles", "background", "render", "done"
    )

    @field_validator("app_dir", "tools_dir", "gen_base", "ai_cache_dir")
    @classmethod
    def _ensure_paths_exist(cls, v: Path) -> Path:
        """Ensure directories exist on validation."""
        v.mkdir(parents=True, exist_ok=True)
        return v

    def get_tool_path(self, tool_name: str) -> Path:
        """Get the path for a specific tool."""
        tool_paths = {
            "ffmpeg": self.ffmpeg_exe,
            "ffprobe": self.ffprobe_exe,
            "yt-dlp": self.ytdlp_exe,
        }
        return tool_paths.get(tool_name, self.tools_dir / tool_name)

# Global settings instance
settings = Settings()
