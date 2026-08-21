from pathlib import Path

import pandas as pd
import torch
from torch.utils.data import Dataset


class AudioDataset(Dataset):
    """PyTorch dataset for audio enhancement samples."""

    FEATURE_COLUMNS = [
        "rms",
        "rms_db",
        "peak",
        "peak_db",
        "loudness_lufs",
        "spectral_centroid",
        "spectral_bandwidth",
        "spectral_rolloff",
        "low_frequency_ratio",
        "mid_frequency_ratio",
        "high_frequency_ratio"
    ]

    TARGET_COLUMN = "target_gain_db"

    def __init__(self, dataset_path: str) -> None:
        path = Path(dataset_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {path}"
            )

        data = pd.read_csv(path)

        if data.empty:
            raise ValueError(
                "Dataset is empty."
            )

        self.features = torch.tensor(
            data[self.FEATURE_COLUMNS].values,
            dtype=torch.float32
        )

        self.targets = torch.tensor(
            data[self.TARGET_COLUMN].values,
            dtype=torch.float32
        ).unsqueeze(1)

    def __len__(self) -> int:
        """Return number of samples."""

        return len(self.features)

    def __getitem__(
        self,
        index: int
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Return features and target for one sample."""

        return (
            self.features[index],
            self.targets[index]
        )