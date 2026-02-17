#!/usr/bin/env python3
"""
Export backtest history for past N days (actual vs predicted close).
Writes web/data/backtest_history.json for charting.
"""

import os
import json
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from xgboost import XGBRegressor

WINDOW_SIZE = 60
TEST_DAYS = 60
EPOCHS = 8
BATCH_SIZE = 32

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
WEB_DATA_DIR = os.path.join(SCRIPT_DIR, "..", "web", "data")
OUTPUT_PATH = os.path.join(WEB_DATA_DIR, "backtest_history.json")


def build_lstm_predictions(df_train, df_test):
    data = df_train[["open", "high", "low", "close"]].values
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    X, y = [], []
    for i in range(WINDOW_SIZE, len(scaled_data)):
        X.append(scaled_data[i - WINDOW_SIZE:i])
        y.append(scaled_data[i])

    X = np.array(X)
    y = np.array(y)

    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=(WINDOW_SIZE, 4)),
        Dropout(0.2),
        LSTM(32),
        Dropout(0.2),
        Dense(16, activation="relu"),
        Dense(4),
    ])

    model.compile(optimizer=Adam(learning_rate=0.001), loss="mse")
    model.fit(X, y, epochs=EPOCHS, batch_size=BATCH_SIZE, verbose=0)

    predictions = []
    last_sequence = scaled_data[-WINDOW_SIZE:]

    for _, row in df_test.iterrows():
        pred_scaled = model.predict(last_sequence.reshape(1, WINDOW_SIZE, 4), verbose=0)
        pred = scaler.inverse_transform(pred_scaled)[0]
        predictions.append(float(pred[3]))

        next_actual = row[["open", "high", "low", "close"]].values
        next_scaled = scaler.transform([next_actual])[0]
        last_sequence = np.vstack([last_sequence[1:], next_scaled])

    return predictions


def build_xgb_predictions(df_train, df_test):
    features_df = df_train[["close"]].copy()
    for lag in range(1, WINDOW_SIZE + 1):
        features_df[f"close_lag{lag}"] = features_df["close"].shift(lag)

    features_df = features_df.dropna()
    feature_cols = [col for col in features_df.columns if col.startswith("close_lag")]

    X_train = features_df[feature_cols].values
    y_train = features_df["close"].shift(-1).dropna().values
    X_train = X_train[:-1]

    model = XGBRegressor(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
        subsample=0.9,
        colsample_bytree=0.9,
    )
    model.fit(X_train, y_train, verbose=False)

    predictions = []
    last_features = X_train[-1].copy()

    for _, row in df_test.iterrows():
        pred_close = model.predict(last_features.reshape(1, -1))[0]
        predictions.append(float(pred_close))

        actual_close = float(row["close"])
        last_features = np.roll(last_features, 1)
        last_features[0] = actual_close

    return predictions


def export_backtest_history():
    history = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "days": TEST_DAYS,
        "symbols": {}
    }

    if not os.path.exists(DATA_DIR):
        print(f"No data directory found: {DATA_DIR}")
        return False

    for filename in os.listdir(DATA_DIR):
        if not filename.lower().endswith(".csv"):
            continue

        symbol = os.path.splitext(filename)[0]
        csv_path = os.path.join(DATA_DIR, filename)

        try:
            df = pd.read_csv(csv_path)
            if "date" not in df.columns or "close" not in df.columns:
                continue

            df["date"] = pd.to_datetime(df["date"], unit="s", errors="coerce")
            df = df.dropna(subset=["date", "open", "high", "low", "close"])
            df = df.sort_values("date").reset_index(drop=True)

            if len(df) < WINDOW_SIZE + TEST_DAYS + 5:
                continue

            df_test = df.tail(TEST_DAYS).reset_index(drop=True)
            df_train = df.iloc[:-TEST_DAYS].reset_index(drop=True)

            lstm_pred = build_lstm_predictions(df_train, df_test)
            xgb_pred = build_xgb_predictions(df_train, df_test)

            dates = df_test["date"].dt.strftime("%Y-%m-%d").tolist()
            actual_close = [round(value, 2) for value in df_test["close"].tolist()]

            ensemble = []
            for i in range(len(dates)):
                lstm_val = lstm_pred[i] if i < len(lstm_pred) else None
                xgb_val = xgb_pred[i] if i < len(xgb_pred) else None
                if lstm_val is not None and xgb_val is not None:
                    ensemble.append(round((lstm_val + xgb_val) / 2, 2))
                elif lstm_val is not None:
                    ensemble.append(round(lstm_val, 2))
                elif xgb_val is not None:
                    ensemble.append(round(xgb_val, 2))
                else:
                    ensemble.append(None)

            history["symbols"][symbol] = {
                "dates": dates,
                "close": actual_close,
                "predicted": {
                    "LSTM": [round(value, 2) for value in lstm_pred],
                    "XGBoost": [round(value, 2) for value in xgb_pred],
                    "Ensemble": ensemble,
                },
            }
            print(f"Backtest ready: {symbol} ({len(dates)} days)")
        except Exception as e:
            print(f"Backtest failed for {symbol}: {e}")

    os.makedirs(WEB_DATA_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    print(f"Wrote {OUTPUT_PATH}")
    return True


def main():
    export_backtest_history()


if __name__ == "__main__":
    main()
