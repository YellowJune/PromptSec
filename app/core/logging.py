"""Centralized logging configuration using Loguru."""

from loguru import logger
import sys


def setup_logging() -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )
    logger.add(
        "promptsec.log",
        rotation="10 MB",
        level="DEBUG",
        format="{time} {level} {message}",
    )


__all__ = ["logger", "setup_logging"]
