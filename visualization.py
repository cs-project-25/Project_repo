# visualization.py
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="darkgrid")  # seaborn look

def events_to_df(google_events):
    df = pd.DataFrame(google_events)
    df["start"] = pd.to_datetime(df["start"])
    df["end"] = pd.to_datetime(df["end"])
    df["calendar"] = df["title"].apply(lambda x: x.split(":")[0])
    df["weekday"] = df["start"].dt.day_name()
    return df

def plot_events_per_calendar(df):
    counts = df["calendar"].value_counts()
    fig, ax = plt.subplots(figsize=(8,4))
    counts.plot(kind="bar", ax=ax)
    ax.set_title("Anzahl Termine pro Kalender")
    ax.set_ylabel("Termine")
    ax.set_xlabel("Kalender")
    st.pyplot(fig)

def plot_events_per_weekday(df):
    order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    df["weekday"] = pd.Categorical(df["weekday"], categories=order, ordered=True)
    weekday_counts = df["weekday"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(8,4))
    weekday_counts.plot(kind="line", marker="o", ax=ax)
    ax.set_title("Termine pro Wochentag")
    ax.set_ylabel("Termine")
    ax.set_xlabel("Wochentag")
    st.pyplot(fig)

def show_visualizations(google_events):
    st.subheader("📊 Datenvisualisierung")
    df = events_to_df(google_events)

    min_date = df["start"].min().date()
    max_date = df["start"].max().date()

    st.write("### Zeitraum auswählen")
    dates = st.date_input(
        "Zeitraum",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if isinstance(dates, tuple):
        start_date, end_date = dates
    else:
        start_date = end_date = dates

    # Button für Anzeige
    if st.button("Grafik anzeigen"):
        mask = (df["start"].dt.date >= start_date) & (df["start"].dt.date <= end_date)
        df_filtered = df[mask]

        if df_filtered.empty:
            st.warning("Keine Termine im ausgewählten Zeitraum.")
            return

        option = st.selectbox(
            "Welche Grafik möchtest du sehen?",
            ["Wer hat die meisten Termine?", "Termine nach Wochentag"]
        )

        if option == "Wer hat die meisten Termine?":
            plot_events_per_calendar(df_filtered)
        else:
            plot_events_per_weekday(df_filtered)
