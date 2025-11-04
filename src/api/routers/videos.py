"""Video generation API endpoints."""

import asyncio
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
import os

from ...automation import PipelineConfig, create_pipeline
from ...automation.youtube_metadata import generate_youtube_metadata, format_metadata_for_display
from ...core.logging import get_logger
from ...video import VideoProject, VideoProjectConfig
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
        "thumbnail_path": None,
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
        thumbnail_path=None,
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
    # Merge in-memory videos with videos from disk
    all_videos = {}

    # First, load videos from disk
    videos_dir = Path("output/videos")
    if videos_dir.exists():
        for video_file in sorted(videos_dir.glob("tech_news_*.mp4"), reverse=True):
            # Extract video ID from filename (e.g., tech_news_20251103_235037.mp4)
            video_id = video_file.stem

            # Skip if already in memory
            if video_id in _videos:
                continue

            # Get file stats
            stat = video_file.stat()
            created_at = datetime.fromtimestamp(stat.st_mtime)

            # Create video entry from disk file
            all_videos[video_id] = {
                "id": video_id,
                "status": VideoStatus.COMPLETED,
                "title": f"Tech News - {created_at.strftime('%Y-%m-%d %H:%M')}",
                "created_at": created_at,
                "video_path": str(video_file),
                "thumbnail_path": None,
                "youtube_url": None,
                "duration": None,
                "segments": [],
                "total_cost": 0.0,
                "error": None,
                "youtube_metadata": None,
            }

    # Then, add in-memory videos (these override disk videos)
    all_videos.update(_videos)

    videos = list(all_videos.values())

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
            thumbnail_path=v.get("thumbnail_path"),
            youtube_url=v["youtube_url"],
            duration=v["duration"],
            segments=v["segments"],
            total_cost=v["total_cost"],
            error=v["error"],
            youtube_metadata=v.get("youtube_metadata"),
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
    # First check in-memory videos
    if video_id in _videos:
        v = _videos[video_id]
        return VideoResponse(
            id=v["id"],
            status=v["status"],
            title=v["title"],
            created_at=v["created_at"],
            video_path=v["video_path"],
            thumbnail_path=v.get("thumbnail_path"),
            youtube_url=v["youtube_url"],
            duration=v["duration"],
            segments=v["segments"],
            total_cost=v["total_cost"],
            error=v["error"],
            youtube_metadata=v.get("youtube_metadata"),
        )

    # Then check disk
    video_file = Path(f"output/videos/{video_id}.mp4")
    if video_file.exists():
        stat = video_file.stat()
        created_at = datetime.fromtimestamp(stat.st_mtime)

        return VideoResponse(
            id=video_id,
            status=VideoStatus.COMPLETED,
            title=f"Tech News - {created_at.strftime('%Y-%m-%d %H:%M')}",
            created_at=created_at,
            video_path=str(video_file),
            thumbnail_path=None,
            youtube_url=None,
            duration=None,
            segments=[],
            total_cost=0.0,
            error=None,
            youtube_metadata=None,
        )

    raise HTTPException(status_code=404, detail=f"Video '{video_id}' not found")


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


@router.get("/{video_id}/stream")
async def stream_video(video_id: str):
    """
    Stream video file for preview.

    Args:
        video_id: Unique video ID

    Returns:
        Video file stream
    """
    # First check in-memory videos
    if video_id in _videos:
        video_data = _videos[video_id]
        if not video_data["video_path"]:
            raise HTTPException(status_code=404, detail="Video file not available yet")
        video_path = Path(video_data["video_path"])
    else:
        # Then check disk
        video_path = Path(f"output/videos/{video_id}.mp4")

    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found on disk")

    # Return video file with proper content type
    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        filename=f"{video_id}.mp4"
    )


@router.get("/{video_id}/thumbnail")
async def get_thumbnail(video_id: str):
    """
    Get thumbnail image for video.

    Args:
        video_id: Unique video ID

    Returns:
        Thumbnail image file
    """
    if video_id not in _videos:
        raise HTTPException(status_code=404, detail=f"Video '{video_id}' not found")

    video_data = _videos[video_id]

    if not video_data.get("thumbnail_path"):
        raise HTTPException(status_code=404, detail="Thumbnail not available yet")

    thumbnail_path = Path(video_data["thumbnail_path"])

    if not thumbnail_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail file not found on disk")

    # Return thumbnail image with proper content type
    return FileResponse(
        path=str(thumbnail_path),
        media_type="image/jpeg",
        filename=f"{video_id}_thumbnail.jpg"
    )


@router.post("/{video_id}/generate-thumbnail")
async def generate_thumbnail_for_video(video_id: str) -> dict:
    """
    Generate thumbnail for an existing video.

    Args:
        video_id: Unique video ID

    Returns:
        Success message with thumbnail path
    """
    if video_id not in _videos:
        raise HTTPException(status_code=404, detail=f"Video '{video_id}' not found")

    video_data = _videos[video_id]

    try:
        # Import thumbnail generator
        from src.video.thumbnail_generator import ThumbnailGenerator
        from pathlib import Path

        # Try to get image from segments first
        background_image = None

        if video_data.get("segments"):
            # Get first segment's image
            first_segment = video_data["segments"][0]
            # Handle both dict and Pydantic model
            if isinstance(first_segment, dict):
                image_path = first_segment.get("image_path")
            else:
                # Pydantic model - use attribute access
                image_path = getattr(first_segment, "image_path", None)

            if image_path:
                bg_path = Path(image_path)
                if bg_path.exists():
                    background_image = bg_path

        # If no image from segments, use any available image from output/images
        if not background_image:
            images_dir = Path("output/images")
            available_images = list(images_dir.glob("*.png"))
            if not available_images:
                raise HTTPException(status_code=404, detail="No background images available")
            # Use the most recent image
            background_image = sorted(available_images, key=lambda p: p.stat().st_mtime, reverse=True)[0]
            logger.info(f"Using fallback image: {background_image}")

        # Initialize thumbnail generator with config
        config_file = Path("config/thumbnail_config.json")
        generator = ThumbnailGenerator(config_file=config_file if config_file.exists() else None)

        # Generate thumbnail
        title = video_data.get("title", "Tech News Digest")
        subtitle = f"Tech News • {video_data.get('created_at', '')[:10]}"

        thumbnail_path = generator.generate(
            title=title,
            background_image_path=background_image,
            subtitle=subtitle,
            use_cache=False
        )

        # Update video data
        video_data["thumbnail_path"] = str(thumbnail_path)

        logger.info(f"Generated thumbnail for video {video_id}: {thumbnail_path}")

        return {
            "status": "success",
            "message": "Thumbnail generated successfully",
            "thumbnail_path": str(thumbnail_path)
        }

    except Exception as e:
        logger.exception(f"Failed to generate thumbnail for video {video_id}")
        raise HTTPException(status_code=500, detail=f"Thumbnail generation failed: {str(e)}")


@router.put("/{video_id}/metadata")
async def update_metadata(video_id: str, metadata: dict) -> dict:
    """
    Update video YouTube metadata.

    Args:
        video_id: Unique video ID
        metadata: Updated metadata (title, description, tags)

    Returns:
        Updated video metadata
    """
    if video_id not in _videos:
        raise HTTPException(status_code=404, detail=f"Video '{video_id}' not found")

    video_data = _videos[video_id]

    # Update metadata
    if "youtube_metadata" not in video_data:
        video_data["youtube_metadata"] = {}

    if "title" in metadata:
        video_data["youtube_metadata"]["title"] = metadata["title"]

    if "description" in metadata:
        video_data["youtube_metadata"]["description"] = metadata["description"]

    if "tags" in metadata:
        video_data["youtube_metadata"]["tags"] = metadata["tags"]

    if "privacy_status" in metadata:
        video_data["youtube_metadata"]["privacy_status"] = metadata["privacy_status"]

    logger.info(f"Updated metadata for video {video_id}")

    return {
        "status": "success",
        "message": "Metadata updated successfully",
        "metadata": video_data["youtube_metadata"]
    }


@router.post("/{video_id}/upload-youtube")
async def upload_to_youtube(video_id: str, background_tasks: BackgroundTasks) -> dict:
    """
    Manually upload video to YouTube.

    This endpoint allows manual upload after video generation.
    Useful for reviewing video before uploading.

    Args:
        video_id: Unique video ID
        background_tasks: FastAPI background tasks

    Returns:
        Upload status
    """
    if video_id not in _videos:
        raise HTTPException(status_code=404, detail=f"Video '{video_id}' not found")

    video_data = _videos[video_id]

    # Check if video exists
    if not video_data.get("video_path"):
        raise HTTPException(status_code=400, detail="Video file not available")

    video_path = Path(video_data["video_path"])
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found on disk")

    # Check if already uploaded
    if video_data.get("youtube_url"):
        raise HTTPException(
            status_code=400,
            detail=f"Video already uploaded to YouTube: {video_data['youtube_url']}"
        )

    # Start upload in background
    background_tasks.add_task(_upload_to_youtube_task, video_id)

    return {
        "status": "started",
        "message": "YouTube upload started in background",
        "video_id": video_id
    }


async def _upload_to_youtube_task(video_id: str) -> None:
    """
    Background task to upload video to YouTube.

    Args:
        video_id: Video ID
    """
    video_data = _videos[video_id]

    try:
        video_data["status"] = VideoStatus.UPLOADING
        logger.info(f"Starting YouTube upload for {video_id}")

        # Get video info
        video_path = Path(video_data["video_path"])
        thumbnail_path = video_data.get("thumbnail_path")
        if thumbnail_path:
            thumbnail_path = Path(thumbnail_path)

        # Create YouTube uploader
        from ...automation.youtube import create_youtube_uploader

        uploader = create_youtube_uploader()

        # Authenticate
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, uploader.authenticate)

        # Get metadata
        youtube_metadata = video_data.get("youtube_metadata", {})
        title = youtube_metadata.get("title", f"Tech News Digest - {datetime.now().strftime('%Y-%m-%d')}")
        description = youtube_metadata.get("description", "Daily tech news digest")
        tags = youtube_metadata.get("tags", ["tech news", "technology", "AI ON"])

        # Upload video
        upload_result = await loop.run_in_executor(
            None,
            uploader.upload_video,
            video_path,
            title,
            description,
            tags,
        )

        video_id_yt = upload_result["video_id"]
        youtube_url = upload_result["video_url"]

        logger.info(f"Video uploaded to YouTube: {youtube_url}")

        # Upload thumbnail if available
        if thumbnail_path and thumbnail_path.exists():
            try:
                logger.info("Uploading thumbnail...")
                await loop.run_in_executor(
                    None,
                    uploader.set_thumbnail,
                    video_id_yt,
                    thumbnail_path,
                )
                logger.info("Thumbnail uploaded successfully")
            except Exception as e:
                logger.warning(f"Thumbnail upload failed: {e}")

        # Update video data
        video_data["status"] = VideoStatus.UPLOADED
        video_data["youtube_url"] = youtube_url

        logger.info(f"Video {video_id} successfully uploaded to YouTube")

    except Exception as e:
        error_msg = str(e)
        logger.error(f"YouTube upload failed for {video_id}: {error_msg}", exc_info=True)
        video_data["status"] = VideoStatus.COMPLETED  # Revert to completed
        video_data["error"] = f"YouTube upload failed: {error_msg}"


@router.put("/{video_id}/edit")
async def edit_video(video_id: str, edit_config: dict, background_tasks: BackgroundTasks) -> dict:
    """
    Edit video configuration and regenerate.

    Args:
        video_id: Unique video ID
        edit_config: Edit configuration
            - segment_ids: List of segment IDs in desired order
            - show_intro: Include intro (bool)
            - show_outro: Include outro (bool)

    Returns:
        Status message
    """
    if video_id not in _videos:
        raise HTTPException(status_code=404, detail=f"Video '{video_id}' not found")

    video_data = _videos[video_id]

    # Validate video can be edited
    if video_data["status"] in [VideoStatus.GENERATING, VideoStatus.UPLOADING]:
        raise HTTPException(
            status_code=400,
            detail="Cannot edit video while it's being generated or uploaded"
        )

    # Store edit configuration
    video_data["edit_config"] = edit_config
    video_data["status"] = VideoStatus.PENDING

    logger.info(f"Regenerating video {video_id} with edit config: {edit_config}")

    # Trigger regeneration in background
    background_tasks.add_task(_regenerate_video, video_id)

    return {
        "status": "success",
        "message": "Video regeneration started",
        "video_id": video_id
    }


async def _regenerate_video(video_id: str) -> None:
    """
    Regenerate video with edit configuration.

    Args:
        video_id: Video ID to regenerate
    """
    video_data = _videos[video_id]

    try:
        video_data["status"] = VideoStatus.GENERATING
        logger.info(f"Regenerating video {video_id}")

        # Get edit config
        edit_config = video_data.get("edit_config", {})
        segment_ids = edit_config.get("segment_ids", [])
        show_intro = edit_config.get("show_intro", True)
        show_outro = edit_config.get("show_outro", True)

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
            enable_youtube_upload=False,  # Don't upload during edit
        )

        # Run pipeline
        pipeline = create_pipeline(config)
        loop = asyncio.get_event_loop()

        # Generate content (segments)
        segments = await loop.run_in_executor(None, pipeline.generate_content, news_list)
        logger.info(f"Generated {len(segments)} segments")

        # Reorder segments if specified
        if segment_ids:
            # Create segment map
            segment_map = {s.segment_id: s for s in segments}
            # Reorder based on segment_ids
            reordered_segments = []
            for seg_id in segment_ids:
                if seg_id in segment_map:
                    reordered_segments.append(segment_map[seg_id])
            segments = reordered_segments

        # Create video with edit config
        from src.video.models import VideoProjectConfig
        video_config = VideoProjectConfig(
            show_intro=show_intro,
            show_outro=show_outro,
        )

        # Create video project
        from src.video.models import VideoProject
        from datetime import datetime

        project = VideoProject(
            project_id=video_id,
            title=video_data["title"],
            config=video_config,
            segments=segments,
        )

        # Compose video
        from src.video.composition.video_composer import VideoComposer
        composer = VideoComposer()
        video_path = await loop.run_in_executor(
            None,
            composer.compose_project,
            project,
            None
        )

        logger.info(f"Video regenerated: {video_path}")

        # Update video data
        video_data["video_path"] = str(video_path)
        video_data["segments"] = [
            VideoSegmentInfo(
                segment_id=s.segment_id,
                title=s.title,
                duration=s.duration or 0.0,
                cost=s.cost or 0.0,
            )
            for s in segments
        ]
        video_data["duration"] = sum(s.duration or 0.0 for s in segments)
        video_data["total_cost"] = sum(s.cost or 0.0 for s in segments)
        video_data["status"] = VideoStatus.COMPLETED

        logger.info(f"Video {video_id} regenerated successfully")

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error regenerating video {video_id}: {error_msg}", exc_info=True)
        video_data["status"] = VideoStatus.FAILED
        video_data["error"] = error_msg


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

        # Generate thumbnail
        thumbnail_path = None
        if pipeline.thumbnail_generator and segments:
            try:
                logger.info("Generating thumbnail...")
                first_segment = segments[0]
                # GeneratedImage uses local_path, not image_path
                image_path = first_segment.image.local_path
                if image_path and Path(image_path).exists():
                    thumbnail_path = await loop.run_in_executor(
                        None,
                        pipeline.thumbnail_generator.generate,
                        first_segment.title,
                        Path(image_path),
                        None,  # output_path
                        f"Tech News • {datetime.now().strftime('%Y년 %m월 %d일')}",  # subtitle (Korean format)
                    )
                    logger.info(f"Thumbnail generated: {thumbnail_path}")
                else:
                    logger.warning(f"Image path not found for thumbnail generation")
            except Exception as e:
                logger.warning(f"Thumbnail generation failed: {e}")

        # Generate YouTube metadata
        project = VideoProject(
            project_id=video_id,
            title=video_data["title"],
            config=VideoProjectConfig(),
            segments=segments,
        )
        youtube_metadata = generate_youtube_metadata(project)
        logger.info(f"YouTube metadata generated for {video_id}")

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
            video_id_yt = upload_result["video_id"]
            youtube_url = upload_result["video_url"]
            logger.info(f"Uploaded to YouTube: {youtube_url}")

            # Upload thumbnail (if generated)
            if thumbnail_path and thumbnail_path.exists() and pipeline.youtube_uploader:
                try:
                    logger.info("Uploading thumbnail to YouTube...")
                    await loop.run_in_executor(
                        None,
                        pipeline.youtube_uploader.set_thumbnail,
                        video_id_yt,
                        thumbnail_path,
                    )
                    logger.info("Thumbnail uploaded to YouTube")
                except Exception as e:
                    logger.warning(f"Thumbnail upload to YouTube failed: {e}")

        # Update video data
        video_data["status"] = VideoStatus.UPLOADED if youtube_url else VideoStatus.COMPLETED
        video_data["video_path"] = str(video_path)
        video_data["thumbnail_path"] = str(thumbnail_path) if thumbnail_path else None
        video_data["youtube_url"] = youtube_url
        video_data["duration"] = sum(s.duration for s in segments)
        video_data["segments"] = [
            VideoSegmentInfo(
                title=s.title,
                duration=s.duration,
                cost=(s.script.total_cost + s.image.total_cost + s.audio.total_cost),
                image_path=str(s.image.local_path) if s.image.local_path else None,
            )
            for s in segments
        ]
        video_data["total_cost"] = sum(seg.cost for seg in video_data["segments"])
        video_data["youtube_metadata"] = youtube_metadata

        logger.info(
            f"Video {video_id} completed - Cost: ${video_data['total_cost']:.4f}, "
            f"Duration: {video_data['duration']:.1f}s"
        )

    except Exception as e:
        logger.error(f"Error generating video {video_id}: {e}", exc_info=True)
        video_data["status"] = VideoStatus.FAILED
        video_data["error"] = str(e)
