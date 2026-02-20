"""
Autoencoder-based anomaly detector using MLPRegressor.
Reconstruction error serves as the anomaly score.
"""
import numpy as np
from sklearn.neural_network import MLPRegressor
import joblib
from config import AE_PARAMS, MODEL_DIR, logger


def train(X):
    """Train autoencoder to reconstruct input; high error = anomaly."""
    X_np = np.array(X)
    model = MLPRegressor(**AE_PARAMS)
    model.fit(X_np, X_np)  # reconstruct input
    path = MODEL_DIR / "autoencoder.joblib"
    joblib.dump(model, path)
    logger.info(f"Autoencoder trained & saved → {path}")
    return model


def reconstruction_error(model, X):
    """Compute per-sample mean squared reconstruction error."""
    X_np = np.array(X)
    X_pred = model.predict(X_np)
    mse = np.mean((X_np - X_pred) ** 2, axis=1)
    return mse


def load():
    path = MODEL_DIR / "autoencoder.joblib"
    return joblib.load(path)
