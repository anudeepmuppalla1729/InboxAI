from fastapi import APIRouter , Request
from fastapi.responses import RedirectResponse
from app.core.auth import get_auth_flow, save_tokens, load_tokens

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
    save_tokens(creds)

    return RedirectResponse(url="http://localhost:5173/connected")  # Redirect to a success page or frontend route

@router.get("/status")
def check_status():
    creds = load_tokens()
    if creds and creds.valid:
        return {"status": "connected"}
    return {"status": "not_connected"}