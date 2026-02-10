"""
Auto-update predictions after market close
Runs at 3:10 PM on weekdays (Monday-Friday)
"""
import schedule
import time
import subprocess
import sys
import os
from datetime import datetime, timedelta

def log_msg(msg):
    """Log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")

def run_update():
    """Run scraper, LSTM, XGBoost, and export predictions"""
    log_msg("🚀 Starting post-market update...")
    
    try:
        # Step 1: Scrape latest data
        log_msg("📊 Scraping latest data...")
        result = subprocess.run(
            [sys.executable, "scrape_stock.py"],
            capture_output=True,
            text=True,
            timeout=600  # 10 min timeout
        )
        if result.returncode == 0:
            log_msg("✅ Scraping completed")
        else:
            log_msg(f"⚠️ Scraping completed with warnings: {result.stderr[:200]}")
        
        # Step 2: LSTM predictions
        log_msg("🧠 Generating LSTM predictions...")
        result = subprocess.run(
            [sys.executable, "lstm_predict.py"],
            capture_output=True,
            text=True,
            timeout=600
        )
        if result.returncode == 0:
            log_msg("✅ LSTM predictions completed")
        else:
            log_msg(f"⚠️ LSTM predictions completed with warnings: {result.stderr[:200]}")
        
        # Step 3: XGBoost predictions
        log_msg("🌲 Generating XGBoost predictions...")
        result = subprocess.run(
            [sys.executable, "xgboost_predict.py"],
            capture_output=True,
            text=True,
            timeout=600
        )
        if result.returncode == 0:
            log_msg("✅ XGBoost predictions completed")
        else:
            log_msg(f"⚠️ XGBoost predictions completed with warnings: {result.stderr[:200]}")
        
        # Step 4: Export to web
        log_msg("📤 Exporting to web interface...")
        result = subprocess.run(
            [sys.executable, "export_predictions.py"],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            log_msg("✅ Export completed")
        else:
            log_msg(f"⚠️ Export completed with warnings: {result.stderr[:200]}")
        
        log_msg("✅ Post-market update COMPLETED - Ready for tomorrow's market!")
        
    except subprocess.TimeoutExpired:
        log_msg("❌ Update timed out")
    except Exception as e:
        log_msg(f"❌ Error during update: {e}")

def schedule_jobs():
    """Schedule jobs for weekdays at market close"""
    
    # Nepal Stock Exchange hours: 9 AM - 3 PM
    # Schedule predictions at 3:10 PM (after close)
    
    for day in ["monday", "tuesday", "wednesday", "thursday", "friday"]:
        getattr(schedule.every(), day).at("15:10").do(run_update)
    
    log_msg("📅 Scheduler started!")
    log_msg("⏰ Will update predictions every weekday at 3:10 PM (after market close)")
    log_msg("Market hours: 9:00 AM - 3:00 PM")
    log_msg("\nPress Ctrl+C to stop scheduler")

def main():
    os.chdir(os.path.dirname(__file__))
    
    print("\n" + "="*70)
    print("🤖 NEPSE Auto-Update Scheduler")
    print("="*70)
    print("\nThis script will automatically:")
    print("  • Scrape latest stock data after market close")
    print("  • Train LSTM and XGBoost models")
    print("  • Generate tomorrow's price predictions")
    print("  • Update web interface")
    print("\nSchedule: Weekdays at 3:10 PM")
    print("="*70 + "\n")
    
    schedule_jobs()
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        log_msg("\n⛔ Scheduler stopped by user")

if __name__ == "__main__":
    main()
