import librosa
import numpy as np

from librosa.feature import rms, spectral_centroid


class AudioFeatureExtractor:
    """Extracts numerical features from an audio signal."""

    def extract(self, audio_path: str) -> np.ndarray:
        """Extract basic audio features."""

        audio, sample_rate = librosa.load(
            audio_path,
            sr=None,
            mono=True
        )

        rms_features = rms(y=audio)

        spectral_features = spectral_centroid(
            y=audio,
            sr=sample_rate
        )

        features = np.concatenate([
            rms_features.flatten(),
            spectral_features.flatten()
        ])

        return features
