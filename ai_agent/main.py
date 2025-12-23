import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# Import services
from services import get_ai_response_with_summary

# Load environment variables
load_dotenv()

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Neon Linde AI Agent")

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    summary: Optional[str] = ""

class ChatResponse(BaseModel):
    answer: str
    summary: str
    metrics: dict

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not request.message:
        raise HTTPException(status_code=400, detail="Message is required")

    try:
        # Call the updated service directly
        # Note: We are waiting for the summary here to ensure data consistency with the backend.
        # Call the updated service directly
        # Note: We are waiting for the summary here to ensure data consistency with the backend.
        # Thanks to Gemini Flash, this is still very fast.
        answer, new_summary, metrics = await get_ai_response_with_summary(request.message, request.summary)
        return ChatResponse(answer=answer, summary=new_summary, metrics=metrics)

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal AI Agent Error")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
