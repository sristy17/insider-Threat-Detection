import os
import logging
from pathlib import Path
from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parents[2]
_ENV_FILE = _ROOT / ".env"
load_dotenv(dotenv_path=_ENV_FILE, override=False)


def _int(key: str, default: int) -> int:
    raw = os.getenv(key)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _float(key: str, default: float) -> float:
    raw = os.getenv(key)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _str(key: str, default: str) -> str:
    return os.getenv(key, default)


def _bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in ("true", "1", "yes")


NUM_USERS    = _int("NUM_USERS",    200)
NUM_DAYS     = _int("NUM_DAYS",     60)
ANOMALY_RATE = _float("ANOMALY_RATE", 0.04)
SEED         = _int("SEED",         42)

IF_N_ESTIMATORS  = _int("IF_N_ESTIMATORS",   200)
IF_CONTAMINATION = _float("IF_CONTAMINATION", 0.05)

SVM_KERNEL = _str("SVM_KERNEL", "rbf")
SVM_NU     = _float("SVM_NU",   0.05)
SVM_GAMMA  = _str("SVM_GAMMA",  "scale")

AE_MAX_ITER       = _int("AE_MAX_ITER",        500)
AE_LEARNING_RATE  = _float("AE_LEARNING_RATE", 0.001)

WEIGHT_IF_SCORE        = _float("WEIGHT_IF_SCORE",        0.30)
WEIGHT_SVM_SCORE       = _float("WEIGHT_SVM_SCORE",       0.25)
WEIGHT_AE_SCORE        = _float("WEIGHT_AE_SCORE",        0.15)
WEIGHT_SENSITIVE_TOTAL = _float("WEIGHT_SENSITIVE_TOTAL", 0.20)
WEIGHT_FAILED_TOTAL    = _float("WEIGHT_FAILED_TOTAL",    0.10)

RISK_CRIT_THRESHOLD   = _int("RISK_CRIT_THRESHOLD",   75)
RISK_HIGH_THRESHOLD   = _int("RISK_HIGH_THRESHOLD",   50)
RISK_MEDIUM_THRESHOLD = _int("RISK_MEDIUM_THRESHOLD", 25)

LOG_LEVEL_STR = _str("LOG_LEVEL", "INFO").upper()
LOG_TO_FILE   = _bool("LOG_TO_FILE", True)
