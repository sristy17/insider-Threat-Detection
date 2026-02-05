import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

np.random.seed(42)

users = 150
days = 45
rows = []

for user in range(users):
    base_login = np.random.randint(8, 11)

    for day in range(days):
        login_hour = int(np.random.normal(base_login, 1.5))
        files = np.random.poisson(6)
        failed = np.random.binomial(4, 0.04)
        sensitive = np.random.binomial(2, 0.08)

        if np.random.rand() < 0.04:
            login_hour = np.random.choice([1, 2, 3, 23])
            files = np.random.randint(80, 250)
            sensitive = np.random.randint(6, 18)
            failed += np.random.randint(2, 6)

        rows.append([
            user, day, abs(login_hour),
            files, failed, sensitive
        ])

df = pd.DataFrame(rows, columns=[
    "user_id", "day", "login_hour",
    "files_accessed", "failed_logins",
    "sensitive_files"
])

df.to_csv(RAW_DIR / "employee_logs.csv", index=False)
print("Synthetic data generated")
