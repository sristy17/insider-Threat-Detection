# Insider Threat Detection System  


## Overview

Insider threats are one of the most challenging problems in cybersecurity because malicious behavior is **rare, subtle, and usually unlabeled**. Traditional rule-based systems fail to generalize, and supervised ML is impractical due to the lack of labeled attack data.

This project implements an **end-to-end Insider Threat Detection System** that:
- Learns **normal employee behavior** from activity logs
- Detects anomalous users using **unsupervised machine learning**
- Converts anomaly scores into **explainable risk scores**
- Presents results in a **SOC-style dashboard** for security analysts

---

## Problem Statement

> How can we detect malicious insiders when:
> - Attacks are rare  
> - There are no labels  
> - Behavior looks normal until it suddenly doesn’t  

### Key Challenges
- No labeled insider threat data
- High false positives with rule-based detection
- Need for explainability in security decisions

---

## Solution Approach

We treat insider threat detection as an **anomaly detection problem**:

- Model *normal* employee behavior
- Detect deviations from the baseline
- Assign interpretable risk scores
- Surface alerts to analysts via a dashboard

---

## Machine Learning Models

### Isolation Forest
- Efficient unsupervised anomaly detection
- Works well for large datasets
- Identifies globally rare patterns

### One-Class SVM
- Learns a boundary around normal behavior
- Detects subtle deviations
- Complements Isolation Forest

### Why Two Models?
Using multiple unsupervised models reduces false positives and improves robustness.

---

## Risk Scoring Engine

Instead of exposing raw ML scores, the system computes an **explainable risk score**:

Risk Score =
0.35 × Isolation Forest Score

0.35 × One-Class SVM Score

0.20 × Sensitive File Access

0.10 × Failed Logins


This bridges the gap between **ML output and security decision-making**.

## Installation & Setup
### Prerequisites
- Supabase account setup

### Clone the Repository
```sh
  git clone https://github.com/sristy17/insider-Threat-Detection.git
  cd insider-Threat-Detection
```

### Install Dependencies
```sh
  pip install -r requirements.txt
```
### Run the Application

#### Option 1: Standard Batch Processing
```sh
python generate_data.py
python run_pipeline.py
streamlit run dashboard/app.py
```

#### Option 2: 🌊 Near-Real-Time Streaming Simulation (NEW!)
```sh
# One-command demo with auto-refresh dashboard
python start_streaming_demo.py
```

Or manually:
```sh
# Terminal 1: Start streaming simulation
python stream_simulation.py

# Terminal 2: Start dashboard with auto-refresh
streamlit run dashboard/app.py
# Toggle "Auto-refresh" in the sidebar
```

See [STREAMING.md](STREAMING.md) for detailed documentation on:
- How streaming simulation works
- Configuration options
- Dashboard auto-refresh features
- Real-world deployment considerations

## Contributing
1. Fork the repository.
2. Create a new branch.
3. Commit your changes.
4. Push the branch and open a pull request.

## License
This project is licensed under the [MIT License](LICENSE).
