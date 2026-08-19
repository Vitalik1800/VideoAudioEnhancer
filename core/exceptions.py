class VideoAudioEnhancerError(Exception):
    """Base exception for the application."""


class InputFileError(VideoAudioEnhancerError):
    """Raised when the input file is invalid or unavailable."""


class VideoProcessingError(VideoAudioEnhancerError):
    """Raised when video processing fails."""


class AudioProcessingError(VideoAudioEnhancerError):
    """Raised when audio processing fails."""


class AIProcessingError(VideoAudioEnhancerError):
    """Raised when AI processing fails."""


class OutputProcessingError(VideoAudioEnhancerError):
    """Raised when output processing fails."""
