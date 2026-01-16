"""
Real-ESRGAN upscaler module.

Wraps the Real-ESRGAN-ncnn-vulkan executable to perform AI-based image
upscaling on extracted video frames. Supports 2x, 3x, and 4x scale factors.
"""

import subprocess
import os
import time
import threading
from pathlib import Path
from typing import Callable, Optional

from core.utils import get_realesrgan_path, get_models_directory, validate_models_exist


class UpscalingError(Exception):
    """Raised when upscaling fails."""
    pass


class Upscaler:
    """
    Handles AI-based frame upscaling using Real-ESRGAN-ncnn-vulkan.

    The upscaler processes frames in batch mode for efficiency, monitoring
    output directory for progress tracking since Real-ESRGAN doesn't provide
    per-frame progress output.
    """

    # Valid scale factors for Real-ESRGAN
    VALID_SCALES = {2, 3, 4}

    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
        scale: int = 2,
        model_name: str = "realesr-animevideov3",
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ):
        """
        Initialize the upscaler.

        Args:
            input_dir: Directory containing input frames.
            output_dir: Directory to save upscaled frames.
            scale: Upscale factor (2, 3, or 4).
            model_name: Name of the Real-ESRGAN model to use.
                       realesr-animevideov3 supports 2x, 3x, 4x.
            progress_callback: Optional callback function(current, total, status).

        Raises:
            ValueError: If scale factor is invalid.
        """
        if scale not in self.VALID_SCALES:
            raise ValueError(
                f"Invalid scale factor: {scale}. "
                f"Valid options are: {sorted(self.VALID_SCALES)}"
            )

        self.input_dir = input_dir
        self.output_dir = output_dir
        self.scale = scale
        self.model_name = model_name
        self.progress_callback = progress_callback
        self._cancelled = False
        self._process: Optional[subprocess.Popen] = None
        self._stderr_output = ""

    def cancel(self) -> None:
        """Cancel the upscaling process."""
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

    def upscale(self) -> int:
        """
        Upscale all frames in the input directory.

        Returns:
            Number of frames upscaled.

        Raises:
            UpscalingError: If upscaling fails.
        """
        self._cancelled = False
        self._stderr_output = ""

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Validate model files exist
        try:
            validate_models_exist(self.model_name, self.scale)
        except Exception as e:
            raise UpscalingError(str(e))

        # Count input frames
        input_frames = list(self.input_dir.glob("frame_*.png"))
        total_frames = len(input_frames)

        if total_frames == 0:
            raise UpscalingError(
                f"No frames found in input directory: {self.input_dir}"
            )

        realesrgan_path = get_realesrgan_path()
        models_dir = get_models_directory()

        # Build Real-ESRGAN command
        # -i: input directory
        # -o: output directory
        # -n: model name
        # -s: scale factor
        # -f: output format (png for quality)
        # -v: verbose output
        cmd = [
            str(realesrgan_path),
            "-i", str(self.input_dir),
            "-o", str(self.output_dir),
            "-n", self.model_name,
            "-s", str(self.scale),
            "-f", "png",
            "-m", str(models_dir),
            "-v"  # Verbose mode for better debugging
        ]

        if self.progress_callback:
            self.progress_callback(0, total_frames, "Starting AI upscaling...")

        try:
            # Start Real-ESRGAN process
            # Use DEVNULL for stdout to prevent buffer issues
            # Capture stderr for error messages
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
                    raise UpscalingError("Upscaling cancelled by user")

                # Count completed frames
                current_count = self._count_output_frames()

                if current_count != last_count:
                    last_count = current_count

                    if self.progress_callback:
                        self.progress_callback(
                            current_count,
                            total_frames,
                            f"Upscaling frame {current_count}/{total_frames}"
                        )

                # Sleep briefly to avoid busy-waiting
                time.sleep(0.25)

            # Wait for stderr thread to finish
            stderr_thread.join(timeout=2.0)

            # Process completed - check return code
            if self._process.returncode != 0:
                stderr = self._stderr_output

                # Check for common error patterns
                if "vkCreateInstance" in stderr or "vulkan" in stderr.lower():
                    raise UpscalingError(
                        "Vulkan GPU initialization failed.\n\n"
                        "Please ensure:\n"
                        "1. Your GPU supports Vulkan\n"
                        "2. GPU drivers are up to date\n"
                        "3. No other GPU-intensive applications are running"
                    )
                elif "out of memory" in stderr.lower() or "memory" in stderr.lower():
                    raise UpscalingError(
                        "GPU ran out of memory.\n\n"
                        "Try closing other applications or using a lower resolution video."
                    )
                else:
                    raise UpscalingError(
                        f"Real-ESRGAN failed (code {self._process.returncode}):\n{stderr}"
                    )

            # Final count of upscaled frames
            upscaled_count = self._count_output_frames()

            if upscaled_count == 0:
                stderr = self._stderr_output
                raise UpscalingError(
                    f"No frames were upscaled. Check GPU compatibility and driver versions.\n"
                    f"Details: {stderr}"
                )

            if self.progress_callback:
                self.progress_callback(
                    upscaled_count,
                    total_frames,
                    f"Upscaled {upscaled_count} frames"
                )

            return upscaled_count

        except subprocess.SubprocessError as e:
            raise UpscalingError(f"Failed to run Real-ESRGAN: {e}")
        finally:
            self._process = None


def upscale_frames(
    input_dir: Path,
    output_dir: Path,
    scale: int = 2,
    model_name: str = "realesr-animevideov3",
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> int:
    """
    Convenience function to upscale frames.

    Args:
        input_dir: Directory containing input frames.
        output_dir: Directory to save upscaled frames.
        scale: Upscale factor (2, 3, or 4).
        model_name: Name of the Real-ESRGAN model to use.
        progress_callback: Optional callback function(current, total, status).

    Returns:
        Number of frames upscaled.
    """
    upscaler = Upscaler(
        input_dir, output_dir, scale, model_name, progress_callback
    )
    return upscaler.upscale()
