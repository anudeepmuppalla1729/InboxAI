from loguru import logger
import os
import base64
from typing import List, Optional, Dict, Any
from email import policy
from email.parser import BytesParser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials

from app.core.auth import load_tokens, save_tokens


class GmailService:
    def __init__(self):
        """
        Single-user Gmail service. Calls load_tokens() from core/auth.py.
        """
        logger.info("Initializing GmailService...")
        self.creds: Optional[Credentials] = load_tokens()

        if not self.creds:
            logger.error("No Google credentials found! User must authenticate first.")
            raise RuntimeError("No Google credentials found. Please authenticate first.")

        self.service = self._build_service()
        logger.success("GmailService initialized successfully.")

    def _build_service(self):
        try:
            service = build("gmail", "v1", credentials=self.creds, cache_discovery=False)
            logger.info("Successfully built Gmail API client.")
            return service
        except Exception as e:
            logger.exception("Failed to build Gmail service:")
            raise


    def get_profile(self) -> Dict[str, Any]:
        """Return Gmail profile info."""
        try:
            profile = self.service.users().getProfile(userId="me").execute()
            logger.debug(f"Gmail profile fetched: {profile}")
            return profile
        except HttpError:
            logger.exception("Error fetching Gmail profile")
            raise

    def list_messages(self, query: Optional[str] = None, max_results: int = 100):
        """List recent messages using Gmail search query."""
        try:
            resp = (
                self.service.users()
                .messages()
                .list(userId="me", q=query, maxResults=max_results)
                .execute()
            )
            msgs = resp.get("messages", [])
            logger.info(f"Fetched {len(msgs)} message IDs")
            return msgs
        except HttpError:
            logger.exception("Error listing Gmail messages")
            raise


    def fetch_message_details(self, message_id: str) -> Dict[str, Any]:
        """Fetch + decode full email."""
        try:
            msg = (
                self.service.users()
                .messages()
                .get(userId="me", id=message_id, format="raw")
                .execute()
            )

            raw_b64 = msg.get("raw")
            if not raw_b64:
                logger.warning("Raw format unavailable, falling back to FULL format.")
                msg_full = (
                    self.service.users()
                    .messages()
                    .get(userId="me", id=message_id, format="full")
                    .execute()
                )
                return self._parse_full_message(msg_full)

            raw_bytes = base64.urlsafe_b64decode(raw_b64.encode("utf-8"))
            email_message = BytesParser(policy=policy.default).parsebytes(raw_bytes)

            body_text, body_html = None, None

            if email_message.is_multipart():
                for part in email_message.walk():
                    ctype = part.get_content_type()
                    if ctype == "text/plain":
                        body_text = (part.get_content() or "").strip()
                    elif ctype == "text/html":
                        body_html = (part.get_content() or "").strip()
            else:
                if email_message.get_content_type() == "text/plain":
                    body_text = email_message.get_content().strip()
                elif email_message.get_content_type() == "text/html":
                    body_html = email_message.get_content().strip()

            headers = dict(email_message.items())

            parsed = {
                "gmail_id": message_id,
                "thread_id": msg.get("threadId"),
                "snippet": msg.get("snippet"),
                "headers": headers,
                "body_text": body_text,
                "body_html": body_html,
                "labelIds": msg.get("labelIds", []),
                "internalDate": msg.get("internalDate"),
            }

            logger.debug(f"Parsed message: {message_id}")
            return parsed

        except HttpError:
            logger.exception(f"Failed fetching details for message {message_id}")
            raise

    # -----------------------
    # Fallback Parser for FULL format
    # -----------------------

    def _parse_full_message(self, msg_full: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Parsing FULL-format message...")
        payload = msg_full.get("payload", {})
        parts = payload.get("parts", [])
        body_text, body_html = None, None

        def decode_part(part):
            data = part.get("body", {}).get("data")
            if not data:
                return None
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

        def walk(p):
            nonlocal body_text, body_html
            if "mimeType" not in p:
                return
            mime = p["mimeType"]
            if mime == "text/plain" and not body_text:
                body_text = decode_part(p)
            elif mime == "text/html" and not body_html:
                body_html = decode_part(p)
            for sp in p.get("parts", []) or []:
                walk(sp)

        walk(payload)

        return {
            "gmail_id": msg_full.get("id"),
            "thread_id": msg_full.get("threadId"),
            "snippet": msg_full.get("snippet"),
            "headers": {h["name"]: h["value"] for h in payload.get("headers", [])},
            "body_text": body_text,
            "body_html": body_html,
            "labelIds": msg_full.get("labelIds", []),
            "internalDate": msg_full.get("internalDate"),
        }

    # -----------------------
    # Sending Email
    # -----------------------

    def send_email(self, to: List[str], subject: str, body: str, html: bool = False):
        """Send an email."""
        try:
            if html:
                msg = MIMEMultipart("alternative")
                msg.attach(MIMEText(body, "html"))
            else:
                msg = MIMEText(body, "plain")

            msg["to"] = ", ".join(to)
            msg["subject"] = subject

            raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
            res = (
                self.service.users()
                .messages()
                .send(userId="me", body={"raw": raw})
                .execute()
            )

            logger.success(f"Email sent: messageId={res.get('id')}")
            return res

        except HttpError:
            logger.exception("Failed to send email")
            raise

    # -----------------------
    # Helper: Fetch Recent Emails
    # -----------------------

    def fetch_recent(self, max_results: int = 10):
        logger.info(f"Fetching {max_results} recent emails...")
        messages = self.list_messages(max_results=max_results)
        detailed = []

        for m in messages:
            try:
                detailed.append(self.fetch_message_details(m["id"]))
            except Exception:
                logger.exception(f"Failed to fetch email {m['id']}")

        logger.success("Fetched and parsed recent emails")
        return detailed
