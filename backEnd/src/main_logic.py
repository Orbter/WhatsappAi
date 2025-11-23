from datetime import datetime
from services.ai_service import create_chat_session, send_message
# Note: You need to update your database import functions to match the new schema
from database.get_from_data import get_or_create_app_user, get_user_google_creds, get_or_create_chat, get_chat_history_as_text
from database.save_new_data import insert_message
from model.gemini_auth import client

def AiServerRunning(request):
    """
    Main controller logic.
    request: ChatRequest object containing user_id (string) and message (string)
    """
    try:
        client_identifier = request.user_id 
        internal_user_id = get_or_create_app_user(client_identifier)
        chat_id = get_or_create_chat(internal_user_id, chat_name="WhatsApp_General")
        insert_message(
            text=request.message, 
            is_from_bot=False, 
            user_id=internal_user_id, 
            chat_id=chat_id
        )
        # this is the google cred i need to chek if it is exist in whattsap
        access_token,refresh_token,scopes = get_user_google_creds(internal_user_id)        

        history_context = get_chat_history_as_text(chat_id, limit=10)

        gemini_session = create_chat_session(client, history_context) 
        
        
        response_text, function_info = send_message(gemini_session, request.message, internal_user_id)
        insert_message(
            text=response_text, 
            is_from_bot=True, 
            user_id=internal_user_id, 
            chat_id=chat_id
        )

        return response_text, function_info


    except Exception as e:
        import traceback
        traceback.print_exc()  # This prints full details to your terminal
        # RETURN THE ACTUAL ERROR TO THE CHAT SO YOU CAN SEE IT
        return f"🛑 DEBUG ERROR: {str(e)}", None