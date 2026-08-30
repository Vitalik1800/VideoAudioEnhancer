import os
import subprocess
from pathlib import Path

import customtkinter as ctk

from app.gui.file_dialog import FileDialog
from video.loader import VideoLoader
from video.splitter import VideoSplitter
from video.output import OutputManager
from video.audio_processor import VideoAudioProcessor
from video.muxer import VideoMuxer
from audio.enhancer import AudioEnhancer


class Application(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Video Audio Enhancer AI")
        self.geometry("800x700")
        self.resizable(False, False)

        self.project_root = Path(__file__).resolve().parents[2]

        self.selected_video: Path | None = None

        self.file_dialog = FileDialog()
        self.video_splitter = VideoSplitter()
        self.output_manager = OutputManager()
        self.video_muxer = VideoMuxer()

        self._create_widgets()

    def _create_widgets(self):
        self.title_label = ctk.CTkLabel(
            self,
            text="Video Audio Enhancer AI",
            font=("Arial", 28, "bold")
        )
        self.title_label.pack(pady=(40, 20))

        self.file_label = ctk.CTkLabel(
            self,
            text="No video selected"
        )
        self.file_label.pack(pady=10)

        self.info_label = ctk.CTkLabel(
            self,
            text="File information will appear here",
            justify="left"
        )
        self.info_label.pack(pady=10)

        self.parts_label = ctk.CTkLabel(
            self,
            text="Parts: not calculated",
            justify="left"
        )
        self.parts_label.pack(pady=5)

        self.ai_label = ctk.CTkLabel(
            self,
            text="AI analysis: not available",
            justify="left"
        )
        self.ai_label.pack(pady=10)

        self.select_button = ctk.CTkButton(
            self,
            text="Select Video",
            command=self._select_video
        )
        self.select_button.pack(pady=10)

        self.open_output_button = ctk.CTkButton(
            self,
            text="Open Results Folder",
            command=self._open_output_directory
        )
        self.open_output_button.pack(pady=10)

        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=500
        )
        self.progress_bar.pack(pady=(30, 10))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            self,
            text="Ready"
        )
        self.status_label.pack(pady=10)

        self.enhance_button = ctk.CTkButton(
            self,
            text="Enhance Audio",
            command=self._enhance_audio
        )
        self.enhance_button.pack(pady=20)

    def _select_video(self):
        video_path = self.file_dialog.select_video()

        if video_path is None:
            self._set_status(
                "Video selection cancelled"
            )
            return

        self.selected_video = video_path

        try:
            info = VideoLoader.load(str(video_path))

            file_size = video_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)

            duration = info["duration"]
            split_count = self.video_splitter.get_split_count(
                duration
            )

            minutes = int(duration // 60)
            seconds = int(duration % 60)

            self.file_label.configure(
                text=f"Selected: {video_path.name}"
            )

            self.info_label.configure(
                text=(
                    f"Resolution: {info['width']}x{info['height']}\n"
                    f"FPS: {info['fps']:.2f}\n"
                    f"Frames: {info['frame_count']}\n"
                    f"Duration: {minutes:02d}:{seconds:02d}\n"
                    f"File size: {file_size_mb:.2f} MB"
                )
            )

            self.parts_label.configure(
                text=f"Parts to process: {split_count}"
            )

            self._set_status(
                "Video loaded successfully"
            )

        except Exception as error:
            self.selected_video = None

            self.file_label.configure(
                text="Failed to load video"
            )

            self.info_label.configure(
                text="File information unavailable"
            )

            self.parts_label.configure(
                text="Parts: not calculated"
            )

            self._set_status(
                f"Error: {error}"
            )

    def _open_output_directory(self):
        if self.selected_video is None:
            self._set_status(
                "Please select a video first"
            )
            return

        try:
            output_directory = (
                self.project_root
                / "output"
                / self.selected_video.stem
            )

            output_directory.mkdir(
                parents=True,
                exist_ok=True
            )

            os.startfile(
                str(output_directory)
            )

            self._set_status(
                "Results folder opened"
            )

        except Exception as error:
            self._set_status(
                f"Failed to open results folder: {error}"
            )

    def _enhance_audio(self):
        if self.selected_video is None:
            self._set_status(
                "Please select a video first"
            )
            return

        try:
            self.enhance_button.configure(
                state="disabled"
            )

            # 1. Load Video
            self._set_progress(
                0.05,
                "Loading video"
            )

            duration = VideoLoader.get_duration(
                str(self.selected_video)
            )

            # 2. Determine number of parts
            self._set_progress(
                0.10,
                "Calculating video parts"
            )

            split_count = self.video_splitter.get_split_count(
                duration
            )

            self.parts_label.configure(
                text=f"Parts to process: {split_count}"
            )

            # 3. Create temporary audio paths
            audio_directory = (
                self.project_root
                / "data"
                / "audio"
            )

            audio_directory.mkdir(
                parents=True,
                exist_ok=True
            )

            audio_path = (
                audio_directory
                / "input.wav"
            )

            enhanced_audio = (
                audio_directory
                / "enhanced.wav"
            )

            # 4. Extract audio from video
            self._set_progress(
                0.20,
                "Extracting audio"
            )

            extract_command = [
                "ffmpeg",
                "-y",
                "-i",
                str(self.selected_video),
                "-vn",
                "-acodec",
                "pcm_s16le",
                "-ar",
                "48000",
                "-ac",
                "1",
                str(audio_path)
            ]

            subprocess.run(
                extract_command,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            if not audio_path.exists():
                raise RuntimeError(
                    "Failed to extract audio from video"
                )

            # 5. AI analysis
            self._set_progress(
                0.30,
                "AI analysis"
            )

            model_path = (
                self.project_root
                / "models"
                / "audio_gain_model.pth"
            )

            enhancer = AudioEnhancer(
                str(model_path)
            )

            gain = enhancer.get_recommended_gain(
                str(audio_path)
            )

            self.ai_label.configure(
                text=(
                    "AI analysis completed\n"
                    f"Recommended Gain: {gain:+.2f} dB"
                )
            )

            # 6. Enhance audio
            self._set_progress(
                0.40,
                "Enhancing audio"
            )

            processor = VideoAudioProcessor(
                str(model_path)
            )

            processor.enhance_audio(
                str(audio_path),
                str(enhanced_audio)
            )

            if not enhanced_audio.exists():
                raise RuntimeError(
                    "Enhanced audio file was not created"
                )

            # 7. Create output directory
            self._set_progress(
                0.50,
                "Creating output directory"
            )

            output_directory = Path(
                self.output_manager.create_output_directory(
                    str(self.selected_video)
                )
            )

            # 8. Split video if required
            self._set_progress(
                0.55,
                "Splitting video"
            )

            if split_count == 1:
                video_parts = [
                    str(self.selected_video)
                ]
            else:
                video_parts = self.video_splitter.split(
                    str(self.selected_video),
                    str(output_directory),
                    duration
                )

            if len(video_parts) != split_count:
                raise RuntimeError(
                    f"Expected {split_count} video parts, "
                    f"but received {len(video_parts)}"
                )

            # 9. Process every video part
            for index, video_part in enumerate(
                video_parts,
                start=1
            ):
                progress = (
                    0.55
                    + (0.40 * index / split_count)
                )

                self._set_progress(
                    progress,
                    f"Processing part {index}/{split_count}"
                )

                # Get actual part duration
                part_duration = VideoLoader.get_duration(
                    video_part
                )

                # Calculate audio start position
                if split_count == 1:
                    start_time = 0
                else:
                    start_time = (
                        sum(
                            VideoLoader.get_duration(
                                video_parts[i]
                            )
                            for i in range(index - 1)
                        )
                    )

                # Create temporary audio for this part
                part_audio = (
                    audio_directory
                    / f"enhanced_part_{index:02d}.wav"
                )

                audio_command = [
                    "ffmpeg",
                    "-y",
                    "-ss",
                    str(start_time),
                    "-i",
                    str(enhanced_audio),
                    "-t",
                    str(part_duration),
                    "-acodec",
                    "pcm_s16le",
                    "-ar",
                    "48000",
                    "-ac",
                    "1",
                    str(part_audio)
                ]

                subprocess.run(
                    audio_command,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                if not part_audio.exists():
                    raise RuntimeError(
                        f"Failed to create audio for part {index}"
                    )

                # Output filename
                output_path = (
                    output_directory
                    / self.video_splitter.get_part_filename(
                        index
                    )
                )

                # Mux video + corresponding audio
                self.video_muxer.mux(
                    str(video_part),
                    str(part_audio),
                    str(output_path)
                )

                if not output_path.exists():
                    raise RuntimeError(
                        f"Output video was not created: "
                        f"{output_path}"
                    )

            # 10. Completed
            self._set_progress(
                1.0,
                "Completed"
            )

            self._set_status(
                f"Processing completed successfully "
                f"({split_count} part(s))"
            )

            self.enhance_button.configure(
                state="normal"
            )

        except Exception as error:
            self.progress_bar.set(0)

            self.ai_label.configure(
                text="AI analysis failed"
            )

            self._set_status(
                f"Processing error: {error}"
            )

            self.enhance_button.configure(
                state="normal"
            )

    def _finish_audio_enhancement(self):
        self._set_progress(
            1.0,
            "Audio enhancement completed"
        )

        self.enhance_button.configure(
            state="normal"
        )

    def _set_progress(self, value: float, status: str):
        self.progress_bar.set(value)

        self._set_status(
            f"{status} ({int(value * 100)}%)"
        )

        self.update_idletasks()

    def _set_status(self, status: str):
        self.status_label.configure(
            text=status
        )

        self.update_idletasks()
