import pandas as pd
from sklearn.preprocessing import StandardScaler
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
RAW = BASE_DIR / "data" / "raw" / "employee_logs.csv"
PROCESSED = BASE_DIR / "data" / "processed"
PROCESSED.mkdir(exist_ok=True)

def build_features():
    df = pd.read_csv(RAW)

    agg = df.groupby("user_id").agg({
        "login_hour": ["mean", "std"],
        "files_accessed": ["mean", "max"],
        "failed_logins": "sum",
        "sensitive_files": "sum"
    })

    agg.columns = [
        "login_mean",
        "login_std",
        "files_mean",
        "files_max",
        "failed_total",
        "sensitive_total"
    ]

    agg = agg.reset_index()

    scaler = StandardScaler()
    scaled = scaler.fit_transform(agg.drop("user_id", axis=1))

    features = pd.DataFrame(scaled, columns=agg.columns[1:])
    features["user_id"] = agg["user_id"]

    features.to_csv(PROCESSED / "features.csv", index=False)
    print("Features built")
