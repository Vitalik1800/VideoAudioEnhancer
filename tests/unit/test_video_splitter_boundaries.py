import pytest

from video.splitter import VideoSplitter


@pytest.fixture
def splitter():
    """Create VideoSplitter instance."""
    return VideoSplitter()


@pytest.mark.parametrize(
    "duration, expected_parts",
    [
        # Just below 30 minutes
        (29 * 60 + 59, 1),

        # Exactly 30 minutes
        (30 * 60, 10),

        # Just below 60 minutes
        (59 * 60 + 59, 10),

        # Exactly 60 minutes
        (60 * 60, 20)
    ]
)
def test_splitter_boundary_values(
    splitter,
    duration,
    expected_parts
):
    """Check VideoSplitter behavior at critical boundaries."""

    assert splitter.get_split_count(
        duration
    ) == expected_parts
