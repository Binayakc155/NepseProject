import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from xgboost import XGBRegressor
import os
import json

WINDOW_SIZE = 60

def backtest_lstm_vs_xgboost(symbol, test_days=30):
    """
    Backtest LSTM and XGBoost on last N days of data
    Returns accuracy metrics for both models
    """
    
    print(f"\n{'='*70}")
    print(f"BACKTESTING {symbol} - Last {test_days} days")
    print(f"{'='*70}\n")
    
    # Load data
    csv_path = f"data/{symbol}.csv"
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'], unit='s')
    df = df.sort_values('date').reset_index(drop=True)
    
    # Use last test_days for backtesting
    df_test = df.tail(test_days).reset_index(drop=True)
    df_train = df.iloc[:-test_days].reset_index(drop=True)
    
    print(f"Training data: {len(df_train)} days")
    print(f"Testing data: {len(df_test)} days")
    
    # =================== LSTM BACKTEST ===================
    print(f"\nLSTM Backtest...")
    
    # Prepare LSTM data
    data = df_train[['open', 'high', 'low', 'close']].values
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)
    
    # Create sequences
    X, y = [], []
    for i in range(WINDOW_SIZE, len(scaled_data)):
        X.append(scaled_data[i-WINDOW_SIZE:i])
        y.append(scaled_data[i])
    
    X = np.array(X)
    y = np.array(y)
    
    # Build LSTM
    model = Sequential([
        LSTM(128, return_sequences=True, input_shape=(WINDOW_SIZE, 4)),
        Dropout(0.2),
        LSTM(64, return_sequences=True),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(4)
    ])
    
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
    model.fit(X, y, epochs=20, batch_size=32, verbose=0)
    
    # Test LSTM on unseen data
    lstm_predictions = []
    last_sequence = scaled_data[-WINDOW_SIZE:]
    
    for i in range(len(df_test)):
        pred_scaled = model.predict(last_sequence.reshape(1, WINDOW_SIZE, 4), verbose=0)
        pred = scaler.inverse_transform(pred_scaled)[0]
        lstm_predictions.append(pred)
        
        # Update sequence with actual next day for next prediction
        next_actual = df_test.iloc[i][['open', 'high', 'low', 'close']].values
        next_scaled = scaler.transform([next_actual])[0]
        last_sequence = np.vstack([last_sequence[1:], next_scaled])
    
    lstm_predictions = np.array(lstm_predictions)
    
    # =================== XGBOOST BACKTEST ===================
    print(f"XGBoost Backtest...")
    
    # Prepare XGBoost data
    features_df = df_train[['open', 'high', 'low', 'close', 'volume']].copy()
    
    for lag in range(1, WINDOW_SIZE + 1):
        features_df[f'open_lag{lag}'] = features_df['open'].shift(lag)
        features_df[f'close_lag{lag}'] = features_df['close'].shift(lag)
        features_df[f'high_lag{lag}'] = features_df['high'].shift(lag)
        features_df[f'low_lag{lag}'] = features_df['low'].shift(lag)
    
    features_df = features_df.dropna()
    
    feature_cols = [col for col in features_df.columns if col.startswith(('open_lag', 'close_lag', 'high_lag', 'low_lag'))]
    
    X_train_xgb = features_df[feature_cols].values
    y_open_train = features_df['open'].shift(-1).dropna().values
    y_high_train = features_df['high'].shift(-1).dropna().values
    y_low_train = features_df['low'].shift(-1).dropna().values
    y_close_train = features_df['close'].shift(-1).dropna().values
    
    X_train_xgb = X_train_xgb[:-1]  # Align with shifted targets
    
    # Train XGBoost models
    xgb_models = {
        'open': XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42),
        'high': XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42),
        'low': XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42),
        'close': XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42)
    }
    
    xgb_models['open'].fit(X_train_xgb, y_open_train, verbose=False)
    xgb_models['high'].fit(X_train_xgb, y_high_train, verbose=False)
    xgb_models['low'].fit(X_train_xgb, y_low_train, verbose=False)
    xgb_models['close'].fit(X_train_xgb, y_close_train, verbose=False)
    
    # Test XGBoost
    xgb_predictions = []
    last_features = X_train_xgb[-1].copy()
    
    for i in range(len(df_test)):
        pred_open = xgb_models['open'].predict(last_features.reshape(1, -1))[0]
        pred_high = xgb_models['high'].predict(last_features.reshape(1, -1))[0]
        pred_low = xgb_models['low'].predict(last_features.reshape(1, -1))[0]
        pred_close = xgb_models['close'].predict(last_features.reshape(1, -1))[0]
        
        xgb_predictions.append([pred_open, pred_high, pred_low, pred_close])
        
        # Update features with actual values
        actual = df_test.iloc[i][['open', 'high', 'low', 'close']].values
        new_feature_row = np.concatenate([actual, actual, actual, actual])  # Simplified
        last_features = np.roll(last_features, -4)
        last_features[-4:] = new_feature_row[:4]
    
    xgb_predictions = np.array(xgb_predictions)
    
    # =================== EVALUATE ===================
    actual_values = df_test[['open', 'high', 'low', 'close']].values
    
    print(f"\n{'='*70}")
    print(f"ACCURACY COMPARISON (MAE - Lower is Better)")
    print(f"{'='*70}\n")
    
    columns = ['Open', 'High', 'Low', 'Close']
    results = {
        'LSTM': {},
        'XGBoost': {}
    }
    
    for col_idx, col_name in enumerate(columns):
        lstm_mae = mean_absolute_error(actual_values[:, col_idx], lstm_predictions[:, col_idx])
        xgb_mae = mean_absolute_error(actual_values[:, col_idx], xgb_predictions[:, col_idx])
        
        lstm_rmse = np.sqrt(mean_squared_error(actual_values[:, col_idx], lstm_predictions[:, col_idx]))
        xgb_rmse = np.sqrt(mean_squared_error(actual_values[:, col_idx], xgb_predictions[:, col_idx]))
        
        results['LSTM'][col_name] = {'MAE': lstm_mae, 'RMSE': lstm_rmse}
        results['XGBoost'][col_name] = {'MAE': xgb_mae, 'RMSE': xgb_rmse}
        
        winner = "LSTM WINS" if lstm_mae < xgb_mae else "XGBOOST WINS"
        
        print(f"{col_name:8}")
        print(f"  LSTM:    MAE={lstm_mae:8.4f}  RMSE={lstm_rmse:8.4f}")
        print(f"  XGBoost: MAE={xgb_mae:8.4f}  RMSE={xgb_rmse:8.4f}  {winner}")
        print()
    
    # Overall winner
    lstm_total_mae = sum([results['LSTM'][col]['MAE'] for col in columns])
    xgb_total_mae = sum([results['XGBoost'][col]['MAE'] for col in columns])
    
    print(f"{'='*70}")
    print(f"OVERALL WINNER:")
    if lstm_total_mae < xgb_total_mae:
        print(f"   LSTM is more accurate (Total MAE: {lstm_total_mae:.4f})")
        print(f"     Use LSTM predictions for {symbol}")
    else:
        print(f"   XGBoost is more accurate (Total MAE: {xgb_total_mae:.4f})")
        print(f"     Use XGBoost predictions for {symbol}")
    print(f"{'='*70}\n")
    
    return {
        'symbol': symbol,
        'lstm_mae': lstm_total_mae,
        'xgb_mae': xgb_total_mae,
        'winner': 'LSTM' if lstm_total_mae < xgb_total_mae else 'XGBoost'
    }

if __name__ == "__main__":
    # Diverse stocks from different sectors
    symbols = [
        # Index
        "NEPSE",
        # Commercial Banks
        "NABIL", "NICA", "SBI", "EBL", "KBL", "ADBL",
        # Hydro Power
        "CHCL", "UPPER", "NHPC", "API", "SHPC",
        # Finance Companies
        "GUFL", "GFCL",
        # Insurance
        "NLIC", "SICL", "HGI",
        # Hotels
        "OHL", "SHL",
        # Manufacturing
        "UNL"
    ]
    
    summary = []
    
    for symbol in symbols:
        try:
            result = backtest_lstm_vs_xgboost(symbol, test_days=30)
            summary.append(result)
        except Exception as e:
            print(f"Error backtesting {symbol}: {e}")
            import traceback
            traceback.print_exc()
    
    if summary:
        print(f"\n{'='*70}")
        print(f"FINAL RECOMMENDATION")
        print(f"{'='*70}\n")
        for s in summary:
            print(f"{s['symbol']:8} → Use {s['winner']}")
            print(f"   LSTM MAE: {s['lstm_mae']:.4f} | XGBoost MAE: {s['xgb_mae']:.4f}")
        print()
        
        # Save accuracy data to JSON for dashboard
        accuracy_data = {}
        for s in summary:
            accuracy_data[s['symbol']] = {
                'lstm_mae': round(s['lstm_mae'], 4),
                'xgboost_mae': round(s['xgb_mae'], 4),
                'better_model': s['winner'],
                'accuracy_diff': round(abs(s['lstm_mae'] - s['xgb_mae']), 4)
            }
        
        predictions_dir = os.path.join(os.path.dirname(__file__), "predictions")
        os.makedirs(predictions_dir, exist_ok=True)
        accuracy_file = os.path.join(predictions_dir, "model_accuracy.json")
        
        with open(accuracy_file, 'w') as f:
            json.dump(accuracy_data, f, indent=2)
        
        print(f"Saved accuracy data to: {accuracy_file}")
        print(f"   Run 'python export_predictions.py' to update dashboard\n")
