"""
Core logging module for Tech News Digest.

Provides a comprehensive logging system with:
- Structured logging (JSON and text formats)
- Sensitive data filtering
- Rate limiting
- Contextual logging
- Rotating file handlers

Usage:
    Basic logging:
        >>> from src.core.logging import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing started")
        >>> logger.error("An error occurred", exc_info=True)

    With decorators:
        >>> from src.core.logging import get_logger, log_execution_time
        >>> logger = get_logger(__name__)
        >>>
        >>> @log_execution_time(logger)
        >>> def process_data():
        >>>     # function code
        >>>     pass

    Custom formatters and filters:
        >>> from src.core.logging import get_logger
        >>> from src.core.logging.filters import ContextFilter
        >>>
        >>> logger = get_logger(__name__)
        >>> logger.addFilter(ContextFilter(request_id="12345"))
        >>> logger.info("Processing request")  # Will include request_id in context
"""

from .filters import (
    ContextFilter,
    LevelFilter,
    ModuleFilter,
    RateLimitFilter,
    SensitiveDataFilter,
)
from .formatters import (
    CompactJSONFormatter,
    JSONFormatter,
    PrettyJSONFormatter,
    TextFormatter,
)
from .logger import (
    LoggerManager,
    get_logger,
    log_execution_time,
    log_function_call,
    shutdown_logging,
)

__all__ = [
    # Main logger functions
    "get_logger",
    "shutdown_logging",
    "LoggerManager",
    # Decorators
    "log_execution_time",
    "log_function_call",
    # Formatters
    "TextFormatter",
    "JSONFormatter",
    "CompactJSONFormatter",
    "PrettyJSONFormatter",
    # Filters
    "SensitiveDataFilter",
    "LevelFilter",
    "ModuleFilter",
    "RateLimitFilter",
    "ContextFilter",
]
