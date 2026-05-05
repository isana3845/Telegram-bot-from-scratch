import requests
from datetime import datetime, timedelta
import random

session = requests.Session()

# 1. Прогреваем сессию
session.get("https://univer.dvfu.ru/schedule")

url = "https://univer.dvfu.ru/schedule/get"

date = datetime.now()
start = date - timedelta((date.weekday() + 1) % 7)
end = start + timedelta(6)

params = {
    "type": "agendaWeek",
    "start": f"{start.strftime('%Y-%m-%d')}T14:00:00.000Z",
    "end": f"{end.strftime('%Y-%m-%d')}T14:00:00.000Z",
    "groups[]": "6886",
    "ppsGuid": "",
    "facilityId": 0
}

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://univer.dvfu.ru/schedule",
    "X-Requested-With": "XMLHttpRequest"
}

response = session.get(url, params=params, headers=headers)

data = response.json()

for event in data.get("events", []):
    print(f"{event['start'][11:16]}-{event['end'][11:16]}\t{event['pps_load']}")
    print(f"{event['title']}\t{event['classroom']}\n")