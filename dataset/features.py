import numpy as np

from audio.analyzer import AudioAnalyzer


class FeatureExtractor:
    """Converts audio analysis results into feature vectors."""

    def __init__(self) -> None:
        self.analyzer = AudioAnalyzer()

    def extract(self, audio_path: str) -> np.ndarray:
        """Extract a numerical feature vector from an audio file."""

        audio_info = self.analyzer.analyze(audio_path)

        features = np.array(
            [
                audio_info.rms,
                audio_info.rms_db,
                audio_info.peak,
                audio_info.peak_db,
                audio_info.loudness_lufs,
                audio_info.spectral_centroid,
                audio_info.spectral_bandwidth,
                audio_info.spectral_rolloff,
                audio_info.low_frequency_ratio,
                audio_info.mid_frequency_ratio,
                audio_info.high_frequency_ratio
            ],
            dtype=np.float32
        )

        return features
    