from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class TTSResult:
    audio_path: Path
    duration: float
    voice: str
    language: str
    success: bool = True
    error_message: Optional[str] = None

class TTSProvider(ABC):
    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        pass

    @abstractmethod
    async def generate(
        self,
        text: str,
        voice: str,
        output_path: Path,
        speed: Optional[float] = None,
    ) -> TTSResult:
        pass

    @abstractmethod
    def get_available_voices(self) -> list[str]:
        pass
