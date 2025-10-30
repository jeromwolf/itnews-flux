"""YouTube player and downloader API endpoints."""

from pathlib import Path
from urllib.parse import quote, unquote

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ...core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/youtube", tags=["youtube-player"])


@router.get("/info/{video_id}")
async def get_video_info(video_id: str) -> dict:
    """
    Get YouTube video information.

    Args:
        video_id: YouTube video ID

    Returns:
        Video metadata
    """
    logger.info(f"Getting video info: {video_id}")

    try:
        import yt_dlp

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)

            return {
                "video_id": video_id,
                "title": info.get("title", ""),
                "channel": info.get("uploader", ""),
                "duration": info.get("duration_string", ""),
                "views": info.get("view_count", 0),
                "upload_date": info.get("upload_date", ""),
                "thumbnail": info.get("thumbnail", ""),
                "description": info.get("description", "")[:500],  # First 500 chars
            }

    except Exception as e:
        logger.error(f"Failed to get video info: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to get video info: {str(e)}")


@router.post("/download/{video_id}")
async def download_video(video_id: str, type: str = "video") -> dict:
    """
    Download YouTube video or audio.

    Args:
        video_id: YouTube video ID
        type: Download type ('video' or 'audio')

    Returns:
        Download information with file path
    """
    logger.info(f"Downloading {type} for video: {video_id}")

    if type not in ["video", "audio"]:
        raise HTTPException(status_code=400, detail="Type must be 'video' or 'audio'")

    try:
        import yt_dlp

        # Create output directory
        output_dir = Path("output/youtube_downloads")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Set download options
        if type == "audio":
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': False,
            }
        else:
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': str(output_dir / '%(title)s.%(ext)s'),
                'merge_output_format': 'mp4',
                'quiet': False,
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=True)

            # Get the downloaded filename
            if type == "audio":
                filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            else:
                filename = ydl.prepare_filename(info)

            logger.info(f"Downloaded: {filename}")

            # URL encode filename for special characters like #
            encoded_filename = quote(Path(filename).name)

            return {
                "status": "success",
                "filename": Path(filename).name,
                "download_url": f"/api/youtube/file/{encoded_filename}",
                "type": type,
            }

    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise HTTPException(status_code=400, detail=f"Download failed: {str(e)}")


@router.get("/file/{filename:path}")
async def get_downloaded_file(filename: str):
    """
    Serve downloaded file.

    Args:
        filename: Downloaded file name (URL encoded)

    Returns:
        File download response
    """
    # Decode URL-encoded filename
    decoded_filename = unquote(filename)
    file_path = Path("output/youtube_downloads") / decoded_filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(file_path),
        filename=decoded_filename,
        media_type='application/octet-stream'
    )
