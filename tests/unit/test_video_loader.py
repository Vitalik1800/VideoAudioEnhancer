import pytest

from video.loader import VideoLoader
import cv2


class DummyCapture:
    """Mock video capture object for unit testing."""

    def __init__(
        self,
        fps: float,
        frame_count: int,
        opened: bool = True
    ):
        self.fps = fps
        self.frame_count = frame_count
        self.opened = opened
        self.released = False

    def is_opened(self):
        return self.opened

    def get(self, property_id):

        if property_id == cv2.CAP_PROP_FPS:
            return self.fps

        if property_id == cv2.CAP_PROP_FRAME_COUNT:
            return self.frame_count

        return 0

    def release(self):
        self.released = True


def test_get_duration(monkeypatch, tmp_path):
    """Check video duration calculation."""

    video_path = tmp_path / "test.mp4"
    video_path.touch()

    capture = DummyCapture(
        fps=30.0,
        frame_count=900
    )

    monkeypatch.setattr(
        VideoLoader,
        "_open_video",
        staticmethod(lambda path: capture)
    )

    duration = VideoLoader.get_duration(
        str(video_path)
    )

    assert duration == pytest.approx(
        30.0
    )


def test_get_duration_with_fractional_result(
    monkeypatch,
    tmp_path
):
    """Check duration with a non-integer result."""

    video_path = tmp_path / "test.mp4"
    video_path.touch()

    capture = DummyCapture(
        fps=25.0,
        frame_count=625
    )

    monkeypatch.setattr(
        VideoLoader,
        "_open_video",
        staticmethod(lambda path: capture)
    )

    duration = VideoLoader.get_duration(
        str(video_path)
    )

    assert duration == pytest.approx(
        25.0
    )


def test_get_duration_uses_frame_count_and_fps(
    monkeypatch,
    tmp_path
):
    """Check that duration is calculated as frames / FPS."""

    video_path = tmp_path / "test.mp4"
    video_path.touch()

    capture = DummyCapture(
        fps=24.0,
        frame_count=1000
    )

    monkeypatch.setattr(
        VideoLoader,
        "_open_video",
        staticmethod(lambda path: capture)
    )

    duration = VideoLoader.get_duration(
        str(video_path)
    )

    assert duration == pytest.approx(
        1000 / 24
    )


def test_get_duration_releases_capture(
    monkeypatch,
    tmp_path
):
    """Check that video capture is released."""

    video_path = tmp_path / "test.mp4"
    video_path.touch()

    capture = DummyCapture(
        fps=30.0,
        frame_count=900
    )

    monkeypatch.setattr(
        VideoLoader,
        "_open_video",
        staticmethod(lambda path: capture)
    )

    VideoLoader.get_duration(
        str(video_path)
    )

    assert capture.released is True


def test_get_duration_invalid_fps(
    monkeypatch,
    tmp_path
):
    """Invalid FPS must raise ValueError."""

    video_path = tmp_path / "test.mp4"
    video_path.touch()

    capture = DummyCapture(
        fps=0.0,
        frame_count=900
    )

    monkeypatch.setattr(
        VideoLoader,
        "_open_video",
        staticmethod(lambda path: capture)
    )

    with pytest.raises(
        ValueError,
        match="Invalid video FPS"
    ):
        VideoLoader.get_duration(
            str(video_path)
        )


def test_get_duration_negative_fps(
    monkeypatch,
    tmp_path
):
    """Negative FPS must raise ValueError."""

    video_path = tmp_path / "test.mp4"
    video_path.touch()

    capture = DummyCapture(
        fps=-30.0,
        frame_count=900
    )

    monkeypatch.setattr(
        VideoLoader,
        "_open_video",
        staticmethod(lambda path: capture)
    )

    with pytest.raises(
        ValueError,
        match="Invalid video FPS"
    ):
        VideoLoader.get_duration(
            str(video_path)
        )
