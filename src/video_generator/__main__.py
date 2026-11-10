"""
Main entry point for Video Generator.

Can be run as:
- python -m video_generator (GUI mode)
- python -m video_generator --console (Console mode)
"""

import argparse
import asyncio
import sys
from pathlib import Path

from .config import settings
from .core import VideoGenerator
from .models import VideoConfig, GenerationMode
from .utils import get_logger, setup_logging

logger = get_logger(__name__)

def console_mode():
    """Run in console mode."""
    print("=" * 60)
    print("Video Generator 4.0 - Console Mode")
    print("=" * 60)
    print()

    # Get mode
    print("Select mode:")
    print("1. Theme (generate from topic)")
    print("2. Scenario (use script)")
    mode_choice = input("Enter choice (1-2): ").strip()
    mode = "theme" if mode_choice != "2" else "scenario"

    # Get text
    print()
    print("Enter your text (press Enter twice to finish):")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if not line.strip():
            if lines:
                break
            continue
        lines.append(line)

    text = "\n".join(lines)

    if not text:
        print("Error: No text provided")
        sys.exit(1)

    # Create generator
    config = VideoConfig(
        mode=GenerationMode.THEME if mode == "theme" else GenerationMode.SCENARIO,
        voice="uk-UA-OstapNeural",
        voice_label="Остап",
        size="1080p",
        include_subtitles=True,
        include_cover=True,
    )

    generator = VideoGenerator(config)

    def progress_callback(msg):
        print(msg)

    generator.on_progress(progress_callback)

    # Ensure ffmpeg
    try:
        generator.ensure_ffmpeg()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Generate video
    try:
        print()
        print("Generating video...")
        print()

        final_path = asyncio.run(generator.generate(text, mode))

        print()
        print("=" * 60)
        print(f"✅ Video generated successfully!")
        print(f"📂 Location: {final_path}")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def gui_mode():
    """Run in GUI mode."""
    try:
        import customtkinter as ctk
    except ImportError:
        print("Error: customtkinter is required for GUI mode")
        print("Install with: pip install customtkinter")
        sys.exit(1)

    from .gui.app import VideoGeneratorApp

    app = VideoGeneratorApp()
    app.run()

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Video Generator 4.0 - AI-Powered Video Creation"
    )
    parser.add_argument(
        "--console",
        action="store_true",
        help="Run in console mode",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(
        level="DEBUG" if args.debug else "INFO",
        console=True,
    )

    if args.console:
        console_mode()
    else:
        gui_mode()

if __name__ == "__main__":
    main()
