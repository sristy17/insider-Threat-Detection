"""
Centralized logging configuration for the Insider Threat Detection System.
Provides structured logging with timestamps, log levels, and consistent
formatting to both console and optional rotating file handler.
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Default log directory (project-root/logs/)
_BASE_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = _BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "insider_threat.log"

# Shared formatter — used by every handler in this project
_FORMATTER = logging.Formatter(
    fmt="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def setup_logger(
    name: str = "insider_threat",
    level: int = logging.INFO,
    log_to_file: bool = True,
    max_bytes: int = 5 * 1024 * 1024,   # 5 MB per log file
    backup_count: int = 3,
) -> logging.Logger:
    """
    Set up and return a configured logger instance.

    The logger writes to:
    - **stdout** (console) at the requested level
    - **logs/insider_threat.log** with rotating file handler (optional)

    Args:
        name:         Logger name (default: ``"insider_threat"``).
        level:        Minimum log level (default: ``logging.INFO``).
        log_to_file:  Whether to attach a rotating file handler (default: True).
        max_bytes:    Max size of a single log file before rotation (default 5 MB).
        backup_count: Number of rotated backup files to keep (default 3).

    Returns:
        logging.Logger: Fully configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers if already configured
    if logger.handlers:
        return logger

    # ── Console handler (stdout) ─────────────────────────────────────────────
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(_FORMATTER)
    logger.addHandler(console_handler)

    # ── Rotating file handler ────────────────────────────────────────────────
    if log_to_file:
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(
                LOG_FILE,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8",
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(_FORMATTER)
            logger.addHandler(file_handler)
        except OSError as exc:
            # If we cannot write logs to disk, warn on console and continue
            logger.warning("Could not create file log handler: %s", exc)

    # Prevent log records from propagating to the root logger
    logger.propagate = False

    return logger


def get_logger(name: str = "insider_threat") -> logging.Logger:
    """
    Retrieve an existing named logger (or the default one).

    Use this in sub-modules to get the already-configured logger without
    re-running setup. If the logger hasn't been set up yet it will be
    initialised with default settings.

    Args:
        name: Logger name to retrieve (default: ``"insider_threat"``).

    Returns:
        logging.Logger: Logger instance.
    """
    existing = logging.getLogger(name)
    if not existing.handlers:
        return setup_logger(name)
    return existing


# ── Module-level default logger ──────────────────────────────────────────────
# Imported by config.py and re-exported for the rest of the project.
logger = setup_logger()
