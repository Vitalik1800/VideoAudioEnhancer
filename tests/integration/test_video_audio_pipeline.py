from pathlib import Path
import subprocess
import wave

import cv2
import numpy as np
import pytest

from core.exceptions import VideoProcessingError, InputFileError
from video.loader import VideoLoader
from video.processor import VideoProcessor
from video.splitter import VideoSplitter
from audio.analyzer import AudioAnalyzer
from audio.enhancer import AudioEnhancer
from audio.extractor import AudioExtractor

import torch

from video.muxer import VideoMuxer


def create_test_video(
    output_path: Path,
    duration: int = 5,
    fps: int = 10
):
    """Create a small test video."""

    width = 320
    height = 240

    fourcc = cv2.VideoWriter_fourcc(
        *"mp4v"
    )

    writer = cv2.VideoWriter(
        str(output_path),
        fourcc,
        fps,
        (width, height)
    )

    frame_count = duration * fps

    for _ in range(frame_count):
        frame = np.zeros(
            (height, width, 3),
            dtype=np.uint8
        )

        writer.write(frame)

    writer.release()


def create_test_audio(
    output_path: Path,
    duration: float = 2.0,
    sample_rate: int = 16000
):
    """Create a simple WAV audio file."""

    samples = int(
        duration * sample_rate
    )

    audio = (
        0.2
        * np.sin(
            2
            * np.pi
            * 440
            * np.arange(samples)
            / sample_rate
        )
    )

    audio = (
        audio * 32767
    ).astype(np.int16)

    with wave.open(
        str(output_path),
        "wb"
    ) as wav_file:

        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        wav_file.writeframes(
            audio.tobytes()
        )


def create_test_video_with_audio(
    video_path: Path,
    audio_path: Path,
    output_path: Path
):
    """Create a test video containing an audio track."""

    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-i",
            str(audio_path),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-shortest",
            str(output_path)
        ],
        check=True
    )


class DummyInference:
    """Dummy AI inference for integration testing."""

    def predict(self, _audio_path: str):
        class Result:
            final_gain = 6.0

        return Result()


@pytest.fixture
def test_video(tmp_path):
    """Create temporary test video."""

    video_path = (
        tmp_path / "test_video.mp4"
    )

    create_test_video(
        video_path
    )

    return video_path


@pytest.fixture
def test_audio(tmp_path):
    """Create temporary test audio."""

    audio_path = (
        tmp_path / "test_audio.wav"
    )

    create_test_audio(
        audio_path
    )

    return audio_path


def test_integration_test_environment(
    project_root,
    test_output_directory,
    test_data_directory
):
    """Check that the integration test environment is ready."""

    assert project_root.exists()
    assert project_root.is_dir()

    assert test_output_directory.exists()
    assert test_output_directory.is_dir()

    assert test_data_directory.exists()
    assert test_data_directory.is_dir()


def test_video_loader_and_splitter_integration(
    test_video,
    tmp_path
):
    """Check integration between VideoLoader and VideoSplitter."""

    duration = VideoLoader.get_duration(
        str(test_video)
    )

    assert duration > 0

    splitter = VideoSplitter()

    split_count = splitter.get_split_count(
        duration
    )

    assert split_count == 1

    output_directory = (
        tmp_path / "parts"
    )

    result = splitter.split(
        str(test_video),
        str(output_directory),
        duration
    )

    assert len(result) == 1

    assert Path(
        result[0]
    ).exists()


def test_video_loader_returns_valid_properties(
    test_video
):
    """Check that loaded video properties are consistent."""

    info = VideoLoader.load(
        str(test_video)
    )

    assert info["width"] == 320
    assert info["height"] == 240
    assert info["fps"] == pytest.approx(
        10.0
    )
    assert info["frame_count"] == 50
    assert info["duration"] == pytest.approx(
        5.0,
        abs=0.2
    )


def test_audio_analyzer_integration(
    test_audio
):
    """Check real audio creation and analysis."""

    analyzer = AudioAnalyzer()

    result = analyzer.analyze(
        str(test_audio)
    )

    assert result.path == test_audio

    assert result.sample_rate == 16000

    assert result.duration == pytest.approx(
        2.0,
        abs=0.01
    )

    assert result.rms > 0
    assert result.peak > 0

    assert result.clipping is False

    assert np.isfinite(
        result.rms_db
    )

    assert np.isfinite(
        result.peak_db
    )

    assert np.isfinite(
        result.loudness_lufs
    )


def test_audio_analyzer_and_ai_integration(
    test_audio
):
    """Check integration between audio analysis and AI recommendation."""

    analyzer = AudioAnalyzer()

    audio_info = analyzer.analyze(
        str(test_audio)
    )

    enhancer = AudioEnhancer.__new__(
        AudioEnhancer
    )

    enhancer.inference = DummyInference()

    gain = enhancer.get_recommended_gain(
        str(test_audio)
    )

    assert audio_info.duration > 0

    assert gain == pytest.approx(
        6.0
    )


def test_full_component_pipeline(
    test_video,
    test_audio,
    tmp_path
):
    """Check the basic integration flow of video, audio and AI components."""

    # 1. Load video
    video_info = VideoLoader.load(
        str(test_video)
    )

    assert video_info["duration"] > 0

    # 2. Determine parts
    splitter = VideoSplitter()

    split_count = splitter.get_split_count(
        video_info["duration"]
    )

    assert split_count == 1

    # 3. Analyze audio
    analyzer = AudioAnalyzer()

    audio_info = analyzer.analyze(
        str(test_audio)
    )

    assert audio_info.duration > 0
    assert audio_info.sample_rate > 0

    # 4. AI recommendation
    enhancer = AudioEnhancer.__new__(
        AudioEnhancer
    )

    enhancer.inference = DummyInference()

    gain = enhancer.get_recommended_gain(
        str(test_audio)
    )

    assert np.isfinite(gain)

    # 5. Verify output directory can be prepared
    output_directory = (
        tmp_path / "output"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    assert output_directory.exists()


def test_input_video_audio_extraction(
    test_video,
    test_audio,
    tmp_path
):
    """Check audio extraction from an input video."""

    video_with_audio = (
        tmp_path / "test_video_with_audio.mp4"
    )

    create_test_video_with_audio(
        test_video,
        test_audio,
        video_with_audio
    )

    extracted_audio = (
        tmp_path / "extracted_audio.wav"
    )

    extractor = AudioExtractor()

    result = extractor.extract(
        str(video_with_audio),
        str(extracted_audio)
    )

    assert result == str(extracted_audio)

    assert extracted_audio.exists()

    assert extracted_audio.stat().st_size > 0

    with wave.open(
        str(extracted_audio),
        "rb"
    ) as wav_file:

        assert wav_file.getnchannels() == 1
        assert wav_file.getsampwidth() == 2
        assert wav_file.getframerate() > 0
        assert wav_file.getnframes()


def test_audio_extraction_and_analysis(
    test_video,
    test_audio,
    tmp_path
):
    """Check integration between audio extraction and audio analysis."""

    # 1. Create video with audio
    video_with_audio = (
        tmp_path / "test_video_with_audio.mp4"
    )

    create_test_video_with_audio(
        test_video,
        test_audio,
        video_with_audio
    )

    assert video_with_audio.exists()

    # 2. Extract audio from video
    extracted_audio = (
        tmp_path / "extracted_audio.wav"
    )

    extractor = AudioExtractor()

    extraction_result = extractor.extract(
        str(video_with_audio),
        str(extracted_audio)
    )

    assert extraction_result == str(
        extracted_audio
    )

    assert extracted_audio.exists()

    assert extracted_audio.stat().st_size > 0

    # 3. Analyze extracted audio
    analyzer = AudioAnalyzer()

    audio_info = analyzer.analyze(
        str(extracted_audio)
    )

    # 4. Verify analysis result
    assert audio_info.path == extracted_audio

    assert audio_info.duration == pytest.approx(
        2.0,
        abs=0.2
    )

    assert audio_info.sample_rate > 0

    assert audio_info.rms > 0

    assert audio_info.peak > 0

    assert audio_info.clipping is False

    assert np.isfinite(
        audio_info.rms_db
    )

    assert np.isfinite(
        audio_info.peak_db
    )

    assert np.isfinite(
        audio_info.loudness_lufs
    )

    assert np.isfinite(
        audio_info.spectral_centroid
    )

    assert np.isfinite(
        audio_info.spectral_bandwidth
    )

    assert np.isfinite(
        audio_info.spectral_rolloff
    )


def test_audio_analysis_and_ai_integration(
    test_video,
    test_audio,
    tmp_path
):
    """Check integration between audio analysis and AI inference."""

    # 1. Create video with audio
    video_with_audio = (
        tmp_path / "test_video_with_audio.mp4"
    )

    create_test_video_with_audio(
        test_video,
        test_audio,
        video_with_audio
    )

    assert video_with_audio.exists()

    # 2. Extract audio
    extracted_audio = (
        tmp_path / "extracted_audio.wav"
    )

    extractor = AudioExtractor()

    extraction_result = extractor.extract(
        str(video_with_audio),
        str(extracted_audio)
    )

    assert extraction_result == str(
        extracted_audio
    )

    assert extracted_audio.exists()

    # 3. Analyze extracted audio
    analyzer = AudioAnalyzer()

    audio_info = analyzer.analyze(
        str(extracted_audio)
    )

    assert audio_info.path == extracted_audio

    assert audio_info.duration > 0

    assert audio_info.sample_rate > 0

    assert audio_info.rms > 0

    assert audio_info.peak > 0

    assert np.isfinite(
        audio_info.loudness_lufs
    )

    # 4. Initialize AI enhancer
    enhancer = AudioEnhancer.__new__(
        AudioEnhancer
    )

    enhancer.inference = DummyInference()

    # 5. Get AI recommendation
    gain = enhancer.get_recommended_gain(
        str(extracted_audio)
    )

    # 6. Verify AI result
    assert isinstance(
        gain,
        float
    )

    assert np.isfinite(
        gain
    )

    assert gain == pytest.approx(
        6.0
    )


def test_ai_gain_enhancement_integration(
    test_audio
):
    """Check integration between AI gain recommendation and enhancement."""

    # 1. Create AudioEnhancer without loading
    # the real AI model.
    enhancer = AudioEnhancer.__new__(
        AudioEnhancer
    )

    enhancer.inference = DummyInference()

    # 2. Get AI-recommended gain
    gain = enhancer.get_recommended_gain(
        str(test_audio)
    )

    assert isinstance(
        gain,
        float
    )

    assert np.isfinite(
        gain
    )

    assert gain == pytest.approx(
        6.0
    )

    # 3. Load WAV audio using standard wave module.
    with wave.open(
        str(test_audio),
        "rb"
    ) as wav_file:

        sample_rate = wav_file.getframerate()
        frame_count = wav_file.getnframes()
        sample_width = wav_file.getsampwidth()

        audio_bytes = wav_file.readframes(
            frame_count
        )

    assert sample_rate > 0
    assert frame_count > 0
    assert sample_width == 2

    # 4. Convert PCM16 audio to PyTorch tensor.
    audio_array = np.frombuffer(
        audio_bytes,
        dtype=np.int16
    ).copy()

    waveform = (
        torch.from_numpy(
            audio_array
        ).float()
        / 32768.0
    )

    waveform = waveform.unsqueeze(0)

    assert waveform.numel() > 0

    # 5. Apply AI-recommended gain.
    enhanced_waveform = enhancer.apply_gain(
        waveform,
        gain
    )

    assert enhanced_waveform.shape == (
        waveform.shape
    )

    # 6. Verify that the gain increased
    # the waveform amplitude.
    original_peak = enhancer.get_peak(
        waveform
    )

    enhanced_peak = enhancer.get_peak(
        enhanced_waveform
    )

    assert enhanced_peak > original_peak

    # 7. Prevent clipping.
    safe_waveform = enhancer.prevent_clipping(
        enhanced_waveform
    )

    safe_peak = enhancer.get_peak(
        safe_waveform
    )

    assert safe_peak <= 1.0

    # 8. Verify that the final waveform
    # still contains audio data.
    assert safe_waveform.numel() > 0


def test_enhancement_to_video_processing_integration(
    test_video,
    test_audio,
    tmp_path
):
    """Check integration between enhanced audio and video processing."""

    # 1. Prepare output video with audio.
    video_with_audio = (
        tmp_path / "test_video_with_audio.mp4"
    )

    create_test_video_with_audio(
        test_video,
        test_audio,
        video_with_audio
    )

    assert video_with_audio.exists()

    # 2. Simulate enhanced audio.
    enhanced_audio = (
        tmp_path / "enhanced_audio.wav"
    )

    with wave.open(
        str(test_audio),
        "rb"
    ) as wav_file:

        sample_rate = wav_file.getframerate()
        frame_count = wav_file.getnframes()
        audio_bytes = wav_file.readframes(
            frame_count
        )

    audio_array = np.frombuffer(
        audio_bytes,
        dtype=np.int16
    ).copy()

    waveform = (
        torch.from_numpy(
            audio_array
        ).float()
        / 32768.0
    )

    waveform = waveform.unsqueeze(0)

    enhancer = AudioEnhancer.__new__(
        AudioEnhancer
    )

    enhanced_waveform = enhancer.normalize(
        waveform,
        target_peak=0.95
    )

    saved_audio = enhancer.save(
        enhanced_waveform,
        sample_rate,
        str(enhanced_audio)
    )

    assert saved_audio == str(
        enhanced_audio
    )

    assert enhanced_audio.exists()

    assert enhanced_audio.stat().st_size > 0

    # 3. Process video using enhanced audio.
    output_video = (
        tmp_path / "processed_video.mp4"
    )

    muxer = VideoMuxer()

    muxer.mux(
        str(video_with_audio),
        str(enhanced_audio),
        str(output_video)
    )

    # 4. Verify processed video.
    assert output_video.exists()

    assert output_video.stat().st_size > 0

    # 5. Verify that the resulting video can be opened.
    capture = cv2.VideoCapture(
        str(output_video)
    )

    try:
        assert capture.isOpened()

        frame_count = int(
            capture.get(
                cv2.CAP_PROP_FRAME_COUNT
            )
        )

        fps = float(
            capture.get(
                cv2.CAP_PROP_FPS
            )
        )

        assert frame_count > 0
        assert fps > 0

    finally:
        capture.release()


def test_short_video_full_pipeline(
    test_video,
    test_audio,
    tmp_path
):
    """Check the full processing pipeline for a short video."""

    # 1. Create a video containing audio.
    video_with_audio = (
        tmp_path / "short_video_with_audio.mp4"
    )

    create_test_video_with_audio(
        test_video,
        test_audio,
        video_with_audio
    )

    assert video_with_audio.exists()
    assert video_with_audio.stat().st_size > 0

    # 2. Load video information.
    video_info = VideoLoader.load(
        str(video_with_audio)
    )

    assert video_info["duration"] > 0
    assert video_info["width"] == 320
    assert video_info["height"] == 240
    assert video_info["fps"] == pytest.approx(
        10.0,
        abs=0.5
    )

    # 3. Check that short video does not require splitting.
    splitter = VideoSplitter()

    split_count = splitter.get_split_count(
        video_info["duration"]
    )

    assert split_count == 1

    # 4. Extract audio from the input video.
    extracted_audio = (
        tmp_path / "short_extracted_audio.wav"
    )

    extractor = AudioExtractor()

    result = extractor.extract(
        str(video_with_audio),
        str(extracted_audio)
    )

    assert result == str(
        extracted_audio
    )

    assert extracted_audio.exists()
    assert extracted_audio.stat().st_size > 0

    # 5. Analyze extracted audio.
    analyzer = AudioAnalyzer()

    audio_info = analyzer.analyze(
        str(extracted_audio)
    )

    assert audio_info.duration > 0
    assert audio_info.sample_rate > 0
    assert audio_info.rms > 0
    assert audio_info.peak > 0

    # 6. Get AI-recommended gain.
    enhancer = AudioEnhancer.__new__(
        AudioEnhancer
    )

    enhancer.inference = DummyInference()

    gain = enhancer.get_recommended_gain(
        str(extracted_audio)
    )

    assert gain == pytest.approx(
        6.0
    )

    # 7. Load extracted audio using wave.
    with wave.open(
        str(extracted_audio),
        "rb"
    ) as wav_file:

        sample_rate = wav_file.getframerate()
        frame_count = wav_file.getnframes()
        audio_bytes = wav_file.readframes(
            frame_count
        )

    audio_array = np.frombuffer(
        audio_bytes,
        dtype=np.int16
    ).copy()

    waveform = (
        torch.from_numpy(
            audio_array
        ).float()
        / 32768.0
    )

    waveform = waveform.unsqueeze(0)

    assert waveform.numel() > 0

    # 8. Apply AI gain.
    enhanced_waveform = enhancer.apply_gain(
        waveform,
        gain
    )

    assert enhancer.get_peak(
        enhanced_waveform
    ) > enhancer.get_peak(
        waveform
    )

    # 9. Prevent clipping.
    enhanced_waveform = (
        enhancer.prevent_clipping(
            enhanced_waveform
        )
    )

    assert enhancer.get_peak(
        enhanced_waveform
    ) <= 1.0

    # 10. Normalize enhanced audio.
    enhanced_waveform = enhancer.normalize(
        enhanced_waveform,
        target_peak=0.95
    )

    assert enhancer.get_peak(
        enhanced_waveform
    ) == pytest.approx(
        0.95,
        abs=0.01
    )

    # 11. Save enhanced audio.
    enhanced_audio = (
        tmp_path / "short_enhanced_audio.wav"
    )

    saved_audio = enhancer.save(
        enhanced_waveform,
        sample_rate,
        str(enhanced_audio)
    )

    assert saved_audio == str(
        enhanced_audio
    )

    assert enhanced_audio.exists()
    assert enhanced_audio.stat().st_size > 0

    # 12. Create final processed video.
    output_video = (
        tmp_path / "short_processed_video.mp4"
    )

    muxer = VideoMuxer()

    muxer.mux(
        str(video_with_audio),
        str(enhanced_audio),
        str(output_video)
    )

    # 13. Verify final output.
    assert output_video.exists()
    assert output_video.stat().st_size > 0

    # 14. Verify that final video can be opened.
    capture = cv2.VideoCapture(
        str(output_video)
    )

    try:
        assert capture.isOpened()

        final_frame_count = int(
            capture.get(
                cv2.CAP_PROP_FRAME_COUNT
            )
        )

        final_fps = float(
            capture.get(
                cv2.CAP_PROP_FPS
            )
        )

        assert final_frame_count > 0
        assert final_fps > 0

    finally:
        capture.release()


def test_video_30_minutes_split_into_10_parts(
    test_video,
    tmp_path,
    monkeypatch
):
    """Check processing scenario for a video of at least 30 minutes."""

    # 1. Prepare input video.
    assert test_video.exists()
    assert test_video.stat().st_size > 0

    # 2. Create VideoSplitter.
    splitter = VideoSplitter()

    # 3. Simulate a 30-minute video.
    duration = 30 * 60

    split_count = splitter.get_split_count(
        duration
    )

    assert split_count == 10

    # 4. Prepare output directory.
    output_directory = (
        tmp_path / "parts"
    )

    # 5. Mock FFmpeg execution.
    # The purpose of this test is to verify the
    # multi-part processing logic without creating
    # a real 30-minute video.
    def fake_run(
        command,
        **_kwargs
    ):
        output_file = Path(
            command[-1]
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file.touch()

    monkeypatch.setattr(
        "subprocess.run",
        fake_run
    )

    # 6. Split the video into 10 parts.
    result = splitter.split(
        str(test_video),
        str(output_directory),
        duration
    )

    # 7. Verify number of parts.
    assert len(result) == 10

    # 8. Verify all output files exist.
    assert all(
        Path(file).exists()
        for file in result
    )

    # 9. Verify correct filenames.
    expected_names = [
        f"video_part_{index:02d}.mp4"
        for index in range(1, 11)
    ]

    actual_names = [
        Path(file).name
        for file in result
    ]

    assert actual_names == expected_names

    # 10. Verify that all parts are located
    # inside the expected output directory.
    assert all(
        Path(file).parent == output_directory
        for file in result
    )


def test_video_60_minutes_split_into_20_parts(
    test_video,
    tmp_path,
    monkeypatch
):
    """Check processing scenario for a video of at least 60 minutes."""

    # 1. Prepare input video.
    assert test_video.exists()
    assert test_video.stat().st_size > 0

    # 2. Create VideoSplitter.
    splitter = VideoSplitter()

    # 3. Simulate a 60-minute video.
    duration = 60 * 60

    split_count = splitter.get_split_count(
        duration
    )

    assert split_count == 20

    # 4. Prepare output directory.
    output_directory = (
        tmp_path / "parts"
    )

    # 5. Mock FFmpeg execution.
    # A real 60-minute video is not required for this
    # integration test.
    def fake_run(
        command,
        **_kwargs
    ):
        output_file = Path(
            command[-1]
        )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file.touch()

    monkeypatch.setattr(
        "subprocess.run",
        fake_run
    )

    # 6. Split the video into 20 parts.
    result = splitter.split(
        str(test_video),
        str(output_directory),
        duration
    )

    # 7. Verify number of parts.
    assert len(result) == 20

    # 8. Verify all output files exist.
    assert all(
        Path(file).exists()
        for file in result
    )

    # 9. Verify correct filenames.
    expected_names = [
        f"video_part_{index:02d}.mp4"
        for index in range(1, 21)
    ]

    actual_names = [
        Path(file).name
        for file in result
    ]

    assert actual_names == expected_names

    # 10. Verify that all parts are located
    # inside the expected output directory.
    assert all(
        Path(file).parent == output_directory
        for file in result
    )


def test_video_without_audio(
    test_video,
    tmp_path
):
    """Check that a video without an audio track is handled correctly."""

    # 1. The test video contains only video frames.
    assert test_video.exists()
    assert test_video.stat().st_size > 0

    # 2. Verify that the input video can be opened.
    capture = cv2.VideoCapture(
        str(test_video)
    )

    try:
        assert capture.isOpened()

        frame_count = int(
            capture.get(
                cv2.CAP_PROP_FRAME_COUNT
            )
        )

        fps = float(
            capture.get(
                cv2.CAP_PROP_FPS
            )
        )

        assert frame_count > 0
        assert fps > 0

    finally:
        capture.release()

    # 3. Try to extract audio from the video.
    extracted_audio = (
        tmp_path / "extracted_audio.wav"
    )

    extractor = AudioExtractor()

    # FFmpeg should fail because the source
    # video does not contain an audio stream.
    with pytest.raises(
        VideoProcessingError
    ):
        extractor.extract(
            str(test_video),
            str(extracted_audio)
        )

    # 4. No valid audio file should be produced.
    assert not extracted_audio.exists()


def test_corrupted_video_file(
    tmp_path
):
    """Check that a corrupted video file is rejected."""

    # 1. Create a corrupted video file.
    corrupted_video = (
        tmp_path / "corrupted_video.mp4"
    )

    corrupted_video.write_bytes(
        b"This is not a valid video file"
    )

    # 2. File must exist and contain data.
    assert corrupted_video.exists()
    assert corrupted_video.stat().st_size > 0

    # 3. VideoLoader must reject the corrupted file.
    with pytest.raises(
        ValueError,
        match="Unable to open video"
    ):
        VideoLoader.load(
            str(corrupted_video)
        )

    # 4. get_duration must also reject it.
    with pytest.raises(
        ValueError,
        match="Unable to open video"
    ):
        VideoLoader.get_duration(
            str(corrupted_video)
        )


def test_unsupported_video_format(
    tmp_path,
    monkeypatch
):
    """Check that unsupported video format is rejected."""

    unsupported_video = (
        tmp_path / "unsupported_video.mp4"
    )

    # Create a valid AVI video.
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "color=c=black:s=320x240:r=10",
            "-t",
            "2",
            "-c:v",
            "mpeg4",
            str(unsupported_video)
        ],
        check=True,
        capture_output=True,
        text=True
    )

    # The file must exist and contain data.
    assert unsupported_video.exists()
    assert unsupported_video.stat().st_size > 0

    processor = VideoProcessor()

    # Simulate an unsupported format returned by FFprobe.
    monkeypatch.setattr(
        processor,
        "get_format",
        lambda _video_path: "unsupported_format"
    )

    # The actual container format must be rejected.
    with pytest.raises(
        InputFileError,
        match="Unsupported video format"
    ):
        processor.validate_format(
            str(unsupported_video)
        )


def tedt_very_quiet_audio(
    tmp_path
):
    """Check that very quiet audio is detected correctly."""

    quiet_audio = (
        tmp_path / "very_quiet_audio.wav"
    )

    sample_rate = 16000
    duration = 2.0

    samples = int(
        duration * sample_rate
    )

    # Very low-amplitude sine wave.
    audio = (
        0.001
        * np.sin(
            2
            * np.pi
            * 440
            * np.arange(samples)
            / sample_rate
        )
    )

    audio = (
        audio * 32767
    ).astype(np.int16)

    with wave.open(
        str(quiet_audio),
        "wb"
    ) as wav_file:

        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        wav_file.writeframes(
            audio.tobytes()
        )

    # Verify that the audio file was created.
    assert quiet_audio.exists()
    assert quiet_audio.stat().st_size > 0

    # Analyze the quiet audio.
    analyzer = AudioAnalyzer()

    result = analyzer.analyze(
        str(quiet_audio)
    )

    # Basic audio properties.
    assert result.duration == pytest.approx(
        2.0,
        abs=0.01
    )

    assert result.sample_rate == 16000

    # Audio must contain a signal.
    assert result.rms > 0
    assert result.peak > 0

    # The signal must be very quiet.
    assert result.rms < 0.001

    assert result.rms_db < -60

    # No clipping should occur.
    assert result.clipping is False

    # Loudness values must be valid.
    assert np.isfinite(
        result.rms_db
    )

    assert np.isfinite(
        result.peak_db
    )

    assert np.isfinite(
        result.loudness_lufs
    )


def test_audio_with_high_peak(
    tmp_path
):
    """Check that high peak audio is detected correctly."""

    high_peak_audio = (
        tmp_path / "high_peak_audio.wav"
    )

    sample_rate = 16000
    duration = 2.0

    samples = int(
        duration * sample_rate
    )

    # High-amplitude sine wave.
    audio = (
        0.99
        * np.sin(
            2
            * np.pi
            * 440
            * np.arange(samples)
            / sample_rate
        )
    )

    audio = (
        audio * 32767
    ).astype(np.int16)

    with wave.open(
        str(high_peak_audio),
        "wb"
    ) as wav_file:

        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        wav_file.writeframes(
            audio.tobytes()
        )

    # Verify that the audio file was created.
    assert high_peak_audio.exists()
    assert high_peak_audio.stat().st_size > 0

    # Analyze the audio.
    analyzer = AudioAnalyzer()

    result = analyzer.analyze(
        str(high_peak_audio)
    )

    # Basic audio properties.
    assert result.duration == pytest.approx(
        2.0,
        abs=0.01
    )

    assert result.sample_rate == 16000

    # Signal must be present.
    assert result.rms > 0
    assert result.peak > 0

    # Peak must be very close to the maximum
    # normalized amplitude.
    assert result.peak == pytest.approx(
        0.99,
        abs=0.01
    )

    # Peak level must be close to 0 dBFS.
    assert result.peak_db > -0.2

    # The generated signal itself must not clip.
    assert result.clipping is False

    # All calculated values must be finite.
    assert np.isfinite(
        result.rms
    )

    assert np.isfinite(
        result.peak_db
    )

    assert np.isfinite(
        result.loudness_lufs
    )


def test_full_pipeline(
    test_video,
    test_audio,
    tmp_path
):
    """Check the complete video/audio processing pipeline."""

    # 1. Prepare input video with audio
    video_with_audio = (
        tmp_path / "input_video.mp4"
    )

    create_test_video_with_audio(
        test_video,
        test_audio,
        video_with_audio
    )

    assert video_with_audio.exists()
    assert video_with_audio.stat().st_size > 0

    # 2. Audio Extraction
    extracted_audio = (
        tmp_path / "extracted_audio.wav"
    )

    extractor = AudioExtractor()

    extraction_result = extractor.extract(
        str(video_with_audio),
        str(extracted_audio)
    )

    assert extraction_result == str(
        extracted_audio
    )

    assert extracted_audio.exists()
    assert extracted_audio.stat().st_size > 0

    # 3. Audio Analysis
    analyzer = AudioAnalyzer()

    audio_info = analyzer.analyze(
        str(extracted_audio)
    )

    assert audio_info.duration > 0
    assert audio_info.sample_rate > 0
    assert audio_info.rms > 0
    assert audio_info.peak > 0

    assert np.isfinite(
        audio_info.rms_db
    )

    assert np.isfinite(
        audio_info.peak_db
    )

    assert np.isfinite(
        audio_info.loudness_lufs
    )

    # 4. AI Recommendation
    enhancer = AudioEnhancer.__new__(
        AudioEnhancer
    )

    enhancer.inference = DummyInference()

    recommended_gain = (
        enhancer.get_recommended_gain(
            str(extracted_audio)
        )
    )

    assert isinstance(
        recommended_gain,
        float
    )

    assert np.isfinite(
        recommended_gain
    )

    assert recommended_gain == pytest.approx(
        6.0
    )

    # 5. Load audio waveform
    with wave.open(
        str(extracted_audio),
        "rb"
    ) as wav_file:

        channels = (
            wav_file.getnchannels()
        )

        sample_width = (
            wav_file.getsampwidth()
        )

        sample_rate = (
            wav_file.getframerate()
        )

        frame_count = (
            wav_file.getnframes()
        )

        raw_audio = (
            wav_file.readframes(
                frame_count
            )
        )

    assert channels == 1
    assert sample_width == 2
    assert sample_rate > 0
    assert frame_count > 0

    # Convert PCM16 audio to normalized float tensor.
    audio_array = np.frombuffer(
        raw_audio,
        dtype=np.int16
    ).astype(
        np.float32
    ) / 32768.0

    waveform = torch.from_numpy(
        audio_array
    ).unsqueeze(0)

    assert waveform.shape[0] == 1
    assert waveform.shape[1] > 0

    # 6. Apply AI-recommended Gain
    enhanced_waveform = (
        enhancer.apply_gain(
            waveform,
            recommended_gain
        )
    )

    assert enhanced_waveform.shape == (
        waveform.shape
    )

    assert not torch.equal(
        enhanced_waveform,
        waveform
    )

    # 7. Prevent Clipping
    safe_waveform = (
        enhancer.prevent_clipping(
            enhanced_waveform
        )
    )

    peak = enhancer.get_peak(
        safe_waveform
    )

    assert peak <= 1.0

    assert np.isfinite(
        peak
    )

    # 8. Verify processed video

    processor = VideoProcessor()

    video_info = (
        processor.get_video_info(
            str(video_with_audio)
        )
    )

    assert video_info.duration > 0
    assert video_info.width == 320
    assert video_info.height == 240
    assert video_info.has_audio is True

    # 9. Split processed video

    splitter = VideoSplitter()

    split_count = (
        splitter.get_split_count(
            video_info.duration
        )
    )

    assert split_count == 1

    output_directory = (
        tmp_path / "output"
    )

    result = splitter.split(
        str(video_with_audio),
        str(output_directory),
        video_info.duration
    )

    assert len(result) == 1

    # 10. Verify final output

    output_file = Path(
        result[0]
    )

    assert output_file.exists()
    assert output_file.stat().st_size > 0

    output_info = (
        processor.get_video_info(
            str(output_file)
        )
    )

    assert output_info.duration > 0
    assert output_info.width == 320
    assert output_info.height == 240
