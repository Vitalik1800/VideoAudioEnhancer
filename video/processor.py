import json
from pathlib import Path

from core.exceptions import InputFileError
from core.validators import FileValidator
from video.ffmpeg_runner import FFMpegRunner
from video.formats import is_supported_format

from models.video import VideoInfo


class VideoProcessor:
    """Provides basic video processing functionality."""

    def __init__(
        self,
        ffmpeg_runner: FFMpegRunner | None = None
    ):
        self.ffmpeg_runner = (
            ffmpeg_runner
            if ffmpeg_runner is not None
            else FFMpegRunner()
        )

    def get_video_info(self, video_path: str) -> VideoInfo:
        """Return basic information about a video file."""

        path = Path(video_path)

        FileValidator.validate_file(path)

        format_name = self.validate_format(video_path)
        duration = self.get_duration(video_path)
        width, height = self.get_resolution(video_path)
        has_audio = self.has_audio(video_path)

        return VideoInfo(
            path=str(path),
            name=path.name,
            format=format_name,
            extension=path.suffix,
            duration=duration,
            width=width,
            height=height,
            has_audio=has_audio
        )

    def get_format(self, video_path: str) -> str:
        """Return the actual container format of a video."""

        video_file = Path(video_path)

        FileValidator.validate_file(video_file)

        result = self.ffmpeg_runner.run_ffprobe(
            [
                "-v",
                "error",
                "-show_entries",
                "format=format_name",
                "-of",
                "json",
                str(video_file)
            ]
        )

        data = json.loads(result.stdout)

        format_name = data.get(
            "format",
            {}
        ).get(
            "format_name"
        )

        if not format_name:
            raise InputFileError(
                f"Unable to determine video format: {video_file}"
            )

        return format_name

    def validate_format(self, video_path: str) -> str:
        """Validate that the video format is supported."""

        format_name = self.get_format(video_path)

        if not is_supported_format(format_name):
            raise InputFileError(
                f"Unsupported video format: {format_name}"
            )

        return format_name

    def get_duration(self, video_path: str) -> float:
        """Return the video duration in seconds."""

        video_file = Path(video_path)

        FileValidator.validate_file(video_file)

        result = self.ffmpeg_runner.run_ffprobe(
            [
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "json",
                str(video_file)
            ]
        )

        data = json.loads(result.stdout)

        duration = data.get(
            "format",
            {}
        ).get(
            "duration"
        )

        if duration is None:
            raise InputFileError(
                f"Unable to determine video duration: {video_file}"
            )

        try:
            return float(duration)
        except (TypeError, ValueError) as error:
            raise InputFileError(
                f"Invalid video duration: {duration}"
            ) from error

    def get_resolution(self, video_path: str) -> tuple[int, int]:
        """Return the video resolution as width and height."""

        video_file = Path(video_path)

        FileValidator.validate_file(video_file)

        result = self.ffmpeg_runner.run_ffprobe(
            [
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height",
                "-of",
                "json",
                str(video_file)
            ]
        )

        data = json.loads(result.stdout)

        streams = data.get("streams", [])

        if not streams:
            raise InputFileError(
                f"Unable to determine video resolution: {video_file}"
            )

        stream = streams[0]

        width = stream.get("width")
        height = stream.get("height")

        if width is None or height is None:
            raise InputFileError(
                f"Invalid video resolution: {video_file}"
            )

        try:
            return int(width), int(height)
        except (TypeError, ValueError) as error:
            raise InputFileError(
                f"Invalid video resolution: {video_file}"
            ) from error

    def has_audio(self, video_path: str) -> bool:
        """Return whether the video contains an audio stream."""

        video_file = Path(video_path)

        FileValidator.validate_file(video_file)

        result = self.ffmpeg_runner.run_ffprobe(
            [
                "-v",
                "error",
                "-select_streams",
                "a:0",
                "-show_entries",
                "stream=index",
                "-of",
                "json",
                str(video_file)
            ]
        )

        data = json.loads(result.stdout)

        streams = data.get("streams", [])

        return bool(streams)

