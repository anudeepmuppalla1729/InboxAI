from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class EmailDocument(BaseModel):
    """
    Represents a processed, cleaned email (ready for vector store).
    """
    gmail_id: str
    thread_id: str
    history_id: Optional[str] = None
    sender: str
    recipients: List[str]
    subject: str
    timestamps: Optional[datetime] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    labels: List[str] = Field(default_factory=list)

class GoogleTokenStore(BaseModel):
    """
    Represents token.json data.
    """
    access_token: str
    refresh_token: Optional[str] = None
    expiry: Optional[datetime] = None
    scopes: List[str] = Field(default_factory=list)
    client_id: str
    client_secret: str
    token_uri: str
