from pathlib import Path

from dataset.feature_store import FeatureStore
from dataset.features import FeatureExtractor
from dataset.target import TargetGainCalculator


class DatasetBuilder:
    """Builds the complete dataset from audio samples."""

    def __init__(
        self,
        feature_extractor: FeatureExtractor,
        target_calculator: TargetGainCalculator,
        feature_store: FeatureStore
    ) -> None:
        self.feature_extractor = feature_extractor
        self.target_calculator = target_calculator
        self.feature_store = feature_store

    def build(
        self,
        input_dir: str,
        source: str = "external"
    ) -> int:
        """Build the complete dataset."""

        directory = Path(input_dir)

        if not directory.exists():
            raise FileNotFoundError(
                f"Input directory not found: {directory}"
            )

        audio_files = sorted(
            directory.rglob("*.wav")
        )

        total = len(audio_files)

        if total == 0:
            raise ValueError(
                f"No WAV files found in {directory}"
            )

        processed = 0

        for index, audio_file in enumerate(
            audio_files,
            start=1
        ):
            print(
                f"[{index}/{total}] "
                f"Building sample: "
                f"{audio_file.name}"
            )

            features = (
                self.feature_extractor.extract(
                    str(audio_file)
                )
            )

            target_gain = (
                self.target_calculator.calculate_from_path(
                    str(audio_file)
                )
            )

            attenuation_db = -target_gain

            self.feature_store.save(
                filename=audio_file.name,
                source=source,
                attenuation_db=attenuation_db,
                features=features,
                target_gain_db=target_gain
            )

            processed += 1

        return processed

