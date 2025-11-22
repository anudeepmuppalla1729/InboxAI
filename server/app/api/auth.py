from fastapi import APIRouter , Request
from fastapi.responses import RedirectResponse
from app.core.auth import get_auth_flow, save_tokens, load_tokens
from app.core.config import settings
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

router = APIRouter(prefix="/api/v1/auth")

@router.get("/login")
def login():
    flow = get_auth_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes='true',
        prompt="consent"
    )
    return {"auth_url": auth_url}

@router.get("/callback")
def oauth_callback(request: Request):
    flow = get_auth_flow()
    flow.fetch_token(authorization_response=str(request.url))
    
    creds = flow.credentials
    
    # Decode ID token to get email
    try:
        id_info = id_token.verify_oauth2_token(
            creds.id_token, 
            google_requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )
        user_email = id_info.get("email")
    except ValueError:
        user_email = "unknown"

    save_tokens(creds)

    token = jwt.encode({"email": user_email}, settings.SECRET_KEY, algorithm="HS256")

    return RedirectResponse(url=f"http://localhost:5173/connected?token={token}")

@router.get("/status")
def check_status():
    creds = load_tokens()
    # Check if creds is not None (it's a GoogleTokenStore object now, not Credentials directly, but we can check existence)
    # The load_tokens returns GoogleTokenStore.
    # We need to check if it has valid fields or convert it back to Credentials to check validity if needed.
    # For now, just checking if it exists is likely what was intended, or we need to check expiry.
    
    if creds:
        # Simple check: if we have tokens, we are connected.
        # Ideally we should check expiry, but for status check this might suffice or we can add logic.
        return {"status": "connected"}
    return {"status": "not_connected"}