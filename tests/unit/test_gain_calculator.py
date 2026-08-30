import torch
import pytest

from audio.enhancer import AudioEnhancer


class DummyInference:
    """Dummy inference object for unit testing."""

    def __init__(self, gain: float = 6.0):
        self.gain = gain

    def predict(self, audio_path: str):
        class Result:
            final_gain = self.gain

        return Result()


@pytest.fixture
def enhancer():
    """
    Create AudioEnhancer without loading the real AI model.
    """

    instance = AudioEnhancer.__new__(
        AudioEnhancer
    )

    instance.inference = DummyInference()

    return instance


def test_recommended_gain(enhancer):
    """Check that recommended gain is returned correctly."""

    gain = enhancer.get_recommended_gain(
        "test_audio.wav"
    )

    assert gain == 6.0


def test_recommended_gain_can_be_negative(enhancer):
    """Check that negative gain is supported."""

    enhancer.inference = DummyInference(
        gain=-3.5
    )

    gain = enhancer.get_recommended_gain(
        "test_audio.wav"
    )

    assert gain == -3.5


def test_apply_zero_gain(enhancer):
    """0 dB gain must not change the waveform."""

    waveform = torch.tensor(
        [[0.2, -0.4, 0.6]]
    )

    result = enhancer.apply_gain(
        waveform,
        0.0
    )

    assert torch.allclose(
        result,
        waveform
    )


def test_apply_positive_gain(enhancer):
    """Check positive gain calculation."""

    waveform = torch.tensor(
        [[0.5]]
    )

    result = enhancer.apply_gain(
        waveform,
        6.0
    )

    expected = waveform * (
        10 ** (6.0 / 20.0)
    )

    assert torch.allclose(
        result,
        expected
    )


def test_apply_negative_gain(enhancer):
    """Check negative gain calculation."""

    waveform = torch.tensor(
        [[0.8]]
    )

    result = enhancer.apply_gain(
        waveform,
        -6.0
    )

    expected = waveform * (
        10 ** (-6.0 / 20.0)
    )

    assert torch.allclose(
        result,
        expected
    )


def test_get_peak(enhancer):
    """Check absolute waveform peak."""

    waveform = torch.tensor(
        [[0.2, -0.8, 0.5, -0.3]]
    )

    peak = enhancer.get_peak(
        waveform
    )

    assert peak == pytest.approx(
        0.8
    )


def test_get_peak_with_negative_values(enhancer):
    """Peak must use absolute amplitude."""

    waveform = torch.tensor(
        [[-0.95, 0.4, -0.7]]
    )

    peak = enhancer.get_peak(
        waveform
    )

    assert peak == pytest.approx(
        0.95
    )


def test_prevent_clipping_when_not_clipped(enhancer):
    """Waveform below 1.0 must remain unchanged."""

    waveform = torch.tensor(
        [[0.2, -0.8, 0.5]]
    )

    result = enhancer.prevent_clipping(
        waveform
    )

    assert torch.equal(
        result,
        waveform
    )


def test_prevent_clipping(enhancer):
    """Waveform above 1.0 must be scaled down."""

    waveform = torch.tensor(
        [[0.5, -2.0, 1.0]]
    )

    result = enhancer.prevent_clipping(
        waveform
    )

    assert enhancer.get_peak(
        result
    ) == pytest.approx(
        1.0
    )


def test_prevent_clipping_preserves_ratio(enhancer):
    """Clipping prevention must scale the entire waveform equally."""

    waveform = torch.tensor(
        [[0.5, -2.0, 1.0]]
    )

    result = enhancer.prevent_clipping(
        waveform
    )

    expected = waveform / 2.0

    assert torch.allclose(
        result,
        expected
    )


def test_normalize(enhancer):
    """Check normalization to target peak."""

    waveform = torch.tensor(
        [[0.2, -0.8, 0.4]]
    )

    result = enhancer.normalize(
        waveform,
        target_peak=0.95
    )

    assert enhancer.get_peak(
        result
    ) == pytest.approx(
        0.95
    )


def test_normalize_zero_waveform(enhancer):
    """Zero waveform must remain zero."""

    waveform = torch.zeros(
        (1, 100)
    )

    result = enhancer.normalize(
        waveform
    )

    assert torch.equal(
        result,
        waveform
    )


@pytest.mark.parametrize(
    "target_peak",
    [
        0.0,
        -0.1,
        1.01,
        2.0
    ]
)
def test_normalize_invalid_target_peak(
    enhancer,
    target_peak
):
    """Invalid target peak values must raise ValueError."""

    waveform = torch.tensor(
        [[0.5]]
    )

    with pytest.raises(ValueError):
        enhancer.normalize(
            waveform,
            target_peak=target_peak
        )
