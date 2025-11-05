import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar

st.set_page_config(page_title="SGBT Events Kalender", layout="wide")

st.title("🎉 Veranstaltungen – St.Gallen-Bodensee Tourismus (Open Data)")

CSV_URL = "https://opendata.sgbt.contentdesk.io/api/Event.csv"

@st.cache_data(ttl=3600)
def load_events():
    df = pd.read_csv(CSV_URL)
    return df

try:
    df = load_events()
except Exception as e:
    st.error(f"Fehler beim Laden der Eventdaten: {e}")
    st.stop()

st.success(f"{len(df)} Events erfolgreich geladen!")

possible_columns = df.columns.str.lower()
date_cols = [c for c in df.columns if "date" in c.lower()]
title_col = next((c for c in df.columns if "title" in c.lower()), None)
end_date_col = next((c for c in df.columns if "end" in c.lower() and "date" in c.lower()), None)
start_date_col = next((c for c in df.columns if "start" in c.lower() or "datefrom" in c.lower()), None)

if not (title_col and start_date_col):
    st.error("Konnte keine Spalten für Titel und Startdatum finden.")
    st.dataframe(df.head())
    st.stop()

events = []
for _, row in df.iterrows():
    try:
        title = str(row[title_col])
        start = pd.to_datetime(row[start_date_col])
        end = pd.to_datetime(row[end_date_col]) if end_date_col and not pd.isna(row[end_date_col]) else start
    except Exception:
        continue

    events.append({
        "title": title,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "color": "#007ACC"
    })

calendar_options = {
    "initialView": "dayGridMonth",
    "locale": "de",
    "height": 650
}

calendar(events=events, options=calendar_options)

with st.expander("📊 Rohdaten anzeigen"):
    st.dataframe(df.head())

st.caption("Datenquelle: [opendata.sgbt.contentdesk.io](https://opendata.sgbt.contentdesk.io/api/Event.csv)")
