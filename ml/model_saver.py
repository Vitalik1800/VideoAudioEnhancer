from pathlib import Path

import torch

from ml.model import GainPredictor


class ModelSaver:
    """Saves and loads trained PyTorch models."""

    def save(
        self,
        model: GainPredictor,
        output_path: str
    ) -> None:
        """Save model state dictionary."""

        path = Path(output_path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        torch.save(
            model.state_dict(),
            path
        )

    def load(
        self,
        model: GainPredictor,
        model_path: str
    ) -> GainPredictor:
        """Load model state dictionary."""

        path = Path(model_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Model not found: {path}"
            )

        state_dict = torch.load(
            path,
            map_location="cpu"
        )

        model.load_state_dict(state_dict)

        return model
