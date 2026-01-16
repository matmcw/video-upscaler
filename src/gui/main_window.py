"""
Main application window for Video Upscaler.

Provides the primary user interface with file selection, settings,
progress display, and processing controls.
"""

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QLabel,
    QLineEdit,
    QFrame,
    QScrollArea,
)

from gui.widgets import (
    FilePickerWidget,
    MultiStepProgress,
    ScaleToggle,
    VideoInfoLabel,
)
from gui.styles import get_stylesheet
from core.video_processor import VideoProcessor
from core.utils import (
    validate_input_video,
    validate_all_dependencies,
    get_video_info,
    generate_output_path,
    VideoValidationError,
)


class MainWindow(QMainWindow):
    """
    Main application window for the Video Upscaler.
    """

    VIDEO_FILTER = (
        "Video Files (*.mp4 *.mkv *.avi *.mov *.wmv *.flv *.webm *.m4v *.mpeg *.mpg);;"
        "All Files (*.*)"
    )

    def __init__(self):
        super().__init__()

        self._processor: Optional[VideoProcessor] = None
        self._is_processing = False
        self._current_stage = ""
        self._output_path: Optional[Path] = None

        self._setup_window()
        self._setup_ui()
        self._connect_signals()

    def _setup_window(self) -> None:
        self.setWindowTitle("Video Upscaler")
        self.setMinimumSize(450, 500)
        self.resize(520, 620)
        self.setStyleSheet(get_stylesheet())

    def _setup_ui(self) -> None:
        # Central widget with scroll area for small windows
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setCentralWidget(scroll)

        # Main container
        container = QWidget()
        scroll.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Title
        title = QLabel("Video Upscaler")
        title.setStyleSheet("font-size: 20pt; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        layout.addSpacing(8)

        # Input section
        input_header = QLabel("Input Video")
        input_header.setProperty("class", "section-header")
        layout.addWidget(input_header)

        self._input_picker = FilePickerWidget(
            label="Select video file to upscale:",
            file_filter=self.VIDEO_FILTER,
            mode="open"
        )
        layout.addWidget(self._input_picker)

        # Video info
        self._video_info = VideoInfoLabel()
        layout.addWidget(self._video_info)

        # Output path (editable)
        output_label = QLabel("Output path:")
        output_label.setProperty("class", "field-label")
        layout.addWidget(output_label)

        self._output_edit = QLineEdit()
        self._output_edit.setPlaceholderText("Output path will be set automatically...")
        self._output_edit.textChanged.connect(self._on_output_changed)
        layout.addWidget(self._output_edit)

        # Separator
        layout.addWidget(self._create_separator())

        # Scale section
        scale_row = QHBoxLayout()
        scale_row.setContentsMargins(0, 0, 0, 0)
        scale_row.setSpacing(16)

        scale_header = QLabel("Scale")
        scale_header.setProperty("class", "section-header")
        scale_row.addWidget(scale_header)

        self._scale_toggle = ScaleToggle()
        scale_row.addWidget(self._scale_toggle)
        scale_row.addStretch()

        layout.addLayout(scale_row)

        # Separator
        layout.addWidget(self._create_separator())

        # Progress section
        progress_header = QLabel("Progress")
        progress_header.setProperty("class", "section-header")
        layout.addWidget(progress_header)

        self._progress = MultiStepProgress()
        layout.addWidget(self._progress)

        # Spacer
        layout.addStretch()

        # Single action button (changes based on state)
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self._action_btn = QPushButton("Start Upscaling")
        self._action_btn.setProperty("class", "primary")
        self._action_btn.setMinimumWidth(160)
        self._action_btn.clicked.connect(self._on_action_clicked)
        button_layout.addWidget(self._action_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def _create_separator(self) -> QFrame:
        sep = QFrame()
        sep.setProperty("class", "separator")
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        return sep

    def _connect_signals(self) -> None:
        self._input_picker.file_selected.connect(self._on_input_selected)
        self._scale_toggle.scale_changed.connect(self._on_scale_changed)

    def _on_scale_changed(self, scale: int) -> None:
        # Update output path with new scale
        input_path = self._input_picker.get_path()
        if input_path:
            self._output_path = generate_output_path(Path(input_path), f"_{scale}x_upscaled")
            self._output_edit.setText(str(self._output_path))

    def _on_output_changed(self, text: str) -> None:
        # Update output path when user edits it
        if text.strip():
            self._output_path = Path(text.strip())
        else:
            self._output_path = None

    def _on_input_selected(self, path: str) -> None:
        if not path:
            self._video_info.clear()
            self._output_path = None
            self._output_edit.clear()
            return

        try:
            input_path = Path(path)
            validate_input_video(input_path)
            info = get_video_info(input_path)

            self._video_info.update_info(
                width=info.width,
                height=info.height,
                fps=info.fps,
                duration=info.duration,
                frame_count=info.frame_count,
                has_audio=info.has_audio
            )

            scale = self._scale_toggle.get_scale()
            self._output_path = generate_output_path(input_path, f"_{scale}x_upscaled")
            self._output_edit.setText(str(self._output_path))

        except VideoValidationError as e:
            self._video_info.clear()
            self._output_path = None
            self._output_edit.clear()
            QMessageBox.warning(self, "Invalid Video", str(e))
        except Exception as e:
            self._video_info.clear()
            self._output_path = None
            self._output_edit.clear()

    def _on_action_clicked(self) -> None:
        if self._is_processing:
            # Cancel action
            result = QMessageBox.question(
                self, "Cancel Processing",
                "Are you sure you want to cancel?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if result == QMessageBox.StandardButton.Yes:
                self._processor.cancel()
        else:
            # Start action
            input_path = self._input_picker.get_path()
            if not input_path:
                QMessageBox.warning(self, "No Input", "Please select an input video file.")
                return

            if not self._output_path:
                QMessageBox.warning(self, "No Output", "Please select a valid input video first.")
                return

            # Check dependencies
            errors = validate_all_dependencies()
            if errors:
                QMessageBox.critical(self, "Missing Dependencies", "\n\n".join(errors))
                return

            # Check if output exists
            if self._output_path.exists():
                result = QMessageBox.question(
                    self, "File Exists",
                    f"Output file already exists:\n{self._output_path.name}\n\nOverwrite?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if result != QMessageBox.StandardButton.Yes:
                    return

            self._start_processing(Path(input_path), self._output_path)

    def _start_processing(self, input_path: Path, output_path: Path) -> None:
        self._is_processing = True
        self._set_processing_ui_state(True)
        self._progress.reset()

        scale = self._scale_toggle.get_scale()

        self._processor = VideoProcessor(
            input_path=input_path,
            output_path=output_path,
            scale=scale
        )

        self._processor.progress_updated.connect(self._on_progress_updated)
        self._processor.processing_complete.connect(self._on_processing_complete)
        self._processor.processing_error.connect(self._on_processing_error)
        self._processor.stage_changed.connect(self._on_stage_changed)

        self._processor.start()

    def _set_processing_ui_state(self, processing: bool) -> None:
        self._input_picker.set_enabled(not processing)
        self._scale_toggle.set_enabled(not processing)
        self._output_edit.setEnabled(not processing)

        if processing:
            self._action_btn.setText("Cancel")
            self._action_btn.setProperty("class", "danger")
        else:
            self._action_btn.setText("Start Upscaling")
            self._action_btn.setProperty("class", "primary")

        # Force style refresh
        self._action_btn.style().unpolish(self._action_btn)
        self._action_btn.style().polish(self._action_btn)

    def _on_progress_updated(self, current: int, total: int, stage: str, message: str) -> None:
        # Map stage names to step IDs
        stage_map = {
            "EXTRACTING": "extract",
            "UPSCALING": "upscale",
            "ASSEMBLING": "assemble",
        }

        step_id = stage_map.get(stage.upper())
        if step_id:
            if step_id != self._current_stage:
                # New stage started
                if self._current_stage:
                    self._progress.complete_step(self._current_stage)
                self._current_stage = step_id
                self._progress.start_step(step_id, total)

            self._progress.update_step(step_id, current, total)

    def _on_processing_complete(self, output_path: str) -> None:
        self._is_processing = False
        self._set_processing_ui_state(False)

        # Complete remaining steps
        if self._current_stage:
            self._progress.complete_step(self._current_stage)
        self._current_stage = ""

        self._processor = None

        QMessageBox.information(
            self, "Complete",
            f"Video upscaling complete!\n\nSaved to:\n{output_path}"
        )

    def _on_processing_error(self, error_message: str) -> None:
        self._is_processing = False
        self._set_processing_ui_state(False)

        if self._current_stage:
            self._progress.error_step(self._current_stage)
        self._current_stage = ""

        self._processor = None

        QMessageBox.critical(self, "Error", f"Processing failed:\n\n{error_message}")

    def _on_stage_changed(self, stage_name: str) -> None:
        pass  # Handled in progress_updated

    def closeEvent(self, event) -> None:
        if self._is_processing:
            result = QMessageBox.question(
                self, "Processing in Progress",
                "Video processing is still running.\n\nQuit anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if result == QMessageBox.StandardButton.Yes:
                if self._processor:
                    self._processor.cancel()
                    self._processor.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
