#!/usr/bin/env python3
"""
Export predictions from CSV files to JSON format for web interface.
Also computes ensemble predictions and generates bullish/bearish signals.
Includes error handling and logging for production reliability.
"""

import os
import sys
import json
import logging
from datetime import datetime
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('export_predictions.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PREDICTIONS_DIR = os.path.join(SCRIPT_DIR, 'predictions')
WEB_DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'web', 'data')
WEB_JSON_FILE = os.path.join(WEB_DATA_DIR, 'predictions.json')
HISTORY_JSON_FILE = os.path.join(WEB_DATA_DIR, 'history.json')

LSTM_CSV = os.path.join(PREDICTIONS_DIR, 'lstm_predictions.csv')
XGBOOST_CSV = os.path.join(PREDICTIONS_DIR, 'xgboost_predictions.csv')

# Create directories if needed
os.makedirs(PREDICTIONS_DIR, exist_ok=True)
os.makedirs(WEB_DATA_DIR, exist_ok=True)


def load_predictions(csv_file):
    """Load predictions CSV with error handling."""
    try:
        if not os.path.exists(csv_file):
            logger.warning(f"File not found: {csv_file}")
            return None
        
        df = pd.read_csv(csv_file)
        logger.info(f"Loaded {len(df)} predictions from {os.path.basename(csv_file)}")
        return df
    except Exception as e:
        logger.error(f"Error loading {csv_file}: {e}")
        return None


def compute_signal(close_price, predicted_close):
    """Compute bullish/bearish signal."""
    if pd.isna(predicted_close) or pd.isna(close_price):
        return 'neutral', 0.0, 0.0
    
    change = predicted_close - close_price
    change_pct = (change / close_price * 100) if close_price != 0 else 0.0
    
    if change_pct > 1:
        signal = 'bullish'
    elif change_pct < -1:
        signal = 'bearish'
    else:
        signal = 'neutral'
    
    return signal, change, change_pct


def export_to_json():
    """Export predictions to JSON format."""
    logger.info("Starting prediction export...")
    
    # Load model accuracy results if available
    accuracy_file = os.path.join(PREDICTIONS_DIR, 'model_accuracy.json')
    model_accuracy = {}
    if os.path.exists(accuracy_file):
        try:
            with open(accuracy_file, 'r') as f:
                model_accuracy = json.load(f)
            logger.info(f"Loaded accuracy data for {len(model_accuracy)} stocks")
        except Exception as e:
            logger.warning(f"Could not load accuracy data: {e}")
    
    # Load both prediction sets
    lstm_df = load_predictions(LSTM_CSV)
    xgboost_df = load_predictions(XGBOOST_CSV)
    
    if lstm_df is None and xgboost_df is None:
        logger.error("No prediction data available")
        return False

    # If only one is available, use that
    if lstm_df is None:
        logger.warning("Using XGBoost predictions only (LSTM not available)")
        combined_df = xgboost_df.copy()
        has_lstm = False
        has_xgboost = True
    elif xgboost_df is None:
        logger.warning("Using LSTM predictions only (XGBoost not available)")
        combined_df = lstm_df.copy()
        has_lstm = True
        has_xgboost = False
    else:
        # Merge on symbol and date
        combined_df = lstm_df.merge(
            xgboost_df,
            on=['symbol', 'date', 'today_close'],
            how='outer',
            suffixes=('_lstm', '_xgb')
        )
        has_lstm = True
        has_xgboost = True

    logger.info(f"Combined {len(combined_df)} predictions")

    # Prepare output structure
    output = {
        'timestamp': datetime.now().isoformat(),
        'models': ['LSTM', 'XGBoost', 'Ensemble'] if (has_lstm and has_xgboost) else (
            ['LSTM'] if has_lstm else ['XGBoost']
        ),
        'stocks': {},
        'metadata': {
            'has_lstm': has_lstm,
            'has_xgboost': has_xgboost,
            'total_predictions': len(combined_df)
        }
    }

    # Group by symbol
    for symbol in combined_df['symbol'].unique():
        data = combined_df[combined_df['symbol'] == symbol].sort_values('date').iloc[-1]

        try:
            today_close = float(data['today_close'])

            # Prepare model predictions with fallback values
            if has_lstm:
                lstm_open = float(data.get('predicted_open_lstm', data.get('predicted_open', 0)))
                lstm_high = float(data.get('predicted_high_lstm', data.get('predicted_high', 0)))
                lstm_low = float(data.get('predicted_low_lstm', data.get('predicted_low', 0)))
                lstm_close = float(data.get('predicted_close_lstm', data.get('predicted_close', 0)))
            else:
                lstm_open = lstm_high = lstm_low = lstm_close = 0

            if has_xgboost:
                xgb_open = float(data.get('predicted_open_xgb', data.get('predicted_open', 0)))
                xgb_high = float(data.get('predicted_high_xgb', data.get('predicted_high', 0)))
                xgb_low = float(data.get('predicted_low_xgb', data.get('predicted_low', 0)))
                xgb_close = float(data.get('predicted_close_xgb', data.get('predicted_close', 0)))
            else:
                xgb_open = xgb_high = xgb_low = xgb_close = 0

            # Compute ensemble (average)
            ensemble_open = (lstm_open + xgb_open) / 2 if (has_lstm and has_xgboost) else (lstm_open or xgb_open)
            ensemble_high = (lstm_high + xgb_high) / 2 if (has_lstm and has_xgboost) else (lstm_high or xgb_high)
            ensemble_low = (lstm_low + xgb_low) / 2 if (has_lstm and has_xgboost) else (lstm_low or xgb_low)
            ensemble_close = (lstm_close + xgb_close) / 2 if (has_lstm and has_xgboost) else (lstm_close or xgb_close)

            # Compute signals using ensemble for primary signal
            signal, change, change_pct = compute_signal(today_close, ensemble_close)

            # Get accuracy info for this stock
            accuracy_info = model_accuracy.get(symbol, {})

            # Structure for web display
            output['stocks'][symbol] = {
                'date': str(data['date']),
                'today_close': today_close,
                'signal': signal,
                'change': round(change, 2),
                'change_pct': round(change_pct, 2),
                'recommended_model': accuracy_info.get('better_model', 'Ensemble'),
                'lstm_mae': accuracy_info.get('lstm_mae'),
                'xgboost_mae': accuracy_info.get('xgboost_mae'),
                'predictions': {}
            }

            # Add model-specific predictions
            if has_lstm:
                output['stocks'][symbol]['predictions']['LSTM'] = {
                    'open': round(lstm_open, 2),
                    'high': round(lstm_high, 2),
                    'low': round(lstm_low, 2),
                    'close': round(lstm_close, 2)
                }

            if has_xgboost:
                output['stocks'][symbol]['predictions']['XGBoost'] = {
                    'open': round(xgb_open, 2),
                    'high': round(xgb_high, 2),
                    'low': round(xgb_low, 2),
                    'close': round(xgb_close, 2)
                }

            if has_lstm and has_xgboost:
                output['stocks'][symbol]['predictions']['Ensemble'] = {
                    'open': round(ensemble_open, 2),
                    'high': round(ensemble_high, 2),
                    'low': round(ensemble_low, 2),
                    'close': round(ensemble_close, 2)
                }

        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
            continue

    # Write JSON
    try:
        with open(WEB_JSON_FILE, 'w') as f:
            json.dump(output, f, indent=2)

        logger.info(f"Successfully exported {len(output['stocks'])} stock predictions to {WEB_JSON_FILE}")
        print(f"\nExport successful!")
        print(f"Total stocks: {len(output['stocks'])}")
        print(f"Models: {', '.join(output['models'])}")
        print(f"Timestamp: {output['timestamp']}")
        return True

    except Exception as e:
        logger.error(f"Error writing JSON: {e}")
        return False


def export_history_json():
    data_dir = os.path.join(SCRIPT_DIR, 'data')
    history = {
        'generated_at': datetime.now().isoformat(timespec='seconds'),
        'symbols': {}
    }

    lstm_df = load_predictions(LSTM_CSV)
    xgboost_df = load_predictions(XGBOOST_CSV)

    def normalize_predictions(df):
        if df is None or df.empty:
            return None
        if 'date' not in df.columns or 'symbol' not in df.columns or 'predicted_close' not in df.columns:
            return None
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.dropna(subset=['date', 'symbol', 'predicted_close'])
        df = df.sort_values('date')
        df = df.groupby(['symbol', 'date'], as_index=False).tail(1)
        return df

    lstm_df = normalize_predictions(lstm_df)
    xgboost_df = normalize_predictions(xgboost_df)

    def build_pred_map(df):
        if df is None or df.empty:
            return {}
        pred_map = {}
        for symbol, group in df.groupby('symbol'):
            pred_map[symbol] = {
                row['date'].strftime('%Y-%m-%d'): float(row['predicted_close'])
                for _, row in group.iterrows()
            }
        return pred_map

    lstm_map = build_pred_map(lstm_df)
    xgb_map = build_pred_map(xgboost_df)

    if not os.path.exists(data_dir):
        logger.warning(f"No data directory found at {data_dir}")
        return False

    for filename in os.listdir(data_dir):
        if not filename.lower().endswith('.csv'):
            continue

        symbol = os.path.splitext(filename)[0]
        csv_path = os.path.join(data_dir, filename)

        try:
            df = pd.read_csv(csv_path)
            if 'date' not in df.columns or 'close' not in df.columns:
                continue

            df['date'] = pd.to_datetime(df['date'], unit='s', errors='coerce')
            df = df.dropna(subset=['date', 'close'])
            df = df.sort_values('date').tail(120)

            dates = df['date'].dt.strftime('%Y-%m-%d').tolist()
            history['symbols'][symbol] = {
                'dates': dates,
                'close': [round(value, 2) for value in df['close'].tolist()],
            }

            predicted = {}
            if lstm_map.get(symbol):
                predicted['LSTM'] = [
                    round(lstm_map[symbol].get(day, None), 2) if day in lstm_map[symbol] else None
                    for day in dates
                ]
            if xgb_map.get(symbol):
                predicted['XGBoost'] = [
                    round(xgb_map[symbol].get(day, None), 2) if day in xgb_map[symbol] else None
                    for day in dates
                ]

            if predicted:
                if 'LSTM' in predicted or 'XGBoost' in predicted:
                    ensemble = []
                    for idx, day in enumerate(dates):
                        lstm_val = predicted.get('LSTM', [None] * len(dates))[idx]
                        xgb_val = predicted.get('XGBoost', [None] * len(dates))[idx]
                        if lstm_val is not None and xgb_val is not None:
                            ensemble.append(round((lstm_val + xgb_val) / 2, 2))
                        elif lstm_val is not None:
                            ensemble.append(lstm_val)
                        elif xgb_val is not None:
                            ensemble.append(xgb_val)
                        else:
                            ensemble.append(None)
                    predicted['Ensemble'] = ensemble

                history['symbols'][symbol]['predicted'] = predicted
        except Exception as e:
            logger.warning(f"Could not process {symbol}: {e}")

    try:
        with open(HISTORY_JSON_FILE, 'w') as f:
            json.dump(history, f, indent=2)
        logger.info(f"Successfully exported history data to {HISTORY_JSON_FILE}")
        return True
    except Exception as e:
        logger.error(f"Error writing history JSON: {e}")
        return False


def main():
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("NEPSE Prediction Export Tool")
    logger.info("=" * 60)
    
    success = export_to_json()

    if success:
        logger.info("Exporting history data for charts")
        export_history_json()
    
    if success:
        logger.info("Export completed successfully")
    else:
        logger.error("Export failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
