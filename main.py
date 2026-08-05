from pathlib import Path
import traceback, time

from src.init import ( channels, files )
from src.pipeline import ( fetch, build, upload, wait )

from src.classes.channel import Channel
from src.init.auth import get_youtubeService
from tools.logger.logger import Logger

def main(files, log, clear, channels):
    dataDIR, stagingDIR, clipsDIR, outputDIR, clientJsonPATH = files[0], files[1], files[2], files[3], files[4]

    try:
        while True:
            for n, ch in enumerate(channels, start=1):
                log(f"In queue channel {n}/{len(channels)}: {ch.name}")
                try:
                    if not ch.youtube_build:
                        ch.youtube_build = get_youtubeService(ch.token_filename, clientJsonPATH, log)

                    clip = fetch.clip(log, ch.subreddit_source)
                    clip_filepath, thumbnail_filepath = build.clip(log, clip["url"], stagingDIR, outputDIR)
                    upload.clip(log, clip_filepath, thumbnail_filepath, ch.category, ch.tags, clip["title"], clip["description"], ch.youtube_build)

                    log(f"[OK] Channel '{ch.name}' processed successfully.")

                except Exception as e:
                    log(f"[ERROR] Channel '{ch.name}' failed.")
                    log(f"  Reason: {e}")
                    log(f"  Traceback:\n{traceback.format_exc()}")

            wait.fullDay(log, dataDIR / "time_lapsed.txt")
            clear()

    except KeyboardInterrupt:
        log(f"EOP with keyboard")
        return

    except Exception as e:
        log(f"EOP with error:\n{e}")
        log(f"EOP with traceback:\n{traceback.format_exc()}")
        return

if __name__ == "__main__":
    logger = Logger(["print", "write"], filepath=Path(__file__).parent / "log.txt")
    log, clear = logger.log, logger.clear

    log("SOP")
    log("Initializing")

    ch_quantity, dataDIR, stagingDIR, clipsDIR, outputDIR, clientJsonPATH = files.init(Path(__file__).parent, log)
    chs = channels.init(ch_quantity, dataDIR, log)

    log("Finished init")
    time.sleep(3)

    main([dataDIR, stagingDIR, clipsDIR, outputDIR, clientJsonPATH], log, clear, chs)
    log("EOP")
