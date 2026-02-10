# ⚡ Quick Start Guide

Get your NEPSE prediction system up and running in 5 minutes.

## 🎯 The Goal

Predict tomorrow's stock prices for 20 Nepal stocks using machine learning (LSTM + XGBoost).

## 🚀 Installation (One-time setup)

### Step 1: Install Python Requirements
```powershell
cd c:\Users\chitr\NepseProject
pip install -r requirements.txt
```

**What this installs:**
- `tensorflow` - Deep learning framework (LSTM models)
- `xgboost` - Gradient boosting (faster predictions)
- `pandas` - Data manipulation
- `playwright` - Web scraping browser automation
- `schedule` - Task scheduling

### Step 2: Verify Installation
```powershell
cd scripts
python -c "import tensorflow; print(f'TensorFlow {tensorflow.__version__} ✅')"
```

---

## 📊 First Time Workflow (20-30 minutes)

This downloads 14 years of historical data and trains models.

```powershell
cd scripts
python run_all.py
```

**What it does:**
1. Scrapes data for 20 stocks (~10 min)
2. Trains LSTM model (~8 min)
3. Trains XGBoost model (~5 min)
4. Exports predictions (~1 min)

**Output:**
- `data/*.csv` - Stock price history
- `predictions/lstm_predictions.csv` - LSTM predictions
- `predictions/xgboost_predictions.csv` - XGBoost predictions
- `../web/data/predictions.json` - Web dashboard data

---

## 🌐 View Results

### Open Web Dashboard
```powershell
cd ..\web
python -m http.server 8000
```

Open browser: **http://localhost:8000**

You should see:
- Stock selector dropdown
- Model selection (LSTM, XGBoost, Ensemble)
- Predicted prices for tomorrow
- Bullish/Bearish indicators

---

## ⏰ Daily Updates (After Market Close)

### Option A: Automatic (Recommended)

Set it and forget it! Runs every weekday at 3:10 PM automatically.

```powershell
cd scripts
python auto_update.py
```

**Keep this terminal open.** It will:
- Download new data after market closes
- Retrain models with updated data
- Update web dashboard automatically

Press `Ctrl+C` to stop.

### Option B: Manual Update

Run anytime to update predictions:

```powershell
cd scripts
python update_now.py
```

This runs: scrape → LSTM train → XGBoost train → export

---

## 🔍 Check System Status

Diagnose any issues:

```powershell
cd scripts
python status_check.py
```

Shows:
- ✅ Data freshness
- ✅ Model files status
- ✅ Web interface ready
- 💡 Suggested actions

---

## 📱 Using the Web Dashboard

1. **Select Model**: Choose LSTM, XGBoost, or Ensemble
2. **Select Stock**: Pick from 20 stocks
3. **Read Prediction**:
   - **OHLC**: Open, High, Low, Close prices
   - **Change**: Expected price change in Rs and %
   - **Signal**: Bullish (📈), Bearish (📉), or Neutral (➡️)

### Understanding Signals

- **Bullish** (Green): Price expected to rise >1%
- **Bearish** (Red): Price expected to fall >-1%
- **Neutral** (Gray): Price change <1%

---

## 🔧 Individual Commands

Run any step separately:

```powershell
# Just scrape new data (5-10 min)
python scrape_stock.py

# Just train LSTM (5-8 min)
python lstm_predict.py

# Just train XGBoost (3-5 min)
python xgboost_predict.py

# Just export to website (1 min)
python export_predictions_v2.py

# Check model accuracy (5 min)
python backtest_comparison.py

# See system status
python status_check.py
```

---

## ❓ FAQ

### Q: Why is the prediction wrong?
**A:** Markets are complex. Models predict based on patterns, but unexpected events may occur.
- Use "Ensemble" model (combines LSTM + XGBoost)
- Check `backtest_comparison.py` to see which model is more accurate

### Q: How often should I update?
**A:** Daily after market close (3-3:10 PM). Auto-update does this automatically.

### Q: Can I predict multiple days ahead?
**A:** Not yet. Current system predicts only tomorrow's prices.

### Q: Which model is more accurate?
**Run this to find out:**
```powershell
python backtest_comparison.py
```
Shows MAE and RMSE scores for each model and stock.

### Q: Can I add my own stocks?
**A:** Yes, edit the `STOCKS` list in `scrape_stock.py` and `lstm_predict.py`. Use stock symbols from nepsealpha.com

### Q: Where is the data stored?
```
scripts/data/*.csv          - Historical prices
scripts/predictions/*.csv   - Model predictions
web/data/predictions.json   - Website data
```

### Q: Dashboard shows old data?
**Fix:**
1. Run `python update_now.py`
2. Hold Ctrl+F5 to hard-refresh browser cache

### Q: How much disk space needed?
- Historical data: ~100 MB
- Models: ~50 MB
- Total: ~200 MB

---

## 🎓 Learning Path

### Beginner: Just use it
```powershell
python update_now.py      # Get predictions
python status_check.py    # Check health
```

### Intermediate: Understand models
```powershell
python backtest_comparison.py  # See which model wins
# Edit lstm_predict.py to adjust hyperparameters
# Edit xgboost_predict.py to change features
```

### Advanced: Customize everything
```powershell
# Add stocks to STOCKS list
# Change window size from 60 to 30/90
# Add more LSTM layers or XGBoost depth
# Build your own export script
```

---

## 📈 Performance Metrics

Model accuracy on last 30 days (`python backtest_comparison.py`):

```
Stock  | LSTM MAE | XGBoost MAE | Better Model
-------|----------|-------------|-------------
NABIL  | ±2.15    | ±1.87      | XGBoost ⭐
NICA   | ±3.42    | ±2.91      | XGBoost ⭐
SBI    | ±1.23    | ±1.44      | LSTM ⭐
...
```

Typically: **XGBoost wins on 55-60%** of stocks, **LSTM wins on 40-45%**

---

## 🚨 Troubleshooting

### "ModuleNotFoundError: No module named 'tensorflow'"
```powershell
pip install tensorflow
```

### "File not found: NABIL.csv"
```powershell
cd scripts
python scrape_stock.py  # Download all data first
```

### "Website shows 404"
```powershell
cd scripts
python export_predictions_v2.py  # Generate JSON file
```

### "Auto updates not working"
- Terminal must stay open
- Only runs on weekdays (Mon-Fri)
- Must be between 3:10 PM - 3:20 PM
- Check: `tail scripts/auto_update.log`

### "Very slow scraping"
- Use existing data: Run `lstm_predict.py` instead of `scrape_stock.py`
- Scraping is slow because it downloads 14+ years per stock

---

## 🔐 File Structure

```
📦 NepseProject
├── 📄 README_USAGE.md          (Detailed docs)
├── 📄 QUICKSTART.md            (This file)
├── 📄 requirements.txt         (Dependencies)
│
├── 📁 scripts/
│   ├── 🐍 scrape_stock.py      (Download prices)
│   ├── 🐍 lstm_predict.py      (LSTM model)
│   ├── 🐍 xgboost_predict.py   (XGBoost model)
│   ├── 🐍 export_predictions_v2.py (JSON export)
│   ├── 🐍 run_all.py           (All steps)
│   ├── 🐍 auto_update.py       (Daily scheduler)
│   ├── 🐍 update_now.py        (Manual trigger)
│   ├── 🐍 status_check.py      (Health check)
│   ├── 🐍 backtest_comparison.py (Accuracy test)
│   ├── 📁 data/                (Stock CSVs)
│   └── 📁 predictions/         (Model outputs)
│
└── 📁 web/
    ├── 📄 index.html           (Dashboard)
    ├── 📄 styles.css           (Styling)
    ├── 📄 app.js               (Interaction)
    └── 📁 data/
        └── 📄 predictions.json (Data for web)
```

---

## ⚡ Power User Tips

### Tip 1: Parallel Execution
Terminal 1:
```powershell
python auto_update.py  # Runs at 3:10 PM daily
```

Terminal 2:
```powershell
python -m http.server 8000 --directory ../web
```

Both run simultaneously.

### Tip 2: Fastest Update
```powershell
# Skip re-download, just retrain (5 min instead of 20)
python lstm_predict.py && python xgboost_predict.py && python export_predictions_v2.py
```

### Tip 3: Monitor Accuracy Over Time
```powershell
# Run daily after market, results accumulate in CSV
python backtest_comparison.py > backtest_$(Get-Date -Format yyyyMMdd).txt
```

### Tip 4: Backup Before Major Changes
```powershell
Copy-Item predictions/ predictions_backup -Recurse -Force
```

---

## 📞 Next Steps

1. **Run it once**: `python run_all.py`
2. **View results**: Open `http://localhost:8000`
3. **Set automation**: `python auto_update.py`
4. **Monitor health**: `python status_check.py`

---

**Ready?** Start with:
```powershell
cd c:\Users\chitr\NepseProject\scripts
python run_all.py
```

Have questions? Check [README_USAGE.md](README_USAGE.md) for detailed documentation.
