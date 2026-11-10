"""
Custom exceptions for Video Generator.
"""

class VideoGenerationError(Exception):
    """Base exception for video generation errors."""
    pass

class TTSError(VideoGenerationError):
    """Error during text-to-speech conversion."""
    pass

class BackgroundGenerationError(VideoGenerationError):
    """Error during background generation."""
    pass

class FFmpegError(VideoGenerationError):
    """Error during FFmpeg operations."""
    pass

class DownloadError(VideoGenerationError):
    """Error during file download."""
    pass

class AIServiceError(VideoGenerationError):
    """Error from AI services (LLM, image generation, etc.)."""
    pass

class ConfigurationError(VideoGenerationError):
    """Error in configuration."""
    pass

class PipelineError(VideoGenerationError):
    """Error during pipeline execution."""
    pass
