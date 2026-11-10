"""
Core video generator implementation.
"""

import asyncio
import json
import os
import re
import shutil
import subprocess
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable, Tuple

from .config import settings
from .models import (
    VideoConfig,
    Scene,
    ProjectState,
    GenerationMode,
    VideoGenerationError,
)
from .utils import (
    ensure_directory,
    download_file,
    get_file_size,
    remove_file,
    get_tool_path,
    run_command,
    get_logger,
    split_sentences,
    format_duration,
)
from .tts.edge_tts import EdgeTTSProvider
from .background.gradient import GradientBackgroundProvider

logger = get_logger(__name__)

class VideoGenerator:
    """
    Main video generator class.

    Handles the complete video generation pipeline:
    1. Script parsing/generation
    2. TTS voice generation
    3. Background generation
    4. Subtitle creation
    5. Final rendering
    """

    def __init__(self, config: Optional[VideoConfig] = None):
        """
        Initialize the video generator.

        Args:
            config: Optional video configuration
        """
        self.config = config or VideoConfig()
        self._workdir: Optional[Path] = None
        self._state: Optional[ProjectState] = None
        self._progress_callbacks: List[Callable[[str], None]] = []

    @property
    def workdir(self) -> Path:
        """Get current working directory."""
        if self._workdir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._workdir = settings.gen_base / timestamp
            ensure_directory(self._workdir)
        return self._workdir

    @property
    def state(self) -> ProjectState:
        """Get current project state."""
        if self._state is None:
            self._state = ProjectState(
                mode=self.config.mode,
                theme="",
                voice=self.config.voice_label,
                size=self.config.size,
                subs=self.config.include_subtitles,
                cover=self.config.include_cover,
                workdir=self.workdir,
            )
        return self._state

    def on_progress(self, callback: Callable[[str], None]) -> None:
        """Register a progress callback."""
        self._progress_callbacks.append(callback)

    def _emit_progress(self, message: str) -> None:
        """Emit progress message to all callbacks."""
        logger.info(message)
        for cb in self._progress_callbacks:
            try:
                cb(message)
            except Exception:
                pass

    def parse_script(self, text: str) -> List[Scene]:
        """
        Parse a script into scenes.

        Args:
            text: Script text with scene markers

        Returns:
            List of Scene objects
        """
        scenes = []

        # Split by scene markers (number followed by dot or parenthesis)
        pattern = r"^\s*(\d+)[.)]\s+(.+)$"

        for line in text.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

            match = re.match(pattern, line, re.MULTILINE)
            if match:
                # This is a scene marker
                scenes.append(Scene(text=match.group(2).strip()))
            elif scenes:
                # Continue previous scene
                scenes[-1].text = scenes[-1].text + "\n" + line
            else:
                # Single scene
                scenes.append(Scene(text=line))

        if not scenes:
            scenes.append(Scene(text=text))

        return scenes

    def generate_script_from_theme(self, theme: str) -> Tuple[List[Scene], str]:
        """
        Generate a script from a theme.

        Args:
            theme: Theme/topic for the video

        Returns:
            Tuple of (scenes, source)
        """
        scenes = [
            Scene(
                text=f"Вітаю! Сьогодні ми поговоримо про {theme}.",
                query=theme,
            ),
            Scene(
                text=f"{theme} - це дуже цікава тема. Давайте розберемо її детальніше.",
                query=f"{theme} details",
            ),
            Scene(
                text=f"Ось кілька важливих аспектів про {theme}.",
                query=f"{theme} aspects",
            ),
            Scene(
                text=f"На завершення, хочеться сказати, що {theme} - це те, що варто вивчати.",
                query=f"{theme} conclusion",
            ),
        ]
        return scenes, "Generated from theme"

    async def generate_voice(
        self,
        scenes: List[Scene],
        voice: str,
    ) -> Tuple[List[Path], List[float]]:
        """
        Generate voiceovers for all scenes.

        Args:
            scenes: List of scenes
            voice: Voice identifier

        Returns:
            Tuple of (audio paths, durations)
        """
        tts = EdgeTTSProvider()

        if not tts.is_available():
            raise VideoGenerationError("TTS provider not available")

        audio_paths = []
        durations = []

        for i, scene in enumerate(scenes):
            output_path = self.workdir / f"voice_{i:02d}.mp3"
            self._emit_progress(f"Generating voice for scene {i+1}/{len(scenes)}...")
            result = await tts.generate(
                text=scene.text,
                voice=voice,
                output_path=output_path,
                rate_pct=0.0,
            )
            audio_paths.append(result.audio_path)
            durations.append(result.duration)
            scene.voice_path = result.audio_path
            scene.duration = result.duration
            self._emit_progress(f"Scene {i+1} voice: {result.duration:.1f}s")

        return audio_paths, durations

    def concat_audio(self, audio_paths: List[Path], output_path: Path) -> Path:
        """
        Concatenate multiple audio files.

        Args:
            audio_paths: List of audio file paths
            output_path: Output concatenated audio path

        Returns:
            Output path
        """
        ffmpeg = get_tool_path("ffmpeg")

        list_path = self.workdir / "audio_list.txt"
        with open(list_path, "w", encoding="utf-8") as f:
            for path in audio_paths:
                f.write(f"file '{path}'\n")

        cmd = [
            str(ffmpeg),
            "-y", "-hide_banner", "-nostdin",
            "-f", "concat", "-safe", "0",
            "-i", str(list_path),
            "-c", "copy",
            str(output_path),
        ]
        run_command(cmd)
        list_path.unlink(missing_ok=True)
        return output_path

    async def generate_backgrounds(
        self,
        scenes: List[Scene],
        durations: List[float],
        width: int,
        height: int,
    ) -> List[Path]:
        """
        Generate background videos for all scenes.

        Args:
            scenes: List of scenes
            durations: List of scene durations
            width: Video width
            height: Video height

        Returns:
            List of background video paths
        """
        provider = GradientBackgroundProvider()
        bg_paths = []

        for i, (scene, duration) in enumerate(zip(scenes, durations)):
            output_path = self.workdir / f"pseg{i:02d}.mp4"
            self._emit_progress(f"Generating background for scene {i+1}...")
            result = await provider.generate(
                query=scene.query or scene.text[:50],
                duration=duration + 0.05,
                width=width,
                height=height,
                output_dir=self.workdir,
                index=i,
                progress_callback=lambda msg: self._emit_progress(msg),
            )
            bg_paths.append(result.video_path)
            scene.background_path = result.video_path
            scene.background_source = result.source
            self._emit_progress(f"Scene {i+1} background: {result.source}")

        return bg_paths

    def create_subtitles(self, scenes: List[Scene], durations: List[float]) -> Path:
        """
        Create SRT subtitles file.

        Args:
            scenes: List of scenes
            durations: List of scene durations

        Returns:
            Path to SRT file
        """
        sub_path = self.workdir / "sub.srt"
        lines = []
        time_offset = 0.0

        for i, (scene, duration) in enumerate(zip(scenes, durations)):
            sentences = split_sentences(scene.text)
            if not sentences:
                sentences = [scene.text]

            weights = [max(len(s.split()), 1) for s in sentences]
            total_weight = sum(weights)
            scale = duration / total_weight if total_weight > 0 else duration / max(len(sentences), 1)

            start_time = time_offset
            for j, (sentence, weight) in enumerate(zip(sentences, weights)):
                end_time = min(start_time + weight * scale, time_offset + duration)
                start_str = format_duration(start_time)
                end_str = format_duration(end_time)
                lines.append(f"{len(lines) + 1}\n{start_str} --> {end_str}\n{sentence}\n")
                start_time = end_time

            time_offset += duration

        with open(sub_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return sub_path

    def render_final_video(
        self,
        bg_paths: List[Path],
        audio_path: Path,
        subtitles_path: Optional[Path] = None,
        width: int = 1920,
        height: int = 1080,
    ) -> Path:
        """
        Render the final video with backgrounds, audio, and subtitles.

        Args:
            bg_paths: List of background video paths
            audio_path: Path to concatenated audio
            subtitles_path: Optional path to subtitles
            width: Video width
            height: Video height

        Returns:
            Path to final video
        """
        ffmpeg = get_tool_path("ffmpeg")
        final_path = self.workdir / "final.mp4"

        concat_list = self.workdir / "bg_list.txt"
        with open(concat_list, "w", encoding="utf-8") as f:
            for path in bg_paths:
                f.write(f"file '{path}'\n")

        bg_concat = self.workdir / "bg_concat.mp4"
        cmd_concat = [
            str(ffmpeg), "-y", "-hide_banner", "-nostdin",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_list),
            "-c", "copy",
            str(bg_concat),
        ]
        run_command(cmd_concat)

        cmd_final = [
            str(ffmpeg), "-y", "-hide_banner", "-nostdin",
            "-i", str(bg_concat),
            "-i", str(audio_path),
        ]

        if subtitles_path and subtitles_path.exists():
            cmd_final.extend(["-vf", settings.sub_style])

        cmd_final.extend([
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            "-pix_fmt", "yuv420p",
            str(final_path),
        ])
        run_command(cmd_final)

        concat_list.unlink(missing_ok=True)
        bg_concat.unlink(missing_ok=True)
        return final_path

    def create_cover(self, title: str) -> Optional[Path]:
        """
        Create a YouTube cover image from the final video.

        Args:
            title: Video title

        Returns:
            Path to cover image or None if failed
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            self._emit_progress("Pillow not installed, skipping cover creation")
            return None

        ffmpeg = get_tool_path("ffmpeg")
        cover_path = self.workdir / "cover.jpg"
        frame_path = self.workdir / "_cover_frame.jpg"

        try:
            cmd = [
                str(ffmpeg), "-y", "-hide_banner", "-nostdin",
                "-ss", "0.7",
                "-i", str(self.workdir / "final.mp4"),
                "-frames:v", "1",
                "-q:v", "2",
                str(frame_path),
            ]
            run_command(cmd, cwd=self.workdir)

            img = Image.open(frame_path).convert("RGB")
            draw = ImageDraw.Draw(img, "RGBA")
            W, H = img.size

            gh = int(H * 0.45)
            for k in range(gh):
                draw.line(
                    [(0, H - gh + k), (W, H - gh + k)],
                    fill=(10, 10, 18, int(210 * (k + 1) / gh))
                )

            font_size = max(24, int(W / 14))
            font = None
            for fp in [
                r"C:\Windows\Fonts\segoeuib.ttf",
                r"C:\Windows\Fonts\arialbd.ttf",
                r"C:\Windows\Fonts\segoeui.ttf",
            ]:
                try:
                    font = ImageFont.truetype(fp, font_size)
                    break
                except Exception:
                    pass

            if font is None:
                raise RuntimeError("No suitable font found")

            clean_title = "".join(ch for ch in title if ord(ch) <= 65535)
            words = clean_title.split()
            text_lines = []
            cur = ""
            for wd in words:
                cand = (cur + " " + wd).strip()
                if cur and draw.textlength(cand, font=font) > W * 0.84:
                    text_lines.append(cur)
                    cur = wd
                else:
                    cur = cand
            if cur:
                text_lines.append(cur)
            text_lines = text_lines[:3]

            lh = int(font_size * 1.3)
            y = H - int(H * 0.06) - lh * len(text_lines)
            for ln in text_lines:
                tw = draw.textlength(ln, font=font)
                draw.text(
                    ((W - tw) / 2, y), ln, font=font, fill=(255, 255, 255, 255),
                    stroke_width=max(2, font_size // 14), stroke_fill=(0, 0, 0, 200)
                )
                y += lh

            img.save(cover_path, quality=90)
            frame_path.unlink()
            self._emit_progress(f"Cover created: cover.jpg")
            return cover_path

        except Exception as e:
            self._emit_progress(f"Cover creation failed: {e}")
            return None

    async def generate(
        self,
        source_text: str,
        mode: str = "theme",
    ) -> Path:
        """
        Generate a complete video from source text.

        Args:
            source_text: Input text (theme or script)
            mode: Generation mode ("theme" or "scenario")

        Returns:
            Path to final video
        """
        self._emit_progress("Starting video generation...")
        self._emit_progress(f"Source: {source_text[:100]}...")

        # 1. Parse/generate script
        self._emit_progress("Processing script...")
        if mode == "theme":
            scenes, source = self.generate_script_from_theme(source_text)
        else:
            scenes = self.parse_script(source_text)
            source = "user script"
            if not scenes:
                raise VideoGenerationError("No scenes found in script")

        if len(scenes) > settings.max_scenes:
            self._emit_progress(f"Too many scenes ({len(scenes)}), truncating to {settings.max_scenes}")
            scenes = scenes[:settings.max_scenes]

        self.state.theme = source_text[:80]
        self.state.scenes = scenes
        self.state.save(self.workdir)

        # 2. Generate voiceovers
        self._emit_progress("Generating voiceovers...")
        audio_paths, durations = await self.generate_voice(
            scenes=scenes,
            voice=self.config.voice,
        )

        audio_path = self.workdir / "voice.mp4"
        self.concat_audio(audio_paths, audio_path)

        # 3. Create subtitles
        if self.config.include_subtitles:
            self._emit_progress("Creating subtitles...")
            sub_path = self.create_subtitles(scenes, durations)
        else:
            sub_path = None

        # 4. Generate backgrounds
        self._emit_progress("Generating backgrounds...")
        width, height = settings.video_sizes.get(self.config.size, (1920, 1080))
        bg_paths = await self.generate_backgrounds(
            scenes=scenes,
            durations=durations,
            width=width,
            height=height,
        )

        # 5. Render final video
        self._emit_progress("Rendering final video...")
        final_path = self.render_final_video(
            bg_paths=bg_paths,
            audio_path=audio_path,
            subtitles_path=sub_path,
            width=width,
            height=height,
        )

        # 6. Create cover
        if self.config.include_cover:
            self._emit_progress("Creating cover...")
            self.create_cover(self.state.theme)

        # 7. Save project state
        self.state.done = True
        self.state.final_path = final_path
        self.state.total_duration = sum(durations)
        self.state.durs = [round(d, 2) for d in durations]
        self.state.save(self.workdir)

        self._emit_progress("Video generation complete!")
        self._emit_progress(f"Output: {final_path}")
        self._emit_progress(f"Duration: {sum(durations):.1f}s")

        return final_path

    def ensure_ffmpeg(self) -> None:
        """Ensure ffmpeg and ffprobe are available."""
        if get_tool_path("ffmpeg").exists():
            return

        self._emit_progress("Downloading ffmpeg...")

        ensure_directory(settings.tools_dir)
        zip_path = settings.tools_dir / "ffmpeg.zip"

        for url in settings.ffmpeg_sources:
            try:
                download_file(
                    url,
                    zip_path,
                    timeout=300,
                    headers={"User-Agent": settings.ua_string},
                )

                import zipfile
                with zipfile.ZipFile(zip_path) as z:
                    names = [n for n in z.namelist() if n.endswith("bin/ffmpeg.exe")]
                    if not names:
                        continue

                    with z.open(names[0]) as src, open(settings.ffmpeg_exe, "wb") as dst:
                        shutil.copyfileobj(src, dst)

                    pn = [n for n in z.namelist() if n.endswith("bin/ffprobe.exe")]
                    if pn:
                        with z.open(pn[0]) as src, open(settings.ffprobe_exe, "wb") as dst:
                            shutil.copyfileobj(src, dst)

                zip_path.unlink()
                self._emit_progress("ffmpeg installed successfully")
                return
            except Exception as e:
                self._emit_progress(f"Failed to download from {url}: {e}")
                continue

        raise VideoGenerationError("Failed to install ffmpeg")
