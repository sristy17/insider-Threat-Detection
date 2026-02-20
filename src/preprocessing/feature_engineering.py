"""
Advanced feature engineering with behavioral ratios,
temporal features, and per-user aggregation.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from config import RAW_CSV, FEATURES_CSV, logger


def build_features():
    df = pd.read_csv(RAW_CSV)

    # ── Per-user aggregations ────────────────────────────
    agg = df.groupby("user_id").agg(
        login_mean=("login_hour", "mean"),
        login_std=("login_hour", "std"),
        files_mean=("files_accessed", "mean"),
        files_max=("files_accessed", "max"),
        files_std=("files_accessed", "std"),
        failed_total=("failed_logins", "sum"),
        sensitive_total=("sensitive_files", "sum"),
        emails_mean=("emails_sent", "mean"),
        emails_max=("emails_sent", "max"),
        usb_total=("usb_usage", "sum"),
        after_hours_mean=("after_hours", "mean"),
        after_hours_max=("after_hours", "max"),
        vpn_total=("vpn_connections", "sum"),
    ).reset_index()

    # ── Behavioural ratio features ───────────────────────
    agg["sensitive_ratio"] = agg["sensitive_total"] / (agg["files_mean"] * df["day"].nunique() + 1)
    agg["failed_login_rate"] = agg["failed_total"] / df["day"].nunique()
    agg["usb_rate"] = agg["usb_total"] / df["day"].nunique()
    agg["vpn_rate"] = agg["vpn_total"] / df["day"].nunique()

    # ── Weekend-specific features ────────────────────────
    weekend = df[df["is_weekend"] == 1].groupby("user_id").agg(
        weekend_files=("files_accessed", "mean"),
        weekend_logins=("login_hour", "mean"),
        weekend_after_hours=("after_hours", "mean"),
    ).reset_index()

    weekday = df[df["is_weekend"] == 0].groupby("user_id").agg(
        weekday_files=("files_accessed", "mean"),
    ).reset_index()

    agg = agg.merge(weekend, on="user_id", how="left")
    agg = agg.merge(weekday, on="user_id", how="left")

    agg["weekend_activity_ratio"] = agg["weekend_files"].fillna(0) / (agg["weekday_files"].fillna(1) + 1)

    # ── Role encoding ────────────────────────────────────
    role_map = df.groupby("user_id")["role"].first()
    agg = agg.merge(role_map, on="user_id", how="left")

    # ── Drop helper columns, keep feature columns ───────
    drop_cols = ["weekend_files", "weekday_files", "weekend_logins", "weekend_after_hours", "role"]
    feature_cols = [c for c in agg.columns if c not in ["user_id"] + drop_cols]

    # ── Scale ────────────────────────────────────────────
    agg = agg.fillna(0)
    scaler = StandardScaler()
    scaled = scaler.fit_transform(agg[feature_cols])

    features = pd.DataFrame(scaled, columns=feature_cols)
    features["user_id"] = agg["user_id"].values
    features["role"] = agg["role"].values if "role" in agg.columns else "unknown"

    features.to_csv(FEATURES_CSV, index=False)
    logger.info(f"Features built → {FEATURES_CSV}  ({len(feature_cols)} features × {len(features)} users)")
    return features
