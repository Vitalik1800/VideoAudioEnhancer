import shutil
from pathlib import Path


class DatasetManager:
    """Manages dataset directory structure."""

    def __init__(self, root_directory: str = "dataset"):
        self.root_directory = Path(root_directory)

    @property
    def original_directory(self) -> Path:
        """Return directory for original audio files."""

        return self.root_directory / "original"

    @property
    def quiet_directory(self) -> Path:
        """Return directory for quiet audio files."""

        return self.root_directory / "quiet"

    @property
    def features_directory(self) -> Path:
        """Return directory for extracted features."""

        return self.root_directory / "features"

    @property
    def splits_directory(self) -> Path:
        """Return directory for dataset splits."""

        return self.root_directory / "splits"

    def get_quiet_directory(self, gain_db: int) -> Path:
        """Return directory for a specific attenuation level."""

        return self.quiet_directory / f"{gain_db}db"

    def create_directories(self) -> None:
        """Create dataset directory structure."""

        directories = [
            self.root_directory,
            self.get_quiet_directory(-6),
            self.get_quiet_directory(-12),
            self.get_quiet_directory(-18),
            self.get_quiet_directory(-24),
            self.features_directory,
            self.splits_directory
        ]

        for directory in directories:
            directory.mkdir(
                parents=True,
                exist_ok=True
            )

    def copy_original_audio(
        self,
        audio_path: str
    ) -> Path:
        """Copy an original audio file into the dataset."""

        source = Path(audio_path)

        if not source.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        destination = (
            self.original_directory /
            source.name
        )

        if destination.exists():
            raise FileExistsError(
                f"Audio file already exists: {destination}"
            )

        shutil.copy2(
            source,
            destination
        )

        return destination
    