from pathlib import Path

from core.exceptions import InputFileError


class VideoProcessor:
    """Provides basic video processing functionality."""

    def get_video_info(self, video_path: str) -> dict:
        """Return basic information about a video file."""

        path = Path(video_path)

        if not path.exists():
            raise InputFileError(
                f"Video file not found: {video_path}"
            )

        return {
            "path": str(path),
            "name": path.name,
            "extension": path.suffix
        }

    def extract_audio(
            self,
            video_path: str,
            output_path: str
    ) -> str:
        """Extract audio from a video file."""

        raise NotImplementedError(
            "Audio extraction is not implemented yet."
        )

    def merge_audio(
            self,
            video_path: str,
            audio_path: str,
            output_path: str
    ) -> str:
        """Merge processed audio with a video file."""

        raise NotImplementedError(
            "Audio and video merging is not implemented yet."
        )
