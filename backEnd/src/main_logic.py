from model.gemini_auth import client
from services.ai_service import create_chat_session,send_message
from services.history import load_history, save_history  # <-- IMPORT your new functions
from database import check_history, create_history, get_or_create_chat,get_user_chats,insert_message,get_user_messages
import os # <-- Import os
HISTORY_DIR = "Gemini_history"
def AiServerRunning(request):
    try:
        if not os.path.exists(HISTORY_DIR):
            os.makedirs(HISTORY_DIR)
        user_history = check_history()

        # user_history_file = os.path.join(HISTORY_DIR, f"Gemini_history_{request.user_id}.json")
        raw_history = load_history(user_history_file)
        gemini = create_chat_session(client, raw_history)  
        response_text, function_info = send_message(gemini, request.message)  
        new_chat = {
            "user": request.message,
            "assistant": response_text
        }
        save_history(user_history_file, new_chat)
        return response_text, function_info
    except Exception as e:
        print(f"ERROR in AiServerRunning: {str(e)}")
        print(traceback.format_exc())  # Print full traceback
        raise  # Re-raise the exception