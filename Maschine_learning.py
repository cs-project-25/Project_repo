#Maschine Learning Tool for suggesting the right activities based on user preferences
# modules/scheduler.py
import requests, io
import pandas as pd
from datetime import datetime, timedelta, time
from ics import Calendar  # pip install ics
from dateutil import parser as date_parser
import pytz

TZ = pytz.timezone("Europe/Zurich")

def load_events_excel(path="data/events.xlsx"): #read events from excel sheet --> right connection!!
    df = pd.read_excel(path)
    # ensure datetimes are tz-aware in Zurich
    for col in ["start_datetime","end_datetime"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col]).dt.tz_localize(TZ, ambiguous="NaT", nonexistent="NaT") \
                        .dt.tz_convert(TZ)
    return df

def fetch_ical_busy_intervals(ical_url, window_start, window_end):
    """Rough parser: returns list of (start, end) datetimes for busy times in window."""
    r = requests.get(ical_url, timeout=10)
    r.raise_for_status()
    c = Calendar(r.text)
    busy = []
    for ev in c.events:
        s = ev.begin.astimezone(TZ).naive if ev.begin else None
        e = ev.end.astimezone(TZ).naive if ev.end else None
        if s and e:
            # consider only events overlapping with window
            if e > window_start and s < window_end:
                # clip to window:
                s_clipped = max(s, window_start)
                e_clipped = min(e, window_end)
                busy.append((s_clipped, e_clipped))
    return busy

def merge_intervals(intervals):
    """Merge list of (start,end) naive datetimes, return sorted non-overlapping list."""
    if not intervals: return []
    intervals = sorted(intervals, key=lambda x: x[0])
    merged = []
    cur_s, cur_e = intervals[0]
    for s,e in intervals[1:]:
        if s <= cur_e:
            cur_e = max(cur_e, e)
        else:
            merged.append((cur_s, cur_e))
            cur_s, cur_e = s, e
    merged.append((cur_s, cur_e))
    return merged

def invert_busy_to_free(busy_intervals, window_start, window_end):
    """Given merged busy intervals, return free intervals inside window."""
    free = []
    cur = window_start
    for s,e in busy_intervals:
        if cur < s:
            free.append((cur, s))
        cur = max(cur, e)
    if cur < window_end:
        free.append((cur, window_end))
    return free

def generate_candidate_slots(free_intervals, slot_length_minutes=60, step_minutes=30):
    """From free intervals, yield candidate slots (start,end)."""
    slots = []
    delta = timedelta(minutes=slot_length_minutes)
    step = timedelta(minutes=step_minutes)
    for s,e in free_intervals:
        cur = s
        while cur + delta <= e:
            slots.append((cur, cur + delta))
            cur += step
    return slots

def find_common_free_slots(users_busy_map, window_start, window_end, slot_length_minutes=60, step_minutes=30, min_attendees=2):
    """
    users_busy_map: {user_id: [(s,e), ...], ...}
    returns list of dicts: {slot_start,slot_end,free_users}
    """
    # 1) For each user compute free intervals
    user_free = {}
    for uid, busy in users_busy_map.items():
        merged = merge_intervals(busy)
        free = invert_busy_to_free(merged, window_start, window_end)
        user_free[uid] = free

    # 2) Generate candidate slots from union of all users' free intervals
    # For simplicity, sample slots per day 08:00-21:00
    candidate_slots = []
    # create union free intervals across users by scanning per slot
    # We'll test each potential slot (stepped) and compute who is free
    day_start = window_start
    while day_start < window_end:
        day_end = min(day_start + timedelta(days=1), window_end)
        # create day search window 08:00-21:00 localized
        ds = datetime.combine(day_start.date(), time(8,0))
        de = datetime.combine(day_start.date(), time(21,0))
        if de < window_start or ds > window_end:
            day_start += timedelta(days=1)
            continue
        s0 = max(ds, window_start)
        e0 = min(de, window_end)
        # iterate slots
        slots = generate_candidate_slots([(s0,e0)], slot_length_minutes, step_minutes)
        candidate_slots.extend(slots)
        day_start += timedelta(days=1)

    # check for each slot who is free
    results = []
    for s,e in candidate_slots:
        free_users = []
        for uid, frees in user_free.items():
            for fs,fe in frees:
                if fs <= s and fe >= e:
                    free_users.append(uid)
                    break
        if len(free_users) >= min_attendees:
            results.append({"slot_start": s, "slot_end": e, "free_users": free_users})
    return results

def score_event_for_users(event_row, user_profiles):
    """
    event_row: pandas Series with category, description, addressLocality
    user_profiles: list of user profile dicts {'user_id', 'preferences':[...] , 'preferred_locations':[...]} 
    returns mean preference score (0..1)
    """
    scores = []
    for u in user_profiles:
        prefs = [p.lower() for p in u.get("preferences",[])]
        score = 0.0
        # category match
        if str(event_row.get("category","")).lower() in prefs:
            score += 1.0
        # keywords in description
        desc = str(event_row.get("description","")).lower()
        keyword_hits = sum(1 for p in prefs if p in desc)
        if keyword_hits:
            score += 0.5
        scores.append(min(score,1.0))
    return sum(scores)/len(scores) if scores else 0.0
