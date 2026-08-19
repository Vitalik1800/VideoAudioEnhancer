class VideoSplitter:
    """Handles splitting videos into multiple parts."""

    SHORT_VIDEO_LIMIT = 30 * 60
    LONG_VIDEO_LIMIT = 60 * 60

    SHORT_SPLIT_COUNT = 10
    LONG_SPLIT_COUNT = 20

    def get_split_count(self, duration: float) -> int:
        """Return the required number of parts based on duration."""

        if duration < self.SHORT_VIDEO_LIMIT:
            return 1

        if duration < self.LONG_VIDEO_LIMIT:
            return self.SHORT_SPLIT_COUNT

        return self.LONG_SPLIT_COUNT

    def split(
        self,
        video_path: str,
        output_directory: str,
        duration: float
    ) -> list[str]:
        """Split a video into the required number of parts."""

        split_count = self.get_split_count(duration)

        if split_count == 1:
            return [video_path]

        raise NotImplementedError(
            "Video splitting is not implemented yet."
        )
