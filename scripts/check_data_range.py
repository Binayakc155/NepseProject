import pandas as pd
from datetime import datetime

# Check NABIL data
df = pd.read_csv('data/NABIL.csv')
df['date'] = pd.to_datetime(df['date'], unit='s')

print(f"NABIL Stock Data:")
print(f"  Total rows: {len(df)}")
print(f"  Start date: {df['date'].min().strftime('%Y-%m-%d')}")
print(f"  End date: {df['date'].max().strftime('%Y-%m-%d')}")
print(f"  Total days span: {(df['date'].max() - df['date'].min()).days} days")
print(f"  Trading days: {len(df)} days")
