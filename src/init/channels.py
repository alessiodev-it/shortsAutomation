from src.classes.channel import Channel
from src.init.auth import get_youtubeService
from pathlib import Path

def init(ch_quantity: int, dataDIR: Path, log) -> list:
    apiDIR = dataDIR / "api"
    channelsDIR = dataDIR / "channels"
    client_secret = apiDIR / "client_secret.json"

    channels = []

    for i in range(1, ch_quantity + 1):
        name, source, token_filename, tags  = _get_dataChannel(channelsDIR / f"ch{i}.txt", log)
        if None in (name, source, token_filename):
            log(f"Skipping channel {i} because data could not be read")
            continue

        channel = Channel()
        channel.name = name
        channel.subreddit_source = source
        channel.token_filename = token_filename
        channel.tags = tags
        channels.append(channel)

        log(f"Channel n.{i} > {name}, {source}, {token_filename} ;")

    for i, channel in enumerate(channels, start=1):
        log(f"Authenticating channel n.{i} > {channel.name}, {channel.subreddit_source}, {channel.token_filename} .")

        channel.youtube_build = get_youtubeService(
            apiDIR / channel.token_filename,
            client_secret,
            log
        )

        log(f"Channel n.{i} > authenticated")

    return channels


def _get_dataChannel(channelPath, log):
    data_to_get = {
        "name": None,
        "subreddit_source": None,
        "token_filename": None,
        "tags": None
    }

    try:
        with open(channelPath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or "=" not in line:
                    continue

                key, value = line.split("=", 1)
                key, value = key.strip(), value.strip()

                if key == "category":
                    value = int(value)
                elif key == "tags":
                    value = [tag.strip() for tag in value.split(",") if tag.strip()]

                if key in data_to_get:
                    data_to_get[key] = value

    except Exception as e:
        log(f"Error reading {channelPath}:\n{e}")
        return None, None, None

    data = data_to_get
    return data["name"], data["subreddit_source"], data["token_filename"], data["tags"]
