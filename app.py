import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
from streamlit_calendar import calendar
import urllib.parse
from google.oauth2.credentials import Credentials

from appointment_data.excel_data import load_excel_events

#Rights I grant to Google
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
#Redirect to my streamlit-website after Google-Login
APP_URL = "https://projectrepo-nelb9xkappkqy6bhbwcmqwp.streamlit.app"

#If token from my previous login is still available in the session, it recreates the credentials objects so that I stay logged in (in the Google-account)
def get_google_creds():
    if "gcal_token" in st.session_state:
        return Credentials.from_authorized_user_info(st.session_state["gcal_token"], SCOPES)
     
    #Creates an OAuth flow using Google login, using my app's client_secret and client_id and requesting access to the calendar of the user that logs in with Google
    flow = Flow.from_client_config(
        st.secrets["GOOGLE_OAUTH_CLIENT"],
        scopes=SCOPES,
        redirect_uri=APP_URL
    )

    #Check if Google redirected the user back to the app with an OAuth code
    #If yes: rebuild the redirect URL, trade the code for OAuth tokens, and save them so the user stays logged in.
    qp = st.query_params
    if "code" in qp:
        current_url = APP_URL
        if qp:
            current_url += "?" + urllib.parse.urlencode(qp, doseq=True)
        flow.fetch_token(authorization_response=current_url)
        creds = flow.credentials

        #Save the OAuth tokens in the session so the user stays logged in on reloads
        st.session_state["gcal_token"] = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
        }
        #Remove the temporary OAuth code from the URL after successful login
        st.query_params.clear()
        #Return the credentials so the app can access Google Calendar
        return creds
    else:
        #If the user is NOT logged in yet: create the Google login URL
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent"
        )
        #Show a button that sends the user to the Google login page
        st.link_button("Connect with Google", auth_url)
        #Stop the script until the user completes the login
        st.stop()

#Run the login flow: return saved Google credentials if the user is logged in, or show the Google login button and stop the app if not.
creds = get_google_creds()

#If credentials exist, the user is successfully logged in
if creds:
    try:
        #Create a Google Calendar API service object using the user's credentials
        service = build("calendar", "v3", credentials=creds)

        #Define the time window: from 1 day ago to 30 days in the future
        time_min = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        time_max = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()

        #Load all calendars that belong to the user
        cal_list = service.calendarList().list().execute()
        calendars = cal_list.get("items", [])

        #Prepare a list where all events from all calendars will be stored
        google_events = []

        # For every calendar of the user, fetch the events in the selected time window
        for cal in calendars:
            cal_id = cal["id"]
            #calendar name (custom name if available, otherwise normal summary)
            cal_summary = cal.get("summaryOverride", cal.get("summary", "Unknown calendar"))

            try:
                #Request up to 100 events from this calendar between time_min and time_max
                events_result = service.events().list(
                    calendarId=cal_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=100,
                    #expand recurring events into single instances
                    singleEvents=True,
                    #sort events by start time
                    orderBy="startTime",
                ).execute()

                #Get the actual list of events from the API response
                events = events_result.get("items", [])

                #Convert each Google event into a simple dictionary for our app
                for event in events:
                    #Show from which calendar the event comes + the event title
                    summary = f"{cal_summary}: " + event.get("summary", "without titel")
                    #Use dateTime if available, otherwise all-day date
                    start = event["start"].get("dateTime", event["start"].get("date"))
                    end = event["end"].get("dateTime", event["end"].get("date"))

                    #Add the event to the unified list used for display and the calendar widget
                    google_events.append({
                        "title": summary,
                        "start": start,
                        "end": end,
                    })

            #If this calendar cannot be read, show a warning but continue with the others
            except Exception as e:
                st.warning(f"Calendar '{cal_summary}' could not be started: {e}")

        #Sort all collected events from all calendars by their start time
        google_events.sort(key=lambda x: x["start"])


        excel_events = load_excel events()
        all_events = google_events + excel_events
        all_events.sort(key=lambda x: x["start"])



        #Show a visual calendar overview using streamlit-calendar
        st.subheader("Calendar overview")
        formatting = {
            "initialView": "timeGridWeek",
            "height": 650,
            "locale": "en",
            "weekNumbers": True,
            "selectable": True,
            "nowIndicator": True,
        }

        #Display all events in an interactive calendar view
        calendar(all_events, formatting)

    #If anything goes wrong in the whole calendar loading process, show an error message
    except Exception as e:
        st.error(f"Error loading calendar data: {e}")








