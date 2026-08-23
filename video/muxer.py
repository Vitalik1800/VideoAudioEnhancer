import subprocess
from pathlib import Path


class VideoMuxer:
    """Combines video and enhanced audio."""

    def mux(
        self,
        video_path: str,
        audio_path: str,
        output_path: str
    ) -> str:
        """Combine video with enhanced audio."""

        video_file = Path(video_path)
        audio_file = Path(audio_path)
        output_file = Path(output_path)

        if not video_file.exists():
            raise FileNotFoundError(
                f"Video file not found: {video_file}"
            )

        if not audio_file.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_file}"
            )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(video_file),
            "-i",
            str(audio_file),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            str(output_file)
        ]

        subprocess.run(
            command,
            check=True
        )

        return str(output_file)
