import pandas as pd
from datetime import datetime
import pytz

TZ = pytz.timezone("Europe/Zurich")

def load_events_from_excel(path="data/events.xlsx"):
"""Load events excel and normalize columns.
Expected columns (case-insensitive): name, start, end, category, description, addresslocality, location
Returns DataFrame with lowercase columns and tz-aware datetimes.
"""
df = pd.read_excel(path)
df.columns = [c.strip().lower() for c in df.columns]

# required columns
required = ["name", "start", "end", "category", "description"]
for r in required:
if r not in df.columns:
raise ValueError(f"Missing column in events.xlsx: {r}")

# parse datetimes and localize to Europe/Zurich if naive
def _ensure_tz(x):
if pd.isna(x):
return pd.NaT
ts = pd.to_datetime(x)
if ts.tzinfo is None:
try:
ts = ts.tz_localize(TZ)
except Exception:
ts = TZ.localize(ts)
else:
ts = ts.tz_convert(TZ)
return ts

df["start"] = df["start"].apply(_ensure_tz)
df["end"] = df["end"].apply(_ensure_tz)

# fill optional cols
for opt in ["addresslocality", "location"]:
if opt not in df.columns:
df[opt] = ""

return df
