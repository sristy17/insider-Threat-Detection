"""
Quick Start Script for Near-Real-Time Streaming Demo

This script orchestrates the streaming simulation:
1. Ensures data and models are ready
2. Launches the streaming simulation in background
3. Starts the dashboard with auto-refresh enabled

Usage:
    python start_streaming_demo.py
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import subprocess
import time
from config import RAW_CSV, MODEL_DIR, logger


def check_prerequisites():
    """Ensure data and models exist before starting streaming."""
    errors = []
    
    # Check raw data
    if not RAW_CSV.exists():
        errors.append(f"Raw data not found at {RAW_CSV}")
        logger.error("❌ Missing raw data. Run: python generate_data.py")
    
    # Check trained models
    model_files = ["isolation_forest.joblib", "one_class_svm.joblib", "autoencoder.joblib"]
    for model_file in model_files:
        if not (MODEL_DIR / model_file).exists():
            errors.append(f"Model {model_file} not found")
    
    if any("Model" in e for e in errors):
        logger.error("❌ Missing trained models. Run: python run_pipeline.py")
    
    return errors


def main():
    """Launch streaming simulation and dashboard."""
    logger.info("=" * 80)
    logger.info("🚀 STARTING NEAR-REAL-TIME STREAMING DEMO")
    logger.info("=" * 80)
    
    # Check prerequisites
    logger.info("Checking prerequisites...")
    errors = check_prerequisites()
    
    if errors:
        logger.error("Prerequisites check failed:")
        for err in errors:
            logger.error("  - %s", err)
        logger.error("\nPlease resolve the issues above before starting the demo.")
        logger.error("\nQuick fix:")
        logger.error("  1. python generate_data.py")
        logger.error("  2. python run_pipeline.py")
        logger.error("  3. python start_streaming_demo.py")
        return 1
    
    logger.info("✅ Prerequisites check passed!\n")
    
    # Start streaming simulation in background
    logger.info("🌊 Starting streaming simulation...")
    logger.info("   This will process users in batches and update scores every 5 seconds")
    logger.info("   Press Ctrl+C to stop\n")
    
    try:
        # Start streaming process
        stream_process = subprocess.Popen(
            [sys.executable, "stream_simulation.py"],
            cwd=BASE_DIR,
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        logger.info("📊 Starting dashboard with auto-refresh...")
        logger.info("   Dashboard will update every 10 seconds automatically")
        logger.info("   Open your browser to the URL shown below\n")
        
        # Start dashboard
        dashboard_process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "dashboard/app.py", 
             "--server.headless", "true"],
            cwd=BASE_DIR,
        )
        
        logger.info("=" * 80)
        logger.info("✅ STREAMING DEMO ACTIVE")
        logger.info("=" * 80)
        logger.info("Dashboard: http://localhost:8501")
        logger.info("Enable 'Auto-refresh' toggle in the sidebar to see live updates")
        logger.info("\nPress Ctrl+C to stop all processes\n")
        
        # Wait for user interrupt
        stream_process.wait()
        dashboard_process.wait()
        
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Shutting down streaming demo...")
        stream_process.terminate()
        dashboard_process.terminate()
        
        # Wait for clean shutdown
        stream_process.wait(timeout=5)
        dashboard_process.wait(timeout=5)
        
        logger.info("✅ Streaming demo stopped")
    
    except Exception as e:
        logger.error("❌ Error during streaming demo: %s", e, exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
