import pandas as pd
from datetime import datetime, timedelta

class CityEventScheduler:
    def __init__(self, excel_path="dummy_city_events_weekly.xlsx"):
        self.excel_path = excel_path

    def load_weekly_events_excel(self):
        """Lädt wöchentliche Events aus Excel"""
        df = pd.read_excel(self.excel_path)
        return df

    def expand_weekly_events(self, df, start_date, end_date):
        """Wandelt wöchentliche Events in konkrete Termine um"""
        events = []
        current_date = start_date
        while current_date <= end_date:
            weekday = current_date.weekday()  # Montag=0
            for _, row in df.iterrows():
                if row["weekday"] == weekday:
                    start_dt = datetime.combine(current_date, datetime.strptime(row["start_time"], "%H:%M").time())
                    end_dt = datetime.combine(current_date, datetime.strptime(row["end_time"], "%H:%M").time())
                    events.append({
                        "event_name": row["event_name"],
                        "start_datetime": start_dt,
                        "end_datetime": end_dt,
                        "location": row["location"]
                    })
            current_date += timedelta(days=1)
        return pd.DataFrame(events)

    def find_common_free_slots(self, calendar_events, start_range, end_range, min_duration=timedelta(hours=1)):
        """Berechnet freie Slots, die allen Nutzern passen"""
        all_busy = []
        for user_events in calendar_events:
            for ev in user_events:
                start = ev.get("start")
                end = ev.get("end")
                if isinstance(start, datetime) and isinstance(end, datetime):
                    all_busy.append((start, end))

        all_busy.sort(key=lambda x: x[0])
        free_slots = []
        current_start = start_range

        for busy_start, busy_end in all_busy:
            if busy_start > current_start:
                slot_end = busy_start
                if slot_end - current_start >= min_duration:
                    free_slots.append((current_start, slot_end))
            if busy_end > current_start:
                current_start = busy_end

        if end_range > current_start:
            if end_range - current_start >= min_duration:
                free_slots.append((current_start, end_range))

        return free_slots

    def suggest_events(self, free_slots, events_df):
        """Filtert Events, die in freie Slots passen"""
        suggestions = []
        for _, event in events_df.iterrows():
            for slot_start, slot_end in free_slots:
                if event["start_datetime"] >= slot_start and event["end_datetime"] <= slot_end:
                    suggestions.append(event)
                    break
        return pd.DataFrame(suggestions)