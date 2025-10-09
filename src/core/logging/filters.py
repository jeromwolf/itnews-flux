"""
Log filters for Tech News Digest.

Provides filters to sanitize sensitive data and control log output.
"""

import logging
import re
from typing import Pattern


class SensitiveDataFilter(logging.Filter):
    """
    Filter to redact sensitive information from logs.

    Automatically redacts:
    - API keys
    - Passwords
    - Tokens
    - Secret keys
    - Email addresses (optional)
    """

    # Patterns for sensitive data
    PATTERNS: list[tuple[Pattern, str]] = [
        # API Keys
        (re.compile(r"(sk-[a-zA-Z0-9]{32,})", re.IGNORECASE), "sk-***REDACTED***"),
        (re.compile(r"(AIza[a-zA-Z0-9_-]{35})", re.IGNORECASE), "AIza***REDACTED***"),
        (re.compile(r"(AKIA[A-Z0-9]{16})", re.IGNORECASE), "AKIA***REDACTED***"),
        # Passwords
        (
            re.compile(r'(?:password|passwd|pwd)["\']?\s*[:=]\s*["\']?([^"\'\s]+)', re.IGNORECASE),
            "password=***REDACTED***",
        ),
        # Tokens
        (
            re.compile(r'(?:token|auth)["\']?\s*[:=]\s*["\']?([^"\'\s]+)', re.IGNORECASE),
            "token=***REDACTED***",
        ),
        # Secret keys
        (
            re.compile(r'(?:secret|api_key)["\']?\s*[:=]\s*["\']?([^"\'\s]+)', re.IGNORECASE),
            "secret=***REDACTED***",
        ),
        # Email addresses (optional, uncomment if needed)
        # (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '***@***.***'),
        # Credit card numbers
        (re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"), "****-****-****-****"),
        # Bearer tokens
        (re.compile(r"Bearer\s+([a-zA-Z0-9_-]+)", re.IGNORECASE), "Bearer ***REDACTED***"),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter and sanitize log record.

        Args:
            record: Log record to filter

        Returns:
            True to keep the record, False to discard
        """
        # Sanitize the message
        if isinstance(record.msg, str):
            record.msg = self._sanitize(record.msg)

        # Sanitize args if present
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: self._sanitize(str(v)) for k, v in record.args.items()}
            elif isinstance(record.args, (list, tuple)):
                record.args = tuple(self._sanitize(str(arg)) for arg in record.args)

        # Sanitize extra context
        if hasattr(record, "extra_context"):
            record.extra_context = {
                k: self._sanitize(str(v)) for k, v in record.extra_context.items()
            }

        return True

    def _sanitize(self, text: str) -> str:
        """
        Remove sensitive information from text.

        Args:
            text: Text to sanitize

        Returns:
            Sanitized text
        """
        for pattern, replacement in self.PATTERNS:
            text = pattern.sub(replacement, text)
        return text


class LevelFilter(logging.Filter):
    """
    Filter logs by level range.

    Example:
        # Only log INFO and WARNING
        filter = LevelFilter(min_level=logging.INFO, max_level=logging.WARNING)
    """

    def __init__(
        self,
        min_level: int = logging.NOTSET,
        max_level: int = logging.CRITICAL,
    ):
        """
        Initialize level filter.

        Args:
            min_level: Minimum log level to accept
            max_level: Maximum log level to accept
        """
        super().__init__()
        self.min_level = min_level
        self.max_level = max_level

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter by level range."""
        return self.min_level <= record.levelno <= self.max_level


class ModuleFilter(logging.Filter):
    """
    Filter logs by module name.

    Example:
        # Only log from news module
        filter = ModuleFilter(include_modules=['src.news'])
    """

    def __init__(
        self,
        include_modules: list[str] | None = None,
        exclude_modules: list[str] | None = None,
    ):
        """
        Initialize module filter.

        Args:
            include_modules: List of module prefixes to include
            exclude_modules: List of module prefixes to exclude
        """
        super().__init__()
        self.include_modules = include_modules or []
        self.exclude_modules = exclude_modules or []

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter by module name."""
        # Check exclusions first
        for module in self.exclude_modules:
            if record.name.startswith(module):
                return False

        # If include list is empty, include all (except excluded)
        if not self.include_modules:
            return True

        # Check inclusions
        for module in self.include_modules:
            if record.name.startswith(module):
                return True

        return False


class RateLimitFilter(logging.Filter):
    """
    Rate limit logs to prevent flooding.

    Example:
        # Max 10 logs per second for this logger
        filter = RateLimitFilter(max_rate=10, interval=1.0)
    """

    def __init__(self, max_rate: int = 100, interval: float = 1.0):
        """
        Initialize rate limit filter.

        Args:
            max_rate: Maximum number of logs per interval
            interval: Time interval in seconds
        """
        super().__init__()
        self.max_rate = max_rate
        self.interval = interval
        self._log_count = 0
        self._last_reset = None

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter by rate limit."""
        import time

        current_time = time.time()

        # Reset counter if interval has passed
        if self._last_reset is None or (current_time - self._last_reset) >= self.interval:
            self._log_count = 0
            self._last_reset = current_time

        # Check rate limit
        if self._log_count >= self.max_rate:
            return False

        self._log_count += 1
        return True


class ContextFilter(logging.Filter):
    """
    Add contextual information to log records.

    Example:
        # Add request ID to all logs
        filter = ContextFilter(request_id="12345")
    """

    def __init__(self, **context):
        """
        Initialize context filter.

        Args:
            **context: Key-value pairs to add to log records
        """
        super().__init__()
        self.context = context

    def filter(self, record: logging.LogRecord) -> bool:
        """Add context to log record."""
        if not hasattr(record, "extra_context"):
            record.extra_context = {}

        record.extra_context.update(self.context)
        return True
