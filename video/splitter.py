import subprocess
from pathlib import Path


class VideoSplitter:
    """Handles splitting videos into multiple parts."""

    SHORT_VIDEO_LIMIT = 30 * 60
    LONG_VIDEO_LIMIT = 60 * 60

    SHORT_SPLIT_COUNT = 10
    LONG_SPLIT_COUNT = 20

    def get_split_count(self, duration: float) -> int:
        """Return the required number of parts based on duration."""

        if duration < self.SHORT_VIDEO_LIMIT:
            return 1

        if duration < self.LONG_VIDEO_LIMIT:
            return self.SHORT_SPLIT_COUNT

        return self.LONG_SPLIT_COUNT

    def get_part_filename(self, part_number: int) -> str:
        """Return a filename for a video part."""

        return f"video_part_{part_number:02d}.mp4"

    def split(
        self,
        video_path: str,
        output_directory: str,
        duration: float
    ) -> list[str]:
        """Split a video into the required number of parts."""

        video_file = Path(video_path)
        output_dir = Path(output_directory)

        if not video_file.exists():
            raise FileNotFoundError(
                f"Video file not found: {video_file}"
            )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        split_count = self.get_split_count(duration)

        if split_count == 1:
            return [str(video_file)]

        part_duration = duration / split_count
        output_files: list[str] = []

        for index in range(split_count):
            start_time = index * part_duration

            output_file = (
                output_dir
                / f"video_part_{index + 1:02d}.mp4"
            )

            command = [
                "ffmpeg",
                "-y",
                "-ss",
                str(start_time),
                "-i",
                str(video_file),
                "-t",
                str(part_duration),
                "-c",
                "copy",
                str(output_file)
            ]

            subprocess.run(
                command,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            output_files.append(str(output_file))

        return output_files
