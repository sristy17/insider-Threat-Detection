from pathlib import Path
import sys
import logging

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from src.utils.config import (
    NUM_USERS,
    NUM_DAYS,
    ANOMALY_RATE,
    SEED,
    IF_N_ESTIMATORS,
    IF_CONTAMINATION,
    SVM_KERNEL,
    SVM_NU,
    SVM_GAMMA,
    AE_MAX_ITER,
    AE_LEARNING_RATE,
    WEIGHT_IF_SCORE,
    WEIGHT_SVM_SCORE,
    WEIGHT_AE_SCORE,
    WEIGHT_SENSITIVE_TOTAL,
    WEIGHT_FAILED_TOTAL,
    RISK_CRIT_THRESHOLD,
    RISK_HIGH_THRESHOLD,
    RISK_MEDIUM_THRESHOLD,
    LOG_LEVEL_STR,
    LOG_TO_FILE,
)
from src.utils.logger import setup_logger

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

ROLES        = ["engineer", "analyst", "manager", "admin", "intern"]
ROLE_WEIGHTS = [0.35, 0.25, 0.15, 0.10, 0.15]

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

LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)
logger    = setup_logger("insider_threat", level=LOG_LEVEL, log_to_file=LOG_TO_FILE)
