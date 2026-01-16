"""
Utility functions for Video Upscaler.

Provides path resolution, binary detection, validation, and video information extraction.
All path operations use pathlib.Path for cross-platform compatibility (though this app
targets Windows specifically).
"""

import subprocess
import sys
import json
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class VideoInfo:
    """Container for video metadata extracted via FFprobe."""
    width: int
    height: int
    fps: float
    frame_count: int
    duration: float  # in seconds
    has_audio: bool
    codec: str


class BinaryNotFoundError(Exception):
    """Raised when a required binary (FFmpeg, Real-ESRGAN) is not found."""
    pass


class VideoValidationError(Exception):
    """Raised when input video validation fails."""
    pass


class VulkanNotSupportedError(Exception):
    """Raised when Vulkan GPU support is not available."""
    pass


def get_app_directory() -> Path:
    """
    Get the application's root directory.

    When running as a PyInstaller bundle, this returns the directory containing
    the executable. When running as a script, returns the src/ parent directory.
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return Path(sys.executable).parent
    else:
        # Running as script - go up from src/core/ to project root
        return Path(__file__).parent.parent.parent


def get_temp_directory() -> Path:
    """
    Get the temporary directory for frame processing.

    Creates a 'temp' folder next to the executable/script for easy access
    and debugging. The folder is created if it doesn't exist.
    """
    temp_dir = get_app_directory() / "temp"
    temp_dir.mkdir(exist_ok=True)
    return temp_dir


def get_models_directory() -> Path:
    """
    Get the models directory where Real-ESRGAN model files are stored.

    Returns the 'models' folder next to the executable/script.
    """
    return get_app_directory() / "models"


def get_ffmpeg_path() -> Path:
    """
    Get the path to the FFmpeg executable.

    Looks for ffmpeg.exe in the application directory.

    Raises:
        BinaryNotFoundError: If ffmpeg.exe is not found.
    """
    ffmpeg_path = get_app_directory() / "ffmpeg.exe"
    if not ffmpeg_path.exists():
        raise BinaryNotFoundError(
            f"FFmpeg not found at: {ffmpeg_path}\n\n"
            "Please download FFmpeg from https://ffmpeg.org/download.html\n"
            "and place ffmpeg.exe in the application folder."
        )
    return ffmpeg_path


def get_ffprobe_path() -> Path:
    """
    Get the path to the FFprobe executable.

    Looks for ffprobe.exe in the application directory.

    Raises:
        BinaryNotFoundError: If ffprobe.exe is not found.
    """
    ffprobe_path = get_app_directory() / "ffprobe.exe"
    if not ffprobe_path.exists():
        raise BinaryNotFoundError(
            f"FFprobe not found at: {ffprobe_path}\n\n"
            "Please download FFmpeg from https://ffmpeg.org/download.html\n"
            "and place ffprobe.exe in the application folder."
        )
    return ffprobe_path


def get_realesrgan_path() -> Path:
    """
    Get the path to the Real-ESRGAN executable.

    Looks for realesrgan-ncnn-vulkan.exe in the application directory.

    Raises:
        BinaryNotFoundError: If the executable is not found.
    """
    realesrgan_path = get_app_directory() / "realesrgan-ncnn-vulkan.exe"
    if not realesrgan_path.exists():
        raise BinaryNotFoundError(
            f"Real-ESRGAN not found at: {realesrgan_path}\n\n"
            "Please download Real-ESRGAN-ncnn-vulkan from:\n"
            "https://github.com/xinntao/Real-ESRGAN/releases\n"
            "and place realesrgan-ncnn-vulkan.exe in the application folder."
        )
    return realesrgan_path


def validate_models_exist(model_name: str = "realesrgan-x4plus") -> Tuple[Path, Path]:
    """
    Validate that the required model files exist.

    Args:
        model_name: Name of the model (without extension).

    Returns:
        Tuple of (bin_path, param_path) for the model files.

    Raises:
        BinaryNotFoundError: If model files are not found.
    """
    models_dir = get_models_directory()
    bin_path = models_dir / f"{model_name}.bin"
    param_path = models_dir / f"{model_name}.param"

    missing = []
    if not bin_path.exists():
        missing.append(str(bin_path))
    if not param_path.exists():
        missing.append(str(param_path))

    if missing:
        raise BinaryNotFoundError(
            f"Model files not found:\n"
            f"  {chr(10).join(missing)}\n\n"
            f"Please download the Real-ESRGAN models from:\n"
            f"https://github.com/xinntao/Real-ESRGAN/releases\n"
            f"and place the .bin and .param files in the 'models' folder."
        )

    return bin_path, param_path


def validate_input_video(video_path: Path) -> None:
    """
    Validate that the input video file exists and is a supported format.

    Args:
        video_path: Path to the input video file.

    Raises:
        VideoValidationError: If the file doesn't exist or has unsupported format.
    """
    if not video_path.exists():
        raise VideoValidationError(f"Input video not found: {video_path}")

    # Supported video extensions
    supported_extensions = {
        '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv',
        '.webm', '.m4v', '.mpeg', '.mpg', '.3gp'
    }

    ext = video_path.suffix.lower()
    if ext not in supported_extensions:
        raise VideoValidationError(
            f"Unsupported video format: {ext}\n"
            f"Supported formats: {', '.join(sorted(supported_extensions))}"
        )


def get_video_info(video_path: Path) -> VideoInfo:
    """
    Extract video metadata using FFprobe.

    Args:
        video_path: Path to the video file.

    Returns:
        VideoInfo dataclass with video metadata.

    Raises:
        VideoValidationError: If video info cannot be extracted.
    """
    ffprobe_path = get_ffprobe_path()

    # Build FFprobe command to get JSON output with stream info
    cmd = [
        str(ffprobe_path),
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(video_path)
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW  # Hide console window on Windows
        )

        if result.returncode != 0:
            raise VideoValidationError(
                f"FFprobe failed to read video:\n{result.stderr}"
            )

        data = json.loads(result.stdout)

    except subprocess.TimeoutExpired:
        raise VideoValidationError("FFprobe timed out while reading video info")
    except json.JSONDecodeError as e:
        raise VideoValidationError(f"Failed to parse FFprobe output: {e}")

    # Find video stream
    video_stream = None
    has_audio = False

    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video" and video_stream is None:
            video_stream = stream
        elif stream.get("codec_type") == "audio":
            has_audio = True

    if video_stream is None:
        raise VideoValidationError("No video stream found in file")

    # Extract dimensions
    width = int(video_stream.get("width", 0))
    height = int(video_stream.get("height", 0))

    if width == 0 or height == 0:
        raise VideoValidationError("Could not determine video dimensions")

    # Extract frame rate (can be fraction like "30000/1001")
    fps_str = video_stream.get("r_frame_rate", "30/1")
    try:
        if "/" in fps_str:
            num, den = fps_str.split("/")
            fps = float(num) / float(den)
        else:
            fps = float(fps_str)
    except (ValueError, ZeroDivisionError):
        fps = 30.0  # Default fallback

    # Extract frame count - try multiple methods
    frame_count = 0

    # Method 1: Direct nb_frames field
    if "nb_frames" in video_stream:
        try:
            frame_count = int(video_stream["nb_frames"])
        except (ValueError, TypeError):
            pass

    # Method 2: Calculate from duration and fps
    if frame_count == 0:
        duration_str = video_stream.get("duration") or data.get("format", {}).get("duration")
        if duration_str:
            try:
                duration = float(duration_str)
                frame_count = int(duration * fps)
            except (ValueError, TypeError):
                pass

    # Method 3: Use format duration
    if frame_count == 0:
        format_info = data.get("format", {})
        if "duration" in format_info:
            try:
                duration = float(format_info["duration"])
                frame_count = int(duration * fps)
            except (ValueError, TypeError):
                frame_count = 0

    # Get duration
    duration = 0.0
    duration_str = video_stream.get("duration") or data.get("format", {}).get("duration", "0")
    try:
        duration = float(duration_str)
    except (ValueError, TypeError):
        if frame_count > 0 and fps > 0:
            duration = frame_count / fps

    # Get codec
    codec = video_stream.get("codec_name", "unknown")

    return VideoInfo(
        width=width,
        height=height,
        fps=fps,
        frame_count=frame_count,
        duration=duration,
        has_audio=has_audio,
        codec=codec
    )


def check_vulkan_support() -> bool:
    """
    Check if Vulkan GPU support is available by running Real-ESRGAN with test parameters.

    Returns:
        True if Vulkan is supported, False otherwise.
    """
    try:
        realesrgan_path = get_realesrgan_path()
    except BinaryNotFoundError:
        return False

    # Run with -h flag to check if it starts properly
    # Real-ESRGAN will fail with a specific error if Vulkan isn't available
    try:
        result = subprocess.run(
            [str(realesrgan_path), "-h"],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        # If help runs successfully, Vulkan should be available
        return True
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        return False


def validate_all_dependencies() -> list[str]:
    """
    Validate all required dependencies are present.

    Returns:
        List of error messages for missing dependencies. Empty list if all present.
    """
    errors = []

    # Check FFmpeg
    try:
        get_ffmpeg_path()
    except BinaryNotFoundError as e:
        errors.append(str(e))

    # Check FFprobe
    try:
        get_ffprobe_path()
    except BinaryNotFoundError as e:
        errors.append(str(e))

    # Check Real-ESRGAN
    try:
        get_realesrgan_path()
    except BinaryNotFoundError as e:
        errors.append(str(e))

    # Check models
    try:
        validate_models_exist()
    except BinaryNotFoundError as e:
        errors.append(str(e))

    return errors


def generate_output_path(input_path: Path, suffix: str = "_upscaled") -> Path:
    """
    Generate a default output path based on the input path.

    Args:
        input_path: Path to the input video.
        suffix: Suffix to add before the extension.

    Returns:
        Path for the output video (e.g., video.mp4 -> video_upscaled.mp4)
    """
    return input_path.parent / f"{input_path.stem}{suffix}{input_path.suffix}"


def format_time(seconds: float) -> str:
    """
    Format seconds into a human-readable time string.

    Args:
        seconds: Number of seconds.

    Returns:
        Formatted string like "1:23" or "2:03:45"
    """
    if seconds < 0:
        return "--:--"

    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def format_file_size(size_bytes: int) -> str:
    """
    Format bytes into human-readable size.

    Args:
        size_bytes: Size in bytes.

    Returns:
        Formatted string like "1.5 GB" or "256 MB"
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"
