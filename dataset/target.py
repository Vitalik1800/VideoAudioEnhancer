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
