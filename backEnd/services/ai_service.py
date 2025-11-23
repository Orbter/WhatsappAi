from google import genai
from google.genai import types
# Note: We are importing the logic, but we will pass user_id dynamically now
from services.calendar_service import create_calendar, list_calendar_list, list_calendar_events, insert_calendar_event, get_today_date
from model.gemini_auth import client

from utils.functionTools import (
    create_calendar_function,
    create_calendar_event_function,
    list_calendar_events_function,
    list_calendar_list_function
)

def create_chat_session(client_start, raw_history):
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
        - "today" -> use {current_date}
        - "tomorrow" -> calculate tomorrow's date
        
        Format: YYYY-MM-DDTHH:MM:SS+02:00
        
        If a calendar name seems incomplete, list calendars first then ask.
        """

    config = types.GenerateContentConfig(
        tools=[tools],
        system_instruction=system_instruction
    )    
    
    gemini_history = raw_history
    
    chatGemini = client_start.chats.create(
        model="gemini-2.5-flash", 
        config=config,
        history=gemini_history
    )
    return chatGemini

def process_function_call(user_id, function_call):
    """
    Process a function call.
    IMPORTANT: We now pass user_id to every calendar function.
    """
    function_response_data = None
    args = dict(function_call.args)
    
    # Inject user_id into the arguments for the calendar service
    args['user_id'] = user_id
    
    try:
        if function_call.name == 'create_calendar':
            function_response_data = create_calendar(**args)
        
        elif function_call.name == 'insert_calendar_event':
            function_response_data = insert_calendar_event(**args)

        elif function_call.name == 'list_calendar_events':
            my_events = list_calendar_events(**args)
            function_response_data = {"my_events": my_events}
        
        elif function_call.name == 'list_calendar_list':
            # list_calendar_list only needs user_id (already in args if we add it, or passed directly)
            calendars = list_calendar_list(user_id=user_id)
            function_response_data = {"calendars": calendars}
            
    except Exception as e:
        function_response_data = {"error": str(e)}
    
    return function_response_data


def send_message(chat_session, user_message, user_id):
    """
    Send a message and handle function calls.
    ADDED: user_id argument to pass to tools.
    """
    response = chat_session.send_message(user_message)
    
    try:
        part = response.candidates[0].content.parts[0]
        
        if part.function_call:
            function_call = part.function_call
            
            function_call_info = {
                "name": function_call.name,
                "args": dict(function_call.args)
            }
            
            function_response_data = process_function_call(user_id, function_call)
            
            if function_response_data is not None:
                function_response_part = types.Part.from_function_response(
                    name=function_call.name,
                    response=function_response_data
                )
                # Send the tool output back to Gemini
                response = chat_session.send_message(function_response_part)
                return response.text, function_call_info
            else:
                return f"Error: Could not execute function {function_call.name}", function_call_info
        else:
            return response.text, None
            
    except Exception as e:
        print(f"Error in send_message: {e}")
        return "Sorry, something went wrong processing your request.", None