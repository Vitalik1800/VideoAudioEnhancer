from pathlib import Path

from core.exceptions import InputFileError
from core.validators import FileValidator
from video.ffmpeg_runner import FFMpegRunner


class AudioExtractor:
    """Extracts audio tracks from video files."""

    def __init__(
        self,
        ffmpeg_runner: FFMpegRunner | None = None
    ):
        self.ffmpeg_runner = (
            ffmpeg_runner
            if ffmpeg_runner is not None
            else FFMpegRunner()
        )

    def extract(
        self,
        video_path: str,
        output_path: str
    ) -> str:
        """Extract the audio track from a video file."""

        video_file = Path(video_path)
        output_file = Path(output_path)

        FileValidator.validate_file(video_file)

        if output_file.exists():
            raise InputFileError(
                f"Output audio file already exists: {output_file}"
            )

        self.ffmpeg_runner.run_ffmpeg(
            [
                "-i",
                str(video_file),
                "-vn",
                "-acodec",
                "pcm_s16le",
                str(output_file)
            ]
        )

        if not output_file.exists():
            raise InputFileError(
                f"Audio extraction failed: {output_file}"
            )

        if output_file.suffix.lower() != ".wav":
            raise InputFileError(
                "Audio output must use WAV format."
            )

        return str(output_file)
