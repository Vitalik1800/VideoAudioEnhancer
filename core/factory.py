from audio.analyzer import AudioAnalyzer
from audio.enhancer import AudioEnhancer
from audio.extractor import AudioExtractor
from output.manager import OutputManager
from processing.pipeline import ProcessingPipeline
from video.processor import VideoProcessor
from video.splitter import VideoSplitter


class ComponentFactory:
    """Creates application components."""

    @staticmethod
    def create_pipeline(
        output_directory: str
    ) -> ProcessingPipeline:

        video_processor = VideoProcessor()
        video_splitter = VideoSplitter()

        audio_extractor = AudioExtractor()
        audio_analyzer = AudioAnalyzer()
        audio_enhancer = AudioEnhancer()

        output_manager = OutputManager(
            output_directory
        )

        return ProcessingPipeline(
            video_processor=video_processor,
            video_splitter=video_splitter,
            audio_extractor=audio_extractor,
            audio_analyzer=audio_analyzer,
            audio_enhancer=audio_enhancer,
            output_manager=output_manager
        )
