"""
Frame extraction module using FFmpeg.

Extracts individual frames from video files as PNG images for processing
by the AI upscaler. Uses high-quality settings to preserve detail.
"""

import subprocess
import threading
import time
from pathlib import Path
from typing import Callable, Optional

from core.utils import get_ffmpeg_path, get_video_info, VideoInfo


class FrameExtractionError(Exception):
    """Raised when frame extraction fails."""
    pass


class FrameExtractor:
    """
    Handles extraction of video frames using FFmpeg.

    Extracts frames as PNG images to preserve quality during the upscaling
    process. Provides progress callbacks for UI updates.
    """

    def __init__(
        self,
        input_path: Path,
        output_dir: Path,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ):
        """
        Initialize the frame extractor.

        Args:
            input_path: Path to the input video file.
            output_dir: Directory to save extracted frames.
            progress_callback: Optional callback function(current, total, status).
        """
        self.input_path = input_path
        self.output_dir = output_dir
        self.progress_callback = progress_callback
        self._cancelled = False
        self._process: Optional[subprocess.Popen] = None
        self._stderr_output = ""

    def cancel(self) -> None:
        """Cancel the extraction process."""
        self._cancelled = True
        if self._process is not None:
            try:
                self._process.terminate()
            except Exception:
                pass

    def _count_output_frames(self) -> int:
        """Count the number of frames in the output directory."""
        if not self.output_dir.exists():
            return 0
        return len(list(self.output_dir.glob("frame_*.png")))

    def _read_stderr(self, pipe):
        """Read stderr in a separate thread to prevent blocking."""
        try:
            for line in pipe:
                self._stderr_output += line
        except Exception:
            pass

    def extract(self) -> int:
        """
        Extract all frames from the video.

        Returns:
            Number of frames extracted.

        Raises:
            FrameExtractionError: If extraction fails.
        """
        self._cancelled = False
        self._stderr_output = ""

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Get video info for progress tracking
        try:
            video_info = get_video_info(self.input_path)
            total_frames = video_info.frame_count
        except Exception as e:
            raise FrameExtractionError(f"Failed to get video info: {e}")

        if total_frames == 0:
            # Estimate based on a typical video if frame count unknown
            total_frames = 1000  # Will be updated as frames are extracted

        ffmpeg_path = get_ffmpeg_path()

        # Build FFmpeg command for frame extraction
        # Using PNG format for lossless quality
        # %08d ensures proper sorting (up to 99,999,999 frames)
        output_pattern = str(self.output_dir / "frame_%08d.png")

        cmd = [
            str(ffmpeg_path),
            "-i", str(self.input_path),
            "-qscale:v", "2",           # High quality
            output_pattern,
            "-y"                         # Overwrite output files
        ]

        if self.progress_callback:
            self.progress_callback(0, total_frames, "Starting frame extraction...")

        try:
            # Start FFmpeg process
            # Use DEVNULL for stdout, capture stderr for errors
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            # Read stderr in a separate thread to prevent blocking
            stderr_thread = threading.Thread(
                target=self._read_stderr,
                args=(self._process.stderr,),
                daemon=True
            )
            stderr_thread.start()

            # Monitor progress by counting output files
            last_count = 0

            while self._process.poll() is None:
                if self._cancelled:
                    self._process.terminate()
                    raise FrameExtractionError("Extraction cancelled by user")

                # Count completed frames
                current_count = self._count_output_frames()

                if current_count != last_count:
                    last_count = current_count

                    if self.progress_callback:
                        self.progress_callback(
                            current_count,
                            total_frames,
                            f"Extracting frame {current_count}/{total_frames}"
                        )

                # Sleep briefly to avoid busy-waiting
                time.sleep(0.1)

            # Wait for stderr thread to finish
            stderr_thread.join(timeout=2.0)

            # Check return code
            if self._process.returncode != 0:
                raise FrameExtractionError(
                    f"FFmpeg extraction failed (code {self._process.returncode}):\n{self._stderr_output}"
                )

            # Count actual extracted frames
            extracted_frames = self._count_output_frames()

            if extracted_frames == 0:
                raise FrameExtractionError(
                    f"No frames were extracted. The video may be corrupted or empty.\n"
                    f"Details: {self._stderr_output}"
                )

            if self.progress_callback:
                self.progress_callback(
                    extracted_frames,
                    extracted_frames,
                    f"Extracted {extracted_frames} frames"
                )

            return extracted_frames

        except subprocess.SubprocessError as e:
            raise FrameExtractionError(f"Failed to run FFmpeg: {e}")
        finally:
            self._process = None


def extract_frames(
    input_path: Path,
    output_dir: Path,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> int:
    """
    Convenience function to extract frames from a video.

    Args:
        input_path: Path to the input video file.
        output_dir: Directory to save extracted frames.
        progress_callback: Optional callback function(current, total, status).

    Returns:
        Number of frames extracted.
    """
    extractor = FrameExtractor(input_path, output_dir, progress_callback)
    return extractor.extract()
