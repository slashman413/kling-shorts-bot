"""
Kling AI API client for text-to-video generation.
Supports both AK/SK (HMAC) and Bearer Token auth.
"""

import os
import time
import hashlib
import hmac
import json
import uuid
from typing import Optional

import requests


class KlingClient:
    """Client for Kling AI video generation API."""

    def __init__(self):
        self.api_base = "https://api.klingai.com"
        
        # Try bearer token first (new auth method)
        self.api_key = os.environ.get("KLING_API_KEY", "")
        if not self.api_key:
            self.api_key = os.environ.get("KLING_ACCESS_KEY", "")
        
        self.is_bearer_token = self.api_key.startswith("api-key-") if self.api_key else False
        
        if not self.is_bearer_token:
            # Fall back to AK/SK HMAC auth
            self.access_key = os.environ.get("KLING_ACCESS_KEY", "")
            self.secret_key = os.environ.get("KLING_SECRET_KEY", "")
            
            if not self.access_key or not self.secret_key:
                raise ValueError(
                    "Kling API credentials not found. Set one of:\n"
                    "  - KLING_API_KEY (new bearer token, starts with 'api-key-')\n"
                    "  - KLING_ACCESS_KEY + KLING_SECRET_KEY (legacy AK/SK pair)\n"
                    "Get them at https://klingai.com → API Platform"
                )

    def _get_headers(self, method: str, path: str, body: str = "") -> dict:
        """Generate appropriate auth headers."""
        if self.is_bearer_token:
            return {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
        else:
            # Legacy AK/SK HMAC signature
            timestamp = str(int(time.time()))
            nonce = str(uuid.uuid4())
            sign_str = f"{method}\n{path}\n{timestamp}\n{nonce}\n{body}"
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
        duration: int = 6,
        cfg_scale: float = 0.5,
        negative_prompt: str = "",
        model: str = "kling-v3",
        aspect_ratio: str = "9:16",
        max_retries: int = 5,
    ) -> dict:
        """
        Generate a video from text prompt using Kling AI.
        Retries on 429 rate-limit with exponential backoff.

        Args:
            prompt: The video description (in English, detailed)
            duration: Video duration in seconds (5 or 10)
            cfg_scale: How strictly to follow the prompt (0-1)
            negative_prompt: What to avoid in the video
            model: Model version (kling-v3 recommended)
            aspect_ratio: "9:16" for vertical Shorts, "16:9" for landscape
            max_retries: Max retries on 429 rate-limit

        Returns:
            Response dict with task_id for status polling
        """
        path = "/v1/videos/text2video"
        url = f"{self.api_base}{path}"

        payload = {
            "model_name": model,
            "prompt": prompt,
            "duration": duration,
            "cfg_scale": cfg_scale,
            "aspect_ratio": aspect_ratio,
        }
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt

        body = json.dumps(payload, ensure_ascii=False)

        headers = self._get_headers("POST", path, body)

        # Retry on 429 with exponential backoff
        for attempt in range(max_retries):
            resp = requests.post(url, headers=headers, data=body, timeout=60)
            if resp.status_code == 429:
                try:
                    err_detail = resp.json()
                except Exception:
                    err_detail = resp.text[:200]
                print(f"    ⏳ Rate limited (429): {err_detail}")
                if attempt < max_retries - 1:
                    wait = min(2 ** attempt * 5, 120)
                    print(f"       Retrying in {wait}s... (attempt {attempt+2}/{max_retries})")
                    time.sleep(wait)
                    continue
                raise RuntimeError(f"Kling API 429 after {max_retries} retries: {err_detail}")
            resp.raise_for_status()
            return resp.json()

    def get_task_status(self, task_id: str) -> dict:
        """Poll for video generation task status."""
        path = f"/v1/videos/text2video/{task_id}"
        url = f"{self.api_base}{path}"

        headers = self._get_headers("GET", path)

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
