import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

sns.set_theme(style="darkgrid")  # Vorgabe vom Prof: seaborn "look"

# -------------------------
# Hilfsfunktion:
# Konvertiert deine google_events Liste in ein DataFrame
# -------------------------
def events_to_df(google_events):
    df = pd.DataFrame(google_events)

    # Start/End in echte Datetimes umwandeln
    df["start"] = pd.to_datetime(df["start"])
    df["end"] = pd.to_datetime(df["end"])

    # Calendar-Namen extrahieren
    df["calendar"] = df["title"].apply(lambda x: x.split(":")[0])

    # Wochentag extrahieren
    df["weekday"] = df["start"].dt.day_name()

    return df


# -------------------------
# VISUALISIERUNG 1:
# "Wer hat die meisten Termine?"
# -------------------------
def plot_events_per_calendar(df):
    counts = df["calendar"].value_counts()

    fig, ax = plt.subplots(figsize=(8, 4))
    counts.plot(kind="bar", ax=ax)
    ax.set_title("Anzahl Termine pro Kalender")
    ax.set_ylabel("Termine")
    ax.set_xlabel("Kalender")
    st.pyplot(fig)


# -------------------------
# VISUALISIERUNG 2:
# "Wie verteilen sich Termine über die Wochentage?"
# -------------------------
def plot_events_per_weekday(df):
    order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    df["weekday"] = pd.Categorical(df["weekday"], categories=order, ordered=True)
    
    weekday_counts = df["weekday"].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(8, 4))
    weekday_counts.plot(kind="line", marker="o", ax=ax)
    ax.set_title("Termine pro Wochentag")
    ax.set_ylabel("Termine")
    ax.set_xlabel("Wochentag")
    st.pyplot(fig)


# -------------------------
# Hauptfunktion: UI + Filter + Graph auswählen
# -------------------------
def show_visualizations(google_events):
    st.subheader("📊 Datenvisualisierung")

    df = events_to_df(google_events)

    # Interaktiver Zeitraumfilter
    min_date = df["start"].min().date()
    max_date = df["start"].max().date()

    st.write("### Zeitraum auswählen")
    start_date, end_date = st.date_input(
        "Zeitraum",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Filter anwenden
    mask = (df["start"].dt.date >= start_date) & (df["start"].dt.date <= end_date)
    df_filtered = df[mask]

    if df_filtered.empty:
        st.warning("Keine Termine im ausgewählten Zeitraum.")
        return

    # Welche Grafik?
    option = st.selectbox(
        "Welche Grafik möchtest du sehen?",
        ["Wer hat die meisten Termine?", "Termine nach Wochentag"]
    )

    if option == "Wer hat die meisten Termine?":
        plot_events_per_calendar(df_filtered)
    else:
        plot_events_per_weekday(df_filtered)

