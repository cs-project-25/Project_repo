import streamlit as st
from modules.user_profiles import init_db, add_user, get_users

st.title("Create or Update Your Profile")

# Initialize database
init_db()

with st.form("user_profile_form"):
    st.subheader("Profile Information")
    name = st.text_input("Name")
    email = st.text_input("Email")

    st.subheader("Activity Preferences")
    pref_sport = st.checkbox("Sport")
    pref_music = st.checkbox("Music")
    pref_food = st.checkbox("Food")
    pref_culture = st.checkbox("Culture")
    pref_outdoor = st.checkbox("Outdoor")

    st.subheader("Calendar Link")
    calendar_link = st.text_input(
        "Paste your calendar link (e.g. Google Calendar iCal URL)",
        placeholder="https://calendar.google.com/calendar/ical/..."
    )

    submitted = st.form_submit_button("Save Profile")

if submitted:
    prefs = []
    if pref_sport: prefs.append("Sport")
    if pref_music: prefs.append("Music")
    if pref_food: prefs.append("Food")
    if pref_culture: prefs.append("Culture")
    if pref_outdoor: prefs.append("Outdoor")

    if name and email and calendar_link:
        add_user(name, email, prefs, calendar_link)
        st.success(f"Profile saved for {name} ✅")
        st.info(f"Preferences: {', '.join(prefs)}")
        st.caption(f"Calendar: {calendar_link}")
    else:
        st.error("Please fill out all fields (name, email, and calendar link).")

st.divider()

st.subheader("Existing Users")
users = get_users()
if users:
    for uid, uname, uemail, uprefs, ucal in users:
        st.markdown(f"""
        **👤 {uname}** ({uemail})  
        • Preferences: {uprefs or '–'}  
        • Calendar: [{ucal}]({ucal})
        """)
else:
    st.write("No profiles found yet.")