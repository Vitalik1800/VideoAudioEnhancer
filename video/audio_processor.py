import subprocess
from pathlib import Path

from audio.loader import AudioLoader
from audio.enhancer import AudioEnhancer


class VideoAudioProcessor:
    """Processes audio of video parts."""

    def __init__(self, model_path: str) -> None:
        self.audio_enhancer = AudioEnhancer(model_path)

    def extract_audio(
        self,
        video_path: str,
        audio_path: str
    ) -> str:
        """Extract audio from a video file."""

        output_file = Path(audio_path)
        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-vn",
            "-acodec",
            "pcm_s161e",
            str(output_file)
        ]

        subprocess.run(
            command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        return str(output_file)

    def enhance_audio(
        self,
        audio_path: str,
        output_path: str
    ) -> str:
        """Enhance extracted audio."""

        waveform, sample_rate = AudioLoader.load(
            audio_path
        )

        gain = self.audio_enhancer.get_recommended_gain(
            audio_path
        )

        enhanced = self.audio_enhancer.apply_gain(
            waveform,
            gain
        )

        protected = self.audio_enhancer.prevent_clipping(
            enhanced
        )

        normalized = self.audio_enhancer.normalize(
            protected
        )

        return self.audio_enhancer.save(
            normalized,
            sample_rate,
            output_path
        )
