import asyncio
import logging
import os
import sys
import threading
from functools import partial
from pathlib import Path
from typing import Callable, Optional

import customtkinter as ctk
from PIL import Image, ImageTk

from video_generator.config import settings
from video_generator.core import VideoGenerator
from video_generator.models.base import GenerationMode, Scene, VideoConfig
from video_generator.utils.logging import setup_logging

logger = logging.getLogger(__name__)

class VideoGeneratorApp:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("Video Generator v4.0")
        self.root.geometry("1200x800")

        setup_logging(level=settings.LOG_LEVEL)

        self.generator = VideoGenerator()

        self.current_project_path: Optional[Path] = None
        self.running = False

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self) -> None:
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)

        self.label = ctk.CTkLabel(
            self.sidebar,
            text="Video Generator",
            font=ctk.CTkFont(size=15, weight="bold"),
        )
        self.label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.mode_var = ctk.StringVar(value="theme")
        self.theme_btn = ctk.CTkRadioButton(
            self.sidebar,
            text="Theme Mode",
            variable=self.mode_var,
            value="theme",
            command=self._on_mode_change,
        )
        self.theme_btn.grid(row=1, column=0, padx=20, pady=5, sticky="w")

        self.scenario_btn = ctk.CTkRadioButton(
            self.sidebar,
            text="Scenario Mode",
            variable=self.mode_var,
            value="scenario",
            command=self._on_mode_change,
        )
        self.scenario_btn.grid(row=2, column=0, padx=20, pady=5, sticky="w")

        self.appearance_mode = ctk.StringVar(value="System")
        self.appearance_btn = ctk.CTkOptionMenu(
            self.sidebar,
            variable=self.appearance_mode,
            values=["Light", "Dark", "System"],
            command=self._change_appearance,
        )
        self.appearance_btn.grid(row=4, column=0, padx=20, pady=10)

        self.scaling_mode = ctk.StringVar(value="100%")
        self.scaling_btn = ctk.CTkOptionMenu(
            self.sidebar,
            variable=self.scaling_mode,
            values=["80%", "90%", "100%", "110%", "120%"],
            command=self._change_scaling,
        )
        self.scaling_btn.grid(row=5, column=0, padx=20, pady=5)

        self.main_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.main_frame.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.top_frame = ctk.CTkFrame(self.main_frame)
        self.top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        self.top_frame.grid_columnconfigure(1, weight=1)

        self.title_entry = ctk.CTkEntry(
            self.top_frame,
            placeholder_text="Video Title",
        )
        self.title_entry.grid(row=0, column=0, padx=(0, 10), pady=10, sticky="ew")
        self.top_frame.grid_columnconfigure(0, weight=1)

        self.generate_btn = ctk.CTkButton(
            self.top_frame,
            text="Generate Video",
            command=self._on_generate,
        )
        self.generate_btn.grid(row=0, column=1, padx=10, pady=10)

        self.content_frame = ctk.CTkScrollableFrame(self.main_frame)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.status_bar = ctk.CTkLabel(
            self.main_frame,
            text="Ready",
            anchor="w",
        )
        self.status_bar.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.progress = ctk.CTkProgressBar(self.main_frame)
        self.progress.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.progress.set(0)

        self._setup_theme_mode()
        self._setup_scenario_mode()
        self._show_mode("theme")

    def _setup_theme_mode(self) -> None:
        self.theme_frame = ctk.CTkFrame(self.content_frame)

        ctk.CTkLabel(
            self.theme_frame,
            text="Theme Settings",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(self.theme_frame, text="Theme:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.theme_var = ctk.StringVar(value="motivation")
        self.theme_menu = ctk.CTkOptionMenu(
            self.theme_frame,
            variable=self.theme_var,
            values=["motivation", "business", "education", "technology", "health"],
        )
        self.theme_menu.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.theme_frame, text="Language:").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.lang_var = ctk.StringVar(value="uk-UA")
        self.lang_menu = ctk.CTkOptionMenu(
            self.theme_frame,
            variable=self.lang_var,
            values=["uk-UA", "en-US", "pl-PL"],
        )
        self.lang_menu.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.theme_frame, text="Voice:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.voice_var = ctk.StringVar(value="uk-UA-NataShaNeural")
        self.voice_menu = ctk.CTkOptionMenu(
            self.theme_frame,
            variable=self.voice_var,
            values=["uk-UA-NataShaNeural", "en-US-GuyNeural", "pl-PL-MarekNeural"],
        )
        self.voice_menu.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.theme_frame, text="Duration (min):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.duration_var = ctk.StringVar(value="5")
        self.duration_entry = ctk.CTkEntry(
            self.theme_frame,
            textvariable=self.duration_var,
        )
        self.duration_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.theme_frame, text="Background:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self.bg_var = ctk.StringVar(value="gradient")
        self.bg_menu = ctk.CTkOptionMenu(
            self.theme_frame,
            variable=self.bg_var,
            values=["gradient", "youtube", "ai_image"],
        )
        self.bg_menu.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.theme_frame, text="Gradient:").grid(row=6, column=0, padx=10, pady=5, sticky="e")
        self.gradient_var = ctk.StringVar(value="blue_gradient")
        self.gradient_menu = ctk.CTkOptionMenu(
            self.theme_frame,
            variable=self.gradient_var,
            values=["black", "white", "blue_gradient", "purple_gradient", "green_gradient", "red_gradient"],
        )
        self.gradient_menu.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.theme_frame, text="YouTube URL:").grid(row=7, column=0, padx=10, pady=5, sticky="e")
        self.youtube_var = ctk.StringVar()
        self.youtube_entry = ctk.CTkEntry(
            self.theme_frame,
            textvariable=self.youtube_var,
            placeholder_text="https://youtube.com/...",
        )
        self.youtube_entry.grid(row=7, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.theme_frame, text="AI Prompt:").grid(row=8, column=0, padx=10, pady=5, sticky="e")
        self.ai_prompt_var = ctk.StringVar()
        self.ai_prompt_entry = ctk.CTkEntry(
            self.theme_frame,
            textvariable=self.ai_prompt_var,
            placeholder_text="abstract background...",
        )
        self.ai_prompt_entry.grid(row=8, column=1, padx=10, pady=5, sticky="ew")

        self.theme_frame.grid_columnconfigure(1, weight=1)

    def _setup_scenario_mode(self) -> None:
        self.scenario_frame = ctk.CTkFrame(self.content_frame)

        ctk.CTkLabel(
            self.scenario_frame,
            text="Scenario Settings",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="w")

        ctk.CTkLabel(self.scenario_frame, text="Scenario Text:").grid(row=1, column=0, padx=10, pady=5, sticky="ne")
        self.scenario_text = ctk.CTkTextbox(
            self.scenario_frame,
            height=200,
            wrap="word",
        )
        self.scenario_text.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.scenario_text.insert("1.0", "Scene 1: Introduction\nThis is the first scene of the video.\n\nScene 2: Main Content\nThis is the main content scene.\n\nScene 3: Conclusion\nThis is the final scene.")

        ctk.CTkLabel(self.scenario_frame, text="Language:").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.scenario_lang_var = ctk.StringVar(value="uk-UA")
        self.scenario_lang_menu = ctk.CTkOptionMenu(
            self.scenario_frame,
            variable=self.scenario_lang_var,
            values=["uk-UA", "en-US", "pl-PL"],
        )
        self.scenario_lang_menu.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.scenario_frame, text="Voice:").grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.scenario_voice_var = ctk.StringVar(value="uk-UA-NataShaNeural")
        self.scenario_voice_menu = ctk.CTkOptionMenu(
            self.scenario_frame,
            variable=self.scenario_voice_var,
            values=["uk-UA-NataShaNeural", "en-US-GuyNeural", "pl-PL-MarekNeural"],
        )
        self.scenario_voice_menu.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.scenario_frame, text="Background:").grid(row=5, column=0, padx=10, pady=5, sticky="e")
        self.scenario_bg_var = ctk.StringVar(value="gradient")
        self.scenario_bg_menu = ctk.CTkOptionMenu(
            self.scenario_frame,
            variable=self.scenario_bg_var,
            values=["gradient", "youtube", "ai_image"],
        )
        self.scenario_bg_menu.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.scenario_frame, text="Width:").grid(row=6, column=0, padx=10, pady=5, sticky="e")
        self.width_var = ctk.StringVar(value="1920")
        self.width_entry = ctk.CTkEntry(
            self.scenario_frame,
            textvariable=self.width_var,
        )
        self.width_entry.grid(row=6, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self.scenario_frame, text="Height:").grid(row=7, column=0, padx=10, pady=5, sticky="e")
        self.height_var = ctk.StringVar(value="1080")
        self.height_entry = ctk.CTkEntry(
            self.scenario_frame,
            textvariable=self.height_var,
        )
        self.height_entry.grid(row=7, column=1, padx=10, pady=5, sticky="ew")

        self.scenario_frame.grid_columnconfigure(1, weight=1)

    def _show_mode(self, mode: str) -> None:
        if mode == "theme":
            self.theme_frame.grid(row=0, column=0, sticky="nsew")
            self.scenario_frame.grid_forget()
        else:
            self.scenario_frame.grid(row=0, column=0, sticky="nsew")
            self.theme_frame.grid_forget()

    def _on_mode_change(self) -> None:
        self._show_mode(self.mode_var.get())

    def _change_appearance(self, mode: str) -> None:
        ctk.set_appearance_mode(mode)

    def _change_scaling(self, scale: str) -> None:
        new_scale = int(scale.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scale)

    def _load_settings(self) -> None:
        try:
            if settings.THEME:
                ctk.set_appearance_mode(settings.THEME)
                self.appearance_mode.set(settings.THEME)
            if settings.SCALING:
                ctk.set_widget_scaling(float(settings.SCALING))
                self.scaling_mode.set(f"{int(float(settings.SCALING) * 100)}%")
        except Exception as e:
            logger.warning(f"Failed to load settings: {e}")

    def _on_generate(self) -> None:
        if self.running:
            return

        self.running = True
        self.generate_btn.configure(state="disabled")
        self.progress.set(0)
        self.status_bar.configure(text="Generating...")

        threading.Thread(target=self._generate_async, daemon=True).start()

    def _generate_async(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            if self.mode_var.get() == "theme":
                loop.run_until_complete(self._generate_theme())
            else:
                loop.run_until_complete(self._generate_scenario())
        finally:
            loop.close()
            self.root.after(0, self._on_generate_complete)

    async def _generate_theme(self) -> None:
        title = self.title_entry.get() or "Untitled"
        theme = self.theme_var.get()
        language = self.lang_var.get()
        voice = self.voice_var.get()
        duration = float(self.duration_var.get() or 5)
        bg_type = self.bg_var.get()

        config = VideoConfig(
            title=title,
            mode=GenerationMode.THEME,
            theme=theme,
            language=language,
            voice=voice,
            duration=duration * 60,
            width=1920,
            height=1080,
            background_type=bg_type,
        )

        if bg_type == "youtube":
            config.youtube_url = self.youtube_var.get()
        elif bg_type == "ai_image":
            config.ai_prompt = self.ai_prompt_var.get()
        elif bg_type == "gradient":
            config.gradient_name = self.gradient_var.get()

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        def progress_callback(progress: float, message: str) -> None:
            self.root.after(0, lambda: self.progress.set(progress))
            self.root.after(0, lambda: self.status_bar.configure(text=message))

        await self.generator.generate_theme_video(
            config=config,
            output_dir=output_dir,
            progress_callback=progress_callback,
        )

    async def _generate_scenario(self) -> None:
        title = self.title_entry.get() or "Untitled"
        scenario_text = self.scenario_text.get("1.0", "end-1c")
        language = self.scenario_lang_var.get()
        voice = self.scenario_voice_var.get()
        bg_type = self.scenario_bg_var.get()
        width = int(self.width_var.get() or 1920)
        height = int(self.height_var.get() or 1080)

        scenes = []
        for line in scenario_text.split("\n"):
            line = line.strip()
            if line.startswith("Scene ") or line.startswith("Сцена "):
                scene_title = line
                scenes.append(Scene(title=scene_title, text=""))
            elif line and scenes:
                scenes[-1].text += line + " "

        if not scenes:
            scenes.append(Scene(title="Scene 1", text=scenario_text))

        config = VideoConfig(
            title=title,
            mode=GenerationMode.SCENARIO,
            scenes=scenes,
            language=language,
            voice=voice,
            width=width,
            height=height,
            background_type=bg_type,
        )

        if bg_type == "youtube":
            config.youtube_url = self.youtube_var.get()
        elif bg_type == "ai_image":
            config.ai_prompt = self.ai_prompt_var.get()

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)

        def progress_callback(progress: float, message: str) -> None:
            self.root.after(0, lambda: self.progress.set(progress))
            self.root.after(0, lambda: self.status_bar.configure(text=message))

        await self.generator.generate_scenario_video(
            config=config,
            output_dir=output_dir,
            progress_callback=progress_callback,
        )

    def _on_generate_complete(self) -> None:
        self.running = False
        self.generate_btn.configure(state="normal")
        self.progress.set(1.0)
        self.status_bar.configure(text="Generation complete!")

    def run(self) -> None:
        self.root.mainloop()

def main() -> None:
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    app = VideoGeneratorApp(root)
    app.run()

if __name__ == "__main__":
    main()
