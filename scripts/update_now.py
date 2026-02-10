#!/usr/bin/env python3
"""
Manual update trigger for prediction pipeline.
Runs scrape → train → predict → export pipeline immediately.
Useful for testing or manual updates outside of scheduled times.
"""

import os
import sys
import subprocess
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_command(script_name, description):
    """Run a Python script and return success status."""
    script_path = os.path.join(SCRIPT_DIR, script_name)
    
    print(f"\n{'='*60}")
    print(f"▶️  {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ {description} timed out (>10 min)")
        return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False


def main():
    """Run the complete update pipeline."""
    print("\n" + "="*60)
    print("  NEPSE PREDICTION SYSTEM - MANUAL UPDATE")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    steps = [
        ('scrape_stock.py', 'Step 1: Scrape latest stock data'),
        ('lstm_predict.py', 'Step 2: Train LSTM and generate predictions'),
        ('xgboost_predict.py', 'Step 3: Train XGBoost and generate predictions'),
        ('export_predictions_v2.py', 'Step 4: Export predictions for web'),
    ]
    
    results = {}
    start_time = datetime.now()
    
    for script, description in steps:
        success = run_command(script, description)
        results[description] = success
        
        # Stop on first failure
        if not success:
            print(f"\n⚠️  Pipeline stopped due to failure")
            break
    
    # Summary
    print(f"\n{'='*60}")
    print("  UPDATE SUMMARY")
    print(f"{'='*60}")
    
    all_success = all(results.values())
    
    for description, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {description}")
    
    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n⏱️  Total time: {elapsed:.0f} seconds ({elapsed/60:.1f} minutes)")
    print(f"🏁 Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if all_success:
        print("\n✅ UPDATE SUCCESSFUL!")
        print("🌐 Web dashboard should now show updated predictions")
        print("📊 Next automatic update scheduled for tomorrow at 3:10 PM")
    else:
        print("\n❌ UPDATE FAILED")
        print("Check the error messages above for details")
        print("💡 Tip: Run 'python status_check.py' for diagnostics")
    
    print("="*60 + "\n")
    
    return 0 if all_success else 1


if __name__ == '__main__':
    sys.exit(main())
