import numpy as np
import soundfile as sf

from audio.features import AudioFeatureExtractor


def create_test_audio(tmp_path):
    sample_rate = 16000
    duration = 1.0

    t = np.linspace(
        0,
        duration,
        int(sample_rate * duration),
        endpoint=False
    )

    audio = 0.5 * np.sin(
        2 * np.pi * 440 * t
    )

    audio_path = tmp_path / "test.wav"

    sf.write(
        audio_path,
        audio,
        sample_rate
    )

    return audio_path


def test_feature_extraction_returns_numpy_array(tmp_path):
    audio_path = create_test_audio(tmp_path)

    extractor = AudioFeatureExtractor()

    features = extractor.extract(
        str(audio_path)
    )

    assert isinstance(features, np.ndarray)


def test_feature_extraction_is_not_empty(tmp_path):
    audio_path = create_test_audio(tmp_path)

    extractor = AudioFeatureExtractor()

    features = extractor.extract(
        str(audio_path)
    )

    assert features.size > 0


def test_feature_extraction_contains_finite_values(tmp_path):
    audio_path = create_test_audio(tmp_path)

    extractor = AudioFeatureExtractor()

    features = extractor.extract(
        str(audio_path)
    )

    assert np.all(
        np.isfinite(features)
    )


def test_feature_extraction_is_one_dimensional(tmp_path):
    audio_path = create_test_audio(tmp_path)

    extractor = AudioFeatureExtractor()

    features = extractor.extract(
        str(audio_path)
    )

    assert features.ndim == 1


def test_feature_extraction_contains_rms_and_spectral_features(
    tmp_path
):
    audio_path = create_test_audio(tmp_path)

    extractor = AudioFeatureExtractor()

    features = extractor.extract(
        str(audio_path)
    )

    assert len(features) > 2


def test_feature_extraction_is_reproducible(tmp_path):
    audio_path = create_test_audio(tmp_path)

    extractor = AudioFeatureExtractor()

    features_first = extractor.extract(
        str(audio_path)
    )

    features_second = extractor.extract(
        str(audio_path)
    )

    np.testing.assert_allclose(
        features_first,
        features_second
    )
