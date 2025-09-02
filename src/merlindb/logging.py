"""Logging configuration for MerlinDB."""

import logging

from rich.logging import RichHandler


def setup_logging(
    level: int = logging.INFO,
    format: str | None = "%(message)s",
    datefmt: str | None = "[%X]",
    *handlers,
) -> None:
    """Set up logging with Rich handler."""
    logging.basicConfig(
        level=level,
        format=format,
        datefmt=datefmt,
        handlers=[RichHandler(rich_tracebacks=True), *handlers],
    )


def get_logger(name: str = "rich") -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name=name)


# Default logger for the module
log = get_logger("merlindb")
