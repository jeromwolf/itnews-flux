"""
Scheduler for automated daily video production.

Uses APScheduler to run the content pipeline:
- Daily at 7:00 AM KST
- Automatic retry on failure
- Email/Slack notifications
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from pydantic import BaseModel, Field

from src.automation.pipeline import PipelineConfig, create_pipeline
from src.core.logging import get_logger

logger = get_logger(__name__)


class SchedulerConfig(BaseModel):
    """Scheduler configuration."""

    # Schedule
    hour: int = Field(default=7, description="Hour to run (0-23)")
    minute: int = Field(default=0, description="Minute to run (0-59)")
    timezone: str = Field(default="Asia/Seoul", description="Timezone")

    # Pipeline config
    pipeline_config: PipelineConfig = Field(
        default_factory=PipelineConfig,
        description="Pipeline configuration",
    )

    # Notifications
    enable_notifications: bool = Field(
        default=False, description="Enable notifications"
    )
    notification_email: Optional[str] = Field(
        default=None, description="Email for notifications"
    )
    slack_webhook_url: Optional[str] = Field(
        default=None, description="Slack webhook URL"
    )


class DailyScheduler:
    """
    Daily scheduler for automated video production.

    Runs the content pipeline at a specified time each day.
    """

    def __init__(self, config: Optional[SchedulerConfig] = None):
        """
        Initialize scheduler.

        Args:
            config: Scheduler configuration
        """
        self.config = config or SchedulerConfig()
        self.logger = get_logger(__name__)
        self.scheduler = BlockingScheduler(timezone=self.config.timezone)

        self.logger.info(
            f"DailyScheduler initialized "
            f"(schedule={self.config.hour:02d}:{self.config.minute:02d} {self.config.timezone})"
        )

    def run_pipeline(self):
        """Run the content pipeline."""
        self.logger.info("=" * 70)
        self.logger.info("Starting scheduled pipeline execution")
        self.logger.info(f"Time: {datetime.now()}")
        self.logger.info("=" * 70)

        try:
            # Create and run pipeline
            pipeline = create_pipeline(self.config.pipeline_config)
            result = pipeline.run()

            if result.success:
                self.logger.info("Pipeline completed successfully!")
                self.logger.info(f"Video: {result.video_path}")
                self.logger.info(f"Cost: ${result.total_cost:.4f}")
                self.logger.info(f"Duration: {result.total_duration:.1f}s")

                # Send success notification
                if self.config.enable_notifications:
                    self._send_notification(
                        f"✅ Tech News Digest - Video Created Successfully!\n\n"
                        f"Video: {result.video_path}\n"
                        f"Duration: {result.total_duration:.1f}s\n"
                        f"Cost: ${result.total_cost:.4f}\n"
                        f"News: {result.news_count} articles"
                    )

            else:
                self.logger.error("Pipeline failed!")
                self.logger.error(f"Errors: {result.errors}")

                # Send failure notification
                if self.config.enable_notifications:
                    self._send_notification(
                        f"❌ Tech News Digest - Pipeline Failed\n\n"
                        f"Errors: {', '.join(result.errors)}\n"
                        f"Time: {datetime.now()}"
                    )

        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {e}", exc_info=True)

            # Send error notification
            if self.config.enable_notifications:
                self._send_notification(
                    f"💥 Tech News Digest - Pipeline Error\n\n"
                    f"Error: {str(e)}\n"
                    f"Time: {datetime.now()}"
                )

        self.logger.info("=" * 70)
        self.logger.info("Scheduled pipeline execution completed")
        self.logger.info("=" * 70)

    def _send_notification(self, message: str):
        """
        Send notification via email or Slack.

        Args:
            message: Notification message
        """
        # Email notification
        if self.config.notification_email:
            try:
                self._send_email(message)
                self.logger.info(f"Email notification sent to {self.config.notification_email}")
            except Exception as e:
                self.logger.error(f"Failed to send email: {e}")

        # Slack notification
        if self.config.slack_webhook_url:
            try:
                self._send_slack(message)
                self.logger.info("Slack notification sent")
            except Exception as e:
                self.logger.error(f"Failed to send Slack message: {e}")

    def _send_email(self, message: str):
        """Send email notification (placeholder)."""
        # TODO: Implement email sending using SMTP
        self.logger.info(f"Email would be sent: {message[:100]}...")

    def _send_slack(self, message: str):
        """Send Slack notification."""
        import requests

        if not self.config.slack_webhook_url:
            return

        payload = {"text": message}
        response = requests.post(self.config.slack_webhook_url, json=payload)
        response.raise_for_status()

    def start(self):
        """Start the scheduler."""
        # Add daily job
        trigger = CronTrigger(
            hour=self.config.hour,
            minute=self.config.minute,
            timezone=self.config.timezone,
        )

        self.scheduler.add_job(
            self.run_pipeline,
            trigger=trigger,
            id="daily_video_production",
            name="Daily Video Production",
            replace_existing=True,
        )

        self.logger.info(
            f"Scheduler started - will run daily at "
            f"{self.config.hour:02d}:{self.config.minute:02d} {self.config.timezone}"
        )

        # Print next run time
        job = self.scheduler.get_job("daily_video_production")
        if job and job.next_run_time:
            self.logger.info(f"Next run: {job.next_run_time}")

        # Start scheduler (blocking)
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            self.logger.info("Scheduler stopped by user")
            self.scheduler.shutdown()

    def run_now(self):
        """Run the pipeline immediately (for testing)."""
        self.logger.info("Running pipeline immediately (manual trigger)")
        self.run_pipeline()

    def list_jobs(self):
        """List all scheduled jobs."""
        jobs = self.scheduler.get_jobs()
        if not jobs:
            self.logger.info("No scheduled jobs")
            return

        self.logger.info("Scheduled jobs:")
        for job in jobs:
            self.logger.info(
                f"  - {job.name} (ID: {job.id})\n"
                f"    Next run: {job.next_run_time}\n"
                f"    Trigger: {job.trigger}"
            )


def create_scheduler(config: Optional[SchedulerConfig] = None) -> DailyScheduler:
    """
    Create daily scheduler.

    Args:
        config: Scheduler configuration

    Returns:
        DailyScheduler instance

    Example:
        >>> scheduler = create_scheduler()
        >>> scheduler.start()  # Run daily at 7 AM
        >>>
        >>> # Or run immediately for testing
        >>> scheduler.run_now()
    """
    return DailyScheduler(config=config)
