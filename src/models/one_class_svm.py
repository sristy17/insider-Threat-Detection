"""One-Class SVM model with persistence."""
from sklearn.svm import OneClassSVM
import joblib
from config import SVM_PARAMS, MODEL_DIR, logger


def train(X):
    model = OneClassSVM(**SVM_PARAMS)
    model.fit(X)
    path = MODEL_DIR / "one_class_svm.joblib"
    joblib.dump(model, path)
    logger.info(f"One-Class SVM trained & saved → {path}")
    return model


def load():
    path = MODEL_DIR / "one_class_svm.joblib"
    return joblib.load(path)
