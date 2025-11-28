import requests
from ics import Calendar
from datetime import datetime, timedelta, time
import pytz

TZ = pytz.timezone("Europe/Zurich")

def fetch_ical_busy_intervals(ical_url, window_start, window_end, timeout=8):
    """Return list of (start, end) timezone-aware datetimes that overlap the window.
    Uses ics.Calendar to parse.
    """
    try:
        r = requests.get(ical_url, timeout=timeout)
        r.raise_for_status()
    except Exception:
        return []
    
    try:
    c = Calendar(r.text)
    except Exception:
        return []

    busy = []
    for ev in c.events:
        try:
            s = ev.begin.astimezone(TZ).naive
            e = ev.end.astimezone(TZ).naive
        except Exception:
            # fallback: try parse strings
            try:
                s = ev.begin
                e = ev.end
            except Exception:
                continue
# convert naive to tz-aware by localizing then convert to TZ
        s = TZ.localize(s)
        e = TZ.localize(e)
        if e > window_start and s < window_end:
            s_clipped = max(s, window_start)
            e_clipped = min(e, window_end)
            busy.append((s_clipped, e_clipped))
    return busy


def merge_intervals(intervals):
    if not intervals:
        return []
    intervals = sorted(intervals, key=lambda x: x[0])
    merged = []
    cur_s, cur_e = intervals[0]
    for s, e in intervals[1:]:
        if s <= cur_e:
            cur_e = max(cur_e, e)
        else:
            merged.append((cur_s, cur_e))
            cur_s, cur_e = s, e
    merged.append((cur_s, cur_e))
    return merged
    
def invert_busy_to_free(busy_intervals, window_start, window_end):
    free = []
    cur =window_start
    for s, e in busy_intervals:
        if cur < s
            free.append((cur, s))
        cur = max (cur, e)
    if cur < window_end:
        free.append ((cur, window_end))
    return free
           
def generate_candidate_slots(free_intervals, slot_length_minutes=60, step_minutes=30):
    from datetime import timedelta
    slots = []
    delta = timedelta(minutes=slot_length_minutes)
    step = timedelta(minutes=step_minutes)
    for s, e in free_intervals:
        cur = s
        while cur + delta <= e:
            slots.append((cur, cur + delta))
            cur += step
    return slots


def find_common_free_slots(users_busy_map, window_start, window_end, slot_length_minutes=60, step_minutes=30, min_attendees=2):
    # compute free intervals per user
    user_free = {}
    for uid, busy in users_busy_map.items():
        merged = merge_intervals(busy)
        free = invert_busy_to_free(merged, window_start, window_end)
        user_free[uid] = free

    # generate day-wise candidate slots (08:00-21:00)
    candidate_slots = []
    day = window_start.replace(hour=0, minute=0, second=0, microsecond=0)
    while day < window_end:
        ds = day.replace(hour=8, minute=0)
        de = day.replace(hour=21, minute=0)
        s0 = max(ds, window_start)
        e0 = min(de, window_end)
        if s0 < e0:
            candidate_slots.extend(generate_candidate_slots([(s0, e0)], slot_length_minutes, step_minutes))
        day = day + timedelta(days=1)
        
    results = []
    for s, e in candidate_slots:
        free_users = []
        for uid, frees in user_free.items():
            for fs, fe in frees:
                if fs <= s and fe >= e:
                    free_users.append(uid)
                    break
        if len(free_users) >= min_attendees:
            results.append({"slot_start": s, "slot_end": e, "free_users": free_users})
    return results


def create_ics_event(title, start_dt, end_dt, description, attendees_emails=None):
    from ics import Calendar, Event
    cal = Calendar()
    e = Event()
    e.name = title
    e.begin = start_dt
    e.end = end_dt
    e.description = description
    # attendees handling can be enhanced for Google Calendar invites
    cal.events.add(e)
    return str(cal)
