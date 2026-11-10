"""
Text utility functions.
"""

import re
from typing import List, Optional

def split_sentences(text: str) -> List[str]:
    """
    Split text into sentences.

    Args:
        text: Input text

    Returns:
        List of sentences
    """
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if s.strip()]

def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and special characters.

    Args:
        text: Input text

    Returns:
        Cleaned text
    """
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text

def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to HH:MM:SS.mmm

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{seconds:06.3f}".replace(".", ",")

def slugify(text: str, max_length: int = 100) -> str:
    """
    Convert text to a URL-safe slug.

    Args:
        text: Input text
        max_length: Maximum length of slug

    Returns:
        URL-safe slug
    """
    slug = re.sub(r"[^\w\s-]", "", text)
    slug = re.sub(r"\s+", "_", slug)
    slug = slug.strip("_")
    slug = slug[:max_length]
    return slug
