import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import pytz

from modules.events_loader import load_events_from_excel
from modules.scheduler import fetch_ical_busy_intervals, find_common_free_slots, create_ics_event
from modules.recommender import SimpleEventRecommender
from modules.llm_wrapper import generate_invitation
from modules.user_profiles import get_users # assumes you have this module already

TZ = pytz.timezone("Europe/Zurich")
st.set_page_config(page_title="Smart Scheduler", layout="wide")
st.title("Smart Scheduler — Vorschläge für gemeinsame Termine")

# Sidebar controls
with st.sidebar:
  st.header("Einstellungen")
  start_date = st.date_input("Zeitraum Start", datetime.now().date())
  days = st.number_input("Tage", min_value=1, max_value=30, value=7)
  slot_len = st.selectbox("Slot Länge (Minuten)", [30, 60, 90], index=1)
  min_attendees = st.slider("Min. Teilnehmer", 2, 20, 2)
  step_minutes = st.selectbox("Step (Min)", [15, 30, 60], index=1)
    
window_start = TZ.localize(datetime.combine(start_date, datetime.min.time()))
window_end = window_start + timedelta(days=days)

st.write(f"Zeitraum: **{window_start.strftime('%Y-%m-%d %H:%M')}** bis **{window_end.strftime('%Y-%m-%d %H:%M')}** ({TZ})")

st.info("Events werden aus data/events.xlsx geladen (Name, Start, End, Category, Description required)")
try:
  events_df = load_events_from_excel("data/events.xlsx")
  st.success(f"{len(events_df)} Events geladen")
except Exception as e:
  st.error(f"Fehler beim Laden der Eventliste: {e}")
  st.stop()

# Load users from your user_profiles module
users = get_users()
if not users:
  st.warning("Keine Benutzerprofile gefunden. Bitte Profile erstellen.")

# Prepare user maps
users_map = {}
user_profiles = {}
for uid, name, email, prefs_str, cal_link in users:
  users_map[uid] = cal_link
  prefs = [p.strip() for p in (prefs_str or "").split(",") if p.strip()]
  user_profiles[uid] = {"user_id": uid, "name": name, "email": email, "preferences": prefs}

if st.button("Vorschläge generieren"):
  st.info("Kalender der Nutzer werden ausgelesen (gecacht werden sollte) ...")
  users_busy = {}
  for uid, cal_url in users_map.items():
    busy = []
    if cal_url:
      try:
        busy = fetch_ical_busy_intervals(cal_url, window_start, window_end)
    except Exception:
        busy = []
    users_busy[uid] = busy

  slots = find_common_free_slots(users_busy, window_start, window_end,slot_length_minutes=slot_len, step_minutes=step_minutes, min_attendees=min_attendees)
slot_length_minutes=slot_len, step_minutes=step_minutes, min_attendees=min_attendees)

st.success(f"{len(slots)} mögliche gemeinsame Slots gefunden")

rec = SimpleEventRecommender(events_df)

suggestions = []
for s in slots:
  free_uids = s["free_users"]
  free_user_profiles = [user_profiles[uid] for uid in free_uids]

  # rank events for these users
  top = rec.rank_events_for_users(free_user_profiles, slot_start=s["slot_start"], slot_end=s["slot_end"], top_n=5)
  top_list = top.to_dict(orient="records")
  
  if top_list:
    # LLM generate invitation texts (stub)
    invites = generate_invitation(s["slot_start"], s["slot_end"], free_user_profiles, top_list)

    suggestions.append({
      "slot_start": s["slot_start"],
      "slot_end": s["slot_end"],
      "free_users": free_user_profiles,
      "top_events": top_list,
      "invites": invites
    })

  if not suggestions:
    st.info("Keine passenden Vorschläge gefunden.")
  else:
    st.header("Vorschläge")
    for ix, sug in enumerate(suggestions):
      ss = sug["slot_start"]
      se = sug["slot_end"]
      st.subheader(f"Slot {ix+1}: {ss.strftime('%Y-%m-%d %H:%M')} — {se.strftime('%H:%M')}")
      st.write(f"Freie Personen: {', '.join([u['name'] for u in sug['free_users']])}")

      st.markdown("**Top Events (match score)**")
      for ev in sug["top_events"]:
        st.write(f"- {ev['name']} ({ev.get('category','-')}) — score {ev.get('match_score',0):.2f}")

      st.markdown("**LLM Einladungsvorschläge**")
      for inv in sug["invites"]:
        st.write(f"- ({inv['tone']}) {inv['text']}")

      col1, col2 = st.columns(2)
      with col1:
          if st.button(f"Als .ics herunterladen (Slot {ix})", key=f"ics_{ix}"):
            # build ICS from top event
            ev = sug['top_events'][0]
            ics_str = create_ics_event(ev['name'], sug['slot_start'], sug['slot_end'], ev.get('description',''))
            st.download_button(f"Download ICS (Slot {ix})", ics_str, file_name=f"suggestion_{ix}.ics", mime="text/calendar")
      with col2:
        if st.button(f"Ignorieren (Slot {ix})", key=f"ignore_{ix}"):
          st.info(f"Vorschlag für Slot {ix} ignoriert")

st.sidebar.markdown("---")
st.sidebar.caption("Smart Scheduler — prototype. Ensure user consent before processing calendars.")
