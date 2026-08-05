import requests

def url_isValid(url) -> bool:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
        return r.status_code == 200
    except:
        return False

def get_data(source_name, limit, type, log):
    url = f"https://www.reddit.com/{source_name}/{type}.json?limit={limit}&t=day"
    log(f"Requesting: {url}")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.118 Safari/537.36",
        "Accept": "application/json"
    }

    try:
        res = requests.get(url, headers=headers, timeout=10)
        log(f"Status code: {res.status_code}")

        if res.status_code != 200:
            log(f"Reddit returned status {res.status_code} for {url}")
            log(f"Response body: {res.text[:500]}")
            return None

        return res.json()
    except Exception as e:
        log(f"Error fetching from reddit {url}: {str(e)}")
        return None

def get_content(data: dict, exception: list = None) -> dict:
    if data is None or "data" not in data or "children" not in data.get("data", {}):
        return {}

    bestVideo = {}
    max_upvotes = -1

    for post in data["data"]["children"]:
        p = post["data"]

        media = p.get("media")
        if p.get("is_video") and media:
            videoURL = media.get("reddit_video", {}).get("dash_url")

            if videoURL and (not exception or videoURL not in exception):
                upvotes = p.get("ups", 0)

                if upvotes > max_upvotes:
                    max_upvotes = upvotes

                    bestVideo = {
                        "url": videoURL,
                        "title": p.get("title", ""),
                        "description": p.get("selftext", ""),
                    }

    return bestVideo
