"""
Centralized configuration for the Insider Threat Detection System.

All tunable values are read from environment variables (via .env) through
`src.utils.config`. Hardcoded literals no longer live here — override any
setting by editing .env or exporting a shell variable before running.
"""
from pathlib import Path
import sys
import logging

# ── Bootstrap: add project root to path ──────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# ── Load env-based settings ───────────────────────────────────────────────────
from src.utils.config import (
    # Data generation
    NUM_USERS,
    NUM_DAYS,
    ANOMALY_RATE,
    SEED,
    # Isolation Forest
    IF_N_ESTIMATORS,
    IF_CONTAMINATION,
    # One-Class SVM
    SVM_KERNEL,
    SVM_NU,
    SVM_GAMMA,
    # Autoencoder
    AE_MAX_ITER,
    AE_LEARNING_RATE,
    # Risk weights
    WEIGHT_IF_SCORE,
    WEIGHT_SVM_SCORE,
    WEIGHT_AE_SCORE,
    WEIGHT_SENSITIVE_TOTAL,
    WEIGHT_FAILED_TOTAL,
    # Risk thresholds
    RISK_CRIT_THRESHOLD,
    RISK_HIGH_THRESHOLD,
    RISK_MEDIUM_THRESHOLD,
    # Logging
    LOG_LEVEL_STR,
    LOG_TO_FILE,
)
from src.utils.logger import setup_logger

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_DIR      = BASE_DIR / "data"
RAW_DIR       = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODEL_DIR     = DATA_DIR / "models"
OUTPUT_DIR    = DATA_DIR / "output"

for _d in [RAW_DIR, PROCESSED_DIR, MODEL_DIR, OUTPUT_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

RAW_CSV      = RAW_DIR      / "employee_logs.csv"
FEATURES_CSV = PROCESSED_DIR / "features.csv"
SCORED_CSV   = OUTPUT_DIR   / "scored_users.csv"

# ── Role definitions ──────────────────────────────────────────────────────────
ROLES        = ["engineer", "analyst", "manager", "admin", "intern"]
ROLE_WEIGHTS = [0.35, 0.25, 0.15, 0.10, 0.15]

# ── Model parameter dicts ─────────────────────────────────────────────────────
IF_PARAMS = {
    "n_estimators":  IF_N_ESTIMATORS,
    "contamination": IF_CONTAMINATION,
    "random_state":  SEED,
}

SVM_PARAMS = {
    "kernel": SVM_KERNEL,
    "nu":     SVM_NU,
    "gamma":  SVM_GAMMA,
}

AE_PARAMS = {
    "hidden_layer_sizes": (32, 16, 8, 16, 32),
    "activation":         "relu",
    "max_iter":           AE_MAX_ITER,
    "random_state":       SEED,
    "learning_rate_init": AE_LEARNING_RATE,
}

# ── Risk scoring ──────────────────────────────────────────────────────────────
RISK_WEIGHTS = {
    "if_score":        WEIGHT_IF_SCORE,
    "svm_score":       WEIGHT_SVM_SCORE,
    "ae_score":        WEIGHT_AE_SCORE,
    "sensitive_total": WEIGHT_SENSITIVE_TOTAL,
    "failed_total":    WEIGHT_FAILED_TOTAL,
}

RISK_THRESHOLDS = {
    "critical": RISK_CRIT_THRESHOLD,
    "high":     RISK_HIGH_THRESHOLD,
    "medium":   RISK_MEDIUM_THRESHOLD,
}

# ── Logger ────────────────────────────────────────────────────────────────────
LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)
logger    = setup_logger("insider_threat", level=LOG_LEVEL, log_to_file=LOG_TO_FILE)
