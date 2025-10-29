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


class ManualNewsRequest(BaseModel):
    """Request schema for manually creating news article."""

    title: str = Field(..., min_length=5, max_length=200, description="News title")
    summary: str = Field(..., min_length=20, max_length=1000, description="News summary")
    content: str | None = Field(None, max_length=5000, description="Full article content (optional)")
    image_url: str | None = Field(None, description="Image URL (optional)")
    category: str = Field(default="ai_ml", description="News category")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "OpenAI Releases Revolutionary GPT-5 Model",
                "summary": "OpenAI has announced the release of GPT-5, featuring breakthrough capabilities in reasoning and multimodal understanding. The new model demonstrates significant improvements over GPT-4.",
                "content": "Full article text here...",
                "image_url": "https://example.com/gpt5-image.jpg",
                "category": "ai_ml"
            }
        }
