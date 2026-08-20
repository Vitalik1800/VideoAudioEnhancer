from dataclasses import dataclass
from pathlib import Path


@dataclass
class AudioInfo:
    """Contains information about an analyzed audio file."""

    path: Path
    duration: float
    sample_rate: int

    rms: float
    rms_db: float

    peak: float
    peak_db: float
    clipping: bool

    loudness_lufs: float

    spectral_centroid: float
    spectral_bandwidth: float
    spectral_rolloff: float

    low_frequency_ratio: float
    mid_frequency_ratio: float
    high_frequency_ratio: float