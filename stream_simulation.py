"""
Near-Real-Time Streaming Simulation for Insider Threat Detection

Simulates streaming data by processing employee logs in batches at regular intervals.
Models are incrementally updated and risk scores are computed in near-real-time.
The dashboard can monitor the continuously updated scored_users.csv.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import numpy as np
import time
import joblib
from datetime import datetime
from config import (
    RAW_CSV, FEATURES_CSV, SCORED_CSV, MODEL_DIR,
    logger, OUTPUT_DIR
)
from src.preprocessing.feature_engineering import build_features
from src.scoring.risk_score import compute, normalise_scores, classify_risk
from src.streaming.incremental_scorer import IncrementalAnomalyScorer
from sklearn.preprocessing import StandardScaler


# ──────────────────────────────────────────────
# Streaming configuration
# ──────────────────────────────────────────────
BATCH_SIZE = 10          # Number of users to process per batch
UPDATE_INTERVAL = 5      # Seconds between batch updates
PROCESS_ALL_FIRST = True # Process all existing data first, then simulate streaming


def stream_logs():
    """
    Main streaming simulation loop.
    
    1. Load raw logs and split into batches by user_id
    2. Process each batch incrementally
    3. Update features, scores, and output periodically
    4. Dashboard reads the continuously updated CSV
    """
    logger.info("=" * 80)
    logger.info("🌊 STREAMING SIMULATION STARTED")
    logger.info("=" * 80)
    
    # Initialize incremental scorer
    scorer = IncrementalAnomalyScorer(MODEL_DIR)
    
    # Load raw data
    if not RAW_CSV.exists():
        logger.error("Raw data not found at %s. Run generate_data.py first.", RAW_CSV)
        return
    
    df_raw = pd.read_csv(RAW_CSV)
    logger.info("Loaded %d rows from %s", len(df_raw), RAW_CSV)
    
    # Get unique users for batching
    all_users = df_raw["user_id"].unique()
    total_users = len(all_users)
    logger.info("Total users to process: %d", total_users)
    
    # Split into batches
    batches = [all_users[i:i + BATCH_SIZE] for i in range(0, total_users, BATCH_SIZE)]
    total_batches = len(batches)
    logger.info("Processing in %d batches of ~%d users", total_batches, BATCH_SIZE)
    
    # Create streaming state directory
    stream_dir = OUTPUT_DIR / "streaming"
    stream_dir.mkdir(exist_ok=True)
    
    # Process batches
    processed_users = []
    
    for batch_num, user_batch in enumerate(batches, 1):
        batch_start = time.time()
        
        logger.info("-" * 80)
        logger.info("📦 Batch %d/%d | Users: %d", batch_num, total_batches, len(user_batch))
        
        # Accumulate processed users
        processed_users.extend(user_batch)
        
        # Extract features for processed users
        features_df = extract_features_for_users(df_raw, processed_users)
        
        if features_df is None or features_df.empty:
            logger.warning("No features extracted for batch %d, skipping", batch_num)
            time.sleep(UPDATE_INTERVAL)
            continue
        
        # Incremental scoring
        scored_df = scorer.score_batch(features_df)
        
        # Save updated results
        scored_df.to_csv(SCORED_CSV, index=False)
        features_df.to_csv(FEATURES_CSV, index=False)
        
        # Save batch metadata
        metadata = {
            "batch_num": batch_num,
            "total_batches": total_batches,
            "users_in_batch": len(user_batch),
            "total_users_processed": len(processed_users),
            "timestamp": datetime.now().isoformat(),
            "high_risk_count": len(scored_df[scored_df["risk_level"] == "High"]),
            "critical_risk_count": len(scored_df[scored_df["risk_level"] == "Critical"]),
        }
        
        pd.DataFrame([metadata]).to_csv(
            stream_dir / "batch_metadata.csv",
            index=False,
            mode='w'
        )
        
        batch_duration = time.time() - batch_start
        
        logger.info(
            "✅ Batch %d complete | Duration: %.2fs | Total processed: %d/%d users",
            batch_num, batch_duration, len(processed_users), total_users
        )
        logger.info(
            "   Risk summary: %d Critical, %d High, %d Medium, %d Low",
            metadata["critical_risk_count"],
            metadata["high_risk_count"],
            len(scored_df[scored_df["risk_level"] == "Medium"]),
            len(scored_df[scored_df["risk_level"] == "Low"]),
        )
        
        # Wait before next batch (skip for last batch)
        if batch_num < total_batches:
            logger.info("⏳ Waiting %ds before next batch...", UPDATE_INTERVAL)
            time.sleep(UPDATE_INTERVAL)
    
    logger.info("=" * 80)
    logger.info("🎉 STREAMING SIMULATION COMPLETED")
    logger.info("=" * 80)
    logger.info("Total users processed: %d", len(processed_users))
    logger.info("Output saved to: %s", SCORED_CSV)


def extract_features_for_users(df_raw, user_ids):
    """
    Extract features for a subset of users from the raw data.
    Matches the exact feature engineering pipeline used in training.
    
    Args:
        df_raw: Full raw dataframe
        user_ids: List of user_ids to process
    
    Returns:
        DataFrame with engineered features for specified users (raw, not scaled)
    """
    # Filter data for selected users
    df_subset = df_raw[df_raw["user_id"].isin(user_ids)].copy()
    
    if df_subset.empty:
        return None
    
    # Per-user aggregations (must match feature_engineering.py exactly)
    agg = df_subset.groupby("user_id").agg(
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
    
    # Behavioral ratio features
    total_days = df_subset["day"].nunique()
    agg["sensitive_ratio"] = agg["sensitive_total"] / (agg["files_mean"] * total_days + 1)
    agg["failed_login_rate"] = agg["failed_total"] / total_days
    agg["usb_rate"] = agg["usb_total"] / total_days
    agg["vpn_rate"] = agg["vpn_total"] / total_days
    
    # Weekend-specific features
    weekend = df_subset[df_subset["is_weekend"] == 1].groupby("user_id").agg(
        weekend_files=("files_accessed", "mean"),
        weekend_logins=("login_hour", "mean"),
        weekend_after_hours=("after_hours", "mean"),
    ).reset_index()
    
    weekday = df_subset[df_subset["is_weekend"] == 0].groupby("user_id").agg(
        weekday_files=("files_accessed", "mean"),
    ).reset_index()
    
    agg = agg.merge(weekend, on="user_id", how="left")
    agg = agg.merge(weekday, on="user_id", how="left")
    
    # Weekend activity ratio
    agg["weekend_activity_ratio"] = agg["weekend_files"].fillna(0) / (agg["weekday_files"].fillna(1) + 1)
    
    # Get role
    role_map = df_subset.groupby("user_id")["role"].first()
    agg = agg.merge(role_map, on="user_id", how="left")
    
    # Fill NaNs with 0
    agg = agg.fillna(0)
    
    # Preserve columns in expected order: user_id, role, features, behavioral columns
    # Keep the columns that match the training pipeline
    drop_cols = ["weekend_files", "weekday_files", "weekend_logins", "weekend_after_hours"]
    feature_cols = [c for c in agg.columns if c not in ["user_id", "role"] + drop_cols]
    
    # Create result dataframe with correct column order
    result = agg[["user_id", "role"] + feature_cols].copy()
    
    return result


if __name__ == "__main__":
    try:
        stream_logs()
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Streaming interrupted by user (Ctrl+C)")
    except Exception as e:
        logger.error("❌ Streaming failed: %s", e, exc_info=True)
        raise
