from pathlib import Path

from audio.enhancer import AudioEnhancer
from output.manager import OutputManager
from video.processor import VideoProcessor
from video.splitter import VideoSplitter

from core.validators import FileValidator
from core.exceptions import InputFileError


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

        FileValidator.validate_file(video_file)

        return video_file

    def process(self, video_path: str) -> None:
        """Process a video through the enhancement pipeline."""

        self._validate_input(video_path)

        print("Starting processing pipeline...")

        video_info = self.video_processor.get_video_info(
            video_path
        )

        print(f"Processing video: {video_info.name}")
        print(f"Format: {video_info.format}")
        print(
            f"Resolution: "
            f"{video_info.width}x{video_info.height}"
        )
        print(f"Duration: {video_info.duration:.2f} seconds")
        print(f"Has audio: {video_info.has_audio}")

        if not video_info.has_audio:
            raise InputFileError(
                f"Video has no audio stream: {video_info.path}"
            )

        split_count = self.video_splitter.get_split_count(
            video_info.duration
        )

        print(
            f"Video will be processed in "
            f"{split_count} part(s)."
        )

        self.output_manager.create_output_directory()

        print("Processing pipeline initialized.")
