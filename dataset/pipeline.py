from pathlib import Path

from dataset.feature_store import FeatureStore
from dataset.features import FeatureExtractor
from dataset.generator import QuietAudioGenerator
from dataset.target import TargetGainCalculator


class DatasetPipeline:
    """Coordinates batch dataset preparation."""

    def __init__(
        self,
        quiet_generator: QuietAudioGenerator,
        feature_extractor: FeatureExtractor,
        target_calculator: TargetGainCalculator,
        feature_store: FeatureStore
    ) -> None:
        self.quiet_generator = quiet_generator
        self.feature_extractor = feature_extractor
        self.target_calculator = target_calculator
        self.feature_store = feature_store

    def process_file(
        self,
        audio_path: str,
        source: str = "external"
    ) -> int:
        """Process one original audio file."""

        audio_file = Path(audio_path)

        quiet_files = (
            self.quiet_generator.generate_all_levels(
                str(audio_file),
                "dataset/quiet"
            )
        )

        processed = 0

        for quiet_file in quiet_files:
            features = self.feature_extractor.extract(
                str(quiet_file)
            )

            target_gain = (
                self.target_calculator.calculate_from_path(
                    str(quiet_file)
                )
            )

            attenuation_db = -target_gain

            self.feature_store.save(
                filename=quiet_file.name,
                source=source,
                attenuation_db=attenuation_db,
                features=features,
                target_gain_db=target_gain
            )

            processed += 1

        return processed

    def process_directory(
        self,
        input_dir: str,
        source: str = "external"
    ) -> int:
        """Process all WAV files in a directory."""

        directory = Path(input_dir)

        if not directory.exists():
            raise FileNotFoundError(
                f"Input directory not found: {directory}"
            )

        audio_files = sorted(
            directory.glob("*.wav")
        )

        total_samples = 0

        for index, audio_file in enumerate(
            audio_files,
            start=1
        ):
            print(
                f"[{index}/{len(audio_files)}] "
                f"Processing {audio_file.name}"
            )

            total_samples += self.process_file(
                str(audio_file),
                source
            )

        return total_samples
