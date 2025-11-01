import sys
import streamlit as st
from streamlit_calendar import calendar
import datetime as dt

st.title("calendar")

if "base_now" not in st.session_state:
    st.session_state.base_now = dt.datetime.now().replace(microsecond=0)
base = st.session_state.base_now

events = [{"title": "Kickoff","start": (base + dt.timedelta(days=1)).strftime("%Y-%m-%d")},{"title": "Sprint Review","start": (base + dt.timedelta(days=3, hours=14)).isoformat(),"end":   (base + dt.timedelta(days=3, hours=15)).isoformat(),},]

formatting = {"initialView": "dayGridWeek","height": 650,"locale": "en","weekNumbers": True,"selectable": True,}

format = ("calendar")

data_df = pd.DataFrame(
    {
        "appointment": [
            datetime(2024, 2, 5, 12, 30),
            datetime(2023, 11, 10, 18, 0),
            datetime(2024, 3, 11, 20, 10),
            datetime(2023, 9, 12, 3, 0),
        ]
    }
)

st.data_editor(
    data_df,
    column_config={
        "appointment": st.column_config.DatetimeColumn(
            "Appointment",
            min_value=datetime(2023, 6, 1),
            max_value=datetime(2025, 1, 1),
            format="D MMM YYYY, h:mm a",
            step=60,
        ),
    },
    hide_index=True,)

calendar(events, formatting)



















