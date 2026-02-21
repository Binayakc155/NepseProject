#!/usr/bin/env python3
"""
Check the status of the prediction pipeline.
Diagnoses issues and provides troubleshooting suggestions.
"""

import os
import sys
import json
from datetime import datetime, timedelta
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PREDICTIONS_DIR = os.path.join(SCRIPT_DIR, 'predictions')
DATA_DIR = os.path.join(SCRIPT_DIR, 'data')
WEB_JSON_FILE = os.path.join(SCRIPT_DIR, '..', 'web', 'data', 'predictions.json')

STOCKS = ['NEPSE', 'NABIL', 'NICA', 'SBI', 'EBL', 'KBL', 'ADBL', 'CHCL', 'UPPER', 
          'NHPC', 'API', 'SHPC', 'GUFL', 'GFCL', 'NLIC', 'SICL', 'HGI', 'OHL', 
          'SHL', 'UNL']


def check_stock_data():
    """Check if stock data CSV files exist and are recent."""
    print("\n STOCK DATA CHECK")
    print("=" * 50)
    
    all_good = True
    for stock in STOCKS:
        csv_file = os.path.join(DATA_DIR, f'{stock}.csv')
        
        if not os.path.exists(csv_file):
            print(f" {stock}: File missing")
            all_good = False
            continue
        
        try:
            df = pd.read_csv(csv_file)
            last_date = pd.to_datetime(df['date'].iloc[-1])
            row_count = len(df)
            
            # Check if data is recent (within 3 days)
            days_old = (datetime.now() - last_date).days
            status = "" if days_old <= 3 else " "
            
            print(f"{status} {stock}: {row_count} rows, latest: {last_date.date()} ({days_old}d old)")
            
            if days_old > 7:
                all_good = False
                
        except Exception as e:
            print(f" {stock}: Error reading CSV - {e}")
            all_good = False
    
    return all_good


def check_prediction_files():
    """Check if prediction files exist and are recent."""
    print("\n PREDICTION FILES CHECK")
    print("=" * 50)
    
    files = {
        'LSTM': os.path.join(PREDICTIONS_DIR, 'lstm_predictions.csv'),
        'XGBoost': os.path.join(PREDICTIONS_DIR, 'xgboost_predictions.csv')
    }
    
    all_good = True
    for model, filepath in files.items():
        if not os.path.exists(filepath):
            print(f" {model}: File missing")
            all_good = False
            continue
        
        try:
            size_mb = os.path.getsize(filepath) / 1024 / 1024
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
            hours_old = (datetime.now() - mtime).total_seconds() / 3600
            
            status = "" if hours_old <= 24 else " "
            print(f"{status} {model}: {size_mb:.2f} MB, {hours_old:.1f}h old")
            
            # Check file has data
            df = pd.read_csv(filepath)
            print(f"   → {len(df)} predictions, stocks: {df['symbol'].nunique()}")
            
            if hours_old > 48:
                all_good = False
                
        except Exception as e:
            print(f" {model}: Error - {e}")
            all_good = False
    
    return all_good


def check_web_json():
    """Check if web JSON is up to date."""
    print("\n WEB INTERFACE CHECK")
    print("=" * 50)
    
    if not os.path.exists(WEB_JSON_FILE):
        print(f" Web JSON missing: {WEB_JSON_FILE}")
        return False
    
    try:
        with open(WEB_JSON_FILE, 'r') as f:
            data = json.load(f)
        
        timestamp = datetime.fromisoformat(data['timestamp'])
        hours_old = (datetime.now() - timestamp).total_seconds() / 3600
        status = " " if hours_old <= 24 else " "
        
        print(f"{status} JSON exported {hours_old:.1f}h ago")
        print(f"   → Models: {', '.join(data['models'])}")
        print(f"   → Stocks: {len(data['stocks'])}/{len(STOCKS)}")
        
        # Show latest signals
        print("\n   Latest signals:")
        for symbol in sorted(data['stocks'].keys())[:5]:
            info = data['stocks'][symbol]
            signal = info['signal'].upper()
            emoji = " " if signal == "BULLISH" else " " if signal == "BEARISH" else " "
            change = info['change_pct']
            print(f"   {emoji} {symbol}: {signal} ({change:+.1f}%)")
        
        return True
        
    except Exception as e:
        print(f" Error reading JSON: {e}")
        return False


def check_auto_update_log():
    """Check auto_update.py log."""
    print("\n AUTO-UPDATE STATUS")
    print("=" * 50)
    
    log_file = os.path.join(SCRIPT_DIR, 'auto_update.log')
    
    if not os.path.exists(log_file):
        print("  Auto-update not running (no log found)")
        return None
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()[-10:]  # Last 10 lines
        
        print("Recent log entries:")
        for line in lines:
            print(f"   {line.rstrip()}")
        
        return True
        
    except Exception as e:
        print(f"  Could not read log: {e}")
        return None


def check_export_log():
    """Check export_predictions log."""
    print("\n EXPORT LOG")
    print("=" * 50)
    
    log_file = os.path.join(SCRIPT_DIR, 'export_predictions.log')
    
    if not os.path.exists(log_file):
        print("No export log found")
        return None
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()[-5:]  # Last 5 lines
        
        print("Recent exports:")
        for line in lines:
            if line.strip():
                print(f"   {line.rstrip()}")
        
        return True
        
    except Exception as e:
        print(f"  Could not read log: {e}")
        return None


def provide_recommendations():
    """Provide actionable recommendations."""
    print("\nRECOMMENDATIONS")
    print("=" * 50)
    
    issues = []
    
    # Check stock data age
    if not check_stock_data():
        issues.append("Stock data is stale (>7 days old)")
    
    # Check predictions age
    pred_lstm = os.path.join(PREDICTIONS_DIR, 'lstm_predictions.csv')
    pred_xgb = os.path.join(PREDICTIONS_DIR, 'xgboost_predictions.csv')
    
    if os.path.exists(pred_lstm):
        age = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(pred_lstm))).total_seconds() / 3600
        if age > 48:
            issues.append("Models haven't been retrained (>48h old)")
    
    if not os.path.exists(WEB_JSON_FILE):
        issues.append("Web interface data is missing")
    
    if issues:
        print("\n ACTIONS TO TAKE:\n")
        
        if "Stock data is stale" in str(issues):
            print("1. Scrape new stock data:")
            print("   python scrape_stock.py\n")
        
        if "Models haven't been retrained" in str(issues):
            print("2. Retrain models:")
            print("   python lstm_predict.py")
            print("   python xgboost_predict.py\n")
        
        if "Web interface data is missing" in str(issues):
            print("3. Export predictions for web:")
            print("   python export_predictions_v2.py\n")
        
        print("Or run all at once:")
        print("   python run_all.py\n")
    else:
        print(" Everything looks good!")
        print("\n Pipeline is healthy and ready to use.")
        print(" Web dashboard should display current predictions.")


def main():
    """Main status check."""
    print("\n" + "="*50)
    print("  NEPSE PREDICTION PIPELINE STATUS")
    print("="*50)
    
    check_stock_data()
    check_prediction_files()
    check_web_json()
    check_auto_update_log()
    check_export_log()
    provide_recommendations()
    
    print("\n" + "="*50 + "\n")


if __name__ == '__main__':
    main()
