"""FastAPI main application."""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ..core.logging import get_logger
from .routers import analytics_router, news_router, schedule_router, videos_router

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Tech News Digest API",
    description="API for automated tech news video generation system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).parent.parent / "web" / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"Mounted static files from {static_dir}")

# Setup Jinja2 templates
templates_dir = Path(__file__).parent.parent / "web" / "templates"
templates = Jinja2Templates(directory=str(templates_dir))
logger.info(f"Loaded templates from {templates_dir}")

# Include routers
app.include_router(news_router, prefix="/api")
app.include_router(videos_router, prefix="/api")
app.include_router(schedule_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - redirect to dashboard."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tech News Digest</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                text-align: center;
                padding: 2rem;
            }
            h1 {
                font-size: 3rem;
                margin-bottom: 1rem;
            }
            p {
                font-size: 1.2rem;
                opacity: 0.9;
                margin-bottom: 2rem;
            }
            .links {
                display: flex;
                gap: 1rem;
                justify-content: center;
                flex-wrap: wrap;
            }
            a {
                display: inline-block;
                padding: 1rem 2rem;
                background: rgba(255, 255, 255, 0.2);
                backdrop-filter: blur(10px);
                border-radius: 8px;
                color: white;
                text-decoration: none;
                transition: all 0.3s;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
            a:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 Tech News Digest</h1>
            <p>AI-Powered Tech News Video Generator</p>
            <div class="links">
                <a href="/dashboard">📊 Dashboard</a>
                <a href="/api/docs">📚 API Docs</a>
                <a href="/api/redoc">📖 ReDoc</a>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Tech News Digest API",
        "version": "1.0.0",
    }


# Web UI routes
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard page."""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/news", response_class=HTMLResponse)
async def news_page(request: Request):
    """News page."""
    return templates.TemplateResponse("news.html", {"request": request})


@app.get("/videos", response_class=HTMLResponse)
async def videos_page(request: Request):
    """Videos page."""
    return templates.TemplateResponse("videos.html", {"request": request})


@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Settings page."""
    return templates.TemplateResponse("settings.html", {"request": request})


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Tech News Digest API starting up...")
    logger.info("API documentation available at /api/docs")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Tech News Digest API shutting down...")
