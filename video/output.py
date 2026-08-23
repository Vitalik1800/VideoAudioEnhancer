from pathlib import Path


class OutputManager:
    """Manages output directories for processed videos."""

    DEFAULT_OUTPUT_DIRECTORY = "output"

    def create_output_directory(
        self,
        video_path: str
    ) -> str:
        """Create and return an output directory for a video."""

        video_file = Path(video_path)

        output_directory = (
            Path(self.DEFAULT_OUTPUT_DIRECTORY)
            / video_file.stem
        )

        output_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        return str(output_directory)
