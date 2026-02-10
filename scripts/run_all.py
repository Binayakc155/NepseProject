"""
Run complete prediction workflow for all stocks
"""
import subprocess
import sys
import os

def run_step(step_name, script_name):
    """Run a script and return success status"""
    print(f"\n{'='*70}")
    print(f"🚀 STEP: {step_name}")
    print(f"{'='*70}\n")
    
    result = subprocess.run(
        [sys.executable, script_name],
        cwd=os.path.dirname(__file__)
    )
    
    if result.returncode == 0:
        print(f"\n✅ {step_name} completed successfully")
        return True
    else:
        print(f"\n❌ {step_name} failed with exit code {result.returncode}")
        return False

def main():
    print(f"\n{'='*70}")
    print(f"📊 NEPSE ML PREDICTION PIPELINE")
    print(f"{'='*70}")
    print(f"This will:")
    print(f"  1. Scrape data for 20 stocks")
    print(f"  2. Train LSTM models and make predictions")
    print(f"  3. Train XGBoost models and make predictions")
    print(f"  4. Export predictions to web interface")
    print(f"{'='*70}\n")
    
    input("Press ENTER to start or CTRL+C to cancel...")
    
    # Step 1: Scrape data
    if not run_step("Data Scraping", "scrape_stock.py"):
        print("\n⚠️  Scraping failed, but continuing with existing data...")
    
    # Step 2: LSTM predictions
    if not run_step("LSTM Prediction", "lstm_predict.py"):
        print("\n⚠️  LSTM prediction failed")
        return
    
    # Step 3: XGBoost predictions
    if not run_step("XGBoost Prediction", "xgboost_predict.py"):
        print("\n⚠️  XGBoost prediction failed")
        return
    
    # Step 4: Export to web
    if not run_step("Export to Web", "export_predictions.py"):
        print("\n⚠️  Export failed")
        return
    
    print(f"\n{'='*70}")
    print(f"✅ PIPELINE COMPLETE")
    print(f"{'='*70}")
    print(f"\nView results:")
    print(f"  - LSTM: predictions/lstm_predictions.csv")
    print(f"  - XGBoost: predictions/xgboost_predictions.csv")
    print(f"  - Web: ../web/data/predictions.json")
    print(f"\nStart web server:")
    print(f"  cd ../web")
    print(f"  python -m http.server 8000")
    print(f"  Open: http://localhost:8000")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
