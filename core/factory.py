from audio.enhancer import AudioEnhancer
from output.manager import OutputManager
from processing.pipeline import ProcessingPipeline
from video.processor import VideoProcessor
from video.splitter import VideoSplitter


class ComponentFactory:
    """Creates application components."""

    @staticmethod
    def create_pipeline(output_directory: str) -> ProcessingPipeline:
        """Create a fully configured processing pipeline."""

        video_processor = VideoProcessor()
        video_splitter = VideoSplitter()
        audio_enhancer = AudioEnhancer()
        output_manager = OutputManager(output_directory)

        return ProcessingPipeline(
            video_processor=video_processor,
            video_splitter=video_splitter,
            audio_enhancer=audio_enhancer,
            output_manager=output_manager
        )