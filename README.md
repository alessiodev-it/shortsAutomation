# shortsAutomation

*Finally. My shorts are automated, and it feels so good.*

---

## Overview

**shortsAutomation** is a fully automated YouTube Shorts publishing engine. It discovers top‑performing videos from Reddit, downloads and crops them vertically (9:16), enhances audio and visual quality, generates an AI‑selected thumbnail, and uploads the finished clip to YouTube. Designed to run continuously, it supports multiple channels, each with its own subreddit source, tags, category, and OAuth credentials — making it easy to maintain a consistent publishing schedule with minimal manual intervention.

---

## Key Features

- **Multi‑Channel Support** – Manage multiple YouTube channels from a single instance, each with independent subreddit sources, tags, categories, and OAuth tokens.
- **Reddit Content Discovery** – Fetches the most upvoted video posts from a given subreddit (top/day) and selects the best one based on upvotes.
- **Video Processing Pipeline** – Downloads the clip with `yt‑dlp`, crops it vertically to 1080×1920, applies brightness and saturation adjustments, and increases audio pitch.
- **Smart Thumbnail Generation** – Uses `OpenCV` to analyse frames for motion, sharpness, brightness, and contrast, automatically selecting the most visually appealing frame as the thumbnail.
- **YouTube Upload** – Uploads the processed video with title, description, tags, category, and privacy setting (public). Supports resumable uploads with progress feedback.
- **Scheduled Publishing** – After each channel is processed, the script sleeps for 24 hours before repeating the cycle, ensuring a steady publishing rhythm.
- **Persistent Logging** – All operations are logged to a file with timestamps, allowing for easy debugging and monitoring.

---

## Installation

```bash
git clone https://github.com/alessiodev-it/shortsAutomation.git
cd shortsAutomation
python -m venv venv
source venv/bin/activate      # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### System Dependencies

- **ffmpeg** – required for video cropping and audio processing.  
  Install on Ubuntu/Debian:
  ```bash
  sudo apt install ffmpeg
  ```
  On macOS:
  ```bash
  brew install ffmpeg
  ```
- **OpenCV** – installed via `pip`, but may require additional system libraries depending on your platform.

---

## Configuration

### 1. Google Cloud Platform Setup

To authenticate with YouTube, you need a **client_secret.json** file from the Google Cloud Console:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project (or select an existing one).
3. Enable the **YouTube Data API v3**.
4. Create OAuth 2.0 credentials (Desktop application type).
5. Download the `client_secret.json` and place it in `data/api/client_secret.json`.

### 2. Channel Configuration

For each YouTube channel you want to automate, create a file in `data/channels/` named `chN.txt` (where `N` is a sequential number, e.g., `ch1.txt`, `ch2.txt`).

The file must contain the following key‑value pairs:

```ini
name=MyChannelName
subreddit_source=r/videos
token_path=token1.pickle
category=22
tags=short, viral, fun
```

| Field | Description |
|-------|-------------|
| `name` | The display name of your channel (used for logging) |
| `subreddit_source` | The subreddit to fetch videos from, e.g., `r/videos` |
| `token_path` | The filename of the OAuth token pickle (will be created automatically on first authentication) |
| `category` | YouTube category ID (e.g., `22` for "People & Vlogs") |
| `tags` | Comma‑separated list of tags for the video |

> **Note:** The `token_path` must be unique per channel. Tokens are stored in `data/api/`.

### 3. Initial Authentication

On first run, the script will detect missing tokens and prompt you to authenticate each channel via the browser (or by copying and pasting the redirect URL). Once authenticated, the token pickle is saved and reused for subsequent runs.

---

## Usage

Start the main script:

```bash
python main.py
```

The script will:
1. Initialise the directory structure.
2. Load and authenticate all configured channels.
3. For each channel:
   - Fetch the top video from the specified subreddit.
   - Download and process the clip.
   - Generate a thumbnail.
   - Upload the video to YouTube.
4. Wait 24 hours, then repeat the loop.

All progress is logged to `log.txt` (and also printed to the console).

To stop the script gracefully, press `Ctrl+C`.

---

## How It Works

### Main Loop (`main.py`)

The script runs an infinite loop that iterates over all configured channels. For each channel, it:

- Ensures the YouTube service is authenticated (`ch.youtube_build`).
- Calls the pipeline stages: **fetch**, **build**, **upload**.
- If any stage fails, the error is logged and the channel is skipped.
- After all channels are processed, the script calls `wait.fullDay()`, which sleeps until 24 hours have elapsed since the last complete cycle.

### Pipeline Stages

#### Fetch
- **`fetch.clip()`** – Requests the top posts from the subreddit using Reddit's JSON API.
- Filters for video posts and selects the one with the highest upvotes.
- Returns the video URL, title, and description.

#### Build
- **`downloadVideo()`** – Downloads the video using `yt-dlp` and merges audio/video into a single MP4.
- **`apply_verticalCrop()`** – Crops the video vertically to 1080×1920 (9:16) using `ffmpeg`. If the source is smaller, it scales up then crops.
- **`apply_genericEffects()`** – Adjusts brightness (+2%), increases saturation (+10%), and raises audio pitch by 5% for a slightly faster, more energetic feel.
- **`generate_thumbnail()`** – Analyses frames from 15% to 90% of the video duration, scoring each based on motion, sharpness, brightness, and contrast. The highest‑scoring frame is saved as `thumbnail.png`.

#### Upload
- **`upload.clip()`** – Builds the video metadata and initiates a resumable upload to YouTube using the official Google API client.
- Prints upload progress and returns the video ID.
- Optionally sets the generated thumbnail.

### Scheduling
- `wait.fullDay()` reads a timestamp file (`data/time_lapsed.txt`) to track when the last full cycle completed.
- If less than 24 hours have passed, it sleeps for the remaining time.
- After the sleep, it updates the timestamp file and continues.

---

## File Structure

```
shortsAutomation/
├── main.py                    # Entry point
├── log.txt                    # Persistent log file (auto‑generated)
├── data/
│   ├── api/
│   │   ├── client_secret.json # OAuth client secret (user‑provided)
│   │   ├── token1.pickle      # OAuth tokens per channel (auto‑generated)
│   │   ├── token2.pickle
│   │   └── token3.pickle
│   ├── channels/
│   │   ├── ch1.txt            # Channel configuration
│   │   ├── ch2.txt
│   │   └── ch3.txt
│   └── time_lapsed.txt        # Timestamp for 24‑hour scheduling
├── src/
│   ├── classes/
│   │   └── channel.py         # Channel dataclass
│   ├── init/
│   │   ├── files.py           # Directory and file initialisation
│   │   ├── auth.py            # YouTube OAuth flow
│   │   └── channels.py        # Channel loading and authentication
│   └── pipeline/
│       ├── build.py           # Orchestrates video processing
│       ├── fetch.py           # Reddit data retrieval
│       ├── upload.py          # YouTube upload logic
│       ├── wait.py            # 24‑hour scheduler
│       └── utils/
│           ├── of_build/
│           │   ├── crop.py    # Vertical crop using ffmpeg
│           │   ├── download.py# Video download using yt‑dlp
│           │   ├── effects.py # Audio/visual enhancements
│           │   └── thumbnail.py # Frame scoring and thumbnail generation
│           └── of_fetch/
│               └── get.py     # Reddit API client
└── tools/
    └── logger/
        └── logger.py          # Custom file/console logger
```

---

## Dependencies

- `yt-dlp` – video downloading
- `google-auth-oauthlib`, `google-api-python-client` – YouTube API
- `opencv-python` – thumbnail generation
- `requests` – Reddit API calls
- `ffmpeg` (system) – video processing

See `requirements.txt` for exact versions (create it by running `pip freeze > requirements.txt`).

---

## License
GNU General Public License v3

---

*Maintained by [Alessio Iacoviello](https://github.com/alessiodev-it) — built for experimentation, refined through practice.*
