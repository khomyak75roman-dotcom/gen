import logging
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageDraw

from video_generator.background.base import BackgroundProvider, BackgroundResult
from video_generator.utils.file_utils import ensure_directory

logger = logging.getLogger(__name__)

class GradientProvider(BackgroundProvider):
    @classmethod
    def get_name(cls) -> str:
        return "gradient"

    def get_available_gradients(self) -> list[Tuple[str, str, str]]:
        return [
            ("black", "#000000", "#000000"),
            ("white", "#FFFFFF", "#FFFFFF"),
            ("blue_gradient", "#1e3a8a", "#3b82f6"),
            ("purple_gradient", "#7c3aed", "#a855f7"),
            ("green_gradient", "#065f46", "#10b981"),
            ("red_gradient", "#7f1d1d", "#ef4444"),
            ("orange_gradient", "#7c2d12", "#f97316"),
            ("pink_gradient", "#831843", "#ec4899"),
        ]

    async def generate(
        self,
        output_path: Path,
        width: int,
        height: int,
        duration: float,
        gradient_name: str = "black",
        **kwargs,
    ) -> BackgroundResult:
        ensure_directory(output_path.parent)

        gradients = self.get_available_gradients()
        gradient = next((g for g in gradients if g[0] == gradient_name), gradients[0])

        color1, color2 = gradient[1], gradient[2]

        try:
            image = Image.new("RGB", (width, height))
            draw = ImageDraw.Draw(image)

            for y in range(height):
                ratio = y / height
                r = int((int(color1[1:3], 16) * (1 - ratio) + int(color2[1:3], 16) * ratio))
                g = int((int(color1[3:5], 16) * (1 - ratio) + int(color2[3:5], 16) * ratio))
                b = int((int(color1[5:7], 16) * (1 - ratio) + int(color2[5:7], 16) * ratio))
                draw.line([(0, y), (width, y)], fill=(r, g, b))

            image.save(str(output_path))

            return BackgroundResult(
                image_path=output_path,
                duration=duration,
            )
        except Exception as e:
            logger.error(f"Gradient generation failed: {e}")
            return BackgroundResult(
                image_path=output_path,
                duration=duration,
                success=False,
                error_message=str(e),
            )
