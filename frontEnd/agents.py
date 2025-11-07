from google import genai
from google.genai import types
from dotenv import load_dotenv 
from calendar_tools import create_calendar, list_calendar_list, list_calendar_events, insert_calendar_event, get_today_date
from history import load_history, save_history
from utils.functionTools import (
    create_calendar_function,
    create_calendar_event_function,
    list_calendar_events_function,
    list_calendar_list_function
)
load_dotenv()



def create_chat_session(client_start):
    """Create a new chat session with the Gemini model."""
    tools = types.Tool(function_declarations=[
        create_calendar_function,
        create_calendar_event_function,
        list_calendar_events_function,
        list_calendar_list_function,
    ])    
    current_date = get_today_date()

    system_instruction = f"""
    You are a calendar assistant for a user in the Asia/Jerusalem timezone.

    IMPORTANT DATE HANDLING:
    Today's date is {current_date}. When users say:
    - "today" → use {current_date}
    - "tomorrow" → calculate tomorrow's date
    - "next Monday" → calculate the next Monday
    - "in 3 days" → calculate 3 days from today

    All datetime strings must be in ISO 8601 format with timezone:
    Format: YYYY-MM-DDTHH:MM:SS+02:00
    Example: 2025-11-01T17:00:00+02:00

    When users say times like "at 5" or "5pm", convert to 24-hour format:
    - "at 5" or "5pm" → 17:00:00
    - "at 5am" → 05:00:00
    - "at noon" → 12:00:00
    """

    config = types.GenerateContentConfig(
        tools=[tools],
        system_instruction=system_instruction
    )    
    
    raw_history = load_history('Gemini_history.json')
    gemini_history = []
    
    for turn in raw_history:
        gemini_history.append({
            "role": "user",
            "parts": [{"text": turn["user"]}]
        })
        gemini_history.append({
            "role": "model",
            "parts": [{"text": turn["assistant"]}]
        })
    
    chatGemini = client_start.chats.create(
        model="gemini-2.5-flash", 
        config=config,
        history=gemini_history
    )
    return chatGemini

def process_function_call(function_call):
    """
    Process a function call from the Gemini model and return the response.
    
    Parameters:
    - function_call: The function call object from Gemini response.
    
    Returns:
    - dict: The function response data, or None if function execution failed.
    """
    function_response_data = None
    
    if function_call.name == 'create_calendar':
        function_response_data = create_calendar(**function_call.args)
    
    elif function_call.name == 'insert_calendar_event':
        function_response_data = insert_calendar_event(**function_call.args)

    elif function_call.name == 'list_calendar_events':
        my_events = list_calendar_events(**function_call.args)
        function_response_data = {"my_events": my_events}
    
    elif function_call.name == 'list_calendar_list':
        calendars = list_calendar_list()
        function_response_data = {"calendars": calendars}
    
    return function_response_data


def send_message(chat_session, user_message):
    """
    Send a message to the chat session and handle function calls.
    
    Parameters:
    - chat_session: The Gemini chat session.
    - user_message: The user's message string or function response.
    
    Returns:
    - tuple: (response_text, function_call_info) where function_call_info is a dict or None.
    """
    response = chat_session.send_message(user_message)
    
    if response.candidates[0].content.parts[0].function_call:
        function_call = response.candidates[0].content.parts[0].function_call
        
        function_call_info = {
            "name": function_call.name,
            "args": dict(function_call.args)
        }
        
        function_response_data = process_function_call(function_call)
        
        if function_response_data is not None:
            function_response_part = types.Part.from_function_response(
                name=function_call.name,
                response=function_response_data
            )
            response = chat_session.send_message(function_response_part)
            return response.text, function_call_info
        else:
            return f"Error: Could not execute function {function_call.name}", function_call_info
    else:
        return response.text, None
    
