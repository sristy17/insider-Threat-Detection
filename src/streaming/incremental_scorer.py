"""
Incremental Anomaly Scoring Module

Loads pre-trained models and scores new batches of data incrementally.
Supports near-real-time risk assessment without full model retraining.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from config import logger, RISK_WEIGHTS, RISK_THRESHOLDS, FEATURES_CSV
from src.scoring.risk_score import compute, normalise_scores, classify_risk


class IncrementalAnomalyScorer:
    """
    Handles incremental scoring of new user data batches.
    
    Uses pre-trained models for fast inference and maintains
    a running aggregate of all scored users.
    """
    
    def __init__(self, model_dir):
        """
        Initialize scorer with pre-trained models.
        
        Args:
            model_dir: Path to directory containing trained model files
        """
        self.model_dir = Path(model_dir)
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_cols = None
        self.all_scored_users = pd.DataFrame()
        
        # Load pre-trained models
        self._load_models()
        
        # Load and fit scaler from existing features
        self._fit_scaler()
        
        logger.info("✅ IncrementalAnomalyScorer initialized with models from %s", model_dir)
    
    def _load_models(self):
        """Load all trained models from disk."""
        model_files = {
            "isolation_forest": self.model_dir / "isolation_forest.joblib",
            "one_class_svm": self.model_dir / "one_class_svm.joblib",
            "autoencoder": self.model_dir / "autoencoder.joblib",
        }
        
        for name, path in model_files.items():
            if path.exists():
                self.models[name] = joblib.load(path)
                logger.info("   Loaded %s from %s", name, path.name)
            else:
                logger.warning("   Model file not found: %s", path)
        
        if not self.models:
            logger.error("❌ No models loaded! Run run_pipeline.py first to train models.")
            raise FileNotFoundError("No trained models found in " + str(self.model_dir))
    
    def _fit_scaler(self):
        """Fit scaler using the original features from FEATURES_CSV."""
        if not FEATURES_CSV.exists():
            logger.error("Features file not found at %s", FEATURES_CSV)
            raise FileNotFoundError(f"Features file not found: {FEATURES_CSV}")
        
        # Load full feature matrix used in training
        df_features = pd.read_csv(FEATURES_CSV)
        
        # Identify feature columns (exclude metadata)
        self.feature_cols = [c for c in df_features.columns if c not in ["user_id", "role"]]
        
        # Fit scaler on full dataset
        X = df_features[self.feature_cols].values
        self.scaler.fit(X)
        logger.info("   Fitted scaler on %d features from %s", len(self.feature_cols), FEATURES_CSV.name)
    
    def score_batch(self, features_df):
        """
        Score a new batch of users and update the aggregate results.
        
        Args:
            features_df: DataFrame with raw aggregated features (NOT scaled)
                        Must have columns: user_id, role, and feature columns
        
        Returns:
            DataFrame with risk scores and levels for all users processed so far
        """
        if features_df is None or features_df.empty:
            logger.warning("Empty features dataframe received")
            return self.all_scored_users
        
        logger.info("Scoring batch of %d users...", len(features_df))
        
        # Extract metadata
        user_ids = features_df["user_id"].values
        role = features_df["role"].values if "role" in features_df.columns else None
        
        # Extract behavioral columns (before scaling)
        sensitive_total = features_df["sensitive_total"].values if "sensitive_total" in features_df.columns else None
        failed_total = features_df["failed_total"].values if "failed_total" in features_df.columns else None
        
        # Get feature columns matching the trained model's expectations
        if self.feature_cols is None:
            logger.error("Feature columns not initialized!")
            return self.all_scored_users
        
        # Build feature matrix using same columns as training
        try:
            X_raw = features_df[self.feature_cols].values
        except KeyError as e:
            logger.error("Missing feature column: %s", e)
            logger.error("Expected columns: %s", self.feature_cols)
            logger.error("Available columns: %s", list(features_df.columns))
            raise
        
        logger.info("   Input shape: %d users × %d features", X_raw.shape[0], X_raw.shape[1])
        
        # Apply the pre-fitted scaler
        X_scaled = self.scaler.transform(X_raw)
        
        # Generate predictions from each model
        scores = pd.DataFrame({"user_id": user_ids})
        
        # Isolation Forest (lower score = more anomalous)
        if "isolation_forest" in self.models:
            if_pred = self.models["isolation_forest"].score_samples(X_scaled)
            # Convert to positive scale (more anomalous = higher score)
            scores["if_score"] = -if_pred
        else:
            scores["if_score"] = 0
        
        # One-Class SVM (lower score = more anomalous)
        if "one_class_svm" in self.models:
            svm_pred = self.models["one_class_svm"].decision_function(X_scaled)
            # Convert to positive scale
            scores["svm_score"] = -svm_pred
        else:
            scores["svm_score"] = 0
        
        # Autoencoder (reconstruction error)
        if "autoencoder" in self.models:
            X_reconstructed = self.models["autoencoder"].predict(X_scaled)
            reconstruction_error = np.mean((X_scaled - X_reconstructed) ** 2, axis=1)
            scores["ae_score"] = reconstruction_error
        else:
            scores["ae_score"] = 0
        
        # Add behavioral features for risk scoring
        if sensitive_total is not None:
            scores["sensitive_total"] = sensitive_total
        else:
            scores["sensitive_total"] = 0
            
        if failed_total is not None:
            scores["failed_total"] = failed_total
        else:
            scores["failed_total"] = 0
        
        if role is not None:
            scores["role"] = role
        
        # Compute raw risk scores
        scores["risk_score_raw"] = scores.apply(compute, axis=1)
        
        # Update aggregate with new batch
        if len(self.all_scored_users) == 0:
            self.all_scored_users = scores
        else:
            self.all_scored_users = pd.concat([
                self.all_scored_users[~self.all_scored_users["user_id"].isin(user_ids)],
                scores
            ], ignore_index=True)
        
        # Normalize scores across ALL users (not just current batch)
        self.all_scored_users["risk_score"] = normalise_scores(
            self.all_scored_users["risk_score_raw"]
        )
        
        # Classify risk levels
        self.all_scored_users["risk_level"] = self.all_scored_users["risk_score"].apply(classify_risk)
        
        # Sort by risk score descending
        self.all_scored_users = self.all_scored_users.sort_values(
            "risk_score", ascending=False
        ).reset_index(drop=True)
        
        logger.info(
            "   Batch scored | Total users: %d | Highest risk: %.2f",
            len(self.all_scored_users),
            self.all_scored_users["risk_score"].max() if len(self.all_scored_users) > 0 else 0
        )
        
        return self.all_scored_users.copy()
    
    def get_current_scores(self):
        """Return the current aggregate of all scored users."""
        return self.all_scored_users.copy()
    
    def get_stats(self):
        """Return summary statistics for the current score distribution."""
        if self.all_scored_users.empty:
            return {}
        
        risk_counts = self.all_scored_users["risk_level"].value_counts().to_dict()
        
        return {
            "total_users": len(self.all_scored_users),
            "critical_count": risk_counts.get("Critical", 0),
            "high_count": risk_counts.get("High", 0),
            "medium_count": risk_counts.get("Medium", 0),
            "low_count": risk_counts.get("Low", 0),
            "mean_risk_score": float(self.all_scored_users["risk_score"].mean()),
            "max_risk_score": float(self.all_scored_users["risk_score"].max()),
            "min_risk_score": float(self.all_scored_users["risk_score"].min()),
        }


# ──────────────────────────────────────────────
# Streaming-specific helper functions
# ──────────────────────────────────────────────

def score_single_user(user_features, models, scaler):
    """
    Score a single user's features (for ultra-low latency use cases).
    
    Args:
        user_features: Dict or Series with user's features
        models: Dict of trained models
        scaler: Fitted StandardScaler
    
    Returns:
        Dict with risk score and level
    """
    # Convert to array
    if isinstance(user_features, dict):
        feature_values = list(user_features.values())
    else:
        feature_values = user_features.values
    
    X = np.array(feature_values).reshape(1, -1)
    X_scaled = scaler.transform(X)
    
    # Score with each model
    if_score = -models["isolation_forest"].score_samples(X_scaled)[0]
    svm_score = -models["one_class_svm"].decision_function(X_scaled)[0]
    
    X_reconstructed = models["autoencoder"].predict(X_scaled)
    ae_score = np.mean((X_scaled - X_reconstructed) ** 2)
    
    # Compute risk
    raw_risk = (
        RISK_WEIGHTS["if_score"] * if_score +
        RISK_WEIGHTS["svm_score"] * svm_score +
        RISK_WEIGHTS["ae_score"] * ae_score +
        RISK_WEIGHTS["sensitive_total"] * user_features.get("sensitive_total", 0) +
        RISK_WEIGHTS["failed_total"] * user_features.get("failed_total", 0)
    )
    
    return {
        "if_score": if_score,
        "svm_score": svm_score,
        "ae_score": ae_score,
        "risk_score": raw_risk,
    }
