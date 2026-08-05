from pathlib import Path

def init(prjDIR: Path, log):
    dataDIR = _make_rootData(prjDIR)
    channelsDIR = _make_channelsDir(dataDIR)
    ch_quantity, apiDIR, client_secret, tokens = _make_apiData(dataDIR, channelsDIR, log)
    outputDIR, stagingDIR, clipsDIR = _make_outputData(prjDIR)
    _make_channelsData(channelsDIR, ch_quantity, log)

    return ch_quantity, dataDIR, stagingDIR, clipsDIR, outputDIR, client_secret


def _make_rootData(prjDIR: Path):
    data = prjDIR / "data"
    data.mkdir(parents=True, exist_ok=True)
    return data

def _make_channelsDir(dataDIR):
    channelsDIR = dataDIR / "channels"
    channelsDIR.mkdir(exist_ok=True)
    return channelsDIR

def _make_apiData(dataDIR: Path, channelsDIR: int, log):
    apiDIR = dataDIR / "api"
    apiDIR.mkdir(exist_ok=True)

    client_secret = apiDIR / "client_secret.json"
    if not client_secret.exists():
        log("There is no client_secret.json")
        return None, None, None

    warning = False
    tokens = []

    ch_quantity = 0
    for f in channelsDIR.iterdir():
        if "ch" in f.stem and f.suffix == ".txt":
            ch_quantity += 1

    for n in range(1, ch_quantity + 1):
        token_path = apiDIR / f"token{n}.pickle"
        tokens.append(token_path)

        if not token_path.exists():
            warning = True

    if warning:
        log("Token missing")
        return None, None, None

    return ch_quantity, apiDIR, client_secret, tokens


def _make_outputData(prjDIR: Path):
    outputDIR = prjDIR / "output"
    stagingDIR = outputDIR / "staging"
    clipsDIR = outputDIR / "clips"

    outputDIR.mkdir(exist_ok=True)
    stagingDIR.mkdir(exist_ok=True)
    clipsDIR.mkdir(exist_ok=True)

    return outputDIR, stagingDIR, clipsDIR


def _make_channelFile(ch_path: Path, log):
    try:
        with open(ch_path, "w", encoding="utf-8") as f:
            f.write("name=None\n")
            f.write("subreddit_source=None\n")
            f.write("token_path=None\n")
            f.write("category=None\n")
            f.write("tags=None\n")
    except Exception as e:
        log(f"Error:\n{e}")
        return False

    return True


def _make_channelsData(channelsDIR: Path, ch_quantity: int, log):
    warning = False

    for n in range(1, ch_quantity + 1):
        ch_path = channelsDIR / f"ch{n}.txt"
        if not ch_path.exists():
            _make_channelFile(ch_path, log)
            warning = True

    if warning:
        log(f"Have been created profiles for each channel in dir: {channelsDIR}")
        log("Go insert expected infos")
