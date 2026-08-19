from pathlib import Path

from audio.enhancer import AudioEnhancer
from output.manager import OutputManager
from video.processor import VideoProcessor
from video.splitter import VideoSplitter


class ProcessingPipeline:
    """Coordinates the video audio enhancement pipeline."""

    def __init__(
        self,
        video_processor: VideoProcessor,
        video_splitter: VideoSplitter,
        audio_enhancer: AudioEnhancer,
        output_manager: OutputManager
    ):
        self.video_processor = video_processor
        self.video_splitter = video_splitter
        self.audio_enhancer = audio_enhancer
        self.output_manager = output_manager

    def _validate_input(self, video_path: str) -> Path:
        """Validate the input video path."""

        video_file = Path(video_path)

        if not video_file.exists():
            raise FileNotFoundError(
                f"Video file not found: {video_path}"
            )

        return video_file

    def process(self, video_path: str) -> None:
        """Process a video through the enhancement pipeline."""

        self._validate_input(video_path)

        print("Starting processing pipeline...")

        video_info = self.video_processor.get_video_info(
            video_path
        )

        print(f"Processing video: {video_info['name']}")

        duration = video_info["duration"]

        split_count = self.video_splitter.get_split_count(
            duration
        )

        print(
            f"Video will be processed in "
            f"{split_count} part(s)."
        )

        self.output_manager.create_output_directory()

        print("Processing pipeline initialized.")

