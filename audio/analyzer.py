import librosa


class AudioAnalyzer:
    """Provides basic audio analysis functionality."""

    def analyze(self, audio_path: str) -> dict:
        """Analyze an audio file and return basic information."""

        audio, sample_rate = librosa.load(
            audio_path,
            sr=None,
            mono=True
        )

        duration = len(audio) / sample_rate

        return {
            "duration": duration,
            "sample_rate": sample_rate,
            "samples": len(audio)
        }