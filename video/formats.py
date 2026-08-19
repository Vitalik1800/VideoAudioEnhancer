SUPPORTED_VIDEO_FORMATS = {
    "mp4",
    "matroska",
    "avi",
    "mov",
    "webm",
    "flv",
    "wmv"
}


def is_supported_format(format_name: str) -> bool:
    """Return whether the video format is supported."""

    formats = {
        value.strip().lower()
        for value in format_name.split(",")
    }

    return bool(
        formats.intersection(SUPPORTED_VIDEO_FORMATS)
    )
