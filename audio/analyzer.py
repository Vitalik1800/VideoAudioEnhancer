from pathlib import Path

import librosa
from librosa import feature
import numpy as np
import pyloudnorm as pyln

from models.audio import AudioInfo


class AudioAnalyzer:
    """Provides basic audio analysis functionality."""

    def analyze(self, audio_path: str) -> AudioInfo:
        """Analyze an audio file and return audio level information."""

        audio, sample_rate = librosa.load(
            audio_path,
            sr=None,
            mono=True
        )

        rms = librosa.feature.rms(y=audio)

        rms_mean = float(rms.mean())

        rms_db = float(
            librosa.amplitude_to_db(
                np.array([rms_mean]),
                ref=1.0
            )[0]
        )

        peak = float(np.max(np.abs(audio)))

        peak_db = float(
            librosa.amplitude_to_db(
                np.array([peak]),
                ref=1.0
            )[0]
        )

        clipping = bool(
            np.any(np.abs(audio) >= 1.0)
        )

        meter = pyln.Meter(sample_rate)

        loudness = float(
            meter.integrated_loudness(audio)
        )

        stft = librosa.stft(audio)

        spectrogram = np.abs(stft)

        frequencies = librosa.fft_frequencies(
            sr=sample_rate
        )

        low_mask = frequencies < 250

        mid_mask = (
            (frequencies >= 250) &
            (frequencies < 4000)
        )

        high_mask = frequencies >= 4000

        low_energy = float(
            spectrogram[low_mask].mean()
        )

        mid_energy = float(
            spectrogram[mid_mask].mean()
        )

        high_energy = float(
            spectrogram[high_mask].mean()
        )

        total_energy = (
            low_energy +
            mid_energy +
            high_energy
        )

        low_ratio = low_energy / total_energy
        mid_ratio = mid_energy / total_energy
        high_ratio = high_energy / total_energy

        spectral_centroid = (
            librosa.feature.spectral_centroid(
                S=spectrogram,
                sr=sample_rate
            )
        )

        spectral_bandwidth = (
            librosa.feature.spectral_bandwidth(
                S=spectrogram,
                sr=sample_rate
            )
        )

        spectral_rolloff = (
            librosa.feature.spectral_rolloff(
                S=spectrogram,
                sr=sample_rate
            )
        )

        return AudioInfo(
            path=Path(audio_path),
            duration=len(audio) / sample_rate,
            sample_rate=sample_rate,

            rms=rms_mean,
            rms_db=rms_db,

            peak=peak,
            peak_db=peak_db,
            clipping=clipping,

            loudness_lufs=loudness,

            spectral_centroid=float(
                spectral_centroid.mean()
            ),
            spectral_bandwidth=float(
                spectral_bandwidth.mean()
            ),
            spectral_rolloff=float(
                spectral_rolloff.mean()
            ),

            low_frequency_ratio=low_ratio,
            mid_frequency_ratio=mid_ratio,
            high_frequency_ratio=high_ratio
        )
