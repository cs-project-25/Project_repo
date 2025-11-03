import requests
from bs4 import BeautifulSoup
from datetime import datetime
import hashlib
def scrape_stgallen_events ():
    url = "https://www.m.stadt.sg.ch/vdpdd/de/index/veranstaltungen/veranstaltungskalender.html"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    events = []

    event_elements = soup.select('.event-listing .event-item')
    for element in event_elements:
        title = element.select_one('.event-title').get_text(strip=True)
        date_str = element.select_one('.event-date').get_text(strip=True)
        date = datetime.strptime(date_str, '%d %B %Y')
        link = element.select_one('a')['href']
        unique_id = hashlib.md5(link.encode('utf-8')).hexdigest()

        event = {
            'id': unique_id,
            'title': title,
            'date': date,
            'link': link
        }
        events.append(event)

    return events
if __name__ == "__main__":
    data = scrape_stgallen_events()
    print(f"{len(data)} Events gefunden.")
    for ev in data[:3]:
        print(ev)
    
