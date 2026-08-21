import torch

from ml.model import GainPredictor


class GainPredictorService:
    """Performs forward pass and predicts required audio gain."""

    def __init__(
        self,
        model: GainPredictor
    ) -> None:
        self.model = model

    def predict(
        self,
        features: torch.Tensor
    ) -> torch.Tensor:
        """Predict gain for the given feature vector."""

        self.model.eval()

        with torch.no_grad():
            prediction = self.model(features)

        return prediction
    