import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import schedule
import time
from scripts.scrape_stock import scrape_stock
import os

# List of 15 stocks + NEPSE index
stocks = [
    "NEPSE",
    "NABIL","NICA","NTC","KBL","HBL",
    "EBL","ADBL","NMB","GBIME","PRVU",
    "SHIVM","UPPER","HDHPC","API","CHCL"
]

def update_and_predict(symbol):
    # Step 1: Scrape latest data
    print(f"Fetching latest data for {symbol}...")
    scrape_stock(symbol)

    # Step 2: Load dataset
    df = pd.read_csv(f"data/{symbol}.csv")
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values('date', inplace=True)

    # Step 3: Feature engineering (previous close)
    df['prev_close'] = df['close'].shift(1)
    df.dropna(inplace=True)

    # Step 4: Train simple RandomForest model
    X = df[['prev_close']]
    y = df['close']
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Step 5: Predict next-day close
    latest = df.iloc[-1]['close']
    prediction = model.predict([[latest]])[0]

    print(f"Predicted next-day close for {symbol}: {prediction:.2f}")

    # Step 6: Save prediction
    os.makedirs("data", exist_ok=True)
    pred_file = "data/predictions.csv"
    if os.path.exists(pred_file):
        preds_df = pd.read_csv(pred_file)
    else:
        preds_df = pd.DataFrame(columns=["symbol","predicted_close","date"])

    new_row = {"symbol": symbol, "predicted_close": prediction, "date": pd.Timestamp.now().date()}
    preds_df = pd.concat([preds_df, pd.DataFrame([new_row])], ignore_index=True)
    preds_df.to_csv(pred_file, index=False)

# Schedule task after market close at 15:10 (3:10 PM)
for day in ["monday","tuesday","wednesday","thursday","friday"]:
    for symbol in stocks:
        schedule.every().__getattribute__(day).at("15:10").do(update_and_predict, symbol=symbol)

print("Automation started... waiting for scheduled tasks.")
while True:
    schedule.run_pending()
    time.sleep(60)
