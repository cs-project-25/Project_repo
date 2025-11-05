import streamlit as st
import requests
from datetime import datetime
from streamlit_calendar import calendar

st.set_page_config(page_title="SGBT Events", layout="wide")

st.title("🎉 Veranstaltungen – St.Gallen-Bodensee Tourismus")

API_URL = "https://opendata.sgbt.contentdesk.io/api/v1/events"

params = {
    "limit": 50,  # Anzahl Events
    # "category": "kultur"  # Beispiel: Filter nach Kategorie
}

try:
    response = requests.get(API_URL, params=params)
    response.raise_for_status()
    data = response.json()
except Exception as e:
    st.error(f"Fehler beim Laden der API: {e}")
    st.stop()
  
events = []
for item in data.get("data", []):
    title = item.get("title", "Ohne Titel")
    start_date = item.get("start_date")
    end_date = item.get("end_date") or start_date

    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
    except Exception:
        continue

    events.append({
        "title": title,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "color": "#1E88E5"  # optional: Eventfarbe
    })

calendar_options = {
    "initialView": "dayGridMonth",
    "locale": "de",
    "height": 650
}

calendar(events=events, options=calendar_options)

st.caption("Eventdaten via Open Data SGBT API")
