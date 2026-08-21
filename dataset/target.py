from pathlib import Path


class TargetGainCalculator:
    """Calculates target gain for a dataset sample."""

    def calculate(self, attenuation_db: float) -> float:
        """Return gain required to compensate attenuation."""

        if attenuation_db >= 0:
            raise ValueError(
                "Attenuation must be negative."
            )

        return float(-attenuation_db)

    def calculate_from_path(
        self,
        audio_path: str
    ) -> float:
        """Determine target gain from an audio file name."""

        filename = Path(audio_path).stem

        parts = filename.rsplit("_", 1)

        if len(parts) != 2:
            raise ValueError(
                f"Cannot determine attenuation: {audio_path}"
            )

        attenuation_text = parts[1].replace("db", "")

        attenuation_db = -float(attenuation_text)

        return self.calculate(attenuation_db)

    def calculate_directory(
        self,
        input_dir: str
    ) -> dict[str, float]:
        """Calculate target gain for all WAV files."""

        directory = Path(input_dir)

        if not directory.exists():
            raise FileNotFoundError(
                f"Input directory not found: {directory}"
            )

        audio_files = sorted(
            directory.rglob("*.wav")
        )

        targets = {}

        for index, audio_file in enumerate(
            audio_files,
            start=1
        ):
            print(
                f"[{index}/{len(audio_files)}] "
                f"Calculating target: "
                f"{audio_file.name}"
            )

            targets[audio_file.name] = (
                self.calculate_from_path(
                    str(audio_file)
                )
            )

        return targets
    