from pathlib import Path

import cv2


class VideoLoader:
    """Loads video files and extracts basic video information."""

    @staticmethod
    def _open_video(file_path: str) -> cv2.VideoCapture:
        """Open a video file."""

        video_file = Path(file_path)

        if not video_file.exists():
            raise FileNotFoundError(
                f"Video file not found: {video_file}"
            )

        capture = cv2.VideoCapture(str(video_file))

        if not capture.isOpened():
            raise ValueError(
                f"Unable to open video: {video_file}"
            )

        return capture

    @staticmethod
    def get_duration(file_path: str) -> float:
        """Return video duration in seconds."""

        capture = VideoLoader._open_video(file_path)

        try:
            fps = float(
                capture.get(cv2.CAP_PROP_FPS)
            )

            frame_count = int(
                capture.get(cv2.CAP_PROP_FRAME_COUNT)
            )

            if fps <= 0:
                raise ValueError(
                    "Invalid video FPS."
                )

            return frame_count / fps

        finally:
            capture.release()

    @staticmethod
    def load(file_path: str) -> dict:
        """Load a video and return its basic properties."""

        video_file = Path(file_path)

        capture = VideoLoader._open_video(
            file_path
        )

        try:
            width = int(
                capture.get(cv2.CAP_PROP_FRAME_WIDTH)
            )

            height = int(
                capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
            )

            fps = float(
                capture.get(cv2.CAP_PROP_FPS)
            )

            frame_count = int(
                capture.get(cv2.CAP_PROP_FRAME_COUNT)
            )

            duration = (
                frame_count / fps
                if fps > 0
                else 0.0
            )

            return {
                "path": str(video_file),
                "width": width,
                "height": height,
                "fps": fps,
                "frame_count": frame_count,
                "duration": duration
            }

        finally:
            capture.release()
            