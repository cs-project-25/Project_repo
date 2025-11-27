# visualization.py
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="darkgrid")


# -----------------------------------------------------------
# Convert events into a clean DataFrame
# -----------------------------------------------------------
def events_to_df(google_events):
    df = pd.DataFrame(google_events)

    df["start"] = pd.to_datetime(df["start"])
    df["end"] = pd.to_datetime(df["end"])
    df["calendar"] = df["title"].apply(lambda x: x.split(":")[0])
    df["weekday"] = df["start"].dt.day_name()

    return df


# -----------------------------------------------------------
# Plot: Number of events per calendar
# -----------------------------------------------------------
def plot_events_per_calendar(df):
    counts = df["calendar"].value_counts()

    fig, ax = plt.subplots(figsize=(8, 4))
    counts.plot(kind="bar", ax=ax)

    ax.set_title("Number of Events per Calendar")
    ax.set_ylabel("Events")
    ax.set_xlabel("Calendar")

    st.pyplot(fig)


# -----------------------------------------------------------
# Plot: Distribution over weekdays
# -----------------------------------------------------------
def plot_events_per_weekday(df):
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df["weekday"] = pd.Categorical(df["weekday"], categories=order, ordered=True)

    weekday_counts = df["weekday"].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(8, 4))
    weekday_counts.plot(kind="line", marker="o", ax=ax)

    ax.set_title("Events by Weekday")
    ax.set_ylabel("Events")
    ax.set_xlabel("Weekday")

    st.pyplot(fig)


# -----------------------------------------------------------
# Main visualization module (called from app.py)
# -----------------------------------------------------------
def show_visualizations(google_events):
    st.subheader("Data Visualization")

    df = events_to_df(google_events)

    min_date = df["start"].min().date()
    max_date = df["start"].max().date()

    dates = st.date_input(
        "Date Range",
        value=(min_date, max_date)
    )

    # Handle both tuple and single-date return values
    if isinstance(dates, tuple) and len(dates) == 2:
        start_date, end_date = dates
    else:
        start_date = end_date = dates

    if start_date > end_date:
        st.warning("Start date cannot be after end date.")
        return

    # ------------------------------------------------------------------
    # IMPORTANT FIX: Persistent button state
    # ------------------------------------------------------------------
    if "show_plot" not in st.session_state:
        st.session_state.show_plot = False

    if st.button("Generate Chart"):
        st.session_state.show_plot = True

    # Stop here unless user has clicked the button
    if not st.session_state.show_plot:
        return

    st.write("### Select Chart Type")

    chart_type = st.selectbox(
        "Chart Type",
        [
            "Events per Calendar",
            "Events by Weekday"
        ]
    )

    mask = (df["start"].dt.date >= start_date) & (df["start"].dt.date <= end_date)
    df_filtered = df[mask]

    if df_filtered.empty:
        st.warning("No events in the selected time range.")
        return

    # ------------------------------------------------------------------
    # Plots
    # ------------------------------------------------------------------
    if chart_type == "Events per Calendar":
        plot_events_per_calendar(df_filtered)

    elif chart_type == "Events by Weekday":
        plot_events_per_weekday(df_filtered)
