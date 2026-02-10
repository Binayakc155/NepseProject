# NEPSE ML Prediction System

Complete machine learning pipeline for predicting Nepal Stock Exchange prices using LSTM and XGBoost.

## 📊 What's Included

- **Data Scraping**: Collects 14+ years of historical data for 20 stocks
- **LSTM Model**: Deep learning for long-term pattern recognition
- **XGBoost Model**: Gradient boosting for short-term predictions
- **Ensemble**: Combines both models for best accuracy
- **Web Dashboard**: Beautiful interface to view predictions
- **Auto-Update**: Automatically updates predictions after market close

## 🚀 Quick Start

### 1. Initial Setup
```powershell
cd scripts
python run_all.py  # Scrapes data and trains models (~20-30 min)
```

### 2. View Dashboard
```powershell
cd ../web
python -m http.server 8000
# Open: http://localhost:8000
```

### 3. Enable Auto-Updates (Optional)
```powershell
cd ../scripts
python auto_update.py
# Runs daily at 3:10 PM (after market close) on weekdays
```

## 📁 Project Structure

```
NepseProject/
├── scripts/
│   ├── scrape_stock.py           # Fetch stock data
│   ├── lstm_predict.py           # LSTM predictions
│   ├── xgboost_predict.py        # XGBoost predictions
│   ├── backtest_comparison.py    # Compare model accuracy
│   ├── export_predictions.py     # Export to web format
│   ├── run_all.py                # Run entire pipeline
│   ├── auto_update.py            # Auto-update after market close
│   ├── data/                     # Stock CSV files
│   └── predictions/              # Prediction CSV files
├── web/
│   ├── index.html                # Web interface
│   ├── styles.css                # Styling
│   ├── app.js                    # Dashboard logic
│   └── data/predictions.json     # Predictions data
└── README.md
```

## 📈 Stocks Covered (20)

**Index**: NEPSE

**Banks**: NABIL, NICA, SBI, EBL, KBL, ADBL

**Hydro**: CHCL, UPPER, NHPC, API, SHPC

**Finance**: GUFL, GFCL

**Insurance**: NLIC, SICL, HGI

**Hotels**: OHL, SHL

**Manufacturing**: UNL

## 🔧 Individual Commands

### Scrape Data (Takes 10-15 min)
```powershell
python scrape_stock.py
```

### Train Models & Predict (Takes 10-20 min)
```powershell
python lstm_predict.py       # LSTM
python xgboost_predict.py    # XGBoost
```

### Compare Model Accuracy
```powershell
python backtest_comparison.py
```

### Manual Update
```powershell
python export_predictions.py
```

### View Comparison
```powershell
python compare_predictions.py
```

## 📊 Understanding the Predictions

### Signals
- **Bullish**: Model predicts price increase (green)
- **Bearish**: Model predicts price decrease (red)
- **Neutral**: Model predicts minimal change

### Models
- **LSTM**: Better for long-term trends, uses last 60 days
- **XGBoost**: Better for short-term patterns, uses lag features
- **Ensemble**: Average of both models (most reliable)

### Metrics (in web dashboard)
- **Open**: Predicted opening price
- **High**: Predicted day high
- **Low**: Predicted day low
- **Close**: Predicted closing price
- **Change**: Expected price change in Rs and %

## 🔄 Auto-Update Workflow

The `auto_update.py` script runs every weekday at 3:10 PM:

1. **Scrapes** latest day's data from nepsealpha.com
2. **Appends** new data to existing CSV (doesn't re-download all history)
3. **Trains** LSTM model with updated data
4. **Trains** XGBoost model with updated data
5. **Exports** predictions to web interface
6. **Dashboard** automatically shows new predictions

To stop auto-updates: Press `Ctrl+C`

## 📝 Requirements

- Python 3.9+
- TensorFlow/Keras
- XGBoost
- Pandas, NumPy
- Playwright
- Schedule

Install all with:
```powershell
pip install -r requirements.txt
```

## ⚙️ Configuration

- **WINDOW_SIZE**: 60 days (lookback period for models)
- **LSTM Epochs**: 30 (training iterations)
- **XGBoost Iterations**: 100
- **Train/Test Split**: 80/20
- **Market Close Time**: 3:10 PM (weekdays)

## 🎯 Model Accuracy

Run backtest to see how accurate each model is:
```powershell
python backtest_comparison.py
```

The script tests on last 30 days and shows:
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- Which model is more accurate

## 🐛 Troubleshooting

**Data not scraping?**
- Check internet connection
- Site might be blocking requests (uses Playwright for reliability)

**Web dashboard showing old data?**
- Run: `python export_predictions.py`
- Then reload browser (Ctrl+F5)

**Models training too slow?**
- Reduce epochs in scripts (default 30-100)
- Use fewer stocks for testing

**Auto-update not running?**
- Terminal must stay open
- Run only on weekdays (Mon-Fri)
- Check system time is correct

## 📞 Support

For issues or improvements, refer to the individual scripts' documentation.

---

**Last Updated**: February 11, 2026
**Stocks**: 20 from 6 sectors
**Historical Data**: 14+ years
**Models**: LSTM + XGBoost
