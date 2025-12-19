import json, pandas as pd, requests
from datetime import datetime

# 1) Download the daily score history (Text/Vision) JSON
url = "https://raw.githubusercontent.com/nakasyou/lmarena-history/main/output/scores.json"
print("Fetching data from lmarena-history...")
data = requests.get(url, timeout=60).json()

# 2) Flatten: date, arena=text, category=overall, model_id, elo
rows = []
for yyyymmdd, arenas in data.items():
    if "text" not in arenas:
        continue
    text = arenas["text"]
    if "overall" not in text:
        continue
    for model_id, elo in text["overall"].items():
        rows.append((yyyymmdd, model_id, float(elo)))

df = pd.DataFrame(rows, columns=["date", "model_id", "elo"])
df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()

# 3) Month-end snapshot: last available day in each month for each model
df = df.sort_values(["model_id", "date"])
month_end = df.groupby(["month", "model_id"], as_index=False).tail(1)

# 4) Get ALL available data (full history)
month_end_all = month_end.copy()

# Save to CSV
month_end_all.to_csv("lmarena_text_overall_elo_monthly.csv", index=False)

print(f"\nData saved to lmarena_text_overall_elo_monthly.csv")
print(f"Total rows: {len(month_end_all)}")
print(f"Unique models: {month_end_all['model_id'].nunique()}")
print(f"Date range: {month_end_all['month'].min().strftime('%Y-%m')} to {month_end_all['month'].max().strftime('%Y-%m')}")
print(f"\nMonths available:")
for m in sorted(month_end_all['month'].unique()):
    count = len(month_end_all[month_end_all['month'] == m])
    print(f"  {m.strftime('%Y-%m')}: {count} models")
