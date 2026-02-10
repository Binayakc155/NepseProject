# 🐍 Scripts Reference Guide

Quick reference for all Python scripts in the project.

---

## 📋 Main Pipeline Scripts

### `run_all.py`
**Purpose:** Execute entire pipeline in sequence
**Runtime:** ~20-30 minutes (first time)
**Frequency:** One-time setup, then optional

```powershell
python run_all.py
```

**What it does:**
1. Scrapes 20 stocks (14+ years of data) - 10-15 min
2. Trains LSTM model - 5-8 min
3. Trains XGBoost model - 3-5 min
4. Exports predictions to JSON - 1 min

**Output:**
- Creates: `scripts/data/*.csv` (6 GB total)
- Creates: `scripts/predictions/*.csv`
- Creates: `web/data/predictions.json`

**Use when:**
- ✅ First-time setup
- ✅ Need full fresh data
- ✅ Want to retrain from scratch

---

### `scrape_stock.py`
**Purpose:** Download stock data from nepsealpha.com
**Runtime:** 5-10 minutes per run
**Frequency:** Daily after market close

```powershell
python scrape_stock.py
```

**What it does:**
1. Launches Playwright browser
2. Navigates to nepsealpha.com
3. Intercepts TradingView API responses
4. Extracts OHLCV data for 20 stocks
5. Appends to existing CSV (incremental)
6. Removes duplicates by date

**Input:**
- None (scrapes from website)

**Output:**
- Updates: `scripts/data/NABIL.csv`
- Updates: `scripts/data/NICA.csv`
- Updates: `scripts/data/` (all 20 stocks)

**Customization:**
```python
# Line 20-25: Edit STOCKS list
STOCKS = ['NABIL', 'NICA', 'SBI', ...]

# Line 50: Change headless mode
browser = p.chromium.launch(headless=True)
```

**Troubleshooting:**
- No data? → Check internet connection
- Timeout? → Increase `page.wait_for_timeout()`
- Empty CSV? → Run again, try different stock

---

### `lstm_predict.py`
**Purpose:** Train LSTM deep learning model & predict next day prices
**Runtime:** 5-8 minutes for 20 stocks
**Frequency:** Daily after data update

```powershell
python lstm_predict.py
```

**What it does:**
1. Loads CSV data for each stock
2. Normalizes prices (0-1 scale)
3. Creates 60-day sliding windows
4. Splits data: 80% train, 20% test
5. Trains LSTM neural network
6. Makes predictions for all stocks
7. Saves predictions to CSV

**Model Architecture:**
```
LSTM(128) → Dropout → LSTM(64) → Dropout → LSTM(32) 
→ Dropout → Dense(16, relu) → Dense(4, linear)
Output: [prediction_open, prediction_high, prediction_low, prediction_close]
```

**Input:**
- Requires: `scripts/data/*.csv`

**Output:**
- Creates: `scripts/predictions/lstm_predictions.csv`

**Hyperparameters (customize in file):**
```python
WINDOW_SIZE = 60      # Days of history per sequence
EPOCHS = 30           # Training iterations
BATCH_SIZE = 16       # Samples per gradient update
DROPOUT_RATE = 0.2    # Regularization
TRAIN_TEST_SPLIT = 0.8  # 80% train, 20% test
```

**Customization Examples:**

*Faster training (less accurate):*
```python
EPOCHS = 10           # Was 30
BATCH_SIZE = 32       # Was 16
```

*Better accuracy (slower):*
```python
EPOCHS = 50           # Was 30
BATCH_SIZE = 8        # Was 16
LSTM layers = add another LSTM(16)
```

*Fewer stocks (testing):*
```python
STOCKS = ['NABIL', 'NICA', 'NEPSE']  # Was all 20
```

**Troubleshooting:**
- Import error? → `pip install tensorflow scikit-learn`
- Out of memory? → Reduce WINDOW_SIZE to 30
- Very slow? → Using CPU (normal), consider GPU setup

---

### `xgboost_predict.py`
**Purpose:** Train XGBoost model & predict next day prices
**Runtime:** 3-5 minutes for 20 stocks
**Frequency:** Daily after data update

```powershell
python xgboost_predict.py
```

**What it does:**
1. Loads CSV data for each stock
2. Creates lag features (60 previous days)
3. Splits data: 80% train, 20% test
4. Trains 4 separate XGBoost models (O, H, L, C)
5. Makes predictions for all stocks
6. Saves predictions to CSV

**Model Configuration:**
```python
{
    'n_estimators': 100,      # Number trees
    'max_depth': 6,           # Tree depth
    'learning_rate': 0.1,     # Shrinkage
    'subsample': 0.8,         # Sample fraction
    'colsample_bytree': 0.8   # Feature fraction
}
```

**Input:**
- Requires: `scripts/data/*.csv`

**Output:**
- Creates: `scripts/predictions/xgboost_predictions.csv`

**Customization Examples:**

*Faster (less accurate):*
```python
'n_estimators': 50,          # Was 100
'max_depth': 4,              # Was 6
```

*Better accuracy (slower):*
```python
'n_estimators': 200,         # Was 100
'max_depth': 8,              # Was 6
'learning_rate': 0.05,       # Was 0.1
```

**Troubleshooting:**
- Import error? → `pip install xgboost scikit-learn`
- Out of memory? → Unlikely, XGBoost is efficient

---

## 🔄 Automation & Utility Scripts

### `auto_update.py`
**Purpose:** Automatically run full pipeline at scheduled times
**Runtime:** Continuous (runs in background)
**Frequency:** Once per day (set and forget)

```powershell
python auto_update.py
```

**Schedule:**
- Runs: Monday-Friday at 3:10 PM (15:10)
- Skips: Weekends (Saturday-Sunday)
- Repeats every day at same time

**What it does:**
1. Checks time every 60 seconds
2. At 3:10 PM: Calls `scrape_stock.py`
3. Then: Calls `lstm_predict.py`
4. Then: Calls `xgboost_predict.py`
5. Then: Calls `export_predictions_v2.py`
6. Logs everything to `auto_update.log`

**Configuration (customize start time):**
```python
# Line 45-50: Change time to different time
schedule.every().monday.at("15:10").do(run_update)     # 3:10 PM
# Change "15:10" to:
#   "14:30" for 2:30 PM
#   "16:00" for 4 PM
#   "09:00" for 9 AM
```

**Output:**
- Creates: `auto_update.log` (timestamped activities)

**Important Notes:**
- ⚠️ Must keep terminal open 24/7
- ⚠️ Won't run on weekends
- ⚠️ Won't run if computer is sleeping
- ⚠️ Check `auto_update.log` for errors

**Troubleshooting:**
- Not running? → Check 'auto_update.log'
- Doesn't update? → Verify system time is correct
- Crashed? → Check error message in log

---

### `update_now.py` (NEW)
**Purpose:** Manually trigger full pipeline immediately
**Runtime:** ~15-20 minutes
**Frequency:** Anytime (manual)

```powershell
python update_now.py
```

**What it does:**
1. Runs `scrape_stock.py`
2. Then `lstm_predict.py`
3. Then `xgboost_predict.py`
4. Then `export_predictions_v2.py`
5. Shows progress and timing
6. Provides summary report

**Output:**
- Console output with progress
- Updates all prediction files
- Updates web dashboard JSON

**Use cases:**
- ✅ Manual update outside of 3:10 PM
- ✅ Testing new parameters
- ✅ Emergency update if auto-update fails
- ✅ Development/debugging

**Customization:**
None needed - just run it!

---

### `export_predictions_v2.py` (NEW)
**Purpose:** Convert CSV predictions to JSON format for web
**Runtime:** 1-2 minutes
**Frequency:** After model training

```powershell
python export_predictions_v2.py
```

**What it does:**
1. Loads `lstm_predictions.csv`
2. Loads `xgboost_predictions.csv`
3. Merges on (symbol, date)
4. Calculates ensemble (average both models)
5. Creates signal: bullish/bearish/neutral
6. Exports to `web/data/predictions.json`
7. Writes detailed log to `export_predictions.log`

**Input:**
- Requires: `lstm_predictions.csv`
- Requires: `xgboost_predictions.csv`

**Output:**
- Creates: `web/data/predictions.json`
- Appends: `export_predictions.log`

**Features:**
- ✅ Graceful handling if one model missing
- ✅ Detailed error logging
- ✅ Console feedback
- ✅ Rounded values for display

**Troubleshooting:**
- Missing files? → Run models first
- JSON wrong format? → Check error in log

---

### `status_check.py` (NEW)
**Purpose:** Diagnose system health & provide recommendations
**Runtime:** <10 seconds
**Frequency:** Daily or when issues occur

```powershell
python status_check.py
```

**Checks:**
- ✅ Stock data freshness (should be < 3 days old)
- ✅ Prediction files exist (should be < 24h old)
- ✅ Web JSON is updated (should be < 24h old)
- ✅ Auto-update logs (recent activity)
- ✅ Export logs (recent runs)

**Output:**
```
📊 STOCK DATA CHECK
✅ NABIL: 3214 rows, latest: 2026-02-10 (0d old)
...

🤖 PREDICTION FILES CHECK
✅ LSTM: 2.5 MB, 2h old
...

🌐 WEB INTERFACE CHECK
✅ JSON exported 2h ago
...

💡 RECOMMENDATIONS
✅ Everything looks good!
```

**Customization:**
None needed - read output for guidance!

---

## 📊 Analysis Scripts

### `backtest_comparison.py`
**Purpose:** Test model accuracy on unseen past data
**Runtime:** 5-10 minutes
**Frequency:** Weekly or when testing changes

```powershell
python backtest_comparison.py
```

**What it does:**
1. Loads data for each stock
2. Trains model on ALL data except last 30 days
3. Tests prediction on last 30 days
4. Calculates MAE (Mean Absolute Error)
5. Calculates RMSE (Root Mean Squared Error)
6. Compares LSTM vs XGBoost
7. Recommends better model per stock

**Output:**
```
Detailed comparison for each stock:
NABIL:
  LSTM MAE: 2.15 Rs, RMSE: 2.67
  XGBoost MAE: 1.87 Rs, RMSE: 2.31
  Better: XGBoost ⭐

NICA:
  ...

Summary:
  XGBoost wins: 12/20 stocks
  LSTM wins: 8/20 stocks
  Use: Ensemble for best accuracy
```

**Use cases:**
- ✅ Validate model quality
- ✅ Choose which model to use
- ✅ Detect if models degraded
- ✅ Test hyperparameter changes

**Customization:**
```python
# Line 20: Change test period
test_period = 30  # Was 30 days, try 7 or 60

# Line 30: Only test specific stocks
STOCKS = ['NABIL', 'NICA', 'NEPSE']
```

---

## 📁 File Dependencies

```
scrape_stock.py
  └─ Creates: scripts/data/*.csv
     
lstm_predict.py
  ├─ Requires: scripts/data/*.csv
  └─ Creates: scripts/predictions/lstm_predictions.csv

xgboost_predict.py
  ├─ Requires: scripts/data/*.csv
  └─ Creates: scripts/predictions/xgboost_predictions.csv

export_predictions_v2.py
  ├─ Requires: lstm_predictions.csv
  ├─ Requires: xgboost_predictions.csv
  └─ Creates: web/data/predictions.json

web/app.js
  └─ Requires: web/data/predictions.json

backtest_comparison.py
  ├─ Requires: scripts/data/*.csv
  └─ Uses: lstm_predict.py, xgboost_predict.py

auto_update.py
  └─ Calls: scrape_stock, lstm_predict, xgboost_predict, export_predictions

update_now.py
  └─ Calls: scrape_stock, lstm_predict, xgboost_predict, export_predictions
```

---

## ⚡ Common Command Sequences

### Sequential (one after another)
```powershell
# Manual full pipeline
python scrape_stock.py
python lstm_predict.py
python xgboost_predict.py
python export_predictions_v2.py
```

### Faster (skip scraping)
```powershell
# Just retrain existing data
python lstm_predict.py
python xgboost_predict.py
python export_predictions_v2.py
```

### Development (single stock)
```powershell
# Edit scripts to have: STOCKS = ['NABIL']
python lstm_predict.py
python xgboost_predict.py
python export_predictions_v2.py
```

### Testing
```powershell
python status_check.py
python backtest_comparison.py
python update_now.py
```

---

## 🔧 Troubleshooting by Script

| Script | Problem | Solution |
|--------|---------|----------|
| **scrape_stock.py** | Empty CSV | Check internet, increase timeout |
| **lstm_predict.py** | Out of memory | Reduce WINDOW_SIZE or BATCH_SIZE |
| **xgboost_predict.py** | Import error | `pip install xgboost` |
| **export_predictions_v2.py** | Missing JSON | Run model scripts first |
| **auto_update.py** | Not running | Check system time, check log |
| **update_now.py** | Fails midway | Check previous error message |
| **status_check.py** | Shows red | Follow recommended actions |
| **backtest_comparison.py** | Takes long | Close other apps, be patient |

---

## 📊 Performance Tips

### To make scraping faster:
- Use `headless=True` in scrape_stock.py (already done)
- Run fewer stocks for testing

### To make training faster:
- Reduce EPOCHS in lstm_predict.py
- Reduce n_estimators in xgboost_predict.py
- Use GPU support (requires CUDA setup)

### To make export faster:
- Already optimized, <1 min typically

### General optimization:
- Run during off-peak hours
- Close other applications
- Use SSD (not HDD)

---

**Last Updated:** February 11, 2026
**Version:** 2.0
**All scripts tested and production-ready** ✅
