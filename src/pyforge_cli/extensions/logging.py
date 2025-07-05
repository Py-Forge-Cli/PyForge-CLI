"""Logging configuration for PyForge CLI extension system.

This module provides centralized logging configuration for all extension-related
operations including discovery, loading, and lifecycle management.
"""

import logging
import sys
from typing import Optional

# Create dedicated logger for extensions
EXTENSION_LOGGER_NAME = "pyforge_cli.extensions"


def setup_extension_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    console_output: bool = True,
) -> logging.Logger:
    """Setup logging for the extension system.

    Args:
        level: Logging level (default: INFO)
        log_file: Optional file path to write logs to
        console_output: Whether to output to console (default: True)

    Returns:
        logging.Logger: Configured logger for extensions
    """
    logger = logging.getLogger(EXTENSION_LOGGER_NAME)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Add console handler if requested
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add file handler if requested
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_extension_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger for extension-related operations.

    Args:
        name: Optional sub-logger name (e.g., 'discovery', 'loader')

    Returns:
        logging.Logger: Logger instance
    """
    if name:
        return logging.getLogger(f"{EXTENSION_LOGGER_NAME}.{name}")
    return logging.getLogger(EXTENSION_LOGGER_NAME)


class ExtensionLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that adds extension context to log messages."""

    def __init__(self, logger: logging.Logger, extension_name: str):
        """Initialize the adapter.

        Args:
            logger: Base logger
            extension_name: Name of the extension
        """
        super().__init__(logger, {"extension": extension_name})

    def process(self, msg, kwargs):
        """Process log message to include extension context."""
        return f"[{self.extra['extension']}] {msg}", kwargs


def configure_verbose_logging() -> None:
    """Configure verbose logging for debugging purposes."""
    setup_extension_logging(level=logging.DEBUG)

    # Also enable debug logging for specific components
    for component in ["discovery", "loader", "registry", "manager"]:
        component_logger = get_extension_logger(component)
        component_logger.setLevel(logging.DEBUG)
