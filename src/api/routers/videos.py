"""Video generation API endpoints."""

import asyncio
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException

from ...automation import PipelineConfig, create_pipeline
from ...core.logging import get_logger
from ..schemas.video import VideoCreateRequest, VideoResponse, VideoSegmentInfo, VideoStatus
from .news import get_cached_news

logger = get_logger(__name__)
router = APIRouter(prefix="/videos", tags=["videos"])

# In-memory video storage (in production, use database)
_videos: dict[str, dict] = {}


@router.post("/", response_model=VideoResponse, status_code=202)
async def create_video(request: VideoCreateRequest, background_tasks: BackgroundTasks) -> VideoResponse:
    """
    Create a new video from selected news articles.

    This is an async operation - the video will be generated in the background.

    Args:
        request: Video creation request with news IDs and settings
        background_tasks: FastAPI background tasks

    Returns:
        Video metadata with status
    """
    # Validate news IDs exist
    missing_ids = []
    for news_id in request.news_ids:
        if get_cached_news(news_id) is None:
            missing_ids.append(news_id)

    if missing_ids:
        raise HTTPException(
            status_code=404, detail=f"News articles not found: {', '.join(missing_ids)}"
        )

    # Create video entry
    video_id = f"video-{datetime.now().strftime('%Y%m%d')}-{uuid4().hex[:6]}"
    video_data = {
        "id": video_id,
        "status": VideoStatus.PENDING,
        "title": f"Tech News Digest - {datetime.now().strftime('%Y-%m-%d')}",
        "created_at": datetime.now(),
        "video_path": None,
        "youtube_url": None,
        "duration": None,
        "segments": [],
        "total_cost": 0.0,
        "error": None,
        "news_ids": request.news_ids,
        "upload_to_youtube": request.upload_to_youtube,
        "style": request.style,
        "voice": request.voice,
    }
    _videos[video_id] = video_data

    logger.info(f"Creating video {video_id} with {len(request.news_ids)} news articles")

    # Start video generation in background
    background_tasks.add_task(_generate_video, video_id)

    return VideoResponse(
        id=video_id,
        status=VideoStatus.PENDING,
        title=video_data["title"],
        created_at=video_data["created_at"],
        video_path=None,
        youtube_url=None,
        duration=None,
        segments=[],
        total_cost=0.0,
        error=None,
    )


@router.get("/", response_model=list[VideoResponse])
async def list_videos(limit: int = 10, status: VideoStatus | None = None) -> list[VideoResponse]:
    """
    List all videos.

    Args:
        limit: Maximum number of videos to return
        status: Filter by status (optional)

    Returns:
        List of videos
    """
    videos = list(_videos.values())

    # Filter by status
    if status:
        videos = [v for v in videos if v["status"] == status]

    # Sort by created_at (descending)
    videos.sort(key=lambda v: v["created_at"], reverse=True)

    return [
        VideoResponse(
            id=v["id"],
            status=v["status"],
            title=v["title"],
            created_at=v["created_at"],
            video_path=v["video_path"],
            youtube_url=v["youtube_url"],
            duration=v["duration"],
            segments=v["segments"],
            total_cost=v["total_cost"],
            error=v["error"],
        )
        for v in videos[:limit]
    ]


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(video_id: str) -> VideoResponse:
    """
    Get video details by ID.

    Args:
        video_id: Unique video ID

    Returns:
        Video details
    """
    if video_id not in _videos:
        raise HTTPException(status_code=404, detail=f"Video '{video_id}' not found")

    v = _videos[video_id]
    return VideoResponse(
        id=v["id"],
        status=v["status"],
        title=v["title"],
        created_at=v["created_at"],
        video_path=v["video_path"],
        youtube_url=v["youtube_url"],
        duration=v["duration"],
        segments=v["segments"],
        total_cost=v["total_cost"],
        error=v["error"],
    )


@router.delete("/{video_id}")
async def delete_video(video_id: str) -> dict:
    """
    Delete a video.

    Args:
        video_id: Unique video ID

    Returns:
        Confirmation message
    """
    if video_id not in _videos:
        raise HTTPException(status_code=404, detail=f"Video '{video_id}' not found")

    video_data = _videos[video_id]

    # Delete video file if exists
    if video_data["video_path"]:
        video_path = Path(video_data["video_path"])
        if video_path.exists():
            video_path.unlink()
            logger.info(f"Deleted video file: {video_path}")

    del _videos[video_id]
    logger.info(f"Deleted video {video_id}")

    return {"status": "success", "message": f"Video {video_id} deleted"}


async def _generate_video(video_id: str) -> None:
    """
    Background task to generate video.

    Args:
        video_id: Video ID to generate
    """
    video_data = _videos[video_id]

    try:
        video_data["status"] = VideoStatus.GENERATING
        logger.info(f"Starting video generation for {video_id}")

        # Get selected news
        news_list = []
        for news_id in video_data["news_ids"]:
            news = get_cached_news(news_id)
            if news:
                news_list.append(news)

        if not news_list:
            raise ValueError("No valid news articles found")

        # Create pipeline config
        config = PipelineConfig(
            news_limit=len(news_list),
            script_style=video_data["style"],
            tts_voice=video_data["voice"],
            enable_youtube_upload=video_data["upload_to_youtube"],
        )

        # Run pipeline (in thread pool to avoid blocking)
        pipeline = create_pipeline(config)
        loop = asyncio.get_event_loop()

        # Generate content
        segments = await loop.run_in_executor(None, pipeline.generate_content, news_list)
        logger.info(f"Generated {len(segments)} segments")

        # Create video
        video_data["status"] = VideoStatus.GENERATING
        video_path = await loop.run_in_executor(None, pipeline.create_video, segments)
        logger.info(f"Video created: {video_path}")

        # Upload to YouTube (if enabled)
        youtube_url = None
        if video_data["upload_to_youtube"] and pipeline.youtube_uploader:
            video_data["status"] = VideoStatus.UPLOADING
            upload_result = await loop.run_in_executor(
                None,
                pipeline.youtube_uploader.upload_video,
                video_path,
                [s.title for s in segments],
            )
            youtube_url = upload_result["video_url"]
            logger.info(f"Uploaded to YouTube: {youtube_url}")

        # Update video data
        video_data["status"] = VideoStatus.UPLOADED if youtube_url else VideoStatus.COMPLETED
        video_data["video_path"] = str(video_path)
        video_data["youtube_url"] = youtube_url
        video_data["duration"] = sum(s.duration for s in segments)
        video_data["segments"] = [
            VideoSegmentInfo(
                title=s.title,
                duration=s.duration,
                cost=(s.script.cost + s.image.cost + s.audio.cost),
            )
            for s in segments
        ]
        video_data["total_cost"] = sum(seg.cost for seg in video_data["segments"])

        logger.info(
            f"Video {video_id} completed - Cost: ${video_data['total_cost']:.4f}, "
            f"Duration: {video_data['duration']:.1f}s"
        )

    except Exception as e:
        logger.error(f"Error generating video {video_id}: {e}", exc_info=True)
        video_data["status"] = VideoStatus.FAILED
        video_data["error"] = str(e)
