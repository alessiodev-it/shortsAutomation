from yt_dlp import YoutubeDL
from pathlib import Path

def downloadVideo(url: str, outdir: Path) -> Path | None:
    output_template = str(outdir / "downloaded.%(ext)s")

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for file in outdir.iterdir():
            if file.stem == "downloaded" and file.suffix == ".mp4":
                return file
    except Exception as e:
        print(e)
        return None

    return None
