from dataclasses import dataclass
from pathlib import Path


@dataclass
class VideoInfo:
    """Contains information about a video file."""

    path: Path
    name: str
    duration: float
    width: int
    height: int
    fps: float
    has_audio: bool
