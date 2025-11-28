import pandas as pd
import streamlit as st
from pathlib import Path
from datetime import datetime

# Korrekter Pfad zur Excel-Datei.
EXCEL_PATH = Path(__file__).parent / "appointments.xlsx"

def load_excel_events():
    """Lädt Termine aus Excel und konvertiert sie in Kalender-Events."""
    try:
        # Versucht, die Datei zu lesen. Erstellt eine leere Datei, falls sie nicht existiert.
        if not EXCEL_PATH.exists():
            df = pd.DataFrame(columns=["title", "start", "end", "color"])
            # Sicherstellen, dass die leere Datei existiert, damit der nachfolgende Code funktioniert
            df.to_excel(EXCEL_PATH, index=False, engine="openpyxl")
            return []
            
        df = pd.read_excel(EXCEL_PATH, engine="openpyxl")

        required_cols = {"title", "start", "end"}
        if not required_cols.issubset(df.columns):
            st.error("Die Datei appointments.xlsx muss die Spalten: title, start, end enthalten.")
            return []

        events = []
        for _, row in df.iterrows():
            # Sicherstellen, dass datetime-Objekte vorliegen
            start_dt = pd.to_datetime(row["start"])
            end_dt = pd.to_datetime(row["end"])
            
            # Konvertierung in ISO 8601-String für das Kalender-Widget
            events.append({
                "title": f"LOKAL: {str(row['title'])}", # Markiert lokale Events
                "start": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                "end": end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
                "color": "#FFC300" # Eigene Farbe für lokale Termine
            })

        return events

    except Exception as e:
        st.error(f"Fehler beim Laden der Excel-Daten: {e}")
        return []

def add_appointment(title, start_date, start_time, end_date, end_time):
    """Fügt einen neuen Termin zur Excel-Datei hinzu."""
    try:
        # Versuche, die vorhandene Datei zu lesen
        df = pd.read_excel(EXCEL_PATH, engine="openpyxl")
    except FileNotFoundError:
        # Erstelle einen neuen DataFrame, falls die Datei nicht existiert
        df = pd.DataFrame(columns=["title", "start", "end"])
    
    # Kombiniere Datum und Zeit zu datetime-Objekten
    start_dt = datetime.combine(start_date, start_time)
    end_dt = datetime.combine(end_date, end_time)

    # Erstelle die neue Zeile
    new_row = pd.DataFrame([{
        "title": title,
        "start": start_dt,
        "end": end_dt
    }])

    # Füge die neue Zeile hinzu und speichere
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(EXCEL_PATH, index=False, engine="openpyxl")
    
    st.success(f"Termin '{title}' erfolgreich zur Excel-Datei hinzugefügt!")
    # Führt das Skript neu aus, um den Kalender zu aktualisieren
    st.rerun()