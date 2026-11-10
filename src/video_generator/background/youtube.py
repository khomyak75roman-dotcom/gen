import logging
import re
from pathlib import Path
from typing import Optional

from video_generator.background.base import BackgroundProvider, BackgroundResult
from video_generator.utils.file_utils import download_file, ensure_directory
from video_generator.utils.path_utils import get_executable
from video_generator.utils.subprocess_utils import run_async

logger = logging.getLogger(__name__)

class YouTubeProvider(BackgroundProvider):
    @classmethod
    def get_name(cls) -> str:
        return "youtube"

    @classmethod
    def validate_url(cls, url: str) -> bool:
        pattern = r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+"
        return re.match(pattern, url) is not None

    async def generate(
        self,
        output_path: Path,
        width: int,
        height: int,
        duration: float,
        url: str,
        **kwargs,
    ) -> BackgroundResult:
        ensure_directory(output_path.parent)

        if not self.validate_url(url):
            return BackgroundResult(
                image_path=output_path,
                duration=duration,
                success=False,
                error_message="Invalid YouTube URL",
            )

        yt_dlp = get_executable("yt-dlp")

        try:
            temp_video = output_path.parent / f"{output_path.stem}_temp.mp4"

            cmd = [
                str(yt_dlp),
                "-f",
                "bestvideo[height<=?1080]+bestaudio/best[height<=?1080]",
                "--no-check-certificate",
                "-o",
                str(temp_video),
                url,
            ]

            result = await run_async(cmd, timeout=300)
            if result.returncode != 0:
                raise Exception(f"yt-dlp failed: {result.stderr}")

            if not temp_video.exists():
                raise Exception("Video file not created")

            final_video = output_path.with_suffix(".mp4")
            temp_video.rename(final_video)

            return BackgroundResult(
                video_path=final_video,
                duration=duration,
            )
        except Exception as e:
            logger.error(f"YouTube background generation failed: {e}")
            return BackgroundResult(
                image_path=output_path,
                duration=duration,
                success=False,
                error_message=str(e),
            )
