"""
Generate realistic synthetic employee activity logs.
Features: login_hour, files_accessed, failed_logins, sensitive_files,
          emails_sent, usb_usage, after_hours, vpn_connections, role, is_weekend.
"""
import pandas as pd
import numpy as np
from config import RAW_CSV, NUM_USERS, NUM_DAYS, ANOMALY_RATE, SEED, ROLES, ROLE_WEIGHTS, logger

np.random.seed(SEED)

# Role-specific baseline profiles  {role: (login_mean, files_lambda, email_lambda, usb_prob)}
ROLE_PROFILES = {
    "engineer":  (9,  8,  12, 0.15),
    "analyst":   (9,  15, 20, 0.05),
    "manager":   (8,  5,  25, 0.03),
    "admin":     (10, 20, 8,  0.25),
    "intern":    (9,  4,  6,  0.02),
}

rows = []

roles_assigned = np.random.choice(ROLES, size=NUM_USERS, p=ROLE_WEIGHTS)

for uid in range(NUM_USERS):
    role = roles_assigned[uid]
    login_base, files_lam, email_lam, usb_prob = ROLE_PROFILES[role]
    personal_offset = np.random.normal(0, 0.5)

    for day in range(NUM_DAYS):
        is_weekend = 1 if (day % 7) >= 5 else 0

        # Normal behaviour
        login_hour = int(np.clip(np.random.normal(login_base + personal_offset, 1.2), 0, 23))
        files = max(0, np.random.poisson(files_lam * (0.3 if is_weekend else 1.0)))
        failed = np.random.binomial(4, 0.04)
        sensitive = np.random.binomial(3, 0.06)
        emails = max(0, np.random.poisson(email_lam * (0.2 if is_weekend else 1.0)))
        usb = 1 if np.random.rand() < usb_prob else 0
        after_hours = max(0, np.random.poisson(0.3))
        vpn = 1 if np.random.rand() < (0.15 if is_weekend else 0.4) else 0

        # Inject anomalies
        if np.random.rand() < ANOMALY_RATE:
            login_hour = int(np.random.choice([0, 1, 2, 3, 4, 22, 23]))
            files = np.random.randint(80, 300)
            sensitive = np.random.randint(8, 25)
            failed += np.random.randint(3, 8)
            emails = np.random.randint(50, 120)
            usb = 1
            after_hours = np.random.randint(3, 8)
            vpn = 1 if is_weekend else vpn

        rows.append([
            uid, role, day, is_weekend, login_hour,
            files, failed, sensitive, emails, usb, after_hours, vpn
        ])

df = pd.DataFrame(rows, columns=[
    "user_id", "role", "day", "is_weekend", "login_hour",
    "files_accessed", "failed_logins", "sensitive_files",
    "emails_sent", "usb_usage", "after_hours", "vpn_connections"
])

df.to_csv(RAW_CSV, index=False)
logger.info(f"Synthetic data generated → {RAW_CSV}  ({len(df)} rows, {NUM_USERS} users, {NUM_DAYS} days)")
