import torch
from torch import nn


class GainLoss:
    """Calculates prediction loss for gain regression."""

    def __init__(self) -> None:
        self.criterion = nn.MSELoss()

    def calculate(
        self,
        prediction: torch.Tensor,
        target: torch.Tensor
    ) -> torch.Tensor:
        """Calculate mean squared error."""

        return self.criterion(
            prediction,
            target
        )
    