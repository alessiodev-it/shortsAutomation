from googleapiclient.discovery import build
from dataclasses import dataclass

@dataclass
class Channel:
    name: str = None
    subreddit_source: str = None
    token_filename: str = None
    youtube_build: build = None
    category: int = None
    tags: list = None
