"""
Main pipeline — feature engineering → model training → risk scoring.
Saves trained models and scored output so the dashboard loads instantly.
"""
import pandas as pd
from config import FEATURES_CSV, SCORED_CSV, logger

from src.preprocessing.feature_engineering import build_features
from src.models.isolation_forest import train as train_if
from src.models.one_class_svm import train as train_svm
from src.models.autoencoder import train as train_ae, reconstruction_error
from src.scoring.risk_score import compute, normalise_scores, classify_risk


def run():
    logger.info("═══ Pipeline start ═══")

    # 1. Feature engineering
    build_features()
    df = pd.read_csv(FEATURES_CSV)
    feature_cols = [c for c in df.columns if c not in ("user_id", "role")]
    X = df[feature_cols]

    # 2. Train models
    if_model  = train_if(X)
    svm_model = train_svm(X)
    ae_model  = train_ae(X)

    # 3. Compute raw anomaly scores
    df["if_score"]  = -if_model.decision_function(X)
    df["svm_score"] = -svm_model.decision_function(X)
    df["ae_score"]  = reconstruction_error(ae_model, X)

    # 4. Risk scoring
    df["risk_score_raw"] = df.apply(compute, axis=1)
    df["risk_score"]     = normalise_scores(df["risk_score_raw"])
    df["risk_level"]     = df["risk_score"].apply(classify_risk)

    # 5. Sort & save
    df = df.sort_values("risk_score", ascending=False).reset_index(drop=True)
    df.to_csv(SCORED_CSV, index=False)
    logger.info(f"Scored data saved → {SCORED_CSV}")
    logger.info(f"Risk distribution: {df['risk_level'].value_counts().to_dict()}")
    logger.info("═══ Pipeline complete ═══")

    return df


if __name__ == "__main__":
    out = run()
    print("\nTop 10 risky users:")
    print(out[["user_id", "role", "risk_score", "risk_level"]].head(10).to_string(index=False))
