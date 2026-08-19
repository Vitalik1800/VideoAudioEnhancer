import customtkinter as ctk


class Application(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Video Audio Enhancer AI")
        self.geometry("800x500")
        self.resizable(False, False)

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

        self.select_button = ctk.CTkButton(
            self,
            text="Select Video",
            command=self._select_video
        )
        self.select_button.pack(pady=10)

        self.output_button = ctk.CTkButton(
            self,
            text="Select Output Folder",
            command=self._select_output_directory
        )
        self.output_button.pack(pady=10)

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

        self.start_button = ctk.CTkButton(
            self,
            text="Start Processing",
            command=self._start_processing
        )
        self.start_button.pack(pady=20)

    def _select_video(self):
        self.status_label.configure(
            text="Video selection is not implemented yet"
        )

    def _select_output_directory(self):
        self.status_label.configure(
            text="Output directory selection is not implemented yet"
        )

    def _start_processing(self):
        self.status_label.configure(
            text="Processing Pipeline is not connected yet"
        )