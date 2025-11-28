import streamlit as st
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
from streamlit_calendar import calendar
import urllib.parse
from google.oauth2.credentials import Credentials

# WICHTIG: Importiere die Funktionen für die lokalen Events aus der Datei excel_data.py
# Stellen Sie sicher, dass sich 'excel_data.py' im selben Verzeichnis befindet.
from excel_data import load_excel_events, add_appointment

# --- 1. Google OAuth und Setup ---

# Rechte, die ich Google gewähre
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
# Redirect zur Streamlit-Website nach dem Google-Login
APP_URL = "https://projectrepo-nelb9xkappkqy6bhbwcmqwp.streamlit.app"

def get_google_creds():
    """Stellt die Google-Anmeldeinformationen wieder her oder initiiert den OAuth-Flow."""
    if "gcal_token" in st.session_state:
        return Credentials.from_authorized_user_info(st.session_state["gcal_token"], SCOPES)
    
    # Erstellt einen OAuth-Flow
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

        # Speichert die OAuth-Tokens in der Session
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
        st.link_button("Connect with Google", auth_url)
        st.stop()

st.set_page_config(layout="wide", page_title="Integriertes Kalender-Dashboard")

# --- 2. Lokale Events laden ---
# Ruft die importierte Funktion auf, um Events aus excel_data.py zu laden
excel_events = load_excel_events()

# Führt den Login-Flow aus (stoppt das Skript, wenn nicht eingeloggt)
creds = get_google_creds()


# --- 3. Google Events laden und Kalender anzeigen ---

if creds:
    st.title("🗓️ Mein Integrierter Kalender (Google + Lokal)")
    google_events = []
    
    try:
        # Erstellt einen Google Calendar API Service
        service = build("calendar", "v3", credentials=creds)

        # Definiere das Zeitfenster
        time_min = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        time_max = (datetime.now(timezone.utc) + timedelta(days=90)).isoformat() # Erhöht auf 90 Tage

        # Lade alle Kalender
        cal_list = service.calendarList().list().execute()
        calendars = cal_list.get("items", [])

        st.subheader("Google Kalender Events laden...")
        
        # ProgressBar, um den Ladevorgang anzuzeigen
        progress_bar = st.progress(0, text="Kalender werden geladen...")
        
        for i, cal in enumerate(calendars):
            cal_id = cal["id"]
            cal_summary = cal.get("summaryOverride", cal.get("summary", "Unbekannter Kalender"))
            
            progress_bar.progress((i + 1) / len(calendars), text=f"Lade Events von: **{cal_summary}**")

            try:
                # Anfrage der Events
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
                    # Konvertiere Google Event-Details
                    summary = f"Google ({cal_summary}): " + event.get("summary", "Ohne Titel")
                    start = event["start"].get("dateTime", event["start"].get("date"))
                    end = event["end"].get("dateTime", event["end"].get("date"))
                    color = cal.get("backgroundColor", None)
                    
                    google_events.append({
                        "title": summary,
                        "start": start,
                        "end": end,
                        "color": color
                    })

            except Exception as e:
                st.warning(f"Kalender '{cal_summary}' konnte nicht geladen werden: {e}")

        progress_bar.empty()
        st.success(f"Laden abgeschlossen! {len(google_events)} Google Events gefunden.")


        # --- 4. Events kombinieren und anzeigen ---
        
        # Kombiniere Google Events und lokale Excel Events
        all_events = google_events + excel_events
        all_events.sort(key=lambda x: x["start"]) # Sortiere alle kombinierten Events

        st.subheader("Gesamtübersicht (Google + Lokal)")
        
        formatting = {
            "initialView": "timeGridWeek",
            "height": 650,
            "locale": "de", # Deutsche Sprache für Tage/Monate
            "weekNumbers": True,
            "selectable": True,
            "nowIndicator": True,
            "headerToolbar": {
                "left": "today prev,next",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek,timeGridDay"
            }
        }

        # Zeige den Kalender mit allen Events an
        calendar(all_events, formatting, key="integrated_calendar_main")
        
        st.markdown("---")
        st.caption(f"Aktive Google Events: {len(google_events)} | Lokale Excel Events: {len(excel_events)}")


        # --- 5. Implementierung der City Events und Visualisierungen (vom Nutzer bereitgestellt) ---
        
        # HINWEIS: Dieser Teil benötigt die externen Module 'city_events_module' und 'visualization',
        # die hier nicht definiert sind. Der Code wird beibehalten, aber möglicherweise
        # zu Fehlern führen, wenn diese Module fehlen.

        # Implementation of city events and time slot searcher Natascha
        try:
            from city_events_module import CityEventScheduler

            st.title("City Event Suggestions")

            # Scheduler initialisieren
            scheduler = CityEventScheduler("dummy_city_events_weekly.xlsx")
            st.success("Scheduler initialized correctly")
            
            # Zeitraum auswählen
            start_date = st.date_input("Start Date", datetime.now().date())
            end_date = st.date_input("End Date", (datetime.now() + timedelta(days=7)).date())

            # Button-gesteuert: Vorschläge nur nach Klick
            if st.button("Find Free Time Slots and Suggest Events"):

                # --- Google-Kalender Events robust in datetime konvertieren ---
                # HINWEIS: Hier wird die 'google_events' Liste verwendet.
                calendar_events = []
                user_events = []

                for ev in google_events:
                    start_raw = ev.get("start")
                    end_raw = ev.get("end")

                    try:
                        if not start_raw or not end_raw:
                            continue

                        if "T" in start_raw:
                            start = datetime.fromisoformat(start_raw)
                        else:
                            start = datetime.fromisoformat(start_raw + "T00:00:00")

                        if "T" in end_raw:
                            end = datetime.fromisoformat(end_raw)
                        else:
                            # End-Datum von Ganztagesevents muss angepasst werden
                            end = datetime.fromisoformat(end_raw + "T23:59:59") 

                        user_events.append({"start": start, "end": end})
                    except Exception as e:
                        st.warning(f"Skipping invalid event: {ev}, error: {e}")

                calendar_events.append(user_events)

                # --- Freie Slots berechnen ---
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

                # --- City-Events laden und Vorschläge filtern ---
                weekly_events = scheduler.load_weekly_events_excel()
                expanded_events = scheduler.expand_weekly_events(
                    weekly_events,
                    datetime.combine(start_date, datetime.min.time()),
                    datetime.combine(end_date, datetime.max.time())
                )

                suggested = scheduler.suggest_events(free_slots, expanded_events)
                st.write("### Suggested City Events")
                if not suggested.empty:
                    st.dataframe(suggested)
                else:
                    st.write("No events fit into the available time slots.")

        except ImportError:
            st.warning("City Event Scheduler Modul konnte nicht gefunden werden. Bitte stellen Sie sicher, dass 'city_events_module.py' existiert.")
        except Exception as e:
            st.error(f"Fehler im City Event Scheduler: {e}")


        # Implementation of visualizing calendar data Natascha
        try:
            from visualization import show_visualizations
            show_visualizations(google_events)
        except ImportError:
            st.warning("Visualisierungsmodul konnte nicht gefunden werden. Bitte stellen Sie sicher, dass 'visualization.py' existiert.")
        except Exception as e:
            st.error(f"Fehler in der Visualisierung: {e}")

    # Wenn etwas beim Laden des Kalenders schief geht
    except Exception as e:
        st.error(f"Error loading calendar data: {e}")


# --- 6. Formular zum Hinzufügen von Terminen (Sidebar) ---

with st.sidebar:
    st.header("➕ Lokalen Termin hinzufügen")
    
    with st.form("add_event_form", clear_on_submit=True):
        new_title = st.text_input("Titel des Termins", max_chars=100)
        
        col1, col2 = st.columns(2)
        with col1:
            new_start_date = st.date_input("Startdatum", datetime.now().date())
            new_end_date = st.date_input("Enddatum", datetime.now().date())
        with col2:
            new_start_time = st.time_input("Startzeit", datetime.now().time())
            # Ende standardmäßig 1 Stunde später
            default_end_time = (datetime.now() + timedelta(hours=1)).time()
            new_end_time = st.time_input("Endzeit", default_end_time)

        submitted = st.form_submit_button("Speichern in appointments.xlsx")

        if submitted:
            if new_title and new_start_date and new_start_time and new_end_date and new_end_time:
                # Validierung der Zeitspanne
                start_dt_check = datetime.combine(new_start_date, new_start_time)
                end_dt_check = datetime.combine(new_end_date, new_end_time)
                
                if end_dt_check <= start_dt_check:
                    st.error("Das Enddatum/die Endzeit muss nach dem Startdatum/der Startzeit liegen.")
                else:
                    # Ruft die importierte Funktion add_appointment auf
                    add_appointment(new_title, new_start_date, new_start_time, new_end_date, new_end_time)
            else:
                st.error("Bitte füllen Sie alle Felder aus.")




