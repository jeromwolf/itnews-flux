"""Schedule management API endpoints."""

from datetime import datetime

from fastapi import APIRouter

from ...core.logging import get_logger
from ..schemas.schedule import ScheduleConfigResponse, ScheduleConfigUpdate

logger = get_logger(__name__)
router = APIRouter(prefix="/schedule", tags=["schedule"])

# In-memory schedule config (in production, use database)
_schedule_config = {
    "enabled": True,
    "hour": 7,
    "minute": 0,
    "timezone": "Asia/Seoul",
    "news_limit": 3,
    "enable_youtube_upload": False,
}


@router.get("/", response_model=ScheduleConfigResponse)
async def get_schedule() -> ScheduleConfigResponse:
    """
    Get current schedule configuration.

    Returns:
        Schedule configuration
    """
    # Calculate next run time
    next_run = None
    if _schedule_config["enabled"]:
        now = datetime.now()
        next_run_time = now.replace(
            hour=_schedule_config["hour"],
            minute=_schedule_config["minute"],
            second=0,
            microsecond=0,
        )
        # If time has passed today, schedule for tomorrow
        if next_run_time <= now:
            from datetime import timedelta

            next_run_time += timedelta(days=1)

        next_run = next_run_time.strftime("%Y-%m-%d %H:%M:%S %Z")

    return ScheduleConfigResponse(
        enabled=_schedule_config["enabled"],
        hour=_schedule_config["hour"],
        minute=_schedule_config["minute"],
        timezone=_schedule_config["timezone"],
        news_limit=_schedule_config["news_limit"],
        enable_youtube_upload=_schedule_config["enable_youtube_upload"],
        next_run=next_run,
    )


@router.put("/", response_model=ScheduleConfigResponse)
async def update_schedule(request: ScheduleConfigUpdate) -> ScheduleConfigResponse:
    """
    Update schedule configuration.

    Args:
        request: Updated schedule configuration

    Returns:
        Updated schedule configuration
    """
    # Update only provided fields
    if request.enabled is not None:
        _schedule_config["enabled"] = request.enabled
        logger.info(f"Schedule enabled: {request.enabled}")

    if request.hour is not None:
        _schedule_config["hour"] = request.hour
        logger.info(f"Schedule hour updated: {request.hour}")

    if request.minute is not None:
        _schedule_config["minute"] = request.minute
        logger.info(f"Schedule minute updated: {request.minute}")

    if request.timezone is not None:
        _schedule_config["timezone"] = request.timezone
        logger.info(f"Schedule timezone updated: {request.timezone}")

    if request.news_limit is not None:
        _schedule_config["news_limit"] = request.news_limit
        logger.info(f"News limit updated: {request.news_limit}")

    if request.enable_youtube_upload is not None:
        _schedule_config["enable_youtube_upload"] = request.enable_youtube_upload
        logger.info(f"YouTube upload enabled: {request.enable_youtube_upload}")

    # Return updated config
    return await get_schedule()


@router.post("/trigger")
async def trigger_now() -> dict:
    """
    Manually trigger video generation now (bypass schedule).

    Returns:
        Confirmation message
    """
    logger.info("Manual video generation triggered")

    # TODO: Integrate with pipeline to actually generate video
    # For now, just return confirmation

    return {
        "status": "triggered",
        "message": "Video generation started",
        "timestamp": datetime.now().isoformat(),
    }
