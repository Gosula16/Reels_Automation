from __future__ import annotations

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from social_reels_automation.config import get_settings
from social_reels_automation.models import ContentBrief


class YouTubeClient:
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]

    def upload_short(self, video_path: Path, brief: ContentBrief) -> tuple[str, str]:
        settings = get_settings()
        youtube = build("youtube", "v3", credentials=self._load_credentials())
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": brief.youtube_title,
                    "description": brief.youtube_description,
                    "categoryId": settings.youtube_category_id,
                    "defaultLanguage": settings.default_language,
                    "tags": brief.hashtags,
                },
                "status": {
                    "privacyStatus": settings.publish_privacy_status,
                    "selfDeclaredMadeForKids": False,
                },
            },
            media_body=MediaFileUpload(str(video_path), chunksize=-1, resumable=True),
        )
        response = request.execute()
        video_id = response["id"]
        return video_id, f"https://www.youtube.com/shorts/{video_id}"

    def _load_credentials(self) -> Credentials:
        settings = get_settings()
        token_file = settings.youtube_token_file
        creds = None
        if not settings.youtube_client_secrets_file.exists():
            raise RuntimeError(
                f"YouTube OAuth secrets file not found at {settings.youtube_client_secrets_file}."
            )
        if token_file.exists():
            creds = Credentials.from_authorized_user_file(str(token_file), self.scopes)

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(settings.youtube_client_secrets_file),
                self.scopes,
            )
            creds = flow.run_local_server(port=0)
            token_file.write_text(creds.to_json(), encoding="utf-8")

        return creds
