import torch
from torch import nn


class GainPredictor(nn.Module):
    """MLP model for predicting required audio gain."""

    def __init__(
        self,
        input_features: int = 11
    ) -> None:
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(input_features, 64),
            nn.ReLU(),

            nn.Linear(64, 32),
            nn.ReLU(),

            nn.Linear(32, 1)
        )

    def forward(
        self,
        x: torch.Tensor
    ) -> torch.Tensor:
        """Perform forward pass."""

        return self.network(x)