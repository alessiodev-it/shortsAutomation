# polyMetrics

*Finally. My data flows in real-time, and it feels so good.*

---

## Overview

**polyMetrics** is a real‑time data streaming backend that aggregates live market data from Polymarket and weather forecasts from OpenMeteo, METAR, and tgftp. It serves structured Server‑Sent Events (SSE) to a clean, minimalist frontend, enabling live monitoring of prediction markets and temperature trends across multiple locations. Built with multithreading, dynamic feed discovery, and thread‑safe state management, it was designed for low‑latency observability without the overhead of WebSockets.

---

## Key Features

- **Live Polymarket Streaming** – Connects to Polymarket's WebSocket and REST APIs to stream market prices, order books, and bid/ask spreads for any event slug.
- **Multi‑Source Weather Data** – Aggregates real‑time and forecast temperatures from OpenMeteo (ensemble models), NOAA METAR, and tgftp.
- **Dynamic Feed Discovery** – Automatically discovers and instantiates feed modules via `pkgutil` — no manual registration required.
- **Thread‑Safe State Management** – All feeds maintain internal state with locks, ensuring consistent snapshots for the main thread.
- **Server‑Sent Events (SSE)** – Lightweight, one‑way streaming to browsers without WebSocket complexity. Includes automatic reconnection and keep‑alive pings.
- **Real‑Time Frontend** – Clean, dark‑themed dashboard showing:
  - Wallet address and USDC balance (via Web3/RPC)
  - API credentials (for debugging)
  - Per‑worker charts with toggleable views (realtime vs. predicted weather)
  - Live clock updating every second
- **Persistent Worker Configuration** – Each worker folder contains a `param.txt` file with a market URL; the loader monitors changes and pushes updates to the fetch loop.
- **Automatic Context Generation** – Includes `generate_context.py`, which produces a dynamic project context file (directory tree + method index) for LLM‑assisted development.

---

## Installation

```bash
git clone https://github.com/alessiodev-it/polyMetrics.git
cd polyMetrics
python -m venv venv
source venv/bin/activate      # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Dependencies (System)

- **Python 3.10+** (due to `ZoneInfo` and dataclasses)
- **No additional system libraries** — all dependencies are pip‑installable.

---

## Configuration

### 1. Environment Variables

Create a `.env` file in `data/.env` with the following keys:

```env
private_key=YOUR_POLYMARKET_PRIVATE_KEY
api_key=YOUR_POLYMARKET_API_KEY
secret=YOUR_POLYMARKET_API_SECRET
passphrase=YOUR_POLYMARKET_API_PASSPHRASE
```

These are used to authenticate with Polymarket's ClobClient and to fetch your USDC balance via Polygon RPC.

### 2. Worker Configuration

For each data stream you want to monitor, create a folder under `data/workers/` with a `param.txt` file:

```
data/workers/
├── w_london_2026_02_20/
│   └── param.txt          # url_market=https://polymarket.com/event/...
├── w_paris_2026_03_01/
│   └── param.txt
└── w_tokyo_2026_01_15/
    └── param.txt
```

Each `param.txt` must contain a single line:

```ini
url_market=https://polymarket.com/event/...-in-london-on-feb-20-2026
```

The URL is parsed to extract:
- **Slug** – used to switch the Polymarket event feed.
- **Location** and **date** – used to initialise weather feeds (predict and realtime).

---

## Usage

Start the main script:

```bash
python main.py
```

The server will start on a random available port (printed to the console). Open `http://127.0.0.1:<port>/analyses/analyses.html` in your browser.

### What happens under the hood

1. **Initialisation** (`files.init`, `user.init`):
   - Creates `data/`, `data/workers/`, `data/.env` if missing.
   - Loads API credentials, derives wallet address, and checks USDC balance.
   - Scans `data/workers/` for worker folders.

2. **Thread Pool** – For each worker folder, three threads are spawned:
   - **Loader** – monitors `param.txt` for changes and pushes new `Worker` objects to `config_queue`.
   - **Fetcher** – consumes `config_queue`, resolves the market slug, and loops over all discovered feed modules:
     - Polymarket feeds → fetch order books and prices.
     - Predict weather feeds → fetch ensemble temperature forecasts.
     - Realtime weather feeds → fetch METAR observations and running max.
   - **Sender** – consumes `data_queue` and broadcasts each packet via SSE to all connected clients.

3. **SSE Server** – A lightweight HTTP server (`server.py`) serves the static frontend and maintains an SSE endpoint (`/events`). Each connected client receives all broadcast packets.

4. **Frontend** – The dashboard (`analyses.html`, `analyses.js`, `analyses.css`) renders:
   - Wallet address and USDC balance.
   - API keys (for debugging).
   - Per‑worker chart cards with toggleable views (realtime vs. predicted temperature).
   - Live updating datetime.

---

## How It Works

### Data Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Worker Folder  │───▶│    Loader       │───▶│  Fetch Queue    │
│  (param.txt)    │    │  (load.py)      │    │  (Worker obj)   │
└─────────────────┘    └─────────────────┘    └────────┬────────┘
                                                       │
                                                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Fetcher (fetch.py)                           │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────────┐    │
│  │ PolymarketFeed │  │ OpenMeteoFeed  │  │ AviationWeather /   │    │
│  │ (WS + REST)    │  │ (ensemble)     │  │ Tgftp (METAR)       │    │
│  └────────┬───────┘  └────────┬───────┘  └───────────┬─────────┘    │
│           │                   │                      │              │
│           └───────────────────┼──────────────────────┘              │
│                               ▼                                     │
│                        Data Queue (packets)                         │
└─────────────────────────────────────────────────────────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌─────────────────────────────────────────────┐
│    Sender       │───▶│   SSE Broadcast (server.py)                 │
│   (send.py)     │    │   → All connected clients (browser)         │
└─────────────────┘    └─────────────────────────────────────────────┘
```

### Feed Modules Interface

All feed modules in `src/classes/` follow a standard interface:

| Method | Description |
|--------|-------------|
| `__init__(...)` | Initialise internal state and lock. |
| `configure(...)` | Update parameters without restarting the thread. |
| `start()` | Start the polling/websocket thread (raises ValueError if already running). |
| `stop()` | Stop the thread and join it. |
| `switch_*(...)` | Atomically stop → reset state → restart (e.g., `switch_event`, `switch_station`). |
| `snapshot()` | Return a thread‑safe deep copy of current data (dict/list). |

### Snapshot Contracts (What fetch.py expects)

#### Polymarket Feed
```python
[
    {
        "question": "Will the temperature in London be ≥ 20°C?",
        "outcome_prices": ["0.45", "0.55"],
        "best_yes_bid": 0.44,
        "best_yes_ask": 0.46,
        "best_no_bid": 0.54,
        "best_no_ask": 0.56,
        "last_update": 1739884800.0,
    }
]
```

#### Predict Weather Feed (OpenMeteo)
```python
{
    "location": "Wellington",
    "country": "New Zealand",
    "date": "2026-02-20",
    "forecast_temp": 22.5,
    "forecast_min": 18.2,
    "forecast_max": 25.1,
    "model_forecasts": {"ecmwf_ifs025": 22.3, "icon_seamless": 22.8},
    "hourly_temps": [{"hour": 0, "temp": 18.2}, ...],
    "unit": "celsius",
    "last_update": 1739884800.0,
}
```

#### Realtime Weather Feed (METAR)
```python
{
    "icao_code": "EGLC",
    "date": "2026-02-20",
    "timezone": "Europe/London",
    "latest_temp": 8,
    "running_max": 9,
    "running_max_time": "14:20",
    "observations_count": 24,
    "last_update": 1739884800.0,
}
```

---

## File Structure

```
polyMetrics/
├── main.py                    # Entry point
├── requirements.txt           # Python dependencies
├── generate_context.py        # LLM context generator (for AI-assisted dev)
├── data/                      # Persistent data
│   ├── .env                   # API credentials (created by user)
│   └── workers/               # Worker configuration folders
│       └── w_*/param.txt      # url_market=...
├── frontend/                  # Static web dashboard
│   ├── analyses/
│   │   ├── analyses.html      # Main dashboard
│   │   ├── analyses.css       # Dark-themed styles
│   │   ├── analyses.js        # SSE client + chart orchestration
│   │   └── display/
│   │       ├── api.js         # Wallet & balance display
│   │       └── worker.js      # Chart.js integration (per-worker charts)
│   ├── favicon.ico
│   └── utils.js               # Live datetime clock
├── src/                       # Core Python logic
│   ├── classes/               # Feed modules (discovered dynamically)
│   │   ├── polymarket_feeds/
│   │   │   └── polymarket_feed.py
│   │   ├── predict_weather_feeds/
│   │   │   └── openmeteo_feed.py
│   │   ├── realtime_weather_feeds/
│   │   │   ├── aviation_weather.py
│   │   │   └── tgftp.py
│   │   └── worker.py          # Worker dataclass
│   ├── init/
│   │   ├── files.py           # Directory & file initialisation
│   │   └── user.py            # Polymarket auth + USDC balance
│   ├── pipeline/
│   │   ├── fetch.py           # Feed orchestration (main loop)
│   │   ├── load.py            # Worker config watcher
│   │   └── send.py            # SSE broadcaster
│   ├── server.py              # HTTP + SSE server
│   └── utils.py               # Helpers (key mappings, log formatting)
├── tools/                     # Shared utilities
│   └── logger/
│       └── logger.py          # File + console logger
└── UTILITY/                   # Development aids
    ├── for_you.txt            # Quick reference for module locations
    └── give_to_ai/            # AI context files (static + generated)
        ├── project_context.txt
        ├── data_flow_map.txt
        └── how_to_build_context.txt
```

---

## Dependencies

- `web3` – Ethereum blockchain interaction (USDC balance)
- `py_clob_client` – Polymarket ClobClient for order books and authentication
- `requests` – HTTP API calls (OpenMeteo, Aviation Weather, tgftp)
- `websockets` – Polymarket WebSocket subscription
- `Chart.js` – Frontend charting (loaded via CDN)

See `requirements.txt` for exact versions.

---

## License
GNU General Public License v3

---

*Maintained by [Alessio Iacoviello](https://github.com/alessiodev-it) — built for streaming, designed for insight.*
