from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import streamlit as st

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

from google_auth_oauthlib.flow import Flow
import streamlit as st

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def get_creds():
    client_config = st.secrets["GOOGLE_OAUTH_CLIENT"]
    flow = Flow.from_client_config(client_config, scopes=SCOPES)

    # Hier explizit die Redirect-URI setzen, damit Google zufrieden ist
    flow.redirect_uri = client_config["web"]["redirect_uris"][0]

    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true')

    st.write("Bitte öffne diesen Link in einem neuen Tab und melde dich bei Google an:")
    st.markdown(f"[🔗 Google Login Link]({auth_url})")
    code = st.text_input("Füge hier den Autorisierungscode ein:")

    if code:
        try:
            flow.fetch_token(code=code)
            st.success("Login erfolgreich!")
            return flow.credentials
        except Exception as e:
            st.error(f"Fehler beim Login: {e}")
    return None



st.title("Team-Kalender")

if st.button("Mit Google verbinden"):
    creds = get_creds()
    st.success("Login erfolgreich!")






from datetime import datetime, timedelta

# Google Calendar API-Client aufbauen
service = build("calendar", "v3", credentials=creds)

# Nächste 7 Tage abrufen
now = datetime.utcnow().isoformat() + "Z"  # 'Z' = UTC-Zeit
in_one_week = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"

events_result = (
    service.events()
    .list(
        calendarId="primary",
        timeMin=now,
        timeMax=in_one_week,
        maxResults=10,
        singleEvents=True,
        orderBy="startTime",
    )
    .execute()
)
events = events_result.get("items", [])

# Anzeige in Streamlit
if not events:
    st.info("Keine Termine in den nächsten 7 Tagen gefunden.")
else:
    st.subheader("📅 Deine nächsten Termine:")
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        st.write(f"**{event['summary']}** – {start}")




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

































