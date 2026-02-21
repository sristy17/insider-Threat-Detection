"""
Main pipeline — feature engineering → model training → risk scoring.
Saves trained models and scored output so the dashboard loads instantly.
"""
import sys
import traceback
import pandas as pd
from config import FEATURES_CSV, SCORED_CSV, logger

from src.preprocessing.feature_engineering import build_features
from src.models.isolation_forest import train as train_if
from src.models.one_class_svm import train as train_svm
from src.models.autoencoder import train as train_ae, reconstruction_error
from src.scoring.risk_score import compute, normalise_scores, classify_risk


def run():
    logger.info("═══ Pipeline start ═══")

    # ── Step 1: Feature engineering ──────────────────────────────────────────
    logger.info("[1/5] Building features from raw employee logs …")
    try:
        build_features()
    except Exception:
        logger.error("[1/5] Feature engineering failed:\n%s", traceback.format_exc())
        raise

    df = pd.read_csv(FEATURES_CSV)
    feature_cols = [c for c in df.columns if c not in ("user_id", "role")]
    X = df[feature_cols]
    logger.info("[1/5] Feature matrix ready: %d users × %d features", len(X), len(feature_cols))

    # ── Step 2: Train models ──────────────────────────────────────────────────
    logger.info("[2/5] Training Isolation Forest …")
    try:
        if_model = train_if(X)
    except Exception:
        logger.error("[2/5] Isolation Forest training failed:\n%s", traceback.format_exc())
        raise

    logger.info("[3/5] Training One-Class SVM …")
    try:
        svm_model = train_svm(X)
    except Exception:
        logger.error("[3/5] One-Class SVM training failed:\n%s", traceback.format_exc())
        raise

    logger.info("[4/5] Training Autoencoder (MLPRegressor) …")
    try:
        ae_model = train_ae(X)
    except Exception:
        logger.error("[4/5] Autoencoder training failed:\n%s", traceback.format_exc())
        raise

    # ── Step 3: Compute raw anomaly scores ───────────────────────────────────
    logger.info("[5/5] Computing anomaly & risk scores …")
    df["if_score"]  = -if_model.decision_function(X)
    df["svm_score"] = -svm_model.decision_function(X)
    df["ae_score"]  = reconstruction_error(ae_model, X)
    logger.info(
        "Raw score stats — IF: mean=%.4f  SVM: mean=%.4f  AE: mean=%.4f",
        df["if_score"].mean(),
        df["svm_score"].mean(),
        df["ae_score"].mean(),
    )

    # ── Step 4: Risk scoring ──────────────────────────────────────────────────
    df["risk_score_raw"] = df.apply(compute, axis=1)
    df["risk_score"]     = normalise_scores(df["risk_score_raw"])
    df["risk_level"]     = df["risk_score"].apply(classify_risk)

    # ── Step 5: Sort & save ───────────────────────────────────────────────────
    df = df.sort_values("risk_score", ascending=False).reset_index(drop=True)
    df.to_csv(SCORED_CSV, index=False)
    logger.info("Scored data saved → %s", SCORED_CSV)

    risk_dist = df["risk_level"].value_counts().to_dict()
    logger.info("Risk distribution: %s", risk_dist)

    critical_count = risk_dist.get("Critical", 0)
    if critical_count > 0:
        logger.warning(
            "%d CRITICAL-risk user(s) detected — immediate SOC review recommended.",
            critical_count,
        )

    logger.info("═══ Pipeline complete ═══")
    return df


if __name__ == "__main__":
    try:
        out = run()
        logger.info("Top 10 risky users:\n%s",
                    out[["user_id", "role", "risk_score", "risk_level"]].head(10).to_string(index=False))
    except Exception:
        logger.error("Pipeline terminated with an unhandled exception:\n%s", traceback.format_exc())
        sys.exit(1)
