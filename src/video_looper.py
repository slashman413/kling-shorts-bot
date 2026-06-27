"""
Video looping utility using FFmpeg.
Takes a Kling-generated video, scales to 720x1280 (Shorts HD),
and creates a seamless loop by repeating N times.
"""

import subprocess
from pathlib import Path


class VideoLooper:
    """Create looping Shorts videos (720x1280) from generated clips."""

    def __init__(self, repeats: int = 4):
        """
        Args:
            repeats: How many times to repeat the clip (3-5 recommended)
                     Total duration = clip_duration × repeats
        """
        self.repeats = repeats

    def create_loop(self, input_path: str, output_path: str = None) -> str:
        """
        Create a seamless 720x1280 Shorts loop by repeating the video N times.

        Args:
            input_path: Path to the input video file
            output_path: Path for the output looped video (auto-generated if None)

        Returns:
            Path to the looped video file
        """
        # Get input video info
        duration = self._get_duration(input_path)
        if not duration or duration <= 0:
            raise ValueError(f"Could not determine duration of {input_path}")

        width, height = self._get_resolution(input_path)
        print(f"[Looper] Input: {width}x{height}, {duration:.1f}s, repeating {self.repeats}x")

        # Calculate total duration
        total_duration = duration * self.repeats

        if not output_path:
            output_path = str(
                Path(input_path).parent / f"loop_{Path(input_path).name}"
            )

        try:
            cmd = [
                "ffmpeg",
                "-y",
                "-stream_loop", str(self.repeats - 1),  # repeat N-1 extra times
                "-i", input_path,
                # -vf (not -filter_complex) so ffmpeg still auto-maps the source audio when present
                "-vf",
                "scale=720:1280:force_original_aspect_ratio=decrease,"
                "pad=720:1280:(ow-iw)/2:(oh-ih)/2:color=black",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "23",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                "-b:a", "128k",
                "-t", str(total_duration),
                "-movflags", "+faststart",
                "-metadata", "title=YouTube Shorts",
                "-metadata", "comment=Shorts",
                output_path,
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120
            )
            if result.returncode != 0:
                # Show stderr for debugging
                error_lines = result.stderr.strip().split("\n")[-10:]
                raise RuntimeError(f"FFmpeg error: {'; '.join(error_lines)}")

            out_duration = self._get_duration(output_path)
            out_w, out_h = self._get_resolution(output_path)
            print(
                f"[Looper] ✅ Output: {out_w}x{out_h}, "
                f"{out_duration:.1f}s ({self.repeats}x loop)"
            )
            return output_path

        except subprocess.TimeoutExpired:
            raise RuntimeError("FFmpeg timed out after 120s")

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

    def _get_resolution(self, video_path: str) -> tuple:
        """Get video resolution (width, height) using ffprobe."""
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_streams",
            video_path,
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            import json
            data = json.loads(result.stdout)
            for stream in data.get("streams", []):
                if stream.get("codec_type") == "video":
                    return (stream.get("width", 0), stream.get("height", 0))
        except (json.JSONDecodeError, KeyError, ValueError):
            pass
        return (0, 0)
