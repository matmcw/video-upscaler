"""
Video processing pipeline orchestrator.

Coordinates the complete video upscaling workflow:
1. Frame extraction from source video
2. AI upscaling of frames
3. Video reassembly with original audio

Runs as a QThread to keep the GUI responsive during processing.
"""

import shutil
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from enum import Enum, auto

from PyQt6.QtCore import QThread, pyqtSignal

from core.utils import (
    get_temp_directory,
    get_video_info,
    validate_input_video,
    validate_all_dependencies,
    generate_output_path,
    VideoInfo
)
from core.frame_extractor import FrameExtractor, FrameExtractionError
from core.upscaler import Upscaler, UpscalingError
from core.video_assembler import VideoAssembler, VideoAssemblyError


class ProcessingStage(Enum):
    """Enumeration of processing stages."""
    IDLE = auto()
    VALIDATING = auto()
    EXTRACTING = auto()
    UPSCALING = auto()
    ASSEMBLING = auto()
    CLEANUP = auto()
    COMPLETE = auto()
    ERROR = auto()
    CANCELLED = auto()


@dataclass
class ProcessingProgress:
    """Container for processing progress information."""
    stage: ProcessingStage
    current_frame: int
    total_frames: int
    status_message: str
    elapsed_time: float = 0.0
    estimated_remaining: float = -1.0


class VideoProcessor(QThread):
    """
    Main video processing pipeline running on a background thread.

    Emits signals to communicate progress and completion status to the GUI.
    Supports cancellation at any stage of processing.

    Signals:
        progress_updated: Emitted when progress changes.
            Args: (current_frame, total_frames, stage_name, status_message)
        processing_complete: Emitted when processing finishes successfully.
            Args: (output_path,)
        processing_error: Emitted when an error occurs.
            Args: (error_message,)
        stage_changed: Emitted when processing stage changes.
            Args: (stage_name,)
    """

    # Qt signals for thread-safe GUI communication
    progress_updated = pyqtSignal(int, int, str, str)  # current, total, stage, message
    processing_complete = pyqtSignal(str)  # output_path
    processing_error = pyqtSignal(str)  # error_message
    stage_changed = pyqtSignal(str)  # stage_name

    def __init__(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        scale: int = 4,
        model_name: str = "realesrgan-x4plus",
        parent=None
    ):
        """
        Initialize the video processor.

        Args:
            input_path: Path to the input video file.
            output_path: Optional path for output video. Auto-generated if None.
            scale: Upscale factor (2, 3, or 4).
            model_name: Name of the Real-ESRGAN model.
            parent: Optional parent QObject.
        """
        super().__init__(parent)

        self.input_path = Path(input_path)
        self.output_path = Path(output_path) if output_path else None
        self.scale = scale
        self.model_name = model_name

        self._cancelled = False
        self._current_stage = ProcessingStage.IDLE
        self._start_time: float = 0
        self._stage_start_time: float = 0

        # Processing components (created during run)
        self._extractor: Optional[FrameExtractor] = None
        self._upscaler: Optional[Upscaler] = None
        self._assembler: Optional[VideoAssembler] = None

        # Temporary directories
        self._temp_base: Optional[Path] = None
        self._frames_input_dir: Optional[Path] = None
        self._frames_output_dir: Optional[Path] = None

    @property
    def is_processing(self) -> bool:
        """Check if processing is currently active."""
        return self._current_stage not in {
            ProcessingStage.IDLE,
            ProcessingStage.COMPLETE,
            ProcessingStage.ERROR,
            ProcessingStage.CANCELLED
        }

    def cancel(self) -> None:
        """
        Request cancellation of the current processing.

        Cancellation is handled gracefully - the current operation will
        complete or be terminated, and temporary files will be cleaned up.
        """
        self._cancelled = True

        # Cancel active components
        if self._extractor:
            self._extractor.cancel()
        if self._upscaler:
            self._upscaler.cancel()
        if self._assembler:
            self._assembler.cancel()

    def _set_stage(self, stage: ProcessingStage) -> None:
        """Update the current processing stage and emit signal."""
        self._current_stage = stage
        self._stage_start_time = time.time()
        self.stage_changed.emit(stage.name)

    def _on_progress(self, current: int, total: int, message: str) -> None:
        """
        Handle progress updates from processing components.

        Calculates ETA and emits progress signal to GUI.
        """
        stage_name = self._current_stage.name.capitalize()

        # Calculate elapsed and estimated time
        elapsed = time.time() - self._stage_start_time
        if current > 0:
            rate = elapsed / current
            remaining = rate * (total - current)
        else:
            remaining = -1

        self.progress_updated.emit(current, total, stage_name, message)

    def _setup_temp_directories(self) -> None:
        """Create temporary directories for frame processing."""
        # Create unique temp directory for this job
        timestamp = int(time.time() * 1000)
        self._temp_base = get_temp_directory() / f"job_{timestamp}"
        self._temp_base.mkdir(parents=True, exist_ok=True)

        self._frames_input_dir = self._temp_base / "input_frames"
        self._frames_output_dir = self._temp_base / "output_frames"

        self._frames_input_dir.mkdir(exist_ok=True)
        self._frames_output_dir.mkdir(exist_ok=True)

    def _cleanup_temp_directories(self) -> None:
        """Remove temporary directories and files."""
        if self._temp_base and self._temp_base.exists():
            try:
                shutil.rmtree(self._temp_base)
            except Exception:
                # Best effort cleanup - don't fail on cleanup errors
                pass

    def run(self) -> None:
        """
        Execute the video processing pipeline.

        This method runs on a background thread. It coordinates:
        1. Input validation
        2. Frame extraction
        3. AI upscaling
        4. Video reassembly
        5. Cleanup

        Progress and completion are communicated via Qt signals.
        """
        self._cancelled = False
        self._start_time = time.time()

        try:
            # Stage 1: Validation
            self._set_stage(ProcessingStage.VALIDATING)
            self.progress_updated.emit(0, 100, "Validating", "Checking dependencies...")

            # Validate dependencies
            errors = validate_all_dependencies()
            if errors:
                raise Exception("\n\n".join(errors))

            # Validate input video
            validate_input_video(self.input_path)

            # Get video info
            video_info = get_video_info(self.input_path)

            # Generate output path if not specified
            if self.output_path is None:
                self.output_path = generate_output_path(
                    self.input_path,
                    f"_{self.scale}x_upscaled"
                )

            self.progress_updated.emit(100, 100, "Validating", "Validation complete")

            if self._cancelled:
                raise Exception("Processing cancelled")

            # Setup temp directories
            self._setup_temp_directories()

            # Stage 2: Frame Extraction
            self._set_stage(ProcessingStage.EXTRACTING)

            self._extractor = FrameExtractor(
                self.input_path,
                self._frames_input_dir,
                self._on_progress
            )

            extracted_count = self._extractor.extract()

            if self._cancelled:
                raise Exception("Processing cancelled")

            # Stage 3: AI Upscaling
            self._set_stage(ProcessingStage.UPSCALING)

            self._upscaler = Upscaler(
                self._frames_input_dir,
                self._frames_output_dir,
                self.scale,
                self.model_name,
                self._on_progress
            )

            upscaled_count = self._upscaler.upscale()

            if self._cancelled:
                raise Exception("Processing cancelled")

            # Stage 4: Video Assembly
            self._set_stage(ProcessingStage.ASSEMBLING)

            self._assembler = VideoAssembler(
                self._frames_output_dir,
                self.input_path,
                self.output_path,
                video_info,
                self._on_progress
            )

            output_path = self._assembler.assemble()

            if self._cancelled:
                raise Exception("Processing cancelled")

            # Stage 5: Cleanup
            self._set_stage(ProcessingStage.CLEANUP)
            self.progress_updated.emit(0, 100, "Cleanup", "Removing temporary files...")

            self._cleanup_temp_directories()

            self.progress_updated.emit(100, 100, "Cleanup", "Cleanup complete")

            # Complete!
            self._set_stage(ProcessingStage.COMPLETE)
            self.processing_complete.emit(str(output_path))

        except FrameExtractionError as e:
            self._set_stage(ProcessingStage.ERROR)
            self._cleanup_temp_directories()
            self.processing_error.emit(f"Frame extraction failed:\n{e}")

        except UpscalingError as e:
            self._set_stage(ProcessingStage.ERROR)
            self._cleanup_temp_directories()
            self.processing_error.emit(f"AI upscaling failed:\n{e}")

        except VideoAssemblyError as e:
            self._set_stage(ProcessingStage.ERROR)
            self._cleanup_temp_directories()
            self.processing_error.emit(f"Video assembly failed:\n{e}")

        except Exception as e:
            if "cancelled" in str(e).lower():
                self._set_stage(ProcessingStage.CANCELLED)
                self._cleanup_temp_directories()
                self.processing_error.emit("Processing was cancelled")
            else:
                self._set_stage(ProcessingStage.ERROR)
                self._cleanup_temp_directories()
                self.processing_error.emit(f"Processing failed:\n{e}")


def process_video(
    input_path: Path,
    output_path: Optional[Path] = None,
    scale: int = 4,
    model_name: str = "realesrgan-x4plus"
) -> VideoProcessor:
    """
    Create and start a video processor.

    This is a convenience function that creates a VideoProcessor thread
    and starts it. Connect to the processor's signals to receive updates.

    Args:
        input_path: Path to the input video file.
        output_path: Optional path for output video.
        scale: Upscale factor (2, 3, or 4).
        model_name: Name of the Real-ESRGAN model.

    Returns:
        VideoProcessor thread instance (already started).
    """
    processor = VideoProcessor(input_path, output_path, scale, model_name)
    processor.start()
    return processor
