from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from .main_logic import AiServerRunning
import os
from google_auth_oauthlib.flow import Flow
from starlette.responses import RedirectResponse
import json
from database.get_from_data import get_or_create_app_user
from database.save_new_data import insert_message, save_user_google_creds

# from database import get_db, init_db, UserCRUD, ConversationCRUD, User
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SRC_DIR)
CLIENT_SECRETS_FILE = os.path.join(BACKEND_DIR, 'client-secret.json')
print(f"📂 Looking for secrets file at: {CLIENT_SECRETS_FILE}")

SCOPES = ['https://www.googleapis.com/auth/calendar']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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


@app.get("/auth/login")
async def login(user_id: str):
    
    # Check if file exists before crashing
    if not os.path.exists(CLIENT_SECRETS_FILE):
        return {"error": f"Still cannot find file at {CLIENT_SECRETS_FILE}. Check terminal for path."}
    
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,  # <--- Use the variable we made
        scopes=SCOPES,
        redirect_uri='http://localhost:8000/auth/callback'
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        state=user_id  
    )
    
    return RedirectResponse(authorization_url)

@app.get("/auth/callback")
async def auth_callback(code: str, state: str):
    try:
        client_identifier = state 
        
        internal_user_id = get_or_create_app_user(client_identifier)
        
        if not internal_user_id:
            return {"error": "Authentication failed: Could not create/find internal user ID."}

        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri='http://localhost:8000/auth/callback'
        )
        flow.fetch_token(code=code)
        creds = flow.credentials

        save_user_google_creds(
            user_id=internal_user_id, 
            service_name='google_calendar', 
            access_token=creds.token,
            refresh_token=creds.refresh_token,
            token_expiry=creds.expiry.isoformat(),
            scopes=json.dumps(creds.scopes) if creds.scopes else None
        )

        return {"message": "Login successful! Tokens saved to Database."}

    except Exception as e:
        # Ensure the whole exception is returned for debugging if something else breaks
        return {"error": f"Authentication failed: {str(e)}"}