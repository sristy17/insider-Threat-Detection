"""
src/utils/config.py — Environment-based configuration loader.

Reads every tunable setting from environment variables (populated via .env).
All values have safe defaults so the project works out-of-the-box without a
.env file. Import constants from here rather than hardcoding them anywhere.

Usage
-----
    from src.utils.config import NUM_USERS, IF_N_ESTIMATORS, RISK_CRIT_THRESHOLD

Shell override (no code change needed):
    $env:NUM_USERS = "50"   # PowerShell
    NUM_USERS=50 python …   # bash/zsh
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (two levels up from this file: src/utils/ → root)
_ROOT = Path(__file__).resolve().parents[2]
_ENV_FILE = _ROOT / ".env"
load_dotenv(dotenv_path=_ENV_FILE, override=False)  # shell env takes priority


# ── Private typed helpers ─────────────────────────────────────────────────────

def _int(key: str, default: int) -> int:
    """Read an integer env var with a fallback default."""
    raw = os.getenv(key)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        logging.warning("Config: %s=%r is not a valid integer — using default %d", key, raw, default)
        return default


def _float(key: str, default: float) -> float:
    """Read a float env var with a fallback default."""
    raw = os.getenv(key)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        logging.warning("Config: %s=%r is not a valid float — using default %g", key, raw, default)
        return default


def _str(key: str, default: str) -> str:
    """Read a string env var with a fallback default."""
    return os.getenv(key, default)


def _bool(key: str, default: bool) -> bool:
    """Read a boolean env var (true/1/yes → True) with a fallback default."""
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in ("true", "1", "yes")


# ── Data generation ───────────────────────────────────────────────────────────

NUM_USERS    = _int("NUM_USERS",    200)
NUM_DAYS     = _int("NUM_DAYS",     60)
ANOMALY_RATE = _float("ANOMALY_RATE", 0.04)
SEED         = _int("SEED",         42)

# ── Isolation Forest ──────────────────────────────────────────────────────────

IF_N_ESTIMATORS  = _int("IF_N_ESTIMATORS",   200)
IF_CONTAMINATION = _float("IF_CONTAMINATION", 0.05)

# ── One-Class SVM ─────────────────────────────────────────────────────────────

SVM_KERNEL = _str("SVM_KERNEL", "rbf")
SVM_NU     = _float("SVM_NU",   0.05)
SVM_GAMMA  = _str("SVM_GAMMA",  "scale")

# ── Autoencoder (MLPRegressor) ────────────────────────────────────────────────

AE_MAX_ITER       = _int("AE_MAX_ITER",        500)
AE_LEARNING_RATE  = _float("AE_LEARNING_RATE", 0.001)

# ── Risk scoring weights ──────────────────────────────────────────────────────

WEIGHT_IF_SCORE        = _float("WEIGHT_IF_SCORE",        0.30)
WEIGHT_SVM_SCORE       = _float("WEIGHT_SVM_SCORE",       0.25)
WEIGHT_AE_SCORE        = _float("WEIGHT_AE_SCORE",        0.15)
WEIGHT_SENSITIVE_TOTAL = _float("WEIGHT_SENSITIVE_TOTAL", 0.20)
WEIGHT_FAILED_TOTAL    = _float("WEIGHT_FAILED_TOTAL",    0.10)

# ── Risk level thresholds (0–100 scale) ───────────────────────────────────────

RISK_CRIT_THRESHOLD   = _int("RISK_CRIT_THRESHOLD",   75)
RISK_HIGH_THRESHOLD   = _int("RISK_HIGH_THRESHOLD",   50)
RISK_MEDIUM_THRESHOLD = _int("RISK_MEDIUM_THRESHOLD", 25)

# ── Logging ───────────────────────────────────────────────────────────────────

LOG_LEVEL_STR = _str("LOG_LEVEL", "INFO").upper()
LOG_TO_FILE   = _bool("LOG_TO_FILE", True)
