import sys
import os
from pathlib import Path

# Fix for PyInstaller
if getattr(sys, 'frozen', False):
    os.environ['PYTHONPATH'] = sys._MEIPASS

# Import all modules
try:
    from video_generator.config import settings
    from video_generator.core import VideoGenerator
    from video_generator.models import VideoConfig, GenerationMode
    from video_generator.utils import get_logger, setup_logging
    from video_generator.gui.app import VideoGeneratorApp
except ImportError:
    from config import settings
    from core import VideoGenerator
    from models import VideoConfig, GenerationMode
    from utils import get_logger, setup_logging
    from gui.app import VideoGeneratorApp

# Rest of your code...
