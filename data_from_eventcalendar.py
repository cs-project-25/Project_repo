import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar

st.set_page_config(page_title="SGBT Events Kalender", layout="wide")

st.title("Veranstaltungen – St.Gallen-Bodensee Tourismus (Open Data)")

CSV_URL = "https://opendata.sgbt.contentdesk.io/api/Event.csv"

@st.cache_data(ttl=3600)
def load_events():
    # robuster CSV-Import
    df = pd.read_csv(
        CSV_URL,
        sep=";",                # Trennzeichen ist oft Semikolon statt Komma
        quotechar='"',          # Felder können Anführungszeichen enthalten
        encoding="utf-8",       # sicherstellen, dass Umlaute korrekt sind
        on_bad_lines="skip"     # Zeilen mit fehlerhafter Struktur überspringen
    )
    return df

try:
    df = load_events()
except Exception as e:
    st.error(f"Fehler beim Laden der Eventdaten: {e}")
    st.stop()

st.success(f"{len(df)} Events erfolgreich geladen!")

df.columns = df.columns.str.strip()

title_col = next((c for c in df.columns if "title" in c.lower() or "name" in c.lower()), None)
start_date_col = next((c for c in df.columns if "start" in c.lower() or "from" in c.lower() or "date" in c.lower()), None)
end_date_col = next((c for c in df.columns if "end" in c.lower() or "to" in c.lower()), None)

if not (title_col and start_date_col):
    st.error("Konnte keine Spalten für Titel und Startdatum finden.")
    st.dataframe(df.head())
    st.stop()

events = []
for _, row in df.iterrows():
    try:
        title = str(row[title_col])
        start = pd.to_datetime(row[start_date_col], errors="coerce")
        if pd.isna(start):
            continue
        end = pd.to_datetime(row[end_date_col], errors="coerce") if end_date_col else start
        if pd.isna(end):
            end = start
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
