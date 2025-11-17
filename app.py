import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
from streamlit_calendar import calendar
import urllib.parse
from google.oauth2.credentials import Credentials

#Rights I grant to Google
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
#Redirect to my streamlit-website after Google-Login
APP_URL = "https://projectrepo-nelb9xkappkqy6bhbwcmqwp.streamlit.app"

#If token from my previous login is still available in the session, it recreates th credentials objects so that I stay logged in (in the Google-account)
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

        time_min = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        time_max = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()

        # 🔥 Alle Kalender laden
        cal_list = service.calendarList().list().execute()
        calendars = cal_list.get("items", [])

        google_events = []

        # 🔥 Für jeden Kalender die Events abfragen
        for cal in calendars:
            cal_id = cal["id"]
            cal_summary = cal.get("summaryOverride", cal.get("summary", "Unbenannter Kalender"))

            try:
                events_result = service.events().list(
                    calendarId=cal_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=100,
                    singleEvents=True,
                    orderBy="startTime",
                ).execute()

                events = events_result.get("items", [])

                for event in events:
                    summary = f"{cal_summary}: " + event.get("summary", "Ohne Titel")
                    start = event["start"].get("dateTime", event["start"].get("date"))
                    end = event["end"].get("dateTime", event["end"].get("date"))

                    google_events.append({
                        "title": summary,
                        "start": start,
                        "end": end,
                    })

            except Exception as e:
                st.warning(f"Calendar '{cal_summary}' could not be started: {e}")

        # Sortieren nach Startzeit
        google_events.sort(key=lambda x: x["start"])

        st.subheader("Your upcoming appointments (All calendars):")

        for ev in google_events:
            st.write(ev["title"], ev["start"], ev["end"])

        st.subheader("Calendar overview")
        formatting = {
            "initialView": "timeGridWeek",
            "height": 650,
            "locale": "en",
            "weekNumbers": True,
            "selectable": True,
            "nowIndicator": True,
        }

        calendar(google_events, formatting)

    except Exception as e:
        st.error(f"Error loading calendar data: {e}")

