"""
YouTube uploader for Tech News Digest.

Handles automated video upload to YouTube:
- OAuth2 authentication
- Video upload with metadata
- Thumbnail upload
- Playlist management
"""

import pickle
from datetime import datetime
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pydantic import BaseModel, Field

from src.core.logging import get_logger

logger = get_logger(__name__)

# YouTube API scopes
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


class YouTubeConfig(BaseModel):
    """YouTube upload configuration."""

    # Authentication
    client_secrets_file: Path = Field(
        default=Path("config/client_secrets.json"),
        description="OAuth2 client secrets file",
    )
    token_file: Path = Field(
        default=Path("config/youtube_token.pickle"),
        description="Stored credentials file",
    )

    # Video metadata
    title_template: str = Field(
        default="Tech News Digest - {date}",
        description="Video title template",
    )
    description_template: str = Field(
        default="""Daily tech news in English for learning!

Today's topics:
{topics}

🎯 Perfect for:
- IT professionals learning English
- Tech enthusiasts
- English learners interested in technology

📚 Subscribe for daily tech news!

#TechNews #English #Learning #IT #Technology""",
        description="Video description template",
    )
    category_id: str = Field(default="28", description="YouTube category (28=Science & Technology)")
    tags: list[str] = Field(
        default=["tech news", "english learning", "IT news", "technology", "daily news"],
        description="Video tags",
    )
    privacy_status: str = Field(
        default="public", description="Privacy status (public/private/unlisted)"
    )

    # Playlist
    playlist_id: Optional[str] = Field(
        default=None, description="Playlist ID to add video to"
    )


class YouTubeUploader:
    """
    YouTube video uploader.

    Handles authentication and video upload to YouTube.
    """

    def __init__(self, config: Optional[YouTubeConfig] = None):
        """
        Initialize YouTube uploader.

        Args:
            config: YouTube configuration
        """
        self.config = config or YouTubeConfig()
        self.logger = get_logger(__name__)
        self.youtube = None

        self.logger.info("YouTubeUploader initialized")

    def authenticate(self) -> bool:
        """
        Authenticate with YouTube API.

        Returns:
            True if authentication successful

        Raises:
            FileNotFoundError: If client secrets file not found
        """
        creds = None

        # Load existing credentials
        if self.config.token_file.exists():
            with open(self.config.token_file, "rb") as token:
                creds = pickle.load(token)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.logger.info("Refreshing credentials...")
                creds.refresh(Request())
            else:
                if not self.config.client_secrets_file.exists():
                    raise FileNotFoundError(
                        f"Client secrets file not found: {self.config.client_secrets_file}\n"
                        f"Please download from Google Cloud Console:\n"
                        f"1. Go to https://console.cloud.google.com/apis/credentials\n"
                        f"2. Create OAuth 2.0 Client ID (Desktop app)\n"
                        f"3. Download JSON and save as {self.config.client_secrets_file}"
                    )

                self.logger.info("Starting OAuth2 flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.config.client_secrets_file), SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials
            self.config.token_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config.token_file, "wb") as token:
                pickle.dump(creds, token)

            self.logger.info("Credentials saved")

        # Build YouTube service
        self.youtube = build("youtube", "v3", credentials=creds)
        self.logger.info("YouTube API authenticated")

        return True

    def upload_video(
        self,
        video_path: Path,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[list[str]] = None,
        topics: Optional[list[str]] = None,
    ) -> dict:
        """
        Upload video to YouTube.

        Args:
            video_path: Path to video file
            title: Video title (uses template if not provided)
            description: Video description (uses template if not provided)
            tags: Video tags (uses config if not provided)
            topics: News topics for description

        Returns:
            Upload response with video ID

        Raises:
            FileNotFoundError: If video file not found
            RuntimeError: If not authenticated
        """
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        if not self.youtube:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        # Generate title
        if not title:
            title = self.config.title_template.format(
                date=datetime.now().strftime("%Y-%m-%d")
            )

        # Generate description
        if not description:
            topics_text = "\n".join(f"• {topic}" for topic in (topics or ["Latest tech news"]))
            description = self.config.description_template.format(topics=topics_text)

        # Use tags from config if not provided
        if not tags:
            tags = self.config.tags

        self.logger.info(f"Uploading video: {title}")
        self.logger.info(f"File: {video_path} ({video_path.stat().st_size / 1024 / 1024:.1f} MB)")

        # Prepare request body
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": self.config.category_id,
            },
            "status": {
                "privacyStatus": self.config.privacy_status,
                "selfDeclaredMadeForKids": False,
            },
        }

        # Create media upload
        media = MediaFileUpload(
            str(video_path),
            chunksize=-1,  # Upload in single request
            resumable=True,
        )

        # Execute upload
        try:
            request = self.youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media,
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    self.logger.info(f"Upload progress: {progress}%")

            video_id = response["id"]
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            self.logger.info(f"Upload complete! Video ID: {video_id}")
            self.logger.info(f"URL: {video_url}")

            # Add to playlist if configured
            if self.config.playlist_id:
                self._add_to_playlist(video_id)

            return {
                "video_id": video_id,
                "video_url": video_url,
                "title": title,
                "privacy_status": self.config.privacy_status,
            }

        except Exception as e:
            self.logger.error(f"Upload failed: {e}", exc_info=True)
            raise

    def _add_to_playlist(self, video_id: str):
        """
        Add video to playlist.

        Args:
            video_id: YouTube video ID
        """
        try:
            self.youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": self.config.playlist_id,
                        "resourceId": {"kind": "youtube#video", "videoId": video_id},
                    }
                },
            ).execute()

            self.logger.info(f"Added to playlist: {self.config.playlist_id}")

        except Exception as e:
            self.logger.error(f"Failed to add to playlist: {e}")

    def set_thumbnail(self, video_id: str, thumbnail_path: Path):
        """
        Set custom thumbnail for video.

        Args:
            video_id: YouTube video ID
            thumbnail_path: Path to thumbnail image
        """
        if not thumbnail_path.exists():
            raise FileNotFoundError(f"Thumbnail not found: {thumbnail_path}")

        try:
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(thumbnail_path)),
            ).execute()

            self.logger.info(f"Thumbnail set for video {video_id}")

        except Exception as e:
            self.logger.error(f"Failed to set thumbnail: {e}")
            raise

    def get_upload_quota(self) -> dict:
        """
        Get YouTube upload quota information.

        Returns:
            Quota information
        """
        # Note: Actual quota checking requires YouTube Data API v3 quota endpoint
        # This is a placeholder for quota management
        return {
            "daily_limit": 10000,  # Default YouTube API quota
            "note": "Check quota at: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas",
        }


def create_youtube_uploader(config: Optional[YouTubeConfig] = None) -> YouTubeUploader:
    """
    Create YouTube uploader.

    Args:
        config: YouTube configuration

    Returns:
        YouTubeUploader instance

    Example:
        >>> uploader = create_youtube_uploader()
        >>> uploader.authenticate()
        >>> result = uploader.upload_video(
        ...     video_path=Path("output/video.mp4"),
        ...     topics=["OpenAI GPT-5", "Tesla AI"]
        ... )
        >>> print(result["video_url"])
    """
    return YouTubeUploader(config=config)
