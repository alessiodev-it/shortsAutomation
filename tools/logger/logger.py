from datetime import datetime
from pathlib import Path
import os

def normalizeJobs(jobs):
    normJobs = []
    try:
        for job in jobs:
            normJobs.append(job.lower().strip())
        return normJobs
    except Exception as e:
        print(e)
    return False

class Logger:
    def __init__(self, jobs: list, filepath: Path = None):
        self.jobs = normalizeJobs(jobs)
        self.filepath = filepath
        self.firm = f"@Log - {filepath}\n"
        self.is_ok = False

        try:
            try:
                content = os.path.getsize(self.filepath) > 0
            except:
                content = False

            if self.jobs:
                if not content and "write" in self.jobs and self.filepath:
                    with open(self.filepath, "w", encoding="utf-8") as f:
                        f.write(self.firm)
            self.is_ok = True
        except Exception as e:
            print(e)

    def log(self, string):
        if not self.is_ok:
            return

        now = datetime.now().strftime("[%Y.%m.%d - %H:%M:%S]")
        string = f"{now}$ > {string}"

        for job in self.jobs:
            if job == "print":
                print(string)

            elif job == "write":
                if self.filepath:
                    with open(self.filepath, "a", encoding="utf-8") as f:
                        f.write(f"{string}\n")
                else:
                    print(f"filepath = {self.filepath}\n")

    def lastLines(self, readline=5):
        if not self.is_ok:
            return

        self.jobs = normalizeJobs(self.jobs)

        if "read" in self.jobs:
            print("__________________________________")
            if self.filepath:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    try:
                        readline = int(readline)
                        print("".join(lines[-readline:]))
                    except:
                        print("".join(lines[-5:]))
            else:
                print(f"filepath = {self.filepath}\n")
            print("__________________________________")

    def clear(self) -> bool:
        if not self.is_ok:
            return

        try:
            if self.filepath:
                with open(self.filepath, "w", encoding="utf-8") as f:
                    f.write(self.firm)
                    return True
        except Exception as e:
            print(e)
            self.is_ok = False

        print(f"'logger' -> is_ok = {self.is_ok}")
        return False

    def setFilepath(self, filepath):
        if not self.is_ok:
            return

        if filepath:
            self.filepath = filepath
            try:
                self.firm = f"@Log - {filepath}\n"
                with open(self.filepath, "w", encoding="utf-8") as f:
                    f.write(self.firm)
                    return True
            except Exception as e:
                print(e)
                self.is_ok = False

        print(f"filepath = {self.filepath}\n")
        return False


    def setJobs(self, jobs) -> bool:
        if not self.is_ok:
            return

        try:
            self.jobs = jobs
            self.jobs = normalizeJobs(self.jobs)
            return True
        except Exception as e:
            print(e)
        return False
