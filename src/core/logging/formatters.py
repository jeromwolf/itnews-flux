"""
Log formatters for Tech News Digest.

Provides JSON and text formatters for structured and human-readable logging.
"""

import json
import logging
import traceback
from datetime import datetime
from typing import Any


class TextFormatter(logging.Formatter):
    """
    Human-readable text formatter with colors for console output.

    Format: [timestamp] LEVEL [module:function:line] message
    """

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }

    def __init__(self, use_colors: bool = True):
        """
        Initialize text formatter.

        Args:
            use_colors: Enable colored output (disable for file logging)
        """
        super().__init__(
            fmt="[%(asctime)s] %(levelname)-8s [%(name)s:%(funcName)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with optional colors."""
        # Add color to level name if enabled
        if self.use_colors and record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
            )

        # Format the base message
        formatted = super().format(record)

        # Add extra context if available
        if hasattr(record, "extra_context"):
            context_str = " | ".join(
                f"{k}={v}" for k, v in record.extra_context.items()
            )
            formatted += f" | {context_str}"

        return formatted


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.

    Outputs logs in JSON format for easy parsing by log aggregation tools.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: dict[str, Any] = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        # Add process and thread info
        log_data["process"] = {
            "id": record.process,
            "name": record.processName,
        }
        log_data["thread"] = {
            "id": record.thread,
            "name": record.threadName,
        }

        # Add exception info if available
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add custom fields from extra parameter
        if hasattr(record, "extra_context"):
            log_data["context"] = record.extra_context

        # Add any other extra attributes
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
                "extra_context",
            ]:
                log_data[key] = value

        return json.dumps(log_data, default=str, ensure_ascii=False)


class CompactJSONFormatter(JSONFormatter):
    """Compact JSON formatter without indentation (for production)."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as compact JSON."""
        formatted = super().format(record)
        # Already compact, just return
        return formatted


class PrettyJSONFormatter(JSONFormatter):
    """Pretty-printed JSON formatter (for development)."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as pretty-printed JSON."""
        log_data = json.loads(super().format(record))
        return json.dumps(log_data, indent=2, default=str, ensure_ascii=False)
