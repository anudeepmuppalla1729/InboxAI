from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag_pipeline import RagPipeline

router = APIRouter()

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Answer a user query about their emails using RAG.
    """
    try:
        pipeline = RagPipeline()
        answer = pipeline.answer_query(request.query)
        return ChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
