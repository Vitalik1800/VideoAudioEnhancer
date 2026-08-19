import subprocess
from typing import Sequence

from core.exceptions import VideoProcessingError


class FFMpegRunner:
    """Provides access to FFMpeg and FFProbe."""

    def __init__(
            self,
            ffmpeg_path: str = "ffmpeg",
            ffprobe_path: str = "ffprobe"
    ):
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path

    def check_ffmpeg(self) -> None:
        """Check whether FFMpeg is available."""

        try:
            subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                check=True
            )
        except FileNotFoundError as error:
            raise VideoProcessingError(
                f"FFMpeg executable not found {self.ffmpeg_path}"
            ) from error
        except subprocess.CalledProcessError as error:
            raise VideoProcessingError(
                "FFMpeg is not available."
            ) from error

    def check_ffprobe(self) -> None:
        """Check whether FFProbe is available."""

        try:
            subprocess.run(
                [self.ffprobe_path, "-version"],
                capture_output=True,
                text=True,
                check=True
            )
        except FileNotFoundError as error:
            raise VideoProcessingError(
                f"FFProbe executable not found: {self.ffprobe_path}"
            ) from error
        except subprocess.CalledProcessError as error:
            raise VideoProcessingError(
                "FFProbe is not available."
            ) from error

    def run_ffmpeg(
        self,
        arguments: Sequence[str]
    ) -> subprocess.CompletedProcess[str]:
        """Run FFMpeg with the provided arguments."""

        command = [
            self.ffmpeg_path,
            *arguments
        ]

        try:
            return subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
        except FileNotFoundError as error:
            raise VideoProcessingError(
                f"FFMpeg executable not found: {self.ffmpeg_path}"
            ) from error
        except subprocess.CalledProcessError as error:
            raise VideoProcessingError(
                self._build_error_message(
                    "FFMpeg",
                    error
                )
            ) from error

    def run_ffprobe(
        self,
        arguments: Sequence[str]
    ) -> subprocess.CompletedProcess[str]:
        """Run FFProbe with the provided arguments."""

        command = [
            self.ffprobe_path,
            *arguments
        ]

        try:
            return subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
        except FileNotFoundError as error:
            raise VideoProcessingError(
                f"FFProbe executable not found: {self.ffprobe_path}"
            ) from error
        except subprocess.CalledProcessError as error:
            raise VideoProcessingError(
                self._build_error_message(
                    "FFProbe",
                    error
                )
            ) from error

    def _build_error_message(
        self,
        tool_name: str,
        error: subprocess.CalledProcessError
    ) -> str:
        """Build a readable error message."""

        stderr = error.stderr.strip()

        if stderr:
            return f"{tool_name} failed: {stderr}"

        return (
            f"{tool_name} failed "
            f"with exit code {error.returncode}."
        )
