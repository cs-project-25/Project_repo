import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import datetime as dt


SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]



import urllib.parse
from google.oauth2.credentials import Credentials

APP_URL = "https://projectrepo-nelb9xkappkqy6bhbwcmqwp.streamlit.app"

def get_google_creds():
    if "gcal_token" in st.session_state:
        return Credentials.from_authorized_user_info(st.session_state["gcal_token"], SCOPES)


    flow = Flow.from_client_config(
        st.secrets["GOOGLE_OAUTH_CLIENT"],
        scopes=SCOPES,
        redirect_uri=APP_URL
    )

    qp = st.query_params
    if "code" in qp:
        current_url = APP_URL
        if qp:
            current_url += "?" + urllib.parse.urlencode(qp, doseq=True)
        flow.fetch_token(authorization_response=current_url)
        creds = flow.credentials

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
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent"
        )
        st.link_button("Mit Google verbinden", auth_url)
        st.stop()

creds = get_google_creds()






import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import datetime as dt


SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]



import urllib.parse
from google.oauth2.credentials import Credentials

APP_URL = "https://projectrepo-nelb9xkappkqy6bhbwcmqwp.streamlit.app"

def get_google_creds():
    if "gcal_token" in st.session_state:
        return Credentials.from_authorized_user_info(st.session_state["gcal_token"], SCOPES)

    flow = Flow.from_client_config(
        st.secrets["GOOGLE_OAUTH_CLIENT"],
        scopes=SCOPES,
        redirect_uri=APP_URL
    )

    qp = st.query_params
    if "code" in qp:
        current_url = APP_URL
        if qp:
            current_url += "?" + urllib.parse.urlencode(qp, doseq=True)
        flow.fetch_token(authorization_response=current_url)
        creds = flow.credentials

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
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent"
        )
        st.link_button("Mit Google verbinden", auth_url)
        st.stop()

creds = get_google_creds()


if creds:
    try:
        service = build("calendar", "v3", credentials=creds)

        from datetime import datetime, timedelta, timezone

        time_min = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        time_max = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()


        events_result = service.events().list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            maxResults=100,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        events = events_result.get("items", [])


        if not events:
            st.info("Keine Termine im nächsten Monat gefunden.")
        else:
            st.subheader("📅 Deine nächsten Termine:")

            google_events = []
            for event in events:
                summary = event.get("summary", "Ohne Titel")
                start = event["start"].get("dateTime", event["start"].get("date"))
                end = event["end"].get("dateTime", event["end"].get("date"))

                st.write(summary, start, end)

                google_events.append({
                    "title": summary,
                    "start": start,
                    "end": end,
                })


            st.subheader("Kalenderübersicht")
            formatting = {
                "initialView": "timeGridWeek",
                "height": 650,
                "locale": "de",
                "weekNumbers": True,
                "selectable": True,
                "nowIndicator": True,
            }
            calendar(google_events, formatting)

    except Exception as e:
        st.error(f"Fehler beim Laden der Kalenderdaten: {e}")









