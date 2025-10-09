"""
Core logging system for Tech News Digest.

This module provides a centralized logging configuration with support for:
- Multiple output formats (JSON, text)
- File and console handlers
- Rotating file logs
- Contextual logging
- Environment-specific log levels
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from .formatters import JSONFormatter, TextFormatter
from .filters import SensitiveDataFilter


class LoggerManager:
    """Centralized logger management system."""

    _instance: Optional["LoggerManager"] = None
    _loggers: dict[str, logging.Logger] = {}

    def __new__(cls) -> "LoggerManager":
        """Singleton pattern to ensure single logger manager instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize logger manager."""
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._setup_root_logger()

    def _setup_root_logger(self) -> None:
        """Setup root logger with default configuration."""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)  # Capture all levels, filter in handlers

        # Remove existing handlers to avoid duplicates
        root_logger.handlers.clear()

    def get_logger(
        self,
        name: str,
        log_level: str = "INFO",
        log_file: Optional[Path] = None,
        log_format: str = "text",
        enable_console: bool = True,
        enable_file: bool = True,
    ) -> logging.Logger:
        """
        Get or create a configured logger.

        Args:
            name: Logger name (typically __name__)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Path to log file (default: logs/{name}.log)
            log_format: Output format ('json' or 'text')
            enable_console: Enable console output
            enable_file: Enable file output

        Returns:
            Configured logger instance

        Example:
            >>> logger = LoggerManager().get_logger(__name__)
            >>> logger.info("Application started")
        """
        # Return existing logger if already configured
        if name in self._loggers:
            return self._loggers[name]

        # Create new logger
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, log_level.upper()))
        logger.propagate = False  # Don't propagate to root logger

        # Add sensitive data filter
        logger.addFilter(SensitiveDataFilter())

        # Setup formatter
        if log_format.lower() == "json":
            formatter = JSONFormatter()
        else:
            formatter = TextFormatter()

        # Console handler
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, log_level.upper()))
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        # File handler with rotation
        if enable_file:
            if log_file is None:
                log_file = Path("logs") / f"{name.replace('.', '_')}.log"

            # Ensure log directory exists
            log_file.parent.mkdir(parents=True, exist_ok=True)

            # Rotating file handler (10MB per file, keep 5 backups)
            file_handler = logging.handlers.RotatingFileHandler(
                filename=log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setLevel(logging.DEBUG)  # Log everything to file
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        # Cache logger
        self._loggers[name] = logger

        return logger

    def shutdown(self) -> None:
        """Shutdown all loggers and handlers gracefully."""
        for logger in self._loggers.values():
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)

        self._loggers.clear()
        logging.shutdown()


# Global logger manager instance
_manager = LoggerManager()


def get_logger(
    name: str,
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None,
    log_format: Optional[str] = None,
    enable_console: bool = True,
    enable_file: bool = True,
) -> logging.Logger:
    """
    Convenience function to get a logger.

    This is the recommended way to get a logger in the application.

    Args:
        name: Logger name (use __name__)
        log_level: Logging level (defaults to env var or INFO)
        log_file: Custom log file path
        log_format: Output format ('json' or 'text')
        enable_console: Enable console output
        enable_file: Enable file output

    Returns:
        Configured logger instance

    Example:
        >>> from src.core.logging import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing started")
        >>> logger.error("An error occurred", exc_info=True)
    """
    # Get defaults from environment if not specified
    import os

    if log_level is None:
        log_level = os.getenv("APP_LOG_LEVEL", "INFO")

    if log_format is None:
        log_format = os.getenv("LOG_FORMAT", "text")

    return _manager.get_logger(
        name=name,
        log_level=log_level,
        log_file=log_file,
        log_format=log_format,
        enable_console=enable_console,
        enable_file=enable_file,
    )


def shutdown_logging() -> None:
    """Shutdown all logging gracefully."""
    _manager.shutdown()


# Convenience functions for common logging patterns
def log_function_call(logger: logging.Logger):
    """
    Decorator to log function calls.

    Example:
        >>> @log_function_call(logger)
        >>> def process_news(news_id: str):
        >>>     pass
    """
    import functools

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(
                f"Calling {func.__name__}",
                extra={
                    "function": func.__name__,
                    "args": args,
                    "kwargs": kwargs,
                },
            )
            try:
                result = func(*args, **kwargs)
                logger.debug(
                    f"Completed {func.__name__}",
                    extra={"function": func.__name__, "result": result},
                )
                return result
            except Exception as e:
                logger.error(
                    f"Error in {func.__name__}: {str(e)}",
                    exc_info=True,
                    extra={"function": func.__name__},
                )
                raise

        return wrapper

    return decorator


def log_execution_time(logger: logging.Logger):
    """
    Decorator to log function execution time.

    Example:
        >>> @log_execution_time(logger)
        >>> def slow_function():
        >>>     time.sleep(2)
    """
    import functools
    import time

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.info(
                    f"{func.__name__} completed in {elapsed:.2f}s",
                    extra={
                        "function": func.__name__,
                        "execution_time": elapsed,
                    },
                )
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    f"{func.__name__} failed after {elapsed:.2f}s: {str(e)}",
                    exc_info=True,
                    extra={
                        "function": func.__name__,
                        "execution_time": elapsed,
                    },
                )
                raise

        return wrapper

    return decorator
