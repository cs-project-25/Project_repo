import sys
import streamlit as st
from streamlit_calendar import calendar
import datetime as dt

st.write("Python executable Streamlit is using:")
st.code(sys.executable)

st.title("calendar")




st.title("This is the calendar")

st.title("📆 Mein Kalender")

# Hier kannst du nun Events einfügen
events = [
    {
        "title": "Kickoff",
        "start": (dt.datetime.now() + dt.timedelta(days=1)).strftime("%Y-%m-%d"),
    },
    {
        "title": "Sprint Review",
        "start": (dt.datetime.now() + dt.timedelta(days=3, hours=14)).isoformat(),
        "end":   (dt.datetime.now() + dt.timedelta(days=3, hours=15)).isoformat(),
    },
]

# Optionen für die Darstellung
cal_options = {
    "initialView": "dayGridMonth",   # Monatsansicht
    "height": 650,
    "locale": "de",
    "weekNumbers": True,
    "selectable": True,
}

# 📅 Kalender anzeigen
calendar(events=events, options=cal_options)








