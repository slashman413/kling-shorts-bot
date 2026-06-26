"""
Video looping utility using FFmpeg.
Takes a Kling-generated video and creates a seamless loop.
"""

import os
import subprocess
import tempfile
from pathlib import Path


class VideoLooper:
    """Create looping Shorts videos from generated clips."""

    def __init__(self, target_duration: int = 12):
        """
        Args:
            target_duration: Target loop duration in seconds (10-15 recommended)
        """
        self.target_duration = target_duration

    def create_loop(self, input_path: str, output_path: str = None) -> str:
        """
        Create a seamless loop by concatenating multiple copies of the video.

        Args:
            input_path: Path to the input video file
            output_path: Path for the output looped video (auto-generated if None)

        Returns:
            Path to the looped video file
        """
        # Get input video duration
        duration = self._get_duration(input_path)
        if not duration or duration <= 0:
            raise ValueError(f"Could not determine duration of {input_path}")

        # Calculate how many copies needed
        copies = max(2, int(self.target_duration / duration) + 1)

        # Create file list for FFmpeg concat
        filelist = []
        for i in range(copies):
            filelist.append(f"file '{input_path}'")

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("\n".join(filelist))
            filelist_path = f.name

        if not output_path:
            output_path = str(
                Path(input_path).parent / f"loop_{Path(input_path).name}"
            )

        try:
            cmd = [
                "ffmpeg",
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", filelist_path,
                "-c", "copy",
                "-t", str(self.target_duration),
                output_path,
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=60
            )
            if result.returncode != 0:
                raise RuntimeError(f"FFmpeg error: {result.stderr}")

            print(
                f"[Looper] Created {self._get_duration(output_path):.1f}s loop: {output_path}"
            )
            return output_path

        finally:
            os.unlink(filelist_path)

    def _get_duration(self, video_path: str) -> float:
        """Get video duration in seconds using ffprobe."""
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            video_path,
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            import json
            data = json.loads(result.stdout)
            return float(data.get("format", {}).get("duration", 0))
        except (json.JSONDecodeError, KeyError, ValueError):
            return 0
