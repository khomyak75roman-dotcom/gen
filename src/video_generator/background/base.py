from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class BackgroundResult:
    image_path: Path
    video_path: Optional[Path] = None
    duration: float = 0.0
    success: bool = True
    error_message: Optional[str] = None

class BackgroundProvider(ABC):
    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        pass

    @abstractmethod
    async def generate(
        self,
        output_path: Path,
        width: int,
        height: int,
        duration: float,
        **kwargs,
    ) -> BackgroundResult:
        pass
