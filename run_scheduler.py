#!/usr/bin/env python3
"""
Tech News Digest - Automated Scheduler

Runs the complete automation system:
- Daily video production at 7 AM
- YouTube upload (optional)
- Notifications (optional)

Usage:
    # Run scheduler (daily at 7 AM)
    python run_scheduler.py

    # Run immediately (manual trigger)
    python run_scheduler.py --now

    # Run with YouTube upload enabled
    python run_scheduler.py --youtube

    # Custom schedule
    python run_scheduler.py --hour 9 --minute 30
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.automation.pipeline import PipelineConfig
from src.automation.scheduler import SchedulerConfig, create_scheduler
from src.core.logging import get_logger

logger = get_logger(__name__)


def print_banner():
    """Print application banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║              🎬 Tech News Digest Scheduler 🎬                ║
    ║                                                              ║
    ║         Automated Daily Video Production System             ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """Run scheduler."""
    parser = argparse.ArgumentParser(
        description="Tech News Digest - Automated Scheduler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Schedule options
    parser.add_argument(
        "--now",
        action="store_true",
        help="Run pipeline immediately (skip scheduler)",
    )
    parser.add_argument(
        "--hour",
        type=int,
        default=7,
        help="Hour to run daily (0-23, default: 7)",
    )
    parser.add_argument(
        "--minute",
        type=int,
        default=0,
        help="Minute to run daily (0-59, default: 0)",
    )
    parser.add_argument(
        "--timezone",
        type=str,
        default="Asia/Seoul",
        help="Timezone (default: Asia/Seoul)",
    )

    # Pipeline options
    parser.add_argument(
        "--news-limit",
        type=int,
        default=3,
        help="Number of news articles (default: 3)",
    )
    parser.add_argument(
        "--max-age",
        type=int,
        default=24,
        help="Max age of news in hours (default: 24)",
    )
    parser.add_argument(
        "--youtube",
        action="store_true",
        help="Enable YouTube upload",
    )

    # Notification options
    parser.add_argument(
        "--email",
        type=str,
        help="Email for notifications",
    )
    parser.add_argument(
        "--slack-webhook",
        type=str,
        help="Slack webhook URL for notifications",
    )

    args = parser.parse_args()

    try:
        print_banner()

        # Create pipeline config
        pipeline_config = PipelineConfig(
            news_limit=args.news_limit,
            max_age_hours=args.max_age,
            enable_youtube_upload=args.youtube,
        )

        # Create scheduler config
        scheduler_config = SchedulerConfig(
            hour=args.hour,
            minute=args.minute,
            timezone=args.timezone,
            pipeline_config=pipeline_config,
            enable_notifications=bool(args.email or args.slack_webhook),
            notification_email=args.email,
            slack_webhook_url=args.slack_webhook,
        )

        # Create scheduler
        scheduler = create_scheduler(scheduler_config)

        # Run immediately or schedule
        if args.now:
            logger.info("Running pipeline immediately...")
            print("\n🚀 Starting pipeline execution...\n")
            scheduler.run_now()
            print("\n✅ Pipeline execution completed!\n")

        else:
            logger.info("Starting scheduler...")
            print(f"\n📅 Scheduler Configuration:")
            print(f"   Time: {args.hour:02d}:{args.minute:02d} {args.timezone}")
            print(f"   News: {args.news_limit} articles (max {args.max_age}h old)")
            print(f"   YouTube: {'Enabled' if args.youtube else 'Disabled'}")
            print(f"   Notifications: {'Enabled' if scheduler_config.enable_notifications else 'Disabled'}")

            if args.youtube:
                print(f"\n⚠️  YouTube upload is ENABLED")
                print(f"   Make sure you have configured:")
                print(f"   1. config/client_secrets.json (OAuth2 credentials)")
                print(f"   2. Run authentication flow on first use")

            print(f"\n🕐 Next run: {args.hour:02d}:{args.minute:02d} {args.timezone}")
            print(f"\n✨ Scheduler started! Press Ctrl+C to stop.\n")

            scheduler.start()

    except KeyboardInterrupt:
        print("\n\n👋 Scheduler stopped by user")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Scheduler failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
