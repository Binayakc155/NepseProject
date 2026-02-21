import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
import os

# LSTM window size (number of days to look back)
WINDOW_SIZE = 60

def prepare_data(df, window_size=60):
    """
    Prepare data for multi-output LSTM (predicts open, high, low, close)
    """
    # Convert Unix timestamp to datetime
    df['date'] = pd.to_datetime(df['date'], unit='s')
    df = df.sort_values('date').reset_index(drop=True)
    
    # Select features: open, high, low, close
    features = ['open', 'high', 'low', 'close']
    data = df[features].values
    
    # Normalize data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)
    
    # Create sequences
    X, y = [], []
    for i in range(window_size, len(scaled_data)):
        X.append(scaled_data[i-window_size:i])  # Last 60 days
        y.append(scaled_data[i])  # Next day values
    
    X = np.array(X)
    y = np.array(y)
    
    return X, y, scaler

def build_lstm_model(input_shape):
    """
    Build LSTM model with 4 outputs (open, high, low, close)
    """
    model = Sequential([
        LSTM(128, return_sequences=True, input_shape=input_shape),
        Dropout(0.2),
        LSTM(64, return_sequences=True),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(16, activation='relu'),
        Dense(4)  # Output: open, high, low, close
    ])
    
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
    return model

def train_and_predict(symbol, epochs=50, batch_size=32):
    """
    Train LSTM and predict tomorrow's prices
    """
    print(f"\n{'='*60}")
    print(f"Predicting for {symbol}")
    print(f"{'='*60}")
    
    # Load data
    csv_path = f"data/{symbol}.csv"
    if not os.path.exists(csv_path):
        print(f"Data file not found: {csv_path}")
        return None
    
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} days of data")
    
    # Prepare data
    X, y, scaler = prepare_data(df, WINDOW_SIZE)
    print(f"Prepared {len(X)} training sequences")
    
    # Split into train and test
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Build and train model
    model = build_lstm_model((X.shape[1], X.shape[2]))
    print(f"\nTraining LSTM model...")
    
    history = model.fit(
        X_train, y_train,
        validation_data=(X_test, y_test),
        epochs=epochs,
        batch_size=batch_size,
        verbose=1
    )
    
    # Evaluate
    test_loss, test_mae = model.evaluate(X_test, y_test, verbose=0)
    print(f"\nTest Loss: {test_loss:.6f}")
    print(f"Test MAE: {test_mae:.6f}")
    
    # Predict tomorrow
    last_sequence = X[-1].reshape(1, WINDOW_SIZE, 4)
    prediction_scaled = model.predict(last_sequence, verbose=0)
    prediction = scaler.inverse_transform(prediction_scaled)[0]
    
    # Get today's actual values
    today = df.iloc[-1]
    
    # Display predictions
    print(f"\n{'='*60}")
    print(f"TOMORROW'S PREDICTION for {symbol}")
    print(f"{'='*60}")
    print(f"Today's Close:      Rs. {today['close']:.2f}")
    print(f"\nPredicted Tomorrow:")
    print(f"  Open:             Rs. {prediction[0]:.2f}")
    print(f"  High:             Rs. {prediction[1]:.2f}")
    print(f"  Low:              Rs. {prediction[2]:.2f}")
    print(f"  Close:            Rs. {prediction[3]:.2f}")
    
    # Calculate expected change
    change = prediction[3] - today['close']
    change_pct = (change / today['close']) * 100
    print(f"\nExpected Change:    Rs. {change:+.2f} ({change_pct:+.2f}%)")
    
    if change > 0:
        print(f"Trend: BULLISH")
    elif change < 0:
        print(f"Trend: BEARISH")
    else:
        print(f"Trend: NEUTRAL")
    
    print(f"{'='*60}\n")
    
    # Save prediction
    save_prediction(symbol, prediction, today['close'])
    
    return {
        'symbol': symbol,
        'predicted_open': prediction[0],
        'predicted_high': prediction[1],
        'predicted_low': prediction[2],
        'predicted_close': prediction[3],
        'today_close': today['close'],
        'change': change,
        'change_pct': change_pct
    }

def save_prediction(symbol, prediction, today_close):
    """
    Save predictions to CSV
    """
    os.makedirs("predictions", exist_ok=True)
    pred_file = "predictions/lstm_predictions.csv"
    
    new_row = {
        "date": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "symbol": symbol,
        "today_close": today_close,
        "predicted_open": prediction[0],
        "predicted_high": prediction[1],
        "predicted_low": prediction[2],
        "predicted_close": prediction[3],
        "change": prediction[3] - today_close,
        "change_pct": ((prediction[3] - today_close) / today_close) * 100
    }
    
    if os.path.exists(pred_file):
        preds_df = pd.read_csv(pred_file)
        preds_df = pd.concat([preds_df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        preds_df = pd.DataFrame([new_row])
    
    preds_df.to_csv(pred_file, index=False)
    print(f"Prediction saved to {pred_file}")

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
    print(f"LSTM Predictions for {len(symbols)} stocks")
    print(f"{'='*60}\n")
    
    results = []
    for i, symbol in enumerate(symbols, 1):
        print(f"\n[{i}/{len(symbols)}] Processing {symbol}...")
        try:
            result = train_and_predict(symbol, epochs=30, batch_size=32)
            if result:
                results.append(result)
        except Exception as e:
            print(f"Error predicting {symbol}: {e}")
    
    # Summary
    if results:
        print(f"\n{'='*60}")
        print(f"PREDICTION SUMMARY")
        print(f"{'='*60}")
        for r in results:
            print(f"{r['symbol']:8} | Close: Rs. {r['predicted_close']:8.2f} | Change: {r['change']:+7.2f} ({r['change_pct']:+6.2f}%)")
        print(f"{'='*60}\n")

