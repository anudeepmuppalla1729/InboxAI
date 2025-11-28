from fastapi import APIRouter, HTTPException
from app.services.rag_pipeline import RagPipeline

router = APIRouter()

@router.get("/highlights")
async def get_highlights():
    """
    Get AI-recommended important emails and summaries.
    """
    try:
        pipeline = RagPipeline()
        highlights = pipeline.get_important_emails()
        return {"highlights": highlights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
