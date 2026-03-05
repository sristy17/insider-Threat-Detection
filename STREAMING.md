# 🌊 Near-Real-Time Streaming Detection

## Overview

This module simulates near-real-time insider threat detection by processing employee activity logs in batches at regular intervals. The system mimics a production streaming environment where:

- **Logs arrive incrementally** (simulated by batch processing)
- **Models score new data continuously** without full retraining
- **Dashboard updates dynamically** every X seconds
- **Risk assessment happens in near-real-time**

## Architecture

```
┌─────────────────────┐
│  Employee Logs      │
│  (Raw CSV)          │
└──────┬──────────────┘
       │ Batch Stream
       ▼
┌─────────────────────┐
│ Stream Simulation   │◄── Processes 10 users every 5s
│ (stream_simulation) │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Incremental Scorer  │◄── Loads pre-trained models
│ (real-time scoring) │    Scores without retraining
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Scored Users CSV   │◄── Updated every batch
│  (Output)           │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Dashboard          │◄── Auto-refreshes every 10s
│  (Streamlit UI)     │    Shows live updates
└─────────────────────┘
```

## Components

### 1. Streaming Simulation (`stream_simulation.py`)

Simulates a real-time data stream by:
- Splitting users into batches (default: 10 users per batch)
- Processing each batch at intervals (default: 5 seconds)
- Extracting features incrementally
- Writing updated results continuously

**Configuration:**
```python
BATCH_SIZE = 10          # Users per batch
UPDATE_INTERVAL = 5      # Seconds between batches
```

### 2. Incremental Scorer (`src/streaming/incremental_scorer.py`)

The `IncrementalAnomalyScorer` class:
- Loads pre-trained ML models (Isolation Forest, SVM, Autoencoder)
- Scores new batches without retraining
- Maintains cumulative results across batches
- Normalizes scores across all processed users

**Key Methods:**
- `score_batch(features_df)` - Score new users and update aggregate
- `get_current_scores()` - Retrieve all scored users
- `get_stats()` - Get summary statistics

### 3. Dynamic Dashboard (`dashboard/app.py`)

Enhanced with streaming capabilities:
- **Auto-refresh toggle** - Enable/disable automatic updates
- **Refresh interval selector** - Choose update frequency (5-60s)
- **Live status banner** - Shows batch progress and high-risk alerts
- **Streaming metadata** - Displays batch number, timestamp, user counts

## Quick Start

### Option 1: Automated Demo Script

```bash
# One-command start (handles prerequisites automatically)
python start_streaming_demo.py
```

This script:
1. ✅ Checks if data and models exist
2. 🌊 Starts streaming simulation
3. 📊 Launches dashboard with auto-refresh
4. 🔴 Shows live updates

### Option 2: Manual Setup

```bash
# Step 1: Generate data (if not done)
python generate_data.py

# Step 2: Train models (if not done)
python run_pipeline.py

# Step 3: Start streaming simulation
python stream_simulation.py

# Step 4: In a separate terminal, start dashboard
streamlit run dashboard/app.py
```

Then:
- Open dashboard at http://localhost:8501
- Toggle **"Auto-refresh"** in the sidebar
- Select refresh interval (10s recommended)
- Watch real-time updates! 🔴

## How It Works

### 1. Batch Processing Flow

```python
# Pseudo-code of streaming loop
for batch in user_batches:
    # Extract features for current batch
    features = extract_features_for_users(raw_data, batch)
    
    # Score incrementally
    scored_df = scorer.score_batch(features)
    
    # Save updated results
    scored_df.to_csv(SCORED_CSV)
    
    # Log progress
    log_batch_metadata(batch_num, risk_counts, timestamp)
    
    # Wait before next batch
    sleep(UPDATE_INTERVAL)
```

### 2. Incremental Scoring

```python
class IncrementalAnomalyScorer:
    def score_batch(self, new_features):
        # 1. Score with pre-trained models
        if_scores = isolation_forest.score_samples(new_features)
        svm_scores = one_class_svm.decision_function(new_features)
        ae_scores = autoencoder.reconstruct(new_features)
        
        # 2. Compute risk scores
        risk_scores = weighted_combination(if_scores, svm_scores, ae_scores)
        
        # 3. Merge with existing results
        all_users = concat([previous_users, new_users])
        
        # 4. Re-normalize across ALL users
        all_users['risk_score'] = normalize(all_users['risk_score_raw'])
        
        return all_users
```

### 3. Dashboard Auto-Refresh

```python
# Dashboard refresh logic
if auto_refresh_enabled:
    elapsed = time.time() - last_refresh
    
    if elapsed >= refresh_interval:
        # Clear cache and reload data
        load_data.clear()
        st.rerun()
    else:
        # Show countdown
        remaining = refresh_interval - elapsed
        st.caption(f"Next refresh in {remaining}s...")
        time.sleep(1)
        st.rerun()
```

## Configuration

### Streaming Parameters

Edit `stream_simulation.py`:
```python
BATCH_SIZE = 10          # Users per batch (lower = more updates)
UPDATE_INTERVAL = 5      # Seconds between batches (lower = faster)
```

### Dashboard Refresh

In the dashboard sidebar:
- **Auto-refresh toggle** - Enable live updates
- **Refresh interval** - 5s, 10s, 15s, 30s, or 60s

## Output Files

### Continuous Updates
- `data/output/scored_users.csv` - Updated every batch with latest scores
- `data/output/streaming/batch_metadata.csv` - Batch progress tracking
- `data/processed/features.csv` - Cumulative feature matrix

### Streaming Metadata Format
```csv
batch_num,total_batches,users_in_batch,total_users_processed,timestamp,high_risk_count,critical_risk_count
5,20,10,50,2026-02-22T14:30:45.123456,3,1
```

## Performance Considerations

### Batch Size Trade-offs

| Batch Size | Update Frequency | Latency | Use Case |
|-----------|------------------|---------|----------|
| 5 users   | High (many updates) | Low | Demo, development |
| 10 users  | Medium | Medium | **Recommended** |
| 50 users  | Low (few updates) | High | Production simulation |

### Refresh Interval Trade-offs

| Interval | Dashboard Load | Smoothness | Use Case |
|----------|---------------|-----------|----------|
| 5s       | High | Very smooth | Demo |
| 10s      | Medium | Smooth | **Recommended** |
| 30s      | Low | Acceptable | Production |
| 60s      | Very low | Jerky | Large datasets |

## Real-World Deployment Considerations

This is a **simulation** for demonstration. For production:

### 1. True Streaming Infrastructure
Replace simulation with real streaming:
- **Apache Kafka** or **AWS Kinesis** for log ingestion
- **Apache Flink** or **Spark Streaming** for processing
- **Redis** or **TimescaleDB** for real-time storage

### 2. Model Serving
Use proper ML serving:
- **TensorFlow Serving** or **TorchServe**
- **MLflow** for model versioning
- **Seldon Core** for Kubernetes deployment

### 3. Scalability
- Horizontal scaling with load balancers
- Distributed scoring across worker nodes
- Message queues for backpressure handling

### 4. Monitoring
- Add alerting (PagerDuty, Slack)
- Metrics collection (Prometheus, Grafana)
- Model drift detection
- Performance monitoring

## Troubleshooting

### Streaming stops mid-process
```bash
# Check logs
tail -f logs/insider_threat.log

# Restart manually
python stream_simulation.py
```

### Dashboard not updating
1. Ensure **Auto-refresh is enabled** in sidebar
2. Check if `data/output/scored_users.csv` is being modified
3. Click **Manual Refresh** button to force update

### Models not found
```bash
# Train models first
python run_pipeline.py

# Verify model files exist
ls data/models/
# Should show: isolation_forest.joblib, one_class_svm.joblib, autoencoder.joblib
```

### High memory usage
- Reduce `BATCH_SIZE` in streaming script
- Increase `UPDATE_INTERVAL` for slower processing
- Restart dashboard periodically for long-running demos

## Examples

### Run a 2-minute demo
```python
# In stream_simulation.py, modify:
BATCH_SIZE = 5           # Faster batches
UPDATE_INTERVAL = 3      # 3-second intervals

# Run for ~2 minutes (200 users / 5 per batch * 3s ≈ 120s)
python stream_simulation.py
```

### Production-like slower stream
```python
# Simulate hourly batch processing
BATCH_SIZE = 50          # Larger batches
UPDATE_INTERVAL = 60     # 1-minute intervals

python stream_simulation.py
```

## License

Part of the Insider Threat Detection System.
See main LICENSE file for details.
