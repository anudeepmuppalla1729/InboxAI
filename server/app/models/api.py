from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class AuthStatusResponse(BaseModel):
    is_authenticated: bool
    email: Optional[str]

class SyncRequest(BaseModel):
    full_sync: bool = False # If True, ignore history_id and fetch by date

class SendEmailRequest(BaseModel):
    to: List[str]
    subject: str
    body: str
    preview: bool = True 