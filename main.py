import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime, timedelta
import os


load_dotenv()

session = requests.Session()

url = "https://univer.dvfu.ru/schedule/get"

login_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
}

login_page = session.get("https://esa.dvfu.ru/", headers=login_headers)
soup = BeautifulSoup(login_page.text, "html.parser")

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
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
    "Referer": "https://univer.dvfu.ru/schedule",
    "Origin": "https://univer.dvfu.ru",
    "X-Requested-With": "XMLHttpRequest"
}

response = session.get(url, params=params, headers=headers)

try:
    for i in range(len(response.json()["events"])):
        resp = response.json()["events"][i]
        print(f"{resp["start"][11:16]}-{resp["end"][11:16]}\t{resp["pps_load"]}\n{resp["title"]}\t{resp["classroom"]}\n")
except Exception as e:
    print(e)