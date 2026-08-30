from pathlib import Path

import pytest

from video.splitter import VideoSplitter


@pytest.fixture
def splitter():
    """Create VideoSplitter instance."""
    return VideoSplitter()


def test_split_count_for_short_video(splitter):
    """Video shorter than 30 minutes must not be split."""

    assert splitter.get_split_count(
        29 * 60 + 59
    ) == 1


def test_split_count_for_30_minutes(splitter):
    """Video of exactly 30 minutes must be split into 10 parts."""

    assert splitter.get_split_count(
        30 * 60
    ) == 10


def test_split_count_for_59_minutes(splitter):
    """Video shorter than 60 minutes must be split into 10 parts."""

    assert splitter.get_split_count(
        59 * 60 + 59
    ) == 10


def test_split_count_for_60_minutes(splitter):
    """Video of exactly 60 minutes must be split into 20 parts."""

    assert splitter.get_split_count(
        60 * 60
    ) == 20


def test_split_count_for_long_video(splitter):
    """Video longer than 60 minutes must be split into 20 parts."""

    assert splitter.get_split_count(
        2 * 60 * 60
    ) == 20


@pytest.mark.parametrize(
    "duration, expected_parts",
    [
        (0, 1),
        (1, 1),
        (29 * 60 + 59, 1),
        (30 * 60, 10),
        (45 * 60, 10),
        (59 * 60 + 59, 10),
        (60 * 60, 20),
        (90 * 60, 20)
    ]
)
def test_split_count_boundaries(
    splitter,
    duration,
    expected_parts
):
    """Check split count for important duration boundaries."""

    assert splitter.get_split_count(
        duration
    ) == expected_parts


def test_part_filename(splitter):
    """Check generated part filenames."""

    assert splitter.get_part_filename(1) == (
        "video_part_01.mp4"
    )

    assert splitter.get_part_filename(10) == (
        "video_part_10.mp4"
    )

    assert splitter.get_part_filename(20) == (
        "video_part_20.mp4"
    )


def test_split_short_video_returns_original_file(
    splitter,
    tmp_path
):
    """Short video must not be split."""

    video_file = tmp_path / "test.mp4"
    video_file.touch()

    result = splitter.split(
        str(video_file),
        str(tmp_path / "output"),
        29 * 60 + 59
    )

    assert result == [
        str(video_file)
    ]


def test_split_creates_expected_number_of_files(
    splitter,
    tmp_path,
    monkeypatch
):
    """Split operation must create the expected number of files."""

    video_file = tmp_path / "test.mp4"
    output_directory = tmp_path / "output"

    video_file.touch()

    def fake_run(
        command,
        **_kwargs
    ):
        output_file = Path(command[-1])
        output_file.touch()

    monkeypatch.setattr(
        "subprocess.run",
        fake_run
    )

    result = splitter.split(
        str(video_file),
        str(output_directory),
        30 * 60
    )

    assert len(result) == 10

    assert output_directory.exists()

    assert all(
        Path(file).exists()
        for file in result
    )


def test_split_creates_correct_filenames(
    splitter,
    tmp_path,
    monkeypatch
):
    """Split operation must use correct part filenames."""

    video_file = tmp_path / "test.mp4"
    output_directory = tmp_path / "output"

    video_file.touch()

    def fake_run(
        command,
        **_kwargs
    ):
        output_file = Path(command[-1])
        output_file.touch()

    monkeypatch.setattr(
        "subprocess.run",
        fake_run
    )

    result = splitter.split(
        str(video_file),
        str(output_directory),
        60 * 60
    )

    expected_names = [
        f"video_part_{index:02d}.mp4"
        for index in range(1, 21)
    ]

    actual_names = [
        Path(file).name
        for file in result
    ]

    assert actual_names == expected_names


def test_split_missing_video_raises_error(
    splitter,
    tmp_path
):
    """Missing source video must raise FileNotFoundError."""

    video_file = tmp_path / "missing.mp4"
    output_directory = tmp_path / "output"

    with pytest.raises(FileNotFoundError):
        splitter.split(
            str(video_file),
            str(output_directory),
            30 * 60
        )
