import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

_BASE_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = _BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "insider_threat.log"

_FORMATTER = logging.Formatter(
    fmt="%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def setup_logger(
    name: str = "insider_threat",
    level: int = logging.INFO,
    log_to_file: bool = True,
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(_FORMATTER)
    logger.addHandler(console_handler)

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
        except OSError:
            pass

    logger.propagate = False
    return logger


def get_logger(name: str = "insider_threat") -> logging.Logger:
    existing = logging.getLogger(name)
    if not existing.handlers:
        return setup_logger(name)
    return existing


logger = setup_logger()
