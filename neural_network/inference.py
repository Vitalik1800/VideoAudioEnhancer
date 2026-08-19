import torch

from neural_network.model import AudioEnhancementModel


class AudioEnhancementInference:
    """Runs inference using the audio enhancement model."""

    def __init__(self, model: AudioEnhancementModel):
        self.model = model
        self.model.eval()

    def predict(self, features: torch.Tensor) -> torch.Tensor:
        """Predict audio enhancement parameters."""

        with torch.no_grad():
            return self.model(features)
