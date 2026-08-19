from dataclasses import dataclass
from pathlib import Path


@dataclass
class AudioInfo:
    """Contains information about an audio file."""

    path: Path
    duration: float
    sample_rate: int
    channels: int
