import httpx
import asyncio
import time
from datetime import date, timedelta
from bs4 import BeautifulSoup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

cache = {}
CACHE_TTL = 260

FACILITIES = [
    {'venue': 'turf-training-centre', 'id': 8347, 'name': 'Field A - TTC1'},
    {'venue': 'turf-training-centre', 'id': 8360, 'name': 'Field B - TTC1'},
    {'venue': 'turf-training-centre', 'id': 8361, 'name': 'Field C - TTC1'},
    {'venue': 'turf-training-centre', 'id': 8366, 'name': 'Field F - TTC4'},
    {'venue': 'turf-training-centre', 'id': 8367, 'name': 'Field G - TTC4'},
    {'venue': 'turf-training-centre', 'id': 8368, 'name': 'Field H - TTC4'},
    {'venue': 'turf-training-centre', 'id': 8369, 'name': 'Field I - TTC4'},
    {'venue': 'edmonton-scottish-society', 'id': 12477, 'name': 'Full Field - Soccer Dome'},
    {'venue': 'edmonton-scottish-society', 'id': 6370, 'name': 'T1 - Soccer Dome'},
    {'venue': 'edmonton-scottish-society', 'id': 6371, 'name': 'T2 - Soccer Dome'},
    {'venue': 'edmonton-scottish-society', 'id': 6372, 'name': 'T3 - Soccer Dome'},
    {'venue': 'edmonton-scottish-society', 'id': 6376, 'name': 'Q1 - Soccer Dome'},
    {'venue': 'edmonton-scottish-society', 'id': 6373, 'name': 'Q2 - Soccer Dome'},
    {'venue': 'edmonton-scottish-society', 'id': 6374, 'name': 'Q3 - Soccer Dome'},
    {'venue': 'edmonton-scottish-society', 'id': 6375, 'name': 'Q4 - Soccer Dome'},
]

async def scrape_facility(client, facility, date):
    r = await client.get(f'https://portal.sportskey.com/venues/{facility["venue"]}/facilities/{facility["id"]}/time_slots?date={date}')
    
    soup = BeautifulSoup(r.text, 'html.parser')
    slots = soup.find_all('div', class_='slot available clickable')

    seen = set()
    available_times = []
    for slot in slots:
        a_tag = slot.find('a')
        if a_tag:
            label = a_tag['aria-label']
            if label.startswith(date):
                time_text = slot.find('span', class_='time me-1').text
                if time_text not in seen:
                    seen.add(time_text)
                    available_times.append(time_text)

    return {'facility': facility['name'], 'slots': available_times}

async def scrape_date(d: str):
    async with httpx.AsyncClient(timeout=20.0) as client:
        tasks = [scrape_facility(client, f, d) for f in FACILITIES]
        results = await asyncio.gather(*tasks)
        cache[d] = (time.time(), list(results))

@app.on_event("startup")
async def warm_cache():
    today = date.today().isoformat()
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    await scrape_date(today)
    await scrape_date(tomorrow)

@app.get("/slots")
async def get_slots(date: str):
    if date in cache:
        cached_time, cached_result = cache[date]
        if time.time() - cached_time < CACHE_TTL:
            return {'date': date, 'results': cached_result, 'cached': True}

    await scrape_date(date)
    cached_time, cached_result = cache[date]
    return {'date': date, 'results': cached_result, 'cached': False}