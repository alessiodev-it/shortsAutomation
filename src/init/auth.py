from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from urllib.parse import urlparse, parse_qs
from pathlib import Path
import pickle, os

SCOPES = [
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.upload"
]

def get_youtubeService(token_path: Path, client_secret_path: Path, log):
    creds = None

    if os.path.exists(token_path):
        try:
            with open(token_path, "rb") as token:
                creds = pickle.load(token)
        except Exception as e:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())

                with open(token_path, "wb") as token:
                    pickle.dump(creds, token)

            except RefreshError as e:
                creds = None
                log("[AUTH] Refresh token failed, forcing re-login")

        if not creds:
            creds = _get_credentials(client_secret_path, token_path, log)

    return build("youtube", "v3", credentials=creds)


def _get_credentials(client_secret_path: Path, token_path: Path, log, port: int = 0):
    flow = InstalledAppFlow.from_client_secrets_file(
        str(client_secret_path),
        SCOPES
    )

    try:
        creds = flow.run_local_server(
            port=port,
            prompt='consent',
            authorization_prompt_message='Visita questo URL per autorizzare: {url}',
            success_message='Autenticazione completata. Puoi chiudere questa finestra.',
            open_browser=True,
            timeout_seconds=300
        )

    except AttributeError as e:
        auth_url, _ = flow.authorization_url(prompt='consent')
        log(f"Visit URL: {auth_url}")

        code_url = input("\nPaste redirect URL here: ").strip()
        parsed = urlparse(code_url)
        code = parse_qs(parsed.query).get('code', [None])[0]

        if code:
            flow.fetch_token(code=code)
            creds = flow.credentials
        else:
            raise ValueError("Unable extracting authorization code from URL")

    except Exception as e:
        raise

    with open(token_path, "wb") as token:
        pickle.dump(creds, token)

    return creds
