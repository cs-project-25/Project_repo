import streamlit as st
import pandas as pd
import requests
import io
from datetime import datetime
from streamlit_calendar import calendar

st.set_page_config(page_title="SGBT Events Kalender", layout="wide")

st.title("🎉 Veranstaltungen – St.Gallen-Bodensee Tourismus (Open Data)")

CSV_URL = "https://opendata.sgbt.contentdesk.io/api/Event.csv"

@st.cache_data(ttl=3600)
def load_events():
    # CSV abrufen und reinigen
    response = requests.get(CSV_URL)
    response.raise_for_status()
    raw = response.text

    cleaned = []
    for line in raw.splitlines():
        if line.count('"') % 2 != 0:
            line = line.replace('"', '')  # unbalancierte Quotes entfernen
        cleaned.append(line)
    cleaned_csv = "\n".join(cleaned)

    df = pd.read_csv(
        io.StringIO(cleaned_csv),
        sep=";", 
        engine="python",
        on_bad_lines="skip",
        encoding="utf-8"
    )
    return df

try:
    df = load_events()
except Exception as e:
    st.error(f"Fehler beim Laden der Eventdaten: {e}")
    st.stop()

st.success(f"{len(df)} Events erfolgreich geladen!")

with st.expander("📋 Spaltenübersicht"):
    st.write(df.columns.tolist())

df.columns = df.columns.str.strip()

title_col = next((c for c in df.columns if "title" in c.lower() or "name" in c.lower()), None)
start_candidates = [c for c in df.columns if any(k in c.lower() for k in ["start", "from", "datum", "date"])]
end_candidates = [c for c in df.columns if any(k in c.lower() for k in ["end", "to", "bis"])]

st.write("🗓️ Erkannte Startdatum-Spalten:", start_candidates)
st.write("🏁 Erkannte Enddatum-Spalten:", end_candidates)

start_date_col = start_candidates[0] if start_candidates else None
end_date_col = end_candidates[0] if end_candidates else None

if not (title_col and start_date_col):
    st.error("❌ Konnte keine Spalten für Titel und Startdatum finden.")
    st.dataframe(df.head())
    st.stop()

def parse_date(value):
    if pd.isna(value):
        return None
    value = str(value).strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    try:
        return pd.to_datetime(value, errors="coerce")
    except Exception:
        return None

events = []
for _, row in df.iterrows():
    start = parse_date(row[start_date_col])
    if not start:
        continue
    end = parse_date(row[end_date_col]) if end_date_col else start
    if not end:
        end = start

    events.append({
        "title": str(row[title_col]),
        "start": start.isoformat(),
        "end": end.isoformat(),
        "color": "#007ACC"
    })

if not events:
    st.warning("⚠️ Keine gültigen Datumswerte gefunden – überprüfe bitte die Spaltennamen oder das Datumsformat.")
else:
    st.success(f"✅ {len(events)} Events mit gültigem Datum gefunden")

calendar_options = {
    "initialView": "dayGridMonth",
    "locale": "de",
    "height": 700,
}

calendar(events=events, options=calendar_options)

with st.expander("📊 Rohdaten anzeigen"):
    st.dataframe(df.head())

st.caption("Datenquelle: [Open Data SGBT](https://opendata.sgbt.contentdesk.io/api/Event.csv)")
