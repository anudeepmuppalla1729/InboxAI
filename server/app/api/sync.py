from fastapi import APIRouter, HTTPException, BackgroundTasks
from loguru import logger
from app.services.gmail_service import GmailService
from app.services.chroma_store import ChromaStore

router = APIRouter()

def run_sync_task():
    """
    Background task to run the sync process.
    """
    try:
        logger.info("Starting background sync task...")
        gmail_service = GmailService()
        chroma_store = ChromaStore()
        
        # Fetch recent emails (e.g., last 50)
        # In a real app, we'd use historyId for incremental sync
        emails = gmail_service.fetch_recent(max_results=50)
        
        if emails:
            logger.info(f"Upserting {len(emails)} emails to ChromaDB...")
            chroma_store.upsert_emails(emails)
            logger.success("Sync completed successfully.")
        else:
            logger.info("No emails found to sync.")
            
    except Exception as e:
        logger.exception("Sync task failed")

@router.post("/sync")
async def trigger_sync(background_tasks: BackgroundTasks):
    """
    Trigger an email sync process in the background.
    """
    background_tasks.add_task(run_sync_task)
    return {"status": "Sync started", "message": "Email synchronization is running in the background."}
