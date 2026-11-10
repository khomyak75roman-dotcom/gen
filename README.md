# Video Generator 4.0

**AI-Powered Video Creation Tool**

A complete rebuild of the video generator with modern architecture, clean code, and improved functionality.

## Features

### Core Capabilities
- **Theme-based generation**: Create videos from a topic/idea
- **Scenario-based generation**: Use predefined script/scenario
- **AI Voiceovers**: Text-to-speech using Microsoft Edge TTS
- **Background Generation**:
  - Gradient backgrounds (built-in)
  - YouTube video backgrounds
  - AI-generated image backgrounds
  - Photo backgrounds from search
- **Subtitles**: Automatic SRT subtitle generation
- **Video Rendering**: Professional ffmpeg-based rendering
- **Cover Creation**: Automatic YouTube cover image
- **Resume Functionality**: Continue interrupted generations

### New in Version 4.0
- **Modular Architecture**: Clean separation of concerns
- **Async/Await**: Non-blocking operations where possible
- **Type Hints**: Full type annotations for better IDE support
- **Configuration Management**: Pydantic-based settings
- **Dependency Injection**: Flexible and testable
- **Proper Logging**: Structured logging infrastructure
- **Testability**: Unit test infrastructure
- **Documentation**: Comprehensive docs

## Installation

### Prerequisites
- Python 3.10+
- FFmpeg (automatically downloaded if not present)
- yt-dlp (automatically downloaded if not present)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/khomyak75roman-dotcom/video-generator.git
cd video-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m video_generator
