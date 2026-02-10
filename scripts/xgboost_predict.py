import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
import os
import json

# Window size for features
WINDOW_SIZE = 60

def create_features(df, window_size=60):
    """
    Create lag features for XGBoost
    """
    df = df.sort_values('date').reset_index(drop=True)
    features_df = df[['open', 'high', 'low', 'close', 'volume']].copy()
    
    # Create lag features (previous days)
    for lag in range(1, window_size + 1):
        features_df[f'open_lag{lag}'] = features_df['open'].shift(lag)
        features_df[f'close_lag{lag}'] = features_df['close'].shift(lag)
        features_df[f'high_lag{lag}'] = features_df['high'].shift(lag)
        features_df[f'low_lag{lag}'] = features_df['low'].shift(lag)
    
    # Create target columns (what we want to predict)
    features_df['target_open'] = features_df['open'].shift(-1)
    features_df['target_high'] = features_df['high'].shift(-1)
    features_df['target_low'] = features_df['low'].shift(-1)
    features_df['target_close'] = features_df['close'].shift(-1)
    
    # Remove NaN rows
    features_df = features_df.dropna()
    
    return features_df

def train_and_predict_xgboost(symbol, epochs=100):
    """
    Train XGBoost and predict tomorrow's prices
    """
    print(f"\n{'='*60}")
    print(f"🚀 XGBoost Prediction for {symbol}")
    print(f"{'='*60}")
    
    # Load data
    csv_path = f"data/{symbol}.csv"
    if not os.path.exists(csv_path):
        print(f"❌ Data file not found: {csv_path}")
        return None
    
    df = pd.read_csv(csv_path)
    df['date'] = pd.to_datetime(df['date'], unit='s')
    print(f"✓ Loaded {len(df)} days of data")
    
    # Create features
    features_df = create_features(df, WINDOW_SIZE)
    print(f"✓ Created features for {len(features_df)} samples")
    
    # Separate features and targets
    target_cols = ['target_open', 'target_high', 'target_low', 'target_close']
    feature_cols = [col for col in features_df.columns if col not in target_cols and col != 'date']
    
    X = features_df[feature_cols].values
    y_open = features_df['target_open'].values
    y_high = features_df['target_high'].values
    y_low = features_df['target_low'].values
    y_close = features_df['target_close'].values
    
    # Split data
    X_train, X_test, y_open_train, y_open_test = train_test_split(
        X, y_open, test_size=0.2, random_state=42
    )
    _, _, y_high_train, y_high_test = train_test_split(
        X, y_high, test_size=0.2, random_state=42
    )
    _, _, y_low_train, y_low_test = train_test_split(
        X, y_low, test_size=0.2, random_state=42
    )
    _, _, y_close_train, y_close_test = train_test_split(
        X, y_close, test_size=0.2, random_state=42
    )
    
    print(f"✓ Training set: {len(X_train)} | Test set: {len(X_test)}")
    
    # Train separate models for each target
    print(f"\n📊 Training XGBoost models...")
    
    models = {}
    mae_scores = {}
    
    for target, y_train, y_test in [
        ('open', y_open_train, y_open_test),
        ('high', y_high_train, y_high_test),
        ('low', y_low_train, y_low_test),
        ('close', y_close_train, y_close_test)
    ]:
        model = XGBRegressor(
            n_estimators=epochs,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            verbose=0
        )
        model.fit(X_train, y_train, verbose=False)
        
        # Evaluate
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        train_mae = np.mean(np.abs(train_pred - y_train))
        test_mae = np.mean(np.abs(test_pred - y_test))
        
        models[target] = model
        mae_scores[target] = test_mae
        print(f"  {target.upper():6} | Train MAE: {train_mae:.4f} | Test MAE: {test_mae:.4f}")
    
    # Predict tomorrow
    last_features = X[-1].reshape(1, -1)
    
    pred_open = models['open'].predict(last_features)[0]
    pred_high = models['high'].predict(last_features)[0]
    pred_low = models['low'].predict(last_features)[0]
    pred_close = models['close'].predict(last_features)[0]
    
    # Get today's actual
    today = df.iloc[-1]
    
    # Display predictions
    print(f"\n{'='*60}")
    print(f"📅 TOMORROW'S XGBOOST PREDICTION for {symbol}")
    print(f"{'='*60}")
    print(f"Today's Close:      {today['close']:.2f}")
    print(f"\nPredicted Tomorrow:")
    print(f"  Open:             {pred_open:.2f}")
    print(f"  High:             {pred_high:.2f}")
    print(f"  Low:              {pred_low:.2f}")
    print(f"  Close:            {pred_close:.2f}")
    
    # Calculate expected change
    change = pred_close - today['close']
    change_pct = (change / today['close']) * 100
    print(f"\nExpected Change:    {change:+.2f} ({change_pct:+.2f}%)")
    
    if change > 0:
        print(f"Trend: 📈 BULLISH")
    elif change < 0:
        print(f"Trend: 📉 BEARISH")
    else:
        print(f"Trend: ➡️ NEUTRAL")
    
    print(f"{'='*60}\n")
    
    # Save predictions
    save_xgboost_prediction(symbol, pred_open, pred_high, pred_low, pred_close, today['close'])
    
    return {
        'symbol': symbol,
        'model': 'XGBoost',
        'predicted_open': pred_open,
        'predicted_high': pred_high,
        'predicted_low': pred_low,
        'predicted_close': pred_close,
        'today_close': today['close'],
        'change': change,
        'change_pct': change_pct,
        'mae_close': mae_scores['close']
    }

def save_xgboost_prediction(symbol, pred_open, pred_high, pred_low, pred_close, today_close):
    """
    Save XGBoost predictions to CSV
    """
    os.makedirs("predictions", exist_ok=True)
    pred_file = "predictions/xgboost_predictions.csv"
    
    new_row = {
        "date": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "symbol": symbol,
        "today_close": today_close,
        "predicted_open": pred_open,
        "predicted_high": pred_high,
        "predicted_low": pred_low,
        "predicted_close": pred_close,
        "change": pred_close - today_close,
        "change_pct": ((pred_close - today_close) / today_close) * 100
    }
    
    if os.path.exists(pred_file):
        preds_df = pd.read_csv(pred_file)
        preds_df = pd.concat([preds_df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        preds_df = pd.DataFrame([new_row])
    
    preds_df.to_csv(pred_file, index=False)
    print(f"✓ Prediction saved to {pred_file}")

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
    
    print(f"\n{'='*60}")
    print(f"🌲 XGBoost Predictions for {len(symbols)} stocks")
    print(f"{'='*60}\n")
    
    results = []
    for i, symbol in enumerate(symbols, 1):
        print(f"\n[{i}/{len(symbols)}] Processing {symbol}...")
        try:
            result = train_and_predict_xgboost(symbol, epochs=100)
            if result:
                results.append(result)
        except Exception as e:
            print(f"❌ Error predicting {symbol}: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    if results:
        print(f"\n{'='*60}")
        print(f"🎯 XGBOOST PREDICTION SUMMARY")
        print(f"{'='*60}")
        for r in results:
            print(f"{r['symbol']:8} | Close: {r['predicted_close']:8.2f} | Change: {r['change']:+7.2f} ({r['change_pct']:+6.2f}%)")
        print(f"{'='*60}\n")
