from pathlib import Path

from core.exceptions import InputFileError


class FileValidator:
    """Validates input files."""

    @staticmethod
    def validate_exists(file_path: Path) -> None:
        """Validate that the file exists."""

        if not file_path.exists():
            raise InputFileError(
                f"Input file not found: {file_path}"
            )

    @staticmethod
    def validate_file(file_path: Path) -> None:
        """Validate that the path points to a regular file."""

        FileValidator.validate_exists(file_path)

        if not file_path.is_file():
            raise InputFileError(
                f"Input path is not a file: {file_path}"
            )
