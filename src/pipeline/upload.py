from googleapiclient.http import MediaFileUpload
from datetime import datetime, timezone
from pathlib import Path
import time

def clip(log, clip_filepath, thumbnail_path, category, tags, title, description, youtube_build):
    log("Uploading clip...")

    metadata = {
        "title": title,
        "description": description,
        "tags": tags,
        "category": category,
        "privacyStatus": "public",
        "publishAt": None
    }

    video_id = _upload(str(clip_filepath), metadata, youtube_build, log)

    if thumbnail_path:
        _set_thumbnail(video_id, thumbnail_path, youtube_build, log)


def _set_thumbnail(video_id, thumbnail_path, youtube_build, log):
    log(f"Setting thumbnail: {thumbnail_path}")
    media = MediaFileUpload(thumbnail_path)
    youtube_build.thumbnails().set(videoId=video_id, media_body=media).execute()
    log("Thumbnail set!")

def _upload(input_file, metadata, youtube, log):
    body = {
        "snippet": {
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata["tags"],
            "categoryId": metadata["category"]
        },
        "status": {
            "privacyStatus": metadata["privacyStatus"],
            "selfDeclaredMadeForKids": metadata.get("madeForKids", False)
        }
    }

    if metadata.get("publishAt"):
        body["status"]["publishAt"] = metadata["publishAt"]

    log("Starting request")
    media = MediaFileUpload(input_file, chunksize=1024*1024, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    log("Request")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            log(f"Upload progress: {int(status.progress() * 100)}%")

    log(f"Clip uploaded! ID: {response['id']}")
    return response["id"]
