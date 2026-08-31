from pathlib import Path

import numpy as np
import soundfile as sf

from audio.enhancer import AudioEnhancer
from ml.inference import GainInference


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_ROOT
    / "ai_models"
    / "audio_gain_model.pth"
)


def create_test_audio(
    output_path: Path,
    duration: float = 1.0,
    sample_rate: int = 16000
) -> None:
    """Create a simple WAV file for inference testing."""

    t = np.linspace(
        0,
        duration,
        int(sample_rate * duration),
        endpoint=False
    )

    audio = 0.5 * np.sin(
        2 * np.pi * 440 * t
    )

    sf.write(
        output_path,
        audio,
        sample_rate
    )


def test_model_file_exists():
    """Check that the trained model exists."""

    assert MODEL_PATH.exists()
    assert MODEL_PATH.is_file()


def test_gain_inference_initialization():
    """Check that GainInference can load the model."""

    inference = GainInference(
        str(MODEL_PATH)
    )

    assert inference is not None


def test_audio_enhancer_initialization():
    """Check that AudioEnhancer initializes correctly."""

    enhancer = AudioEnhancer(
        str(MODEL_PATH)
    )

    assert enhancer is not None
    assert enhancer.inference is not None


def test_model_prediction_returns_value(tmp_path):
    """Check that AI inference returns a prediction."""

    audio_path = (
        tmp_path / "test_audio.wav"
    )

    create_test_audio(
        audio_path
    )

    enhancer = AudioEnhancer(
        str(MODEL_PATH)
    )

    gain = enhancer.get_recommended_gain(
        str(audio_path)
    )

    assert gain is not None


def test_model_prediction_is_numeric(tmp_path):
    """Check that AI prediction is numeric."""

    audio_path = (
        tmp_path / "test_audio.wav"
    )

    create_test_audio(
        audio_path
    )

    enhancer = AudioEnhancer(
        str(MODEL_PATH)
    )

    gain = enhancer.get_recommended_gain(
        str(audio_path)
    )

    assert isinstance(
        gain,
        (int, float, np.number)
    )


def test_model_prediction_is_finite(tmp_path):
    """Check that AI prediction is a finite value."""

    audio_path = (
        tmp_path / "test_audio.wav"
    )

    create_test_audio(
        audio_path
    )

    enhancer = AudioEnhancer(
        str(MODEL_PATH)
    )

    gain = enhancer.get_recommended_gain(
        str(audio_path)
    )

    assert np.isfinite(gain)


def test_missing_model_raises_error(tmp_path):
    """Check behaviour when model file is missing."""

    missing_model = (
        tmp_path / "missing_model.pth"
    )

    try:
        AudioEnhancer(
            str(missing_model)
        )
    except Exception:
        return

    assert False, (
        "AudioEnhancer should fail when "
        "the model file does not exist"
    )
