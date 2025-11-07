from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import streamlit as st

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def get_creds():
    flow = InstalledAppFlow.from_client_config(
        st.secrets["GOOGLE_OAUTH_CLIENT"], SCOPES
    )
    creds = flow.run_console()
    return creds

st.title("Team-Kalender")

if st.button("Mit Google verbinden"):
    creds = get_creds()
    st.success("Login erfolgreich!")



import sys
import streamlit as st
from streamlit_calendar import calendar
import datetime as dt


st.title("calendar")

if "base_now" not in st.session_state:
    st.session_state.base_now = dt.datetime.now().replace(microsecond=0)
base = st.session_state.base_now

events = [{"title": "Kickoff","start": (base + dt.timedelta(days=1)).strftime("%Y-%m-%d")},{"title": "Sprint Review","start": {"title": "Sprint Review","start": (base + dt.timedelta(days=3, hours=14)).isoformat(),"end":   (base + dt.timedelta(days=3, hours=15)).isoformat(),"allDay": False,}}]

formatting = {"initialView": "timeGridWeek","height": 650,"locale": "en","weekNumbers": True,"selectable": True, "nowIndicator": True}

calendar(events, formatting)






























