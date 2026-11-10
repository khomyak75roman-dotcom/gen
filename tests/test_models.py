import pytest
from pydantic import ValidationError

from video_generator.models.base import (
    BackgroundType,
    GenerationMode,
    ProjectState,
    Scene,
    VideoConfig,
)
from video_generator.models.exceptions import (
    BackgroundError,
    PipelineError,
    TTSError,
    VideoGenerationError,
)

class TestScene:
    def test_scene_creation(self):
        scene = Scene(title="Test Scene", text="This is a test scene.")
        assert scene.title == "Test Scene"
        assert scene.text == "This is a test scene."
        assert scene.duration == 0.0
        assert scene.audio_path is None
        assert scene.background_path is None

    def test_scene_with_all_fields(self):
        scene = Scene(
            title="Full Scene",
            text="Complete scene text",
            duration=10.5,
            audio_path="/path/to/audio.mp3",
            background_path="/path/to/bg.png",
        )
        assert scene.title == "Full Scene"
        assert scene.text == "Complete scene text"
        assert scene.duration == 10.5
        assert scene.audio_path == "/path/to/audio.mp3"
        assert scene.background_path == "/path/to/bg.png"

class TestVideoConfig:
    def test_theme_config(self):
        config = VideoConfig(
            title="Test Video",
            mode=GenerationMode.THEME,
            theme="motivation",
            language="uk-UA",
            voice="uk-UA-NataShaNeural",
            duration=300,
        )
        assert config.title == "Test Video"
        assert config.mode == GenerationMode.THEME
        assert config.theme == "motivation"
        assert config.language == "uk-UA"
        assert config.voice == "uk-UA-NataShaNeural"
        assert config.duration == 300
        assert config.width == 1920
        assert config.height == 1080

    def test_scenario_config(self):
        scenes = [
            Scene(title="Scene 1", text="First scene"),
            Scene(title="Scene 2", text="Second scene"),
        ]
        config = VideoConfig(
            title="Scenario Video",
            mode=GenerationMode.SCENARIO,
            scenes=scenes,
            language="en-US",
            voice="en-US-GuyNeural",
        )
        assert config.title == "Scenario Video"
        assert config.mode == GenerationMode.SCENARIO
        assert len(config.scenes) == 2
        assert config.scenes[0].title == "Scene 1"
        assert config.scenes[1].text == "Second scene"

    def test_config_with_custom_resolution(self):
        config = VideoConfig(
            title="Custom Res",
            mode=GenerationMode.THEME,
            width=1280,
            height=720,
        )
        assert config.width == 1280
        assert config.height == 720

    def test_config_with_background_settings(self):
        config = VideoConfig(
            title="BG Test",
            mode=GenerationMode.THEME,
            background_type=BackgroundType.YOUTUBE,
            youtube_url="https://youtube.com/test",
        )
        assert config.background_type == BackgroundType.YOUTUBE
        assert config.youtube_url == "https://youtube.com/test"

class TestProjectState:
    def test_project_state_creation(self):
        config = VideoConfig(
            title="Test Project",
            mode=GenerationMode.THEME,
        )
        state = ProjectState(
            config=config,
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00",
        )
        assert state.config.title == "Test Project"
        assert state.created_at == "2024-01-01T00:00:00"
        assert state.completed_steps == []
        assert state.errors == []

    def test_project_state_with_progress(self):
        config = VideoConfig(title="Progress Test", mode=GenerationMode.THEME)
        state = ProjectState(
            config=config,
            current_step="Generating audio",
            completed_steps=["Parse script", "Generate scenes"],
            total_steps=5,
            scenes_processed=2,
        )
        assert state.current_step == "Generating audio"
        assert len(state.completed_steps) == 2
        assert state.total_steps == 5
        assert state.scenes_processed == 2

class TestExceptions:
    def test_exception_hierarchy(self):
        assert issubclass(VideoGenerationError, Exception)
        assert issubclass(TTSError, VideoGenerationError)
        assert issubclass(BackgroundError, VideoGenerationError)
        assert issubclass(PipelineError, VideoGenerationError)

    def test_exception_messages(self):
        error = TTSError("TTS generation failed")
        assert str(error) == "TTS generation failed"

        error = BackgroundError("Background download failed")
        assert str(error) == "Background download failed"

        error = PipelineError("Pipeline step failed")
        assert str(error) == "Pipeline step failed"

class TestBackgroundType:
    def test_background_type_values(self):
        assert BackgroundType.GRADIENT == "gradient"
        assert BackgroundType.YOUTUBE == "youtube"
        assert BackgroundType.AI_IMAGE == "ai_image"

class TestGenerationMode:
    def test_generation_mode_values(self):
        assert GenerationMode.THEME == "theme"
        assert GenerationMode.SCENARIO == "scenario"
