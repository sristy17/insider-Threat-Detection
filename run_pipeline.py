from pathlib import Path
import pandas as pd

from src.preprocessing.feature_engineering import build_features
from src.models.isolation_forest import train as train_if
from src.models.one_class_svm import train as train_svm
from src.scoring.risk_score import compute

BASE_DIR = Path(__file__).resolve().parent
FEATURES = BASE_DIR / "data" / "processed" / "features.csv"

def run():
    build_features()
    df = pd.read_csv(FEATURES)
    X = df.drop("user_id", axis=1)

    if_model = train_if(X)
    svm_model = train_svm(X)

    df["if_score"] = -if_model.decision_function(X)
    df["svm_score"] = -svm_model.decision_function(X)
    df["risk_score"] = df.apply(compute, axis=1)

    return df.sort_values("risk_score", ascending=False)

if __name__ == "__main__":
    out = run()
    print(out.head())
