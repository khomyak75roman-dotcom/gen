import asyncio
import logging
from pathlib import Path
from typing import Optional

import edge_tts
from edge_tts import Communicate, VoicesManager

from video_generator.models.exceptions import TTSError
from video_generator.tts.base import TTSProvider, TTSResult
from video_generator.utils.file_utils import ensure_directory
from video_generator.utils.subprocess_utils import run_async

logger = logging.getLogger(__name__)

class EdgeTTSProvider(TTSProvider):
    _voices_manager: Optional[VoicesManager] = None

    @classmethod
    def get_name(cls) -> str:
        return "edge-tts"

    @classmethod
    async def _get_voices_manager(cls) -> VoicesManager:
        if cls._voices_manager is None:
            cls._voices_manager = VoicesManager()
            await cls._voices_manager.reload_data()
        return cls._voices_manager

    def get_available_voices(self) -> list[str]:
        try:
            voices = asyncio.run(self._get_voices_manager())
            return [v["Name"] for v in voices.find()]
        except Exception as e:
            logger.warning(f"Failed to load EdgeTTS voices: {e}")
            return []

    async def generate(
        self,
        text: str,
        voice: str,
        output_path: Path,
        speed: Optional[float] = None,
    ) -> TTSResult:
        ensure_directory(output_path.parent)

        try:
            communicate = Communicate(text, voice)
            if speed is not None:
                communicate = communicate.with_rate(speed)

            await communicate.save(str(output_path))

            duration = await self._get_audio_duration(output_path)

            return TTSResult(
                audio_path=output_path,
                duration=duration,
                voice=voice,
                language=voice.split("-")[0] if "-" in voice else "en",
            )
        except Exception as e:
            logger.error(f"EdgeTTS generation failed: {e}")
            return TTSResult(
                audio_path=output_path,
                duration=0.0,
                voice=voice,
                language="en",
                success=False,
                error_message=str(e),
            )

    async def _get_audio_duration(self, audio_path: Path) -> float:
        try:
            result = await run_async(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(audio_path)],
                capture_output=True,
                text=True,
            )
            return float(result.stdout.strip())
        except Exception as e:
            logger.warning(f"Could not get audio duration: {e}")
            return 0.0
