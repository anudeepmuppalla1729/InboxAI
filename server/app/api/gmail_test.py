from fastapi import APIRouter
from loguru import logger

from app.services.gmail_service import GmailService

router = APIRouter(prefix="/api/v1/gmail", tags=["Gmail Test"])


@router.get("/profile")
def gmail_profile():
    """
    Test: Fetch Gmail profile (email address, total messages, total threads)
    """
    logger.info("Testing Gmail profile...")
    svc = GmailService()
    return svc.get_profile()


@router.get("/list")
def list_recent_emails(max_results: int = 10):
    """
    Test: List last N email metadata (IDs + threadIds)
    """
    logger.info(f"Listing last {max_results} emails...")
    svc = GmailService()
    return svc.list_messages(max_results=max_results)


@router.get("/details/{message_id}")
def get_message_details(message_id: str):
    """
    Test: Fetch full email contents (headers, body_text, body_html)
    """
    logger.info(f"Fetching details for email: {message_id}")
    svc = GmailService()
    return svc.fetch_message_details(message_id)


@router.post("/send")
def send_email(to: str, subject: str, body: str):
    """
    Test: Send a simple email.
    Example call:
    POST /api/v1/gmail/send?to=test@gmail.com&subject=Hello&body=This is a test
    """
    logger.info(f"Sending test email to {to}")
    svc = GmailService()
    return svc.send_email([to], subject, body)
