"""
Risk scoring engine.
Combines three model scores + behavioral signals into a 0–100 risk score
and assigns categorical risk levels.
"""
import numpy as np
from config import RISK_WEIGHTS, RISK_THRESHOLDS


def compute(row):
    """Compute weighted risk score from model outputs and behavioural features."""
    raw = (
        RISK_WEIGHTS["if_score"]        * row.get("if_score", 0) +
        RISK_WEIGHTS["svm_score"]       * row.get("svm_score", 0) +
        RISK_WEIGHTS["ae_score"]        * row.get("ae_score", 0) +
        RISK_WEIGHTS["sensitive_total"] * row.get("sensitive_total", 0) +
        RISK_WEIGHTS["failed_total"]    * row.get("failed_total", 0)
    )
    return raw


def normalise_scores(series):
    """Min-max normalise a pandas Series to 0–100 scale."""
    mn, mx = series.min(), series.max()
    if mx == mn:
        return series * 0
    return ((series - mn) / (mx - mn)) * 100


def classify_risk(score):
    """Return risk level string based on thresholds."""
    if score >= RISK_THRESHOLDS["critical"]:
        return "Critical"
    elif score >= RISK_THRESHOLDS["high"]:
        return "High"
    elif score >= RISK_THRESHOLDS["medium"]:
        return "Medium"
    return "Low"


def risk_breakdown(row):
    """Return dict with per-factor contribution percentages."""
    total = abs(row.get("risk_score", 1)) or 1
    return {
        "Isolation Forest": round(RISK_WEIGHTS["if_score"] * row.get("if_score", 0) / total * 100, 1),
        "One-Class SVM":    round(RISK_WEIGHTS["svm_score"] * row.get("svm_score", 0) / total * 100, 1),
        "Autoencoder":      round(RISK_WEIGHTS["ae_score"] * row.get("ae_score", 0) / total * 100, 1),
        "Sensitive Files":  round(RISK_WEIGHTS["sensitive_total"] * row.get("sensitive_total", 0) / total * 100, 1),
        "Failed Logins":    round(RISK_WEIGHTS["failed_total"] * row.get("failed_total", 0) / total * 100, 1),
    }
