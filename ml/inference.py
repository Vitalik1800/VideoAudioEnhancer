from dataclasses import dataclass
from pathlib import Path

import torch

from dataset.features import FeatureExtractor
from ml.model import GainPredictor


@dataclass
class InferenceResult:
    """Stores the result of audio gain inference."""

    loudness_lufs: float
    raw_gain: float
    final_gain: float


class GainInference:
    """Runs AI-based audio gain inference."""

    MIN_GAIN = -12.0
    MAX_GAIN = 12.0

    def __init__(self, model_path: str) -> None:
        self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model file not found: {self.model_path}"
            )

        self.feature_extractor = FeatureExtractor()

        self.model = GainPredictor()

        self.model.load_state_dict(
            torch.load(
                self.model_path,
                map_location="cpu"
            )
        )

        self.model.eval()

    def predict(self, audio_path: str) -> InferenceResult:
        """Predict the recommended gain for an audio file."""

        audio_file = Path(audio_path)

        if not audio_file.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_file}"
            )

        features = self.feature_extractor.extract(
            str(audio_file)
        )

        input_tensor = torch.tensor(
            features,
            dtype=torch.float32
        ).unsqueeze(0)

        with torch.no_grad():
            prediction = self.model(input_tensor)

        raw_gain = float(
            prediction.squeeze().item()
        )

        final_gain = max(
            self.MIN_GAIN,
            min(raw_gain, self.MAX_GAIN)
        )

        loudness_lufs = float(features[4])

        return InferenceResult(
            loudness_lufs=loudness_lufs,
            raw_gain=raw_gain,
            final_gain=final_gain
        )


        