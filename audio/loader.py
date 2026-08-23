import torch
import soundfile as sf


class AudioLoader:
    """Loads WAV audio files."""

    @staticmethod
    def load(
        file_path: str
    ) -> tuple[torch.Tensor, int]:
        """Load WAV file and return waveform with sample rate."""

        audio, sample_rate = sf.read(
            file_path,
            dtype="float32",
            always_2d=True
        )

        waveform = torch.from_numpy(
            audio.T.copy()
        )

        return waveform, sample_rate

