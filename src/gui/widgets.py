"""
Custom PyQt6 widgets for Video Upscaler.

Provides reusable widgets for file selection and progress display.
"""

import time
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QProgressBar,
    QLabel,
    QFileDialog,
    QFrame,
    QSizePolicy,
)

from core.utils import format_time


class FilePickerWidget(QWidget):
    """
    A widget for selecting files with a text field and browse button.

    Supports drag-and-drop of files and displays the selected path.
    """

    file_selected = pyqtSignal(str)

    def __init__(
        self,
        label: str = "File:",
        file_filter: str = "All Files (*.*)",
        mode: str = "open",
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self._file_filter = file_filter
        self._mode = mode
        self._last_directory = str(Path.home())

        self._setup_ui(label)
        self._setup_drag_drop()

    def _setup_ui(self, label: str) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Label
        self._label = QLabel(label)
        self._label.setProperty("class", "field-label")
        layout.addWidget(self._label)

        # Input row
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)

        # Path input
        self._path_input = QLineEdit()
        self._path_input.setPlaceholderText("Select a file or drag and drop here...")
        self._path_input.textChanged.connect(self._on_text_changed)
        input_layout.addWidget(self._path_input, stretch=1)

        # Browse button
        self._browse_btn = QPushButton("Browse")
        self._browse_btn.setFixedWidth(80)
        self._browse_btn.clicked.connect(self._on_browse_clicked)
        input_layout.addWidget(self._browse_btn)

        layout.addLayout(input_layout)

    def _setup_drag_drop(self) -> None:
        self._path_input.setAcceptDrops(True)
        self._path_input.dragEnterEvent = self._drag_enter_event
        self._path_input.dropEvent = self._drop_event

    def _drag_enter_event(self, event) -> None:
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def _drop_event(self, event) -> None:
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.set_path(file_path)

    def _on_browse_clicked(self) -> None:
        if self._mode == "open":
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select File", self._last_directory, self._file_filter
            )
        else:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save File", self._last_directory, self._file_filter
            )

        if file_path:
            self._last_directory = str(Path(file_path).parent)
            self.set_path(file_path)

    def _on_text_changed(self, text: str) -> None:
        self.file_selected.emit(text)

    def get_path(self) -> str:
        return self._path_input.text().strip()

    def set_path(self, path: str) -> None:
        self._path_input.setText(path)

    def clear(self) -> None:
        self._path_input.clear()

    def set_enabled(self, enabled: bool) -> None:
        self._path_input.setEnabled(enabled)
        self._browse_btn.setEnabled(enabled)


class StepProgressBar(QWidget):
    """
    A progress bar for a single processing step.

    Shows: 15% [345/13543] (10:43) in the center of the bar.
    """

    def __init__(self, step_name: str, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._step_name = step_name
        self._start_time: Optional[float] = None
        self._current = 0
        self._total = 0

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 4)
        layout.setSpacing(4)

        # Step label
        self._step_label = QLabel(self._step_name)
        self._step_label.setProperty("class", "step-label")
        layout.addWidget(self._step_label)

        # Progress bar with text overlay
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setTextVisible(True)
        self._progress_bar.setFormat("Waiting...")
        self._progress_bar.setMinimumHeight(28)
        layout.addWidget(self._progress_bar)

    def reset(self) -> None:
        self._start_time = None
        self._current = 0
        self._total = 0
        self._progress_bar.setValue(0)
        self._progress_bar.setFormat("Waiting...")
        self._progress_bar.setProperty("class", "")
        self._progress_bar.style().unpolish(self._progress_bar)
        self._progress_bar.style().polish(self._progress_bar)

    def start(self, total: int) -> None:
        self._start_time = time.time()
        self._total = total
        self._current = 0
        self._progress_bar.setValue(0)
        self._update_format()

    def update_progress(self, current: int, total: int) -> None:
        self._current = current
        self._total = total if total > 0 else self._total

        if self._total > 0:
            percent = int((current / self._total) * 100)
            self._progress_bar.setValue(percent)

        self._update_format()

    def _update_format(self) -> None:
        if self._total == 0:
            self._progress_bar.setFormat("Waiting...")
            return

        percent = int((self._current / self._total) * 100) if self._total > 0 else 0

        # Calculate ETA
        eta_str = "--:--"
        if self._start_time and self._current > 0:
            elapsed = time.time() - self._start_time
            rate = elapsed / self._current
            remaining = rate * (self._total - self._current)
            eta_str = format_time(remaining)

        # Format: 15% [345/13543] (10:43)
        self._progress_bar.setFormat(
            f"{percent}% [{self._current:,}/{self._total:,}] ({eta_str})"
        )

    def set_complete(self) -> None:
        self._progress_bar.setValue(100)
        self._progress_bar.setFormat("100% - Complete")
        self._progress_bar.setProperty("class", "complete")
        self._progress_bar.style().unpolish(self._progress_bar)
        self._progress_bar.style().polish(self._progress_bar)

    def set_error(self) -> None:
        self._progress_bar.setFormat("Error")
        self._progress_bar.setProperty("class", "error")
        self._progress_bar.style().unpolish(self._progress_bar)
        self._progress_bar.style().polish(self._progress_bar)

    def set_active(self, active: bool) -> None:
        """Highlight this step as currently active."""
        self._step_label.setProperty("class", "step-label-active" if active else "step-label")
        self._step_label.style().unpolish(self._step_label)
        self._step_label.style().polish(self._step_label)


class MultiStepProgress(QWidget):
    """
    Container for multiple step progress bars.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._steps: dict[str, StepProgressBar] = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Create progress bars for each step
        steps = [
            ("extract", "1. Extract Frames"),
            ("upscale", "2. AI Upscale"),
            ("assemble", "3. Assemble Video"),
        ]

        for step_id, step_name in steps:
            progress = StepProgressBar(step_name)
            self._steps[step_id] = progress
            layout.addWidget(progress)

    def reset(self) -> None:
        for step in self._steps.values():
            step.reset()

    def start_step(self, step_id: str, total: int) -> None:
        if step_id in self._steps:
            # Deactivate all, activate current
            for sid, step in self._steps.items():
                step.set_active(sid == step_id)
            self._steps[step_id].start(total)

    def update_step(self, step_id: str, current: int, total: int) -> None:
        if step_id in self._steps:
            self._steps[step_id].update_progress(current, total)

    def complete_step(self, step_id: str) -> None:
        if step_id in self._steps:
            self._steps[step_id].set_complete()
            self._steps[step_id].set_active(False)

    def error_step(self, step_id: str) -> None:
        if step_id in self._steps:
            self._steps[step_id].set_error()


class ScaleToggle(QWidget):
    """
    A toggle button group for selecting scale factor.
    """

    scale_changed = pyqtSignal(int)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._buttons: dict[int, QPushButton] = {}
        self._current_scale = 2
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scales = [2, 3, 4]

        for scale in scales:
            btn = QPushButton(f"{scale}x")
            btn.setCheckable(True)
            btn.setChecked(scale == 2)
            btn.setProperty("class", "scale-toggle")
            btn.setMinimumHeight(36)
            btn.clicked.connect(lambda checked, s=scale: self._on_scale_clicked(s))

            # Round corners only on ends
            if scale == scales[0]:
                btn.setProperty("position", "left")
            elif scale == scales[-1]:
                btn.setProperty("position", "right")
            else:
                btn.setProperty("position", "middle")

            self._buttons[scale] = btn
            layout.addWidget(btn)

    def _on_scale_clicked(self, scale: int) -> None:
        self._current_scale = scale
        for s, btn in self._buttons.items():
            btn.setChecked(s == scale)
        self.scale_changed.emit(scale)

    def get_scale(self) -> int:
        return self._current_scale

    def set_scale(self, scale: int) -> None:
        if scale in self._buttons:
            self._current_scale = scale
            for s, btn in self._buttons.items():
                btn.setChecked(s == scale)

    def set_enabled(self, enabled: bool) -> None:
        for btn in self._buttons.values():
            btn.setEnabled(enabled)


class VideoInfoLabel(QWidget):
    """
    Compact video information display.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        self._info_label = QLabel("No video selected")
        self._info_label.setProperty("class", "video-info")
        layout.addWidget(self._info_label)
        layout.addStretch()

    def clear(self) -> None:
        self._info_label.setText("No video selected")

    def update_info(
        self,
        width: int,
        height: int,
        fps: float,
        duration: float,
        frame_count: int,
        has_audio: bool
    ) -> None:
        audio_str = "Audio" if has_audio else "No Audio"
        self._info_label.setText(
            f"{width}x{height} | {fps:.1f}fps | {format_time(duration)} | "
            f"{frame_count:,} frames | {audio_str}"
        )
