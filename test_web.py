#!/usr/bin/env python3
"""Test the web interface."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def test_import():
    """Test that all modules import correctly."""
    print("=" * 70)
    print("🧪 Testing Web Interface Imports")
    print("=" * 70)

    try:
        print("✓ Importing FastAPI app...")
        from src.api.main import app

        print("✓ FastAPI app imported successfully")

        # Check routes
        routes = [route.path for route in app.routes]
        print(f"\n📍 Registered routes ({len(routes)}):")
        for route in sorted(routes):
            print(f"  - {route}")

        # Check API routers
        api_routes = [r for r in routes if r.startswith("/api/")]
        print(f"\n🔌 API endpoints: {len(api_routes)}")

        # Check UI routes
        ui_routes = [r for r in routes if r in ["/", "/dashboard", "/news", "/videos", "/settings"]]
        print(f"🎨 UI pages: {len(ui_routes)}")
        for route in ui_routes:
            print(f"  - {route}")

        print("\n" + "=" * 70)
        print("✅ All imports successful!")
        print("=" * 70)
        print("\n💡 To start the server:")
        print("   python run_web.py --reload")
        print("\n📊 Then visit:")
        print("   http://127.0.0.1:8000/dashboard")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_import()
    sys.exit(0 if success else 1)
