from dataclasses import dataclass
from pathlib import Path


@dataclass
class VideoInfo:
    """Contains information about a video file."""

    path: str
    name: str
    extension: str
    format: str
    duration: float
    width: int
    height: int
    has_audio: bool
