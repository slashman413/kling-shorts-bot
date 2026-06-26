"""
YouTube uploader using YouTube Data API v3.
Requires OAuth 2.0 setup - see setup_guide.md
"""

import os
import pickle
import json
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


class YouTubeUploader:
    """Upload videos to YouTube channel."""

    def __init__(self):
        self.client_id = os.environ.get("YOUTUBE_CLIENT_ID")
        self.client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
        self.refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")
        self.token_file = self._get_token_path()

        if not all([self.client_id, self.client_secret, self.refresh_token]):
            raise ValueError(
                "YouTube OAuth not configured.\n"
                "Required env vars:\n"
                "  YOUTUBE_CLIENT_ID\n"
                "  YOUTUBE_CLIENT_SECRET\n"
                "  YOUTUBE_REFRESH_TOKEN\n\n"
                "See setup_guide.md for OAuth setup instructions."
            )

        self.service = self._authenticate()

    def _get_token_path(self) -> Path:
        return Path(os.environ.get("YOUTUBE_TOKEN_PATH", "./youtube_token.pickle"))

    def _authenticate(self):
        """Authenticate with YouTube using OAuth 2.0 refresh token."""
        creds = Credentials(
            None,
            refresh_token=self.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=SCOPES,
        )

        # Refresh token to get access token
        creds.refresh(Request())
        return build("youtube", "v3", credentials=creds)

    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list[str],
        category_id: str = "24",  # 24 = Entertainment (Shorts-friendly)
        privacy_status: str = "public",
    ) -> Optional[str]:
        """
        Upload a video to YouTube Shorts.

        Args:
            video_path: Path to the video file
            title: Video title (max 100 chars for Shorts)
            description: Video description
            tags: List of hashtags/keywords
            category_id: YouTube category ID
            privacy_status: public / unlisted / private

        Returns:
            YouTube video ID if successful
        """
        body = {
            "snippet": {
                "title": title[:100],
                "description": description,
                "tags": tags,
                "categoryId": category_id,
                "defaultLanguage": "zh-TW",
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False,
            },
        }

        # For Shorts, set the appropriate flag
        # YouTube auto-detects Shorts (vertical aspect ratio, <60s)

        media = MediaFileUpload(
            video_path,
            chunksize=1024 * 1024,
            resumable=True,
        )

        request = self.service.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media,
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"[YouTube] Upload progress: {int(status.progress() * 100)}%")

        video_id = response.get("id")
        print(f"[YouTube] Uploaded! Video ID: {video_id}")
        print(f"[YouTube] URL: https://youtube.com/watch?v={video_id}")
        return video_id

    def upload_shorts_batch(
        self, videos: list[dict], shorts_prefix: str = "#Shorts"
    ) -> list[str]:
        """
        Upload multiple videos as Shorts.

        Args:
            videos: List of dicts with keys: path, title, description, tags
            shorts_prefix: Prefix for Shorts title

        Returns:
            List of YouTube video IDs
        """
        video_ids = []
        for i, video in enumerate(videos):
            print(f"\n[YouTube] Uploading video {i+1}/{len(videos)}: {video['title']}")

            vid = self.upload_video(
                video_path=video["path"],
                title=f"{shorts_prefix} {video['title']}",
                description=video.get("description", ""),
                tags=video.get("tags", []),
            )
            if vid:
                video_ids.append(vid)

        return video_ids
