import torch

from ml.model import GainPredictor


class GainOptimizer:
    """Provides optimizer for the gain prediction model."""

    LEARNING_RATE = 0.001

    def __init__(
        self,
        model: GainPredictor,
        learning_rate: float = LEARNING_RATE
    ) -> None:
        self.model = model

        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=learning_rate
        )

    def zero_grad(self) -> None:
        """Clear accumulated gradients."""

        self.optimizer.zero_grad()

    def step(self) -> None:
        """Update model parameters."""

        self.optimizer.step()