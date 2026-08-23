import torch
import torchaudio

from ml.inference import GainInference

import wave
from pathlib import Path


class AudioEnhancer:
    """Handles audio enhancement operations."""

    def __init__(
        self,
        model_path: str = "models/audio_gain_model.pth"
    ) -> None:
        self.inference = GainInference(model_path)

    def get_recommended_gain(
        self,
        audio_path: str
    ) -> float:
        """Get AI-recommended gain for an audio file."""

        result = self.inference.predict(audio_path)

        return result.final_gain

    def apply_gain(
        self,
        waveform: torch.tensor,
        gain_db: float
    ) -> torch.Tensor:
        """Apply gain in decibels to an audio waveform."""

        gain_linear = 10 ** (gain_db / 20.0)

        return waveform * gain_linear

    def get_peak(
        self,
        waveform: torch.Tensor
    ) -> float:
        """Get the absolute peak amplitude of an audio waveform."""

        return float(waveform.abs().max().item())

    def prevent_clipping(
        self,
        waveform: torch.Tensor
    ) -> torch.Tensor:
        """Prevent clipping by limiting the waveform peak."""

        peak = waveform.abs().max().item()

        if peak <= 1.0:
            return waveform

        return waveform / peak

    def normalize(
        self,
        waveform: torch.Tensor,
        target_peak: float = 0.95
    ) -> torch.Tensor:
        """Normalize audio waveform to the target peak."""

        if target_peak <= 0.0 or target_peak > 1.0:
            raise ValueError(
                "target_peak must be between 0 and 1."
            )

        peak = waveform.abs().max().item()

        if peak == 0.0:
            return waveform

        return waveform * (target_peak / peak)

    def save(
        self,
        waveform: torch.Tensor,
        sample_rate: int,
        output_path: str
    ) -> str:
        """Save enhanced audio as a WAV file."""

        output_file = Path(output_path)
        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        audio = waveform.detach().cpu().squeeze(0)

        audio = torch.clamp(
            audio,
            -1.0,
            1.0
        )

        pcm16 = (
            audio * 32767.0
        ).to(torch.int16)

        with wave.open(str(output_file), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(
                pcm16.numpy().tobytes()
            )

        return str(output_file)

    def enhance(
        self,
        audio_path: str,
        output_path: str
    ) -> str:
        """Enhance an audio file."""

        raise NotImplementedError(
            "AI-based audio enhancement is not implemented yet."
        )
