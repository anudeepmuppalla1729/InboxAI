import os
import json
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from app.core.config import settings  # ← IMPORTANT: loads .env via pydantic-settings

# Allow HTTP for local OAuth
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

TOKEN_PATH = "storage/tokens.json"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]

def get_auth_flow():
    print("\n--- GOOGLE OAUTH DEBUG ---")
    print("CLIENT ID:", settings.GOOGLE_CLIENT_ID)
    print("CLIENT SECRET:", settings.GOOGLE_CLIENT_SECRET)
    print("REDIRECT URI:", settings.GOOGLE_REDIRECT_URI)
    print("----------------------------\n")

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
            }
        },
        scopes=SCOPES,
    )

    flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
    return flow


def save_tokens(creds: Credentials):
    data = {
        "access_token": creds.token,
        "refresh_token": creds.refresh_token,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
        "expiry": creds.expiry.isoformat() if creds.expiry else None,
        "token_uri": creds.token_uri,
    }

    os.makedirs("storage", exist_ok=True)

    with open(TOKEN_PATH, "w") as f:
        json.dump(data, f, indent=4)


def load_tokens() -> Credentials | None:
    if not os.path.exists(TOKEN_PATH):
        return None

    with open(TOKEN_PATH, "r") as f:
        data = json.load(f)

    creds = Credentials(
        token=data["access_token"],
        refresh_token=data["refresh_token"],
        client_id=data["client_id"],
        client_secret=data["client_secret"],
        token_uri=data["token_uri"],
        scopes=data["scopes"],
    )

    # Refresh token if expired
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        save_tokens(creds)

    return creds
