from sklearn.ensemble import IsolationForest
import joblib
from config import IF_PARAMS, MODEL_DIR, logger


def train(X):
    model = IsolationForest(**IF_PARAMS)
    model.fit(X)
    path = MODEL_DIR / "isolation_forest.joblib"
    joblib.dump(model, path)
    logger.info(f"Isolation Forest trained & saved → {path}")
    return model


def load():
    path = MODEL_DIR / "isolation_forest.joblib"
    return joblib.load(path)
