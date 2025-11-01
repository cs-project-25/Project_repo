import sys
import streamlit as st

st.write("Python executable Streamlit is using:")
st.code(sys.executable)

st.title("This is our app")
st.write("We connected everything")
st.write("I'm losing my nerves")
st.write("Changes can be done by collaborators")
st.write("Hello")
st.write("test4")
st.write("another test")
st.write("Best app ever!")



import streamlit as st
from streamlit_calendar import calendar
import datetime as dt

st.title("📆 Vollansicht Kalender (FullCalendar)")

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
    "initialView": "dayGridMonth",   # auch möglich: 'timeGridWeek', 'listWeek'
    "height": 650,
    "locale": "de",
    "weekNumbers": True,
    "selectable": True,
}

st.info("Klicke auf einen Tag, um ein Event zu erzeugen (Demo).")

returned = calendar(
    events=events,
    options=cal_options,
    custom_css="""
    .fc-toolbar-title { font-size: 1.25rem; }
    """
)

# Optional: Reaktion auf Klicks/Selections ausgeben
if returned and "dateClick" in returned:
    st.write("Tag geklickt:", returned["dateClick"]["dateStr"])
if returned and "eventClick" in returned:
    st.write("Event geklickt:", returned["eventClick"]["event"]["title"])


import streamlit as st

st.subheader("Google Kalender (Embed)")
google_url = "https://calendar.google.com/calendar/embed?src=DEINE_ID&ctz=Europe%2FZurich"
st.components.v1.iframe(google_url, width=900, height=650)







