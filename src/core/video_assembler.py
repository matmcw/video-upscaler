"""
Video assembly module using FFmpeg.

Reassembles upscaled frames into a video file, preserving the original
audio track from the source video. Uses H.264 encoding with high quality
settings by default.
"""

import subprocess
import re
from pathlib import Path
from typing import Callable, Optional

from core.utils import get_ffmpeg_path, get_video_info, VideoInfo


class VideoAssemblyError(Exception):
    """Raised when video assembly fails."""
    pass


class VideoAssembler:
    """
    Handles reassembly of upscaled frames into a video file.

    Combines upscaled frames with the original audio track to create
    the final output video. Uses FFmpeg with high-quality encoding settings.
    """

    def __init__(
        self,
        frames_dir: Path,
        original_video: Path,
        output_path: Path,
        video_info: Optional[VideoInfo] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ):
        """
        Initialize the video assembler.

        Args:
            frames_dir: Directory containing upscaled frames.
            original_video: Path to original video (for audio extraction).
            output_path: Path for the output video file.
            video_info: Optional VideoInfo for the original video.
            progress_callback: Optional callback function(current, total, status).
        """
        self.frames_dir = frames_dir
        self.original_video = original_video
        self.output_path = output_path
        self.video_info = video_info
        self.progress_callback = progress_callback
        self._cancelled = False
        self._process: Optional[subprocess.Popen] = None

    def cancel(self) -> None:
        """Cancel the assembly process."""
        self._cancelled = True
        if self._process is not None:
            try:
                self._process.terminate()
            except Exception:
                pass

    def assemble(self) -> Path:
        """
        Assemble frames into a video with the original audio.

        Returns:
            Path to the output video file.

        Raises:
            VideoAssemblyError: If assembly fails.
        """
        self._cancelled = False

        # Get video info if not provided
        if self.video_info is None:
            try:
                self.video_info = get_video_info(self.original_video)
            except Exception as e:
                raise VideoAssemblyError(f"Failed to get video info: {e}")

        # Count frames to assemble
        frames = sorted(self.frames_dir.glob("frame_*.png"))
        total_frames = len(frames)

        if total_frames == 0:
            raise VideoAssemblyError(
                f"No frames found in directory: {self.frames_dir}"
            )

        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        ffmpeg_path = get_ffmpeg_path()

        # Determine output format and codec based on file extension
        output_ext = self.output_path.suffix.lower()
        codec_args = self._get_codec_args(output_ext)

        # Build FFmpeg command
        frame_pattern = str(self.frames_dir / "frame_%08d.png")

        cmd = [
            str(ffmpeg_path),
            # Input: Image sequence
            "-framerate", str(self.video_info.fps),
            "-i", frame_pattern,
        ]

        # Add audio from original video if it has audio
        if self.video_info.has_audio:
            cmd.extend([
                "-i", str(self.original_video),
                "-map", "0:v",      # Video from first input (frames)
                "-map", "1:a?",     # Audio from second input (original) if present
            ])

        # Add codec settings
        cmd.extend(codec_args)

        # Add common output settings
        cmd.extend([
            "-pix_fmt", "yuv420p",   # Compatible pixel format
            "-movflags", "+faststart",  # Enable fast start for web playback
            "-progress", "pipe:1",    # Output progress to stdout
            "-y",                     # Overwrite output
            str(self.output_path)
        ])

        if self.progress_callback:
            self.progress_callback(0, total_frames, "Assembling video...")

        try:
            # Start FFmpeg process
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            current_frame = 0

            # Parse FFmpeg progress output
            while True:
                if self._cancelled:
                    self._process.terminate()
                    raise VideoAssemblyError("Assembly cancelled by user")

                line = self._process.stdout.readline()
                if not line:
                    break

                # FFmpeg progress output contains "frame=N" lines
                if line.startswith("frame="):
                    try:
                        frame_num = int(line.split("=")[1].strip())
                        current_frame = frame_num

                        if self.progress_callback:
                            self.progress_callback(
                                current_frame,
                                total_frames,
                                f"Encoding frame {current_frame}/{total_frames}"
                            )
                    except (ValueError, IndexError):
                        pass

            # Wait for process to complete
            self._process.wait()

            if self._process.returncode != 0:
                stderr = self._process.stderr.read()
                raise VideoAssemblyError(
                    f"FFmpeg encoding failed (code {self._process.returncode}):\n{stderr}"
                )

            # Verify output file was created
            if not self.output_path.exists():
                raise VideoAssemblyError(
                    "Output video was not created. FFmpeg may have encountered an error."
                )

            # Check output file has reasonable size
            output_size = self.output_path.stat().st_size
            if output_size < 1000:  # Less than 1KB is suspicious
                raise VideoAssemblyError(
                    "Output video appears to be corrupted (file too small)."
                )

            if self.progress_callback:
                self.progress_callback(
                    total_frames,
                    total_frames,
                    "Video assembly complete"
                )

            return self.output_path

        except subprocess.SubprocessError as e:
            raise VideoAssemblyError(f"Failed to run FFmpeg: {e}")
        finally:
            self._process = None

    def _get_codec_args(self, output_ext: str) -> list[str]:
        """
        Get FFmpeg codec arguments based on output format.

        Args:
            output_ext: Output file extension (e.g., '.mp4').

        Returns:
            List of FFmpeg arguments for codec settings.
        """
        # Default to high-quality H.264 encoding
        # CRF 18 is visually lossless for most content
        # preset: slower gives better quality/size ratio

        if output_ext in {'.mp4', '.m4v', '.mov'}:
            return [
                "-c:v", "libx264",
                "-crf", "18",
                "-preset", "slow",
                "-c:a", "aac",
                "-b:a", "192k"
            ]
        elif output_ext == '.mkv':
            return [
                "-c:v", "libx264",
                "-crf", "18",
                "-preset", "slow",
                "-c:a", "copy"  # Copy audio codec in MKV
            ]
        elif output_ext == '.webm':
            return [
                "-c:v", "libvpx-vp9",
                "-crf", "20",
                "-b:v", "0",
                "-c:a", "libopus",
                "-b:a", "192k"
            ]
        elif output_ext == '.avi':
            return [
                "-c:v", "libx264",
                "-crf", "18",
                "-preset", "slow",
                "-c:a", "mp3",
                "-b:a", "192k"
            ]
        else:
            # Default fallback
            return [
                "-c:v", "libx264",
                "-crf", "18",
                "-preset", "slow",
                "-c:a", "aac",
                "-b:a", "192k"
            ]


def assemble_video(
    frames_dir: Path,
    original_video: Path,
    output_path: Path,
    video_info: Optional[VideoInfo] = None,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> Path:
    """
    Convenience function to assemble a video from frames.

    Args:
        frames_dir: Directory containing upscaled frames.
        original_video: Path to original video (for audio extraction).
        output_path: Path for the output video file.
        video_info: Optional VideoInfo for the original video.
        progress_callback: Optional callback function(current, total, status).

    Returns:
        Path to the output video file.
    """
    assembler = VideoAssembler(
        frames_dir, original_video, output_path, video_info, progress_callback
    )
    return assembler.assemble()
