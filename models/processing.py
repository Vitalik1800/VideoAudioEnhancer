from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProcessingResult:
    """Represents the result of video processing."""

    success: bool
    output_paths: list[Path]
    error_message: str | None = None
