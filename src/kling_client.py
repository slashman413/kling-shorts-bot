"""
Kling AI API client for text-to-video generation.
API docs: https://docs.klingai.com/api-reference/videos/create-video-text-to-video
"""

import os
import time
import hashlib
import hmac
import json
import uuid
from datetime import datetime
from typing import Optional

import requests


class KlingClient:
    """Client for Kling AI video generation API."""

    def __init__(self):
        self.access_key = os.environ.get("KLING_ACCESS_KEY", "")
        self.secret_key = os.environ.get("KLING_SECRET_KEY", "")
        self.api_base = "https://api.klingai.com"
        if not self.access_key or not self.secret_key:
            raise ValueError(
                "KLING_ACCESS_KEY and KLING_SECRET_KEY must be set in environment variables. "
                "Get them at https://klingai.com → API Platform"
            )

    def _generate_signature(self, method: str, path: str, body: str = "") -> dict:
        """Generate Kling API signature using AK/SK."""
        timestamp = str(int(time.time()))
        nonce = str(uuid.uuid4())

        # Build signature string
        sign_str = f"{method}\n{path}\n{timestamp}\n{nonce}\n{body}"

        # HMAC-SHA256 signature
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            sign_str.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        return {
            "Content-Type": "application/json",
            "AccessKey": self.access_key,
            "Signature": signature,
            "Timestamp": timestamp,
            "Nonce": nonce,
        }

    def text_to_video(
        self,
        prompt: str,
        duration: int = 5,
        cfg_scale: float = 0.5,
        negative_prompt: str = "",
        model: str = "kling-v3",
    ) -> dict:
        """
        Generate a video from text prompt using Kling AI.

        Args:
            prompt: The video description (in English, detailed)
            duration: Video duration in seconds (5 or 10)
            cfg_scale: How strictly to follow the prompt (0-1)
            negative_prompt: What to avoid in the video
            model: Model version

        Returns:
            Response dict with task_id for status polling
        """
        path = "/v1/videos/text2video"
        url = f"{self.api_base}{path}"

        body = json.dumps({
            "model_name": model,
            "prompt": prompt,
            "duration": duration,
            "cfg_scale": cfg_scale,
            "negative_prompt": negative_prompt or None,
        }, ensure_ascii=False)

        headers = self._generate_signature("POST", path, body)

        resp = requests.post(url, headers=headers, data=body, timeout=60)
        resp.raise_for_status()
        return resp.json()

    def get_task_status(self, task_id: str) -> dict:
        """Poll for video generation task status."""
        path = f"/v1/videos/text2video/{task_id}"
        url = f"{self.api_base}{path}"

        headers = self._generate_signature("GET", path)

        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def wait_for_video(self, task_id: str, poll_interval: int = 10, timeout: int = 600) -> Optional[str]:
        """
        Poll until video is ready, return video URL.

        Args:
            task_id: Task ID from text_to_video()
            poll_interval: Seconds between polls
            timeout: Max seconds to wait

        Returns:
            Video URL string, or None if failed/timed out
        """
        start = time.time()
        while time.time() - start < timeout:
            result = self.get_task_status(task_id)
            status = result.get("data", {}).get("task_status", "")

            if status == "succeed":
                videos = result.get("data", {}).get("task_result", {}).get("videos", [])
                if videos:
                    return videos[0].get("url")
                return None
            elif status == "failed":
                print(f"[Kling] Task {task_id} failed: {result.get('data', {}).get('message', '')}")
                return None

            print(f"[Kling] Task {task_id}: {status}, waiting {poll_interval}s...")
            time.sleep(poll_interval)

        print(f"[Kling] Task {task_id} timed out after {timeout}s")
        return None
