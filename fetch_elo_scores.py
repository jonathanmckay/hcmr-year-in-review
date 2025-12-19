import json, pandas as pd, requests
from datetime import datetime

# 1) Download the daily score history (Text/Vision) JSON
url = "https://raw.githubusercontent.com/nakasyou/lmarena-history/main/output/scores.json"
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

# 4) Last 12 months (relative to "today" on your machine)
cutoff = (pd.Timestamp.today().to_period("M") - 11).to_timestamp()
month_end_12 = month_end[month_end["month"] >= cutoff].copy()

# Optional: keep only models with enough coverage
# month_end_12 = month_end_12.groupby("model_id").filter(lambda g: len(g) >= 10)

month_end_12.to_csv("lmarena_text_overall_elo_monthly_last12.csv", index=False)
print(month_end_12.head(20))
print(f"\nTotal rows: {len(month_end_12)}")
print(f"Unique models: {month_end_12['model_id'].nunique()}")
print(f"Date range: {month_end_12['month'].min()} to {month_end_12['month'].max()}")

