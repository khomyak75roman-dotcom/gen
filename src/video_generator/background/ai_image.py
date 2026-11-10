import logging
from pathlib import Path
from typing import Optional

import requests

from video_generator.background.base import BackgroundProvider, BackgroundResult
from video_generator.config import settings
from video_generator.utils.file_utils import ensure_directory

logger = logging.getLogger(__name__)

class AIImageProvider(BackgroundProvider):
    @classmethod
    def get_name(cls) -> str:
        return "ai_image"

    async def generate(
        self,
        output_path: Path,
        width: int,
        height: int,
        duration: float,
        prompt: str = "",
        **kwargs,
    ) -> BackgroundResult:
        ensure_directory(output_path.parent)

        if not prompt:
            prompt = "abstract background, minimalistic, gradient colors"

        try:
            api_key = settings.AI_IMAGE_API_KEY
            if not api_key:
                return BackgroundResult(
                    image_path=output_path,
                    duration=duration,
                    success=False,
                    error_message="AI Image API key not configured",
                )

            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

            payload = {
                "text_prompts": [{"text": prompt}],
                "cfg_scale": 7,
                "height": height,
                "width": width,
                "steps": 30,
            }

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "image/png",
            }

            response = requests.post(url, json=payload, headers=headers, timeout=120)
            response.raise_for_status()

            with open(str(output_path), "wb") as f:
                f.write(response.content)

            return BackgroundResult(
                image_path=output_path,
                duration=duration,
            )
        except Exception as e:
            logger.error(f"AI Image generation failed: {e}")
            return BackgroundResult(
                image_path=output_path,
                duration=duration,
                success=False,
                error_message=str(e),
            )
