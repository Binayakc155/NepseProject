import os
import pandas as pd

data_folder = "data"

files_to_check = [
    "NEPSE.csv",
    "NABIL.csv","NICA.csv","NTC.csv","KBL.csv","HBL.csv",
    "EBL.csv","ADBL.csv","NMB.csv","GBIME.csv","PRVU.csv",
    "SHIVM.csv","UPPER.csv","HDHPC.csv","API.csv","CHCL.csv"
]

for file_name in files_to_check:
    file_path = os.path.join(data_folder, file_name)
    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)
            if df.empty:
                print(f"{file_name} ❌ exists but EMPTY")
            else:
                print(f"{file_name} ✅ exists, rows: {len(df)}")
        except pd.errors.EmptyDataError:
            print(f"{file_name} ❌ exists but EMPTY or invalid format")
    else:
        print(f"{file_name} ❌ NOT found")
