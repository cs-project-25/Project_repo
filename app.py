import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import datetime as dt

# --- Google Calendar API Setup ---
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]



import urllib.parse
from google.oauth2.credentials import Credentials

APP_URL = "https://projectrepo-nelb9xkappkqy6bhbwcmqwp.streamlit.app"

def get_google_creds():
    # Wenn schon eingeloggt, gespeicherte Token wiederverwenden
    if "gcal_token" in st.session_state:
        return Credentials.from_authorized_user_info(st.session_state["gcal_token"], SCOPES)

    # Web-OAuth Flow
    flow = Flow.from_client_config(
        st.secrets["GOOGLE_OAUTH_CLIENT"],
        scopes=SCOPES,
        redirect_uri=APP_URL
    )

    qp = st.query_params
    if "code" in qp:
        # Google hat zurückgeleitet mit ?code=...
        current_url = APP_URL
        if qp:
            current_url += "?" + urllib.parse.urlencode(qp, doseq=True)
        flow.fetch_token(authorization_response=current_url)
        creds = flow.credentials

        # Token speichern für spätere Requests
        st.session_state["gcal_token"] = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
        }
        st.query_params.clear()
        return creds
    else:
        # Noch kein Login: Button anzeigen
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent"
        )
        st.link_button("Mit Google verbinden", auth_url)
        st.stop()

creds = get_google_creds()





# Nur wenn Login erfolgreich war:
if creds:
    try:
        service = build("calendar", "v3", credentials=creds)

        # Nächste 7 Tage abrufen
        now = datetime.utcnow().isoformat() + "Z"
        in_one_week = (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"

        events_result = service.events().list(
            calendarId="primary",
            timeMin=now,
            timeMax=in_one_week,
            maxResults=10,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = events_result.get("items", [])

        if not events:
            st.info("Keine Termine in den nächsten 7 Tagen gefunden.")
        else:
            st.subheader("📅 Deine nächsten Termine:")
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                st.write(f"**{event['summary']}** – {start}")

    except Exception as e:
        st.error(f"Fehler beim Laden der Kalenderdaten: {e}")


# --- Visualer Kalender ---
st.subheader("Kalenderübersicht")

if "base_now" not in st.session_state:
    st.session_state.base_now = dt.datetime.now().replace(microsecond=0)
base = st.session_state.base_now

# Beispiel-Ereignisse (können später mit echten Daten ersetzt werden)
demo_events = [
    {"title": "Kickoff", "start": (base + dt.timedelta(days=1)).strftime("%Y-%m-%d")},
    {
        "title": "Sprint Review",
        "start": (base + dt.timedelta(days=3, hours=14)).isoformat(),
        "end": (base + dt.timedelta(days=3, hours=15)).isoformat(),
        "allDay": False,
    },
]

formatting = {
    "initialView": "timeGridWeek",
    "height": 650,
    "locale": "de",
    "weekNumbers": True,
    "selectable": True,
    "nowIndicator": True,
}

calendar(demo_events, formatting)







