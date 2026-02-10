import pandas as pd
import os

def compare_predictions():
    """
    Compare LSTM vs XGBoost predictions side by side
    """
    
    lstm_file = "predictions/lstm_predictions.csv"
    xgboost_file = "predictions/xgboost_predictions.csv"
    
    if not os.path.exists(lstm_file):
        print("❌ LSTM predictions not found. Run: python lstm_predict.py")
        return
    
    if not os.path.exists(xgboost_file):
        print("❌ XGBoost predictions not found. Run: python xgboost_predict.py")
        return
    
    # Load predictions
    lstm_df = pd.read_csv(lstm_file)
    xgboost_df = pd.read_csv(xgboost_file)
    
    print(f"\n{'='*100}")
    print(f"🎯 LSTM vs XGBOOST PREDICTION COMPARISON")
    print(f"{'='*100}\n")
    
    # Compare for each stock
    symbols = lstm_df['symbol'].unique()
    
    for symbol in symbols:
        lstm_row = lstm_df[lstm_df['symbol'] == symbol].iloc[-1]
        xgb_row = xgboost_df[xgboost_df['symbol'] == symbol].iloc[-1]
        
        print(f"\n📊 {symbol} - Tomorrow's Prediction")
        print(f"{'-'*100}")
        
        print(f"{'Metric':<15} {'Today Close':<15} {'LSTM Predict':<18} {'XGBoost Predict':<18} {'Difference':<15}")
        print(f"{'-'*100}")
        
        # Compare close prices
        today_close = lstm_row['today_close']
        lstm_close = lstm_row['predicted_close']
        xgb_close = xgb_row['predicted_close']
        diff_close = abs(lstm_close - xgb_close)
        
        print(f"{'Close Price':<15} Rs. {today_close:<14.2f} Rs. {lstm_close:<17.2f} Rs. {xgb_close:<17.2f} {diff_close:<14.2f}")
        
        # Compare open prices
        lstm_open = lstm_row['predicted_open']
        xgb_open = xgb_row['predicted_open']
        diff_open = abs(lstm_open - xgb_open)
        
        print(f"{'Open Price':<15} {'-':<15} Rs. {lstm_open:<17.2f} Rs. {xgb_open:<17.2f} {diff_open:<14.2f}")
        
        # Compare high prices
        lstm_high = lstm_row['predicted_high']
        xgb_high = xgb_row['predicted_high']
        diff_high = abs(lstm_high - xgb_high)
        
        print(f"{'High Price':<15} {'-':<15} Rs. {lstm_high:<17.2f} Rs. {xgb_high:<17.2f} {diff_high:<14.2f}")
        
        # Compare low prices
        lstm_low = lstm_row['predicted_low']
        xgb_low = xgb_row['predicted_low']
        diff_low = abs(lstm_low - xgb_low)
        
        print(f"{'Low Price':<15} {'-':<15} Rs. {lstm_low:<17.2f} Rs. {xgb_low:<17.2f} {diff_low:<14.2f}")
        
        # Compare trends
        lstm_change_pct = lstm_row['change_pct']
        xgb_change_pct = xgb_row['change_pct']
        
        print(f"\n{'Change %':<15} {'-':<15} {lstm_change_pct:+17.2f}% {xgb_change_pct:+17.2f}%")
        
        # Determine trends
        lstm_trend = "📈 BULLISH" if lstm_change_pct > 0 else "📉 BEARISH" if lstm_change_pct < 0 else "➡️ NEUTRAL"
        xgb_trend = "📈 BULLISH" if xgb_change_pct > 0 else "📉 BEARISH" if xgb_change_pct < 0 else "➡️ NEUTRAL"
        
        print(f"{'Trend':<15} {'-':<15} {lstm_trend:<18} {xgb_trend:<18}")
        
        # Recommendation
        print(f"\n💡 Recommendation:")
        if lstm_trend == xgb_trend:
            print(f"   ✓ BOTH agree: {lstm_trend}")
        else:
            print(f"   ⚠️  DISAGREEMENT: LSTM says {lstm_trend}, XGBoost says {xgb_trend}")
        
        # Average prediction (ensemble)
        ensemble_close = (lstm_close + xgb_close) / 2
        ensemble_change_pct = ((ensemble_close - today_close) / today_close) * 100
        ensemble_trend = "📈 BULLISH" if ensemble_change_pct > 0 else "📉 BEARISH" if ensemble_change_pct < 0 else "➡️ NEUTRAL"
        
        print(f"\n🎯 ENSEMBLE (Average):")
        print(f"   Close Price:    Rs. {ensemble_close:.2f}")
        print(f"   Change:         {ensemble_change_pct:+.2f}%")
        print(f"   Trend:          {ensemble_trend}")
    
    print(f"\n{'='*100}")
    print(f"💾 Predictions saved:")
    print(f"   - LSTM:    {lstm_file}")
    print(f"   - XGBoost: {xgboost_file}")
    print(f"{'='*100}\n")

if __name__ == "__main__":
    compare_predictions()
