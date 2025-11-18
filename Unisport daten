import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import re

def get_pilates_events():
    """
    Scrapt die aktuellen Pilates-Kurse der UniSG
    und liefert eine Liste von Event-Dictionaries:
    [{
        "summary": Kursname,
        "location": Ort,
        "description": Beschreibung,
        "start": datetime,
        "end": datetime
    }, ...]
    """
    url = "https://www.sportprogramm.unisg.ch/unisg/angebote/aktueller_zeitraum/_Pilates.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Tabelle extrahieren
    table = soup.find("table")
    if table is None:
        return []

    rows = []
    for tr in table.find_all("tr"):
        cols = [c.get_text(strip=True) for c in tr.find_all(["td", "th"])]
        if cols:
            rows.append(cols)

    if len(rows) < 2:
        return []

    df = pd.DataFrame(rows[1:], columns=[c.strip() for c in rows[0]])

    # Hilfsfunktion zum Parsen von Buchung/Datum & Zeit
    def parse_buchung(buchung_text, zeit_text):
        match_date = re.search(r"ab (\d{1,2}\.\d{1,2})", buchung_text)
        if match_date:
            day_month = match_date.group(1)
            year = datetime.today().year
            datum_str = f"{day_month}.{year}"
            try:
                datum = datetime.strptime(datum_str, "%d.%m.%Y")
                match_time = re.match(r"(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})", zeit_text)
                if match_time:
                    h1,m1,h2,m2 = map(int, match_time.groups())
                    start = datum.replace(hour=h1, minute=m1)
                    end = datum.replace(hour=h2, minute=m2)
                    return start, end
                else:
                    return datum, datum + timedelta(hours=1)
            except:
                return None,None
        return None,None

    # Alle Kurse verarbeiten
    pilates_events = []
    for idx, row in df.iterrows():
        kursname = row.get("Details", "Pilates Kurs")
        ort = row.get("Ort", "")
        zeit = row.get("Zeit", "")
        buchung = row.get("Buchung", "")
        start,end = parse_buchung(buchung, zeit)
        if start and end:
            pilates_events.append({
                "summary": kursname,
                "location": ort,
                "description": "Unisport HSG Pilates Kurs",
                "start": start,
                "end": end
            })
    return pilates_events
