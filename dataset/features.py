from pathlib import Path

import numpy as np

from audio.analyzer import AudioAnalyzer


class FeatureExtractor:
    """Converts audio analysis results into feature vectors."""

    FEATURE_COUNT = 11

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

        if len(features) != self.FEATURE_COUNT:
            raise ValueError(
                f"Expected {self.FEATURE_COUNT} features, "
                f"got {len(features)}"
            )

        return features

    def extract_directory(
        self,
        input_dir: str,
    ) -> dict[str, np.ndarray]:
        """Extract feature vectors from all WAV files."""

        directory = Path(input_dir)

        if not directory.exists():
            raise FileNotFoundError(
                f"Input directory not found: {directory}"
            )

        audio_files = sorted(
            directory.rglob("*.wav")
        )

        features = {}

        for index, audio_file in enumerate(
            audio_files,
            start=1
        ):
            print(
                f"[{index}/{len(audio_files)}] "
                f"Extracting features: {audio_file.name}"
            )

            features[audio_file.name] = (
                self.extract(str(audio_file))
            )

        return features
    