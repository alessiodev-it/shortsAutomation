from src.pipeline.utils.of_fetch.get import (
    get_data, get_content, url_isValid
)
import requests

def clip(log, source_name: str, limit: int = 100, type : str = "top") -> str:
    log("Fetching clip...")

    data = get_data(source_name, limit, type, log)
    log(f"DATA=\n{data}\n")

    if data is None:
        log(f"Failed to fetch data from Reddit for {source_name}")
        return None

    exception = []
    for n in range(limit):
        video = get_content(data, exception)
        url = video.get("url")
        if not url:
            break

        if url_isValid(video["url"]):
            log(f"VIDEO=\n{video}\n")
            return video
        else:
            exception.append(video["url"])

    else:
        log(f"VIDEO=\n{video}\n")
        return video
