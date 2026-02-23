# NepseProject - Stock Price Prediction System

A machine learning-powered stock price prediction system for NEPSE (Nepal Stock Exchange) stocks. Uses LSTM and XGBoost models to predict future stock prices with a web-based dashboard for visualization.

## 🎯 Features

- **Dual ML Models**: LSTM and XGBoost algorithms for price prediction
- **Multi-Output Predictions**: Predicts Open, High, Low, and Close prices
- **Stock Data Management**: Automated data scraping and preprocessing
- **Backtesting Framework**: Evaluate model performance against historical data
- **Web Dashboard**: Interactive "ArthaVed" dashboard for visualization
- **Real-time Updates**: Support for updating predictions and stock data
- **Batch Processing**: Run predictions for multiple stocks simultaneously

## 📁 Project Structure

```
NepseProject/
├── scripts/                      # Main Python scripts
│   ├── run_all.py               # Execute complete prediction pipeline
│   ├── lstm_predict.py          # LSTM model training and prediction
│   ├── xgboost_predict.py       # XGBoost model training and prediction
│   ├── scrape_stock.py          # Fetch stock data from API
│   ├── backtest_comparison.py   # Compare model performance
│   ├── compare_predictions.py   # Analyze prediction differences
│   ├── export_backtest_history.py # Export backtest results
│   ├── export_predictions.py    # Export predictions to JSON
│   ├── export_predictions_v2.py # Updated export format
│   ├── update_now.py            # Quick update script
│   ├── status_check.py          # Check system status
│   └── data/                    # Stock CSV files
│       ├── NEPSE.csv
│       ├── NABIL.csv
│       ├── KBL.csv
│       └── ...
│
├── web/                         # Web dashboard (ArthaVed)
│   ├── index.html              # Dashboard UI
│   ├── app.js                  # Frontend logic
│   ├── styles.css              # Styling
│   └── data/
│       ├── predictions.json    # Latest predictions
│       ├── history.json        # Historical data
│       └── backtest_history.json # Backtest results
│
├── check_data.py               # Verify data integrity
└── requirements.txt            # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or conda
- Virtual environment manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd NepseProject
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify data files**
   ```bash
   python check_data.py
   ```

## 📊 Usage

### Run Complete Prediction Pipeline
Execute all steps to scrape data, train models, and generate predictions:
```bash
cd scripts
python run_all.py
```

### Run Individual Predictions

**LSTM Predictions:**
```bash
python lstm_predict.py
```
- Trains LSTM neural network on historical data
- Generates next-day price predictions
- Saves results to `predictions/lstm_predictions.csv`

**XGBoost Predictions:**
```bash
python xgboost_predict.py
```
- Trains gradient boosting model
- Generates next-day price predictions
- Saves results to `predictions/xgboost_predictions.csv`

### Update Stock Data
```bash
python scrape_stock.py    # Full data scrape
python update_now.py      # Quick update
```

### Backtesting
```bash
python backtest_comparison.py   # Compare LSTM vs XGBoost
python compare_predictions.py   # Analyze prediction differences
```

### Export Results
```bash
python export_predictions.py      # Export predictions to JSON
python export_backtest_history.py # Export backtest results
```

### System Status
```bash
python status_check.py    # Check system and data status
```

## 🤖 ML Models

### LSTM (Long Short-Term Memory)
- **Architecture**: Multi-layer LSTM with dropout regularization
- **Window Size**: 60 days of historical data
- **Output**: 4-value predictions (Open, High, Low, Close)
- **Features**: Open, High, Low, Close prices
- **Normalization**: MinMaxScaler (0-1 range)

### XGBoost (eXtreme Gradient Boosting)
- **Architecture**: Gradient boosting regression
- **Window Size**: 60 days lag features
- **Output**: 4-value predictions (Open, High, Low, Close)
- **Features**: Lag features for each OHLC value
- **Training**: Tree-based ensemble learning

## 📈 Dashboard (ArthaVed)

Interactive web dashboard for visualizing predictions:
- **Quick Stats**: Total stocks, bullish/bearish indicators
- **Price Predictions**: Next-day forecasts for all stocks
- **Historical Charts**: Performance tracking
- **Backtest Results**: Model comparison and accuracy metrics

To view the dashboard, open `web/index.html` in a web browser.

## 📂 Data Format

### Input CSV Files (`scripts/data/`)
```csv
date,open,high,low,close,volume
1609459200,1000,1050,950,1030,50000
1609545600,1030,1080,1020,1070,60000
...
```
- **date**: Unix timestamp
- **open, high, low, close**: Price values in NPR
- **volume**: Trading volume

### Output JSON Files (`web/data/`)
```json
{
  "predictions": [
    {
      "symbol": "NABIL",
      "date": "2026-02-23",
      "lstm": {"open": 1200, "high": 1250, "low": 1180, "close": 1220},
      "xgboost": {"open": 1210, "high": 1260, "low": 1190, "close": 1230}
    }
  ]
}
```

## 🔧 Configuration

### Model Parameters

**LSTM** (`lstm_predict.py`):
- `WINDOW_SIZE`: 60 (days of lookback)
- `epochs`: Variable (default in function)
- `batch_size`: Configurable

**XGBoost** (`xgboost_predict.py`):
- `WINDOW_SIZE`: 60 (lag features)
- `epochs`: 100 (tree iterations)

Edit the script files directly to modify these parameters.

## 📦 Dependencies

Key packages required:
- **pandas**: Data manipulation
- **numpy**: Numerical computing
- **scikit-learn**: ML preprocessing and model evaluation
- **xgboost**: Gradient boosting
- **tensorflow/keras**: Deep learning (LSTM)
- **matplotlib/seaborn**: Visualization

See `requirements.txt` for complete list.

## 🧪 Testing & Validation

- **check_data.py**: Validate CSV data integrity
- **status_check.py**: System diagnostics
- **backtest_comparison.py**: Model performance evaluation
- **compare_predictions.py**: Cross-model analysis

## 📊 Output Locations

| Output | Location | Format |
|--------|----------|--------|
| LSTM Predictions | `scripts/predictions/lstm_predictions.csv` | CSV |
| XGBoost Predictions | `scripts/predictions/xgboost_predictions.csv` | CSV |
| Model Accuracy | `scripts/predictions/model_accuracy.json` | JSON |
| Web Predictions | `web/data/predictions.json` | JSON |
| Backtest History | `web/data/backtest_history.json` | JSON |

## ⚠️ Important Notes

1. **Data Requirements**: Ensure CSV files in `scripts/data/` have sufficient historical data (minimum recommended: 100+ days)
2. **Training Time**: Initial LSTM model training may take several minutes
3. **Memory**: Large datasets may require significant RAM for model training
4. **Predictions**: Models are trained on historical data; real-world accuracy varies

## 🔄 Workflow

Standard workflow for daily predictions:

```
1. scrape_stock.py (Update latest data)
   ↓
2. lstm_predict.py + xgboost_predict.py (Generate predictions)
   ↓
3. export_predictions.py (Export to JSON)
   ↓
4. View results in web dashboard
   ↓
5. (Optional) backtest_comparison.py (Validate accuracy)
```

## 🤝 Contributing

To contribute improvements:
1. Test changes against existing predictions
2. Update documentation if modifying ML parameters
3. Ensure data format compatibility

## 📝 License

[Add your license information here]

## 📧 Contact & Support

For issues, questions, or improvements, please [add contact information].

---

**Last Updated**: February 2026
**Project Status**: Active
