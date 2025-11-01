import sys
import streamlit as st
from streamlit_calendar import calendar
import datetime as dt

st.title("calendar")

if "base_now" not in st.session_state:
    st.session_state.base_now = dt.datetime.now().replace(microsecond=0)
base = st.session_state.base_now

events = [{"title": "Kickoff","start": (base + dt.timedelta(days=1)).strftime("%Y-%m-%d")},{"title": "Sprint Review","start": {
        "title": "Sprint Review",
        "start": (base + dt.timedelta(days=3, hours=14)).isoformat(),  # 2025-11-04T14:00:00
        "end":   (base + dt.timedelta(days=3, hours=15)).isoformat(),  # 2025-11-04T15:00:00
        "allDay": False,}}]

formatting = {"initialView": "timeGridWeek","height": 650,"locale": "en","weekNumbers": True,"selectable": True, "nowIndicator": True}

format = ("calendar")


calendar(events, formatting)
























