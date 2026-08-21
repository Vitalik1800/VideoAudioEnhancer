from pathlib import Path

import pandas as pd


class DatasetValidator:
    """Validates dataset structure and values."""

    EXPECTED_SAMPLES = 8000

    REQUIRED_COLUMNS = [
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
        "high_frequency_ratio",
    ]

    def validate(self, dataset_path: str) -> dict:
        """Validate dataset and return validation results."""

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

        if len(data) != self.EXPECTED_SAMPLES:
            raise ValueError(
                f"Expected {self.EXPECTED_SAMPLES} samples, "
                f"got {len(data)}"
            )

        missing_columns = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in data.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing columns: {missing_columns}"
            )

        if data[self.FEATURE_COLUMNS].isnull().any().any():
            raise ValueError(
                "Dataset contains NaN feature values."
            )

        if data["target_gain_db"].isnull().any():
            raise ValueError(
                "Dataset contains NaN target values."
            )

        if (data["rms"] < 0).any():
            raise ValueError(
                "RMS contains negative values."
            )

        if (data["peak"] < 0).any():
            raise ValueError(
                "Peak contains negative values."
            )

        if (data["peak"] > 1.0).any():
            raise ValueError(
                "Peak exceeds normalized range."
            )

        if (
            data["target_gain_db"]
            .isin([6.0, 12.0, 18.0, 24.0])
            .all()
            is False
        ):
            raise ValueError(
                "Invalid target gain value."
            )

        ratio_columns = [
            "low_frequency_ratio",
            "mid_frequency_ratio",
            "high_frequency_ratio",
        ]

        ratio_sum = data[ratio_columns].sum(axis=1)

        if not ((ratio_sum > 0.99) & (ratio_sum < 1.01)).all():
            raise ValueError(
                "Frequency ratios do not sum to approximately 1."
            )

        return {
            "samples": len(data),
            "features": len(self.FEATURE_COLUMNS),
            "columns": len(data.columns),
            "valid": True,
        }
    