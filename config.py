"""
Centralized configuration for the Insider Threat Detection System.
All paths, model parameters, and thresholds are defined here.
"""
from pathlib import Path
import logging

# ──────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODEL_DIR = DATA_DIR / "models"
OUTPUT_DIR = DATA_DIR / "output"

for d in [RAW_DIR, PROCESSED_DIR, MODEL_DIR, OUTPUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

RAW_CSV = RAW_DIR / "employee_logs.csv"
FEATURES_CSV = PROCESSED_DIR / "features.csv"
SCORED_CSV = OUTPUT_DIR / "scored_users.csv"

# ──────────────────────────────────────────────
# Data Generation
# ──────────────────────────────────────────────
NUM_USERS = 200
NUM_DAYS = 60
ANOMALY_RATE = 0.04
SEED = 42

ROLES = ["engineer", "analyst", "manager", "admin", "intern"]
ROLE_WEIGHTS = [0.35, 0.25, 0.15, 0.10, 0.15]

# ──────────────────────────────────────────────
# Model Parameters
# ──────────────────────────────────────────────
IF_PARAMS = {
    "n_estimators": 200,
    "contamination": 0.05,
    "random_state": SEED,
}

SVM_PARAMS = {
    "kernel": "rbf",
    "nu": 0.05,
    "gamma": "scale",
}

# Autoencoder (MLPRegressor-based)
AE_PARAMS = {
    "hidden_layer_sizes": (32, 16, 8, 16, 32),
    "activation": "relu",
    "max_iter": 500,
    "random_state": SEED,
    "learning_rate_init": 0.001,
}

# ──────────────────────────────────────────────
# Risk Scoring
# ──────────────────────────────────────────────
RISK_WEIGHTS = {
    "if_score": 0.30,
    "svm_score": 0.25,
    "ae_score": 0.15,
    "sensitive_total": 0.20,
    "failed_total": 0.10,
}

RISK_THRESHOLDS = {
    "critical": 75,
    "high": 50,
    "medium": 25,
}

# ──────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────
LOG_FORMAT = "%(asctime)s │ %(levelname)-8s │ %(message)s"
LOG_LEVEL = logging.INFO

logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)
logger = logging.getLogger("insider_threat")
