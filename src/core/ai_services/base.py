"""
Base AI service for Tech News Digest.

Provides abstract base class for all AI services with:
- OpenAI client management
- Rate limiting
- Retry logic
- Cost tracking
- Caching
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional

from openai import OpenAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.core.config import get_settings
from src.core.logging import get_logger, log_execution_time

settings = get_settings()
logger = get_logger(__name__)


class AIServiceError(Exception):
    """Base exception for AI services."""

    pass


class RateLimitError(AIServiceError):
    """Rate limit exceeded."""

    pass


class GenerationError(AIServiceError):
    """Content generation failed."""

    pass


class BaseAIService(ABC):
    """
    Abstract base class for AI services.

    Provides common functionality for:
    - OpenAI client management
    - Retry logic
    - Rate limiting
    - Cost tracking
    - Caching
    """

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        enable_cache: bool = True,
    ):
        """
        Initialize AI service.

        Args:
            cache_dir: Directory for caching generated content
            enable_cache: Enable caching
        """
        self.logger = get_logger(self.__class__.__name__)
        self.settings = get_settings()

        # OpenAI client
        self.client = OpenAI(api_key=self.settings.openai.api_key)

        # Cache settings
        self.cache_dir = cache_dir or Path("output/cache")
        self.enable_cache = enable_cache and self.settings.cache_enabled
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Cost tracking
        self.total_cost = 0.0
        self.request_count = 0

        self.logger.info(
            f"{self.__class__.__name__} initialized "
            f"(cache={self.enable_cache}, dir={self.cache_dir})"
        )

    @abstractmethod
    def generate(self, *args, **kwargs) -> Any:
        """
        Generate content using AI service.

        This method must be implemented by subclasses.

        Returns:
            Generated content (specific to service)
        """
        pass

    @retry(
        retry=retry_if_exception_type((RateLimitError, GenerationError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=60),
    )
    def _call_api_with_retry(self, api_func, *args, **kwargs) -> Any:
        """
        Call API with retry logic.

        Args:
            api_func: API function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            API response

        Raises:
            RateLimitError: If rate limit is exceeded
            GenerationError: If generation fails
        """
        try:
            self.logger.debug(f"Calling API: {api_func.__name__}")
            response = api_func(*args, **kwargs)
            self.request_count += 1
            return response

        except Exception as e:
            error_msg = str(e).lower()

            # Rate limit errors
            if "rate_limit" in error_msg or "429" in error_msg:
                self.logger.warning(
                    f"Rate limit exceeded: {e}", extra={"attempt": self.request_count}
                )
                raise RateLimitError(f"Rate limit exceeded: {e}") from e

            # Generation errors
            if "content_policy" in error_msg or "invalid_request" in error_msg:
                self.logger.error(f"Generation failed: {e}")
                raise GenerationError(f"Generation failed: {e}") from e

            # Unknown errors
            self.logger.error(f"API call failed: {e}", exc_info=True)
            raise GenerationError(f"API call failed: {e}") from e

    def _get_cache_path(self, key: str, extension: str = "json") -> Path:
        """
        Get cache file path for given key.

        Args:
            key: Cache key (will be hashed)
            extension: File extension

        Returns:
            Cache file path
        """
        import hashlib

        # Hash the key to create filename
        hash_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hash_key}.{extension}"

    def _load_from_cache(self, key: str, extension: str = "json") -> Optional[Any]:
        """
        Load content from cache.

        Args:
            key: Cache key
            extension: File extension

        Returns:
            Cached content or None
        """
        if not self.enable_cache:
            return None

        cache_path = self._get_cache_path(key, extension)

        if not cache_path.exists():
            self.logger.debug(f"Cache miss: {key[:50]}...")
            return None

        try:
            # Check cache TTL
            import time

            cache_age = time.time() - cache_path.stat().st_mtime
            max_age = getattr(self.settings, "cache_ttl_news", 3600)  # 1 hour default

            if cache_age > max_age:
                self.logger.debug(f"Cache expired: {key[:50]}... (age={cache_age:.0f}s)")
                cache_path.unlink()
                return None

            # Load from cache
            if extension == "json":
                import json

                with open(cache_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.logger.info(f"Cache hit: {key[:50]}...")
                    return data
            else:
                # Binary file
                self.logger.info(f"Cache hit: {cache_path.name}")
                return cache_path

        except Exception as e:
            self.logger.warning(f"Cache load failed: {e}")
            return None

    def _save_to_cache(
        self, key: str, content: Any, extension: str = "json"
    ) -> Path:
        """
        Save content to cache.

        Args:
            key: Cache key
            content: Content to cache
            extension: File extension

        Returns:
            Cache file path
        """
        if not self.enable_cache:
            return None

        cache_path = self._get_cache_path(key, extension)

        try:
            if extension == "json":
                import json

                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(content, f, ensure_ascii=False, indent=2)
            else:
                # Assume content is bytes
                with open(cache_path, "wb") as f:
                    f.write(content)

            self.logger.debug(f"Saved to cache: {cache_path.name}")
            return cache_path

        except Exception as e:
            self.logger.warning(f"Cache save failed: {e}")
            return None

    def get_stats(self) -> dict[str, Any]:
        """
        Get service statistics.

        Returns:
            Statistics dictionary
        """
        return {
            "service": self.__class__.__name__,
            "total_cost": round(self.total_cost, 4),
            "request_count": self.request_count,
            "cache_enabled": self.enable_cache,
            "cache_dir": str(self.cache_dir),
        }

    def reset_stats(self) -> None:
        """Reset statistics."""
        self.total_cost = 0.0
        self.request_count = 0
        self.logger.info("Statistics reset")

    def clear_cache(self) -> int:
        """
        Clear all cached files.

        Returns:
            Number of files deleted
        """
        if not self.cache_dir.exists():
            return 0

        count = 0
        for file in self.cache_dir.glob("*"):
            if file.is_file():
                file.unlink()
                count += 1

        self.logger.info(f"Cleared {count} cached files")
        return count
