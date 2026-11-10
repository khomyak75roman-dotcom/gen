import logging
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from video_generator.tts.base import TTSProvider, TTSResult
from video_generator.utils.file_utils import ensure_directory
from video_generator.utils.subprocess_utils import run_sync

logger = logging.getLogger(__name__)

class SAPIProvider(TTSProvider):
    @classmethod
    def get_name(cls) -> str:
        return "sapi"

    def get_available_voices(self) -> list[str]:
        try:
            result = run_sync(
                ["powershell", "-Command", "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).GetInstalledVoices() | % { $_.VoiceInfo.Name }"],
                capture_output=True,
                text=True,
            )
            voices = result.stdout.strip().split("\n")
            return [v.strip() for v in voices if v.strip()]
        except Exception as e:
            logger.warning(f"Failed to get SAPI voices: {e}")
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
            with tempfile.NamedTemporaryFile(suffix=".ps1", delete=False, mode="w", encoding="utf-8") as f:
                speed_param = ""
                if speed is not None:
                    speed_param = f" -Rate {int(speed * 10)}"

                script = f"""
$speech = New-Object System.Speech.Synthesis.SpeechSynthesizer
$speech.SelectVoice("{voice}")
$speech.Rate = {int(speed * 10) if speed else 0}
$speech.SetOutputToAudioStream([System.IO.File]::Create("{output_path.resolve()}"), [System.Speech.AudioFormat.SpeechAudioFormatInfo]::new(44100, 16, 2, [System.Speech.AudioFormat.AudioChannel]::Stereo))
$speech.Speak("{text.replace('"', '""')}")
$speech.Close()
"""
                f.write(script)
                temp_script = f.name

            result = await run_async(["powershell", "-ExecutionPolicy", "Bypass", "-File", temp_script])
            if result.returncode != 0:
                raise Exception(f"SAPI generation failed: {result.stderr}")

            os.unlink(temp_script)

            duration = await self._get_audio_duration(output_path)

            return TTSResult(
                audio_path=output_path,
                duration=duration,
                voice=voice,
                language="en",
            )
        except Exception as e:
            logger.error(f"SAPI generation failed: {e}")
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
