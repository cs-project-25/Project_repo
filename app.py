import sys
import streamlit as st
from streamlit_calendar import calendar
import datetime as dt

st.title("calendar")

if "base_now" not in st.session_state:
    st.session_state.base_now = dt.datetime.now().replace(microsecond=0)
base = st.session_state.base_now


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


cal_options = {
    "initialView": "dayGridMonth",   # Monatsansicht
    "height": 650,
    "locale": "en",
    "weekNumbers": True,
    "selectable": True,
}

calendar(events=events, options=cal_options)












