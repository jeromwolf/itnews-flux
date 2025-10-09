#!/usr/bin/env python3
"""Run the Tech News Digest web server."""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Run the web server."""
    parser = argparse.ArgumentParser(description="Tech News Digest Web Server")
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload (development mode)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (default: 1)",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("🎬 Tech News Digest - Web Server")
    print("=" * 70)
    print(f"🌐 Server: http://{args.host}:{args.port}")
    print(f"📊 Dashboard: http://{args.host}:{args.port}/dashboard")
    print(f"📚 API Docs: http://{args.host}:{args.port}/api/docs")
    print(f"🔄 Reload: {'Enabled' if args.reload else 'Disabled'}")
    print("=" * 70)
    print()

    # Import uvicorn here to avoid import issues
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers if not args.reload else 1,  # reload mode requires workers=1
        log_level="info",
    )


if __name__ == "__main__":
    main()
