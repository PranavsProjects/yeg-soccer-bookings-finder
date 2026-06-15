# YEG Soccer Bookings Finder

A full-stack web app that aggregates real-time field availability across Edmonton's major indoor soccer facilities — so you spend less time clicking through booking portals and more time playing.

**Live:** [yeg-soccer-bookings-finder.vercel.app](https://yeg-soccer-bookings-finder.vercel.app)

---

## The Problem

Booking a soccer field in Edmonton means checking multiple websites separately — TTC1, TTC4 Nisku, and the Edmonton Soccer Dome all run on different pages with no unified view. This app solves that by pulling live availability across all facilities into one place.

---

## Features

- **Live availability** — real-time slot data fetched directly from SportsKey's booking portal
- **Auto-loads today** — availability for the current date loads automatically on page open
- **Future date search** — check any upcoming date with a single date picker
- **Multi-venue carousel** — browse TTC1, TTC4, and the Soccer Dome in a clean slide-based UI
- **2-minute cache** — results are cached server-side to minimize load times on repeated searches
- **Cache warming on startup** — today and tomorrow's data is pre-fetched when the server boots, making first loads instant

---

## Facilities Covered

| Venue | Fields |
|---|---|
| Turf Training Centre — TTC1 (59th Ave NW) | Field A, Field B, Field C |
| Turf Training Centre — TTC4 (Nisku) | Field F, Field G, Field H, Field I |
| Edmonton Soccer Dome (Scottish Society) | Full Field, T1–T3 (9v9), Q1–Q4 (7v7) |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, httpx, BeautifulSoup4 |
| Scraping | HTML parsing of SportsKey's booking portal |
| Caching | In-memory Python dict with TTL |
| Frontend | Vanilla HTML/CSS/JavaScript |
| Backend Deploy | Render (free tier) |
| Frontend Deploy | Vercel |

---

## How It Works

SportsKey — the booking platform used by TTC and the Soccer Dome — renders availability as HTML. The backend scrapes this HTML asynchronously across all 15 facilities in parallel, parses the available time slots, filters by the requested date, deduplicates results, and returns clean JSON.

```
User selects date
      ↓
Frontend calls GET /slots?date=YYYY-MM-DD
      ↓
FastAPI checks cache → if stale, scrapes all 15 facilities concurrently
      ↓
BeautifulSoup parses .slot.available.clickable elements
      ↓
Returns JSON: [{ facility, slots: ["09:00 AM", "10:00 AM", ...] }]
      ↓
Frontend renders venue cards with available time tags
```

---

## Running Locally

**Prerequisites:** Python 3.10+, pip

```bash
# Clone the repo
git clone https://github.com/PranavsProjects/yeg-soccer-bookings-finder.git
cd yeg-soccer-bookings-finder

# Set up backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload
```

Open `frontend/index.html` in your browser. The frontend will call `localhost:8000` by default — update the `API` constant in `index.html` to point to your local server if needed.

---

## API

```
GET /slots?date=YYYY-MM-DD
```

**Response:**
```json
{
  "date": "2026-06-21",
  "cached": false,
  "results": [
    {
      "facility": "Field A - TTC1",
      "slots": ["09:00 AM", "10:00 AM", "02:00 PM"]
    },
    ...
  ]
}
```

---

## Project Structure

```
yeg-soccer-bookings-finder/
├── backend/
│   ├── main.py          # FastAPI app — scraping, caching, API endpoint
│   └── requirements.txt
├── frontend/
│   └── index.html       # Single-page frontend
└── README.md
```

---

## Limitations

- **Render free tier spin-down** — the backend sleeps after 15 minutes of inactivity. First request after idle can take 30–60 seconds. The frontend retries automatically up to 3 times.
- **FC Viktoria / CatchCorner** — requires login to view availability, so it cannot be scraped without authentication. Direct booking link provided instead.
- **ESA facilities (Finnly)** and **EZFacility** block automated access and have no public API.
- **SportsKey schema changes** — if SportsKey updates their HTML structure, the parser may need updating.

---

## Roadmap

- [ ] SMS/email alerts when a specific time slot opens up
- [ ] Filter by field size (11v11, 9v9, 7v7)
- [ ] Mobile app (React Native)
- [ ] Add more Edmonton facilities as they move to bookable platforms
- [ ] Persistent caching with Redis to survive server restarts

---

## Author

**Pranav Penmetsa**
Computing Science, University of Alberta
[GitHub](https://github.com/PranavsProjects)
