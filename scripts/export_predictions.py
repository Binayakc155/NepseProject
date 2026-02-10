import json
import os
from datetime import datetime

import pandas as pd


def load_latest_predictions(csv_path, model_name):
    if not os.path.exists(csv_path):
        return {}

    df = pd.read_csv(csv_path)
    if df.empty:
        return {}

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    else:
        df["date"] = pd.Timestamp.now()

    df = df.sort_values("date")
    latest = df.groupby("symbol", as_index=False).tail(1)

    results = {}
    for _, row in latest.iterrows():
        results[row["symbol"]] = {
            "model": model_name,
            "date": row.get("date").strftime("%Y-%m-%d") if pd.notna(row.get("date")) else "",
            "today_close": float(row.get("today_close", "nan")),
            "predicted_open": float(row.get("predicted_open", "nan")),
            "predicted_high": float(row.get("predicted_high", "nan")),
            "predicted_low": float(row.get("predicted_low", "nan")),
            "predicted_close": float(row.get("predicted_close", "nan")),
            "change": float(row.get("change", "nan")),
            "change_pct": float(row.get("change_pct", "nan")),
        }

    return results


def load_model_accuracy():
    """Load model accuracy data from backtest results."""
    base_dir = os.path.dirname(__file__)
    accuracy_file = os.path.join(base_dir, "predictions", "model_accuracy.json")
    
    if not os.path.exists(accuracy_file):
        print(f"ℹ️  No accuracy file found at {accuracy_file}")
        print("   Run 'python backtest_comparison.py' to generate accuracy data.")
        return {}
    
    try:
        with open(accuracy_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Could not load accuracy data: {e}")
        return {}


def add_accuracy_info(predictions_dict, accuracy_data):
    """Add accuracy info (recommended model, MAE) to each stock's predictions."""
    for symbol, pred_data in predictions_dict.items():
        if symbol in accuracy_data:
            acc = accuracy_data[symbol]
            pred_data["recommended_model"] = acc.get("better_model", "Ensemble")
            pred_data["lstm_mae"] = acc.get("lstm_mae")
            pred_data["xgboost_mae"] = acc.get("xgboost_mae")
        else:
            pred_data["recommended_model"] = "Ensemble"
            pred_data["lstm_mae"] = None
            pred_data["xgboost_mae"] = None
    return predictions_dict


def build_ensemble(lstm_data, xgb_data):
    symbols = set(lstm_data.keys()) | set(xgb_data.keys())
    ensemble = {}

    for symbol in symbols:
        l = lstm_data.get(symbol)
        x = xgb_data.get(symbol)

        if l and x:
            today_close = l.get("today_close", x.get("today_close"))
            predicted_open = (l["predicted_open"] + x["predicted_open"]) / 2
            predicted_high = (l["predicted_high"] + x["predicted_high"]) / 2
            predicted_low = (l["predicted_low"] + x["predicted_low"]) / 2
            predicted_close = (l["predicted_close"] + x["predicted_close"]) / 2
        elif l:
            today_close = l.get("today_close")
            predicted_open = l["predicted_open"]
            predicted_high = l["predicted_high"]
            predicted_low = l["predicted_low"]
            predicted_close = l["predicted_close"]
        elif x:
            today_close = x.get("today_close")
            predicted_open = x["predicted_open"]
            predicted_high = x["predicted_high"]
            predicted_low = x["predicted_low"]
            predicted_close = x["predicted_close"]
        else:
            continue

        change = predicted_close - today_close if today_close == today_close else float("nan")
        change_pct = (change / today_close) * 100 if today_close not in (None, 0) else float("nan")

        ensemble[symbol] = {
            "model": "Ensemble",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "today_close": today_close,
            "predicted_open": predicted_open,
            "predicted_high": predicted_high,
            "predicted_low": predicted_low,
            "predicted_close": predicted_close,
            "change": change,
            "change_pct": change_pct,
        }

    return ensemble


def main():
    base_dir = os.path.dirname(__file__)
    lstm_csv = os.path.join(base_dir, "predictions", "lstm_predictions.csv")
    xgb_csv = os.path.join(base_dir, "predictions", "xgboost_predictions.csv")

    print("📊 Loading predictions...")
    lstm_data = load_latest_predictions(lstm_csv, "LSTM")
    xgb_data = load_latest_predictions(xgb_csv, "XGBoost")
    ensemble = build_ensemble(lstm_data, xgb_data)

    print("🎯 Loading model accuracy data...")
    accuracy_data = load_model_accuracy()

    print("⭐ Adding accuracy recommendations...")
    lstm_data = add_accuracy_info(lstm_data, accuracy_data)
    xgb_data = add_accuracy_info(xgb_data, accuracy_data)
    ensemble = add_accuracy_info(ensemble, accuracy_data)

    symbols = sorted(set(list(lstm_data.keys()) + list(xgb_data.keys())))

    output = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "symbols": symbols,
        "models": {
            "LSTM": lstm_data,
            "XGBoost": xgb_data,
            "Ensemble": ensemble,
        },
    }

    web_data_dir = os.path.join(base_dir, "..", "web", "data")
    os.makedirs(web_data_dir, exist_ok=True)
    output_path = os.path.join(web_data_dir, "predictions.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"✅ Wrote {output_path}")
    if accuracy_data:
        print(f"   Including accuracy data for {len(accuracy_data)} stocks")
    else:
        print("   ℹ️  No accuracy data (run backtest_comparison.py to generate)")


if __name__ == "__main__":
    main()
