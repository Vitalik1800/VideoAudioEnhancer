from pathlib import Path

import numpy as np
import pandas as pd


class FeatureStore:
    """Stores extracted audio feature vectors."""

    COLUMNS = [
        "filename",
        "source",
        "attenuation_db",
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
        "high_frequency_ratio",
        "target_gain_db",
    ]

    def __init__(self, output_path: str):
        self.output_path = Path(output_path)

    def save(
        self,
        filename: str,
        source: str,
        attenuation_db: float,
        features: np.ndarray,
        target_gain_db: float
    ) -> None:
        """Append a feature vector to the CSV dataset."""

        if len(features) != 11:
            raise ValueError(
                "Feature vector must contain 11 values."
            )

        row = [
            filename,
            source,
            attenuation_db,
            *features.tolist(),
            target_gain_db
        ]

        self.output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        row_df = pd.DataFrame(
            [row],
            columns=self.COLUMNS
        )

        if self.output_path.exists():
            row_df.to_csv(
                self.output_path,
                mode="a",
                header=False,
                index=False
            )
        else:
            row_df.to_csv(
                self.output_path,
                index=False
            )
