"""News API schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class NewsResponse(BaseModel):
    """Response schema for a single news article."""

    id: str = Field(..., description="Unique news ID")
    title: str
    summary: str
    url: str
    published_at: datetime
    source: str
    category: str
    score: float = Field(..., ge=0.0, description="Relevance score")
    image_url: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "techcrunch-123",
                "title": "OpenAI Releases GPT-5",
                "summary": "OpenAI announced the release of GPT-5...",
                "url": "https://techcrunch.com/...",
                "published_at": "2025-10-09T10:00:00Z",
                "source": "techcrunch",
                "category": "AI/ML",
                "score": 8.5,
                "image_url": "https://example.com/image.jpg",
            }
        }


class NewsListResponse(BaseModel):
    """Response schema for list of news articles."""

    total: int
    news: list[NewsResponse]
    fetched_at: datetime


class NewsSelectionRequest(BaseModel):
    """Request to select specific news articles."""

    news_ids: list[str] = Field(..., min_length=1, max_length=10)

    class Config:
        json_schema_extra = {"example": {"news_ids": ["techcrunch-123", "theverge-456"]}}
