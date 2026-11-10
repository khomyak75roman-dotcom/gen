"""
Base data models for Video Generator.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any

class GenerationMode(Enum):
    """Video generation modes."""
    THEME = "theme"      # Generate from a theme/topic
    SCENARIO = "scenario"  # Use predefined script/scenario

@dataclass
class Scene:
    """
    Represents a single scene in the video.
    """
    text: str
    query: Optional[str] = None
    url: Optional[str] = None
    duration: Optional[float] = None
    duration_target: Optional[float] = None
    background_source: Optional[str] = None
    background_path: Optional[Path] = None
    voice_path: Optional[Path] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "text": self.text,
            "q": self.query,
            "url": self.url,
            "dur": self.duration,
            "dur_target": self.duration_target,
            "bg_source": self.background_source,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scene":
        """Create from dictionary."""
        return cls(
            text=data.get("text", ""),
            query=data.get("q") or data.get("query"),
            url=data.get("url"),
            duration=data.get("dur") or data.get("duration"),
            duration_target=data.get("dur_target") or data.get("duration_target"),
            background_source=data.get("bg_source") or data.get("background_source"),
        )

@dataclass
class VideoConfig:
    """
    Configuration for video generation.
    """
    mode: GenerationMode = GenerationMode.THEME
    voice: str = "uk-UA-OstapNeural"
    voice_label: str = "Остап"
    size: str = "1080p"
    width: int = 1920
    height: int = 1080
    include_subtitles: bool = True
    include_cover: bool = True
    use_ai_clips: bool = False

    @property
    def resolution(self) -> tuple[int, int]:
        """Get resolution tuple."""
        return (self.width, self.height)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VideoConfig":
        """Create from dictionary."""
        return cls(
            mode=GenerationMode(data.get("mode", "theme")),
            voice=data.get("voice", "uk-UA-OstapNeural"),
            voice_label=data.get("voice_label", "Остап"),
            size=data.get("size", "1080p"),
            width=data.get("width", 1920),
            height=data.get("height", 1080),
            include_subtitles=data.get("subs", data.get("include_subtitles", True)),
            include_cover=data.get("cover", data.get("include_cover", True)),
            use_ai_clips=data.get("ai_clips", data.get("use_ai_clips", False)),
        )

@dataclass
class ProjectState:
    """
    Represents the state of a video generation project.
    """
    version: str = "4.0.0"
    mode: GenerationMode = GenerationMode.THEME
    theme: str = ""
    voice: str = ""
    size: str = ""
    subs: bool = True
    cover: bool = True
    scenes: List[Scene] = field(default_factory=list)

    # Runtime state
    current_stage: str = "start"
    workdir: Optional[Path] = None
    done: bool = False
    final_path: Optional[Path] = None
    bg_sources: List[str] = field(default_factory=list)
    durs: List[float] = field(default_factory=list)
    total_duration: float = 0.0

    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "mode": self.mode.value,
            "theme": self.theme,
            "voice": self.voice,
            "size": self.size,
            "subs": self.subs,
            "cover": self.cover,
            "scenes": [s.to_dict() for s in self.scenes],
            "current_stage": self.current_stage,
            "done": self.done,
            "final": str(self.final_path) if self.final_path else None,
            "bg_sources": self.bg_sources,
            "durs": self.durs,
            "total": self.total_duration,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], workdir: Optional[Path] = None) -> "ProjectState":
        """Create from dictionary."""
        scenes = [Scene.from_dict(s) for s in data.get("scenes", [])]

        return cls(
            version=data.get("version", "4.0.0"),
            mode=GenerationMode(data.get("mode", "theme")),
            theme=data.get("theme", ""),
            voice=data.get("voice", ""),
            size=data.get("size", ""),
            subs=data.get("subs", True),
            cover=data.get("cover", True),
            scenes=scenes,
            current_stage=data.get("current_stage", "start"),
            workdir=workdir,
            done=data.get("done", False),
            final_path=Path(data["final"]) if data.get("final") else None,
            bg_sources=data.get("bg_sources", []),
            durs=data.get("durs", []),
            total_duration=data.get("total", 0.0),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
        )

    def save(self, workdir: Path) -> None:
        """Save state to project.json."""
        import json
        project_file = workdir / "project.json"
        with open(project_file, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, workdir: Path) -> Optional["ProjectState"]:
        """Load state from project.json."""
        import json
        project_file = workdir / "project.json"
        if not project_file.exists():
            return None
        with open(project_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data, workdir=workdir)
