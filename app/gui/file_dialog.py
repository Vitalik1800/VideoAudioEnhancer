from pathlib import Path
import tkinter as tk
from tkinter import filedialog


class FileDialog:
    """Provides file selection functionality."""

    SUPPORTED_VIDEO_FORMATS = (
        "*.mp4",
        "*.mkv",
        "*.avi",
        "*.mov",
        "*.webm",
        "*.flv",
        "*.wmv"
    )

    def select_video(self) -> Path | None:
        """Open a dialog and return the selected video path."""

        root = tk.Tk()
        root.withdraw()

        file_path = filedialog.askopenfilename(
            title="Select a video file",
            filetypes=[
                (
                    "Video files",
                    " ".join(self.SUPPORTED_VIDEO_FORMATS)
                ),
                ("All files", "*.*")
            ]
        )

        root.destroy()

        if not file_path:
            return None

        return Path(file_path)
    