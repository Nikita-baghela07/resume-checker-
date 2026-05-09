from fastapi import APIRouter, HTTPException
from app.models.request_models import ChatRequest, ChatResponse
from app.services import chat_service
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(data: ChatRequest):
    """
    Real-time career coaching chatbot.
    """
    logger.info(f"💬 Chat request: {data.message[:50]}...")
    
    try:
        response_text = chat_service.get_chat_response(
            message=data.message,
            history=data.history,
            resume_context=data.resume_context,
            jd_context=data.jd_context,
            optimization_results=data.optimization_results
        )
        
        return ChatResponse(response=response_text)
        
    except Exception as e:
        logger.error(f"Chat route error: {e}")
        raise HTTPException(status_code=500, detail="Internal chatbot error")
