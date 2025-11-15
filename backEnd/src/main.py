from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from .main_logic import AiServerRunning
import os

# from database import get_db, init_db, UserCRUD, ConversationCRUD, User


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],    
    allow_headers=["*"],    
)

class ChatRequest(BaseModel):
    """
    client front end sends to api
    Example:
    {
        "user_id": "972501234567",
        "message": "Create a calendar called Work"
    }
    """
    user_id: str      
    message: str     
    session_id: Optional[str] = None 

class ChatResponse(BaseModel):
    """
    what our API sends back to client.
    
    Example:
    {
        "user_id": "+972501234567",
        "response": "created the Work calendar!",
        "function_called": "create_calendar",
        "success": true
    }
    """
    user_id: str
    response: str
    function_called: Optional[str] = None
    success: bool = True

@app.get('/')
def root():
    return {'message':'api is running'}

@app.get('/chat',response_model=ChatRequest)
async def getMessage(user_id: str,message: str,session_id: Optional[str]):
    return {'all_messages':'niga'}

@app.post('/chat',response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response_text, function_info = AiServerRunning(request)
        return ChatResponse(
            user_id=request.user_id,
            response=response_text,
            function_called=function_info.get('name') if function_info else None,
            success=True
        )
    
    except Exception as e:
        return ChatResponse(
            user_id=request.user_id,
            response=f"Error processing request: {str(e)}",
            function_called=None,
            success=False
        )



@app.get('/niga')
def yotam(text):
    return {'text':{text}}

@app.get("/health")
def health_check():
    """Simple health check endpoint for the frontend"""
    return {"status": "ok"}