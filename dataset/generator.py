from pathlib import Path

import soundfile as sf


class QuietAudioGenerator:
    """Generates quieter copies of audio files."""

    ATTENUATION_LEVELS = (-6.0, -12.0, -18.0, -24.0)

    def generate(
        self,
        audio_path: str,
        output_dir: str,
        attenuation_db: float
    ) -> Path:
        """Create a quieter copy of an audio file."""

        input_path = Path(audio_path)
        output_directory = Path(output_dir)

        if not input_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {input_path}"
            )

        if attenuation_db not in self.ATTENUATION_LEVELS:
            raise ValueError(
                f"Unsupported attenuation level: {attenuation_db} dB"
            )

        output_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        audio, sample_rate = sf.read(
            input_path,
            always_2d=False
        )

        gain = 10 ** (attenuation_db / 20.0)

        quiet_audio = audio * gain

        output_name = (
            f"{input_path.stem}"
            f"_{abs(attenuation_db):g}db"
            f"{input_path.suffix}"
        )

        output_path = output_directory / output_name

        sf.write(
            output_path,
            quiet_audio,
            sample_rate
        )

        return output_path

    def generate_all_levels(
        self,
        audio_path: str,
        output_root: str
    ) -> list[Path]:
        """Generate quieter copies for all attenuation levels."""

        output_paths = []

        for attenuation_db in self.ATTENUATION_LEVELS:
            level_name = f"{abs(attenuation_db):g}db"

            output_dir = (
                Path(output_root) / level_name
            )

            output_path = self.generate(
                audio_path,
                str(output_dir),
                attenuation_db
            )

            output_paths.append(output_path)

        return output_paths

    def generate_directory(
        self,
        input_dir: str,
        output_root: str
    ) -> int:
        """Generate quiet copies for all WAV files."""

        input_directory = Path(input_dir)

        if not input_directory.exists():
            raise FileNotFoundError(
                f"Input directory not found: {input_directory}"
            )

        audio_files = sorted(
            input_directory.glob("*.wav")
        )

        total_generated = 0

        for index, audio_file in enumerate(
            audio_files,
            start=1
        ):
            print(
                f"[{index}/{len(audio_files)}] "
                f"{audio_file.name}"
            )

            generated = self.generate_all_levels(
                str(audio_file),
                output_root
            )

            total_generated += len(generated)

        return total_generated
