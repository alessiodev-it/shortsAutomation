from pathlib import Path
import time

sleepingTime = 24 * 60 * 60  # 24 ore

def fullDay(log, time_file: Path):
    time_file.parent.mkdir(parents=True, exist_ok=True)

    if time_file.exists():
        with open(time_file, "r") as f:
            try:
                last_timestamp = float(f.read().strip())
            except ValueError:
                last_timestamp = time.time()
    else:
        last_timestamp = time.time()

    elapsed = time.time() - last_timestamp
    remaining = sleepingTime - elapsed

    if remaining <= 0:
        log("24 hours already passed!")
        with open(time_file, "w") as f:
            f.write(str(time.time()))
        return

    log(f"Sleeping for {remaining:.2f} seconds...")
    time.sleep(remaining)

    with open(time_file, "w") as f:
        f.write(str(time.time()))

    log("24 hours completed!")
