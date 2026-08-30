import wave
from pathlib import Path

import numpy as np
import pytest

from audio.analyzer import AudioAnalyzer


@pytest.fixture
def audio_file(tmp_path: Path) -> Path:
    """Create a temporary WAV file for testing."""

    sample_rate = 48000
    duration = 2
    frequency = 440

    samples = np.arange(
        sample_rate * duration
    )

    audio = (
        0.5
        * np.sin(
            2 * np.pi * frequency * samples / sample_rate
        )
    )

    audio = (
        audio * 32767
    ).astype(np.int16)

    audio_path = tmp_path / "test_audio.wav"

    with wave.open(
        str(audio_path),
        "wb"
    ) as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(audio.tobytes())

    return audio_path


@pytest.fixture
def analyzer() -> AudioAnalyzer:
    """Create AudioAnalyzer instance."""

    return AudioAnalyzer()


def test_duration(
    analyzer: AudioAnalyzer,
    audio_file: Path
):
    """Test audio duration calculation."""

    result = analyzer.analyze(
        str(audio_file)
    )

    assert result.duration == pytest.approx(
        2.0,
        abs=0.01
    )


def test_sample_rate(
    analyzer: AudioAnalyzer,
    audio_file: Path
):
    """Test sample rate detection."""

    result = analyzer.analyze(
        str(audio_file)
    )

    assert result.sample_rate == 48000


def test_rms(
    analyzer: AudioAnalyzer,
    audio_file: Path
):
    """Test RMS calculation."""

    result = analyzer.analyze(
        str(audio_file)
    )

    assert result.rms > 0
    assert result.rms == pytest.approx(
        0.3535,
        abs=0.01
    )


def test_rms_db(
    analyzer: AudioAnalyzer,
    audio_file: Path
):
    """Test RMS dB calculation."""

    result = analyzer.analyze(
        str(audio_file)
    )

    assert np.isfinite(result.rms_db)
    assert result.rms_db < 0


def test_peak(
    analyzer: AudioAnalyzer,
    audio_file: Path
):
    """Test peak amplitude calculation."""

    result = analyzer.analyze(
        str(audio_file)
    )

    assert 0 < result.peak <= 1
    assert result.peak == pytest.approx(
        0.5,
        abs=0.01
    )


def test_peak_db(
    analyzer: AudioAnalyzer,
    audio_file: Path
):
    """Test peak dB calculation."""

    result = analyzer.analyze(
        str(audio_file)
    )

    assert np.isfinite(result.peak_db)
    assert result.peak_db == pytest.approx(
        -6.02,
        abs=0.1
    )


def test_clipping(
    analyzer: AudioAnalyzer,
    audio_file: Path
):
    """Test clipping detection."""

    result = analyzer.analyze(
        str(audio_file)
    )

    assert result.clipping is False


def test_loudness(
    analyzer: AudioAnalyzer,
    audio_file: Path
):
    """Test LUFS loudness calculation."""

    result = analyzer.analyze(
        str(audio_file)
    )

    assert np.isfinite(
        result.loudness_lufs
    )


def test_spectral_features(
    analyzer: AudioAnalyzer,
    audio_file: Path
):
    """Test spectral feature calculation."""

    result = analyzer.analyze(
        str(audio_file)
    )

    assert result.spectral_centroid > 0
    assert result.spectral_bandwidth > 0
    assert result.spectral_rolloff > 0


def test_frequency_ratios(
    analyzer: AudioAnalyzer,
    audio_file: Path
):
    """Test frequency band ratios."""

    result = analyzer.analyze(
        str(audio_file)
    )

    assert result.low_frequency_ratio >= 0
    assert result.mid_frequency_ratio >= 0
    assert result.high_frequency_ratio >= 0

    total_ratio = (
        result.low_frequency_ratio
        + result.mid_frequency_ratio
        + result.high_frequency_ratio
    )

    assert total_ratio == pytest.approx(
        1.0,
        abs=0.001
    )


def test_audio_path(
    analyzer: AudioAnalyzer,
    audio_file: Path
):
    """Test returned audio path."""

    result = analyzer.analyze(
        str(audio_file)
    )

    assert result.path == audio_file
