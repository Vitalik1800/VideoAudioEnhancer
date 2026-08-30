from pathlib import Path

import pytest


@pytest.fixture
def project_root():
    """Return the project root directory."""

    return Path(__file__).resolve().parents[2]


@pytest.fixture
def test_output_directory(tmp_path):
    """Create an isolated temporary output directory."""

    output_directory = (
        tmp_path / "output"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    return output_directory


@pytest.fixture
def test_data_directory(
    project_root
):
    """Return the integration test data directory."""

    data_directory = (
        project_root
        / "tests"
        / "data"
    )

    data_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    return data_directory
