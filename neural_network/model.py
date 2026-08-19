import torch
from torch import nn


class AudioEnhancementModel(nn.Module):
    """Neural network for audio enhancement."""

    def __init__(self, input_size: int = 2):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(input_size, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Run a forward pass."""

        return self.network(x)
