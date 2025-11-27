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
        calendar(google_events, formatting, key="google_calendar_main")

    #If anything goes wrong in the whole calendar loading process, show an error message
    except Exception as e:
        st.error(f"Error loading calendar data: {e}")



#Implementation of city events and time slot searcher Natascha
from city_events_dummy import CityEventScheduler

st.write("Checking scheduler...")
try:
    scheduler = CityEventScheduler("dummy_city_events_weekly.xlsx")
    st.success("Scheduler initialized correctly")
except Exception as e:
    st.error(f"Scheduler initialization failed: {e}")

st.subheader("City Event Suggestions")

scheduler = CityEventScheduler("dummy_city_events_weekly.xlsx")

# Zeitraum auswählen
start_date = st.date_input("Start Date", datetime.now())
end_date = st.date_input("End Date", datetime.now() + timedelta(days=7))

# Button-gesteuert: Vorschläge nur bei Klick
if st.button("Find Free Time Slots and Suggest Events"):

    # --- Schritt 1: Google-Kalender Events robust in datetime konvertieren ---
    calendar_events = []
    user_events = []

    for ev in google_events:  # google_events aus deinem bisherigen Code
        start_raw = ev.get("start")
        end_raw = ev.get("end")
        try:
            # überspringe Events ohne Datum
            if start_raw is None or end_raw is None:
                continue

            # All-Day Event oder datetime
            if "T" in start_raw:
                start = datetime.fromisoformat(start_raw)
            else:
                start = datetime.fromisoformat(start_raw + "T00:00:00")

            if "T" in end_raw:
                end = datetime.fromisoformat(end_raw)
            else:
                end = datetime.fromisoformat(end_raw + "T23:59:59")

            user_events.append({"start": start, "end": end})
        except Exception as e:
            st.warning(f"Skipping invalid event: {ev}, error: {e}")

    calendar_events.append(user_events)

    # --- Schritt 2: Freie Slots berechnen ---
    free_slots = scheduler.find_common_free_slots(
        calendar_events,
        datetime.combine(start_date, datetime.min.time()),
        datetime.combine(end_date, datetime.max.time())
    )

    st.write("### Free Slots (all users)")
    if free_slots:
        for s, e in free_slots:
            st.write(f"{s} - {e}")
    else:
        st.write("No free slots available.")

    # --- Schritt 3: Stadt-Events laden und expandieren ---
    weekly_events = scheduler.load_weekly_events_excel()
    expanded_events = scheduler.expand_weekly_events(
        weekly_events,
        datetime.combine(start_date, datetime.min.time()),
        datetime.combine(end_date, datetime.max.time())
    )

    # --- Schritt 4: Vorschläge filtern ---
    suggested = scheduler.suggest_events(free_slots, expanded_events)
    st.write("### Suggested City Events")
    if not suggested.empty:
        st.dataframe(suggested)
    else:
        st.write("No events fit into the available time slots.")
        

#Implementation of visualizing calendar data Natascha

from visualization import show_visualizations
show_visualizations(google_events)





