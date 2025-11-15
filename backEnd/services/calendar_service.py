import json 
from utils.api_auth import create_google_calendar_service
from datetime import datetime, timedelta,date

client_secret = 'client-secret.json'

def construct_google_calendar_client(client_secret):
    """
    Construct a Google Calendar API client.
    
    Parameters:
    - client_secret (str): Path to the client secret JSON file.
    
    Returns:
    - service: The Google Calendar API service instance.
    """
    API_NAME = 'calendar'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    service = create_google_calendar_service(
        client_secret,
        API_NAME,
        API_VERSION,
        *SCOPES
    )
    return service

calendar_service = construct_google_calendar_client(client_secret)

def create_calendar(name):
    """
    Create a new calendar.
    
    Parameters:
    - name (str): The name of the calendar list.
    
    Returns:
    - dict: a dictionary that contains the ID of the new calendar list.
    """
    calendar_list = {
        'summary': name,
    }
    created_calendar_list = calendar_service.calendars().insert(body=calendar_list).execute()
    return created_calendar_list

def get_CalenderId(calender_name, allTheListFunction):
    allCalenders = allTheListFunction()
    for calender in allCalenders:
        if calender['name'] == calender_name:
            return calender['id']
    return None
 
def list_calendar_list(max_capacity=200):
    """
    List calendar lists until the total number of items reaches max_capacity.
    
    Parameters:
    - max_capacity (int or str optional): The  maximum number of calendar lists to retrieve. Defaults to 200.
        if a string is provided, it will be converted to an integer.
    
    Returns:
    - dict: a dictionaries containing cleaned calendar list information with 'id', 'name', and 'description'.
    """
    if isinstance(max_capacity, str):
        max_capacity = int(max_capacity)
        
    all_calendars = []
    all_calendars_cleaned = []
    next_page_token = None
    capacity_tracker = 0

    while True:
        calendar_list = calendar_service.calendarList().list(
            maxResults = min(200, max_capacity - capacity_tracker),
            pageToken = next_page_token
        ).execute()
        calendars = calendar_list.get('items', [])
        all_calendars.extend(calendars)
        capacity_tracker += len(calendars)
        if capacity_tracker >= max_capacity:
            break
        next_page_token = calendar_list.get('nextPageToken')
        if not next_page_token:
            break
    for calendar in all_calendars:
        all_calendars_cleaned.append(
            {
                'id': calendar.get('id'),
                'name': calendar.get('summary'),
                'description': calendar.get('description', ''),
            }
        )
    return all_calendars_cleaned

def list_calendar_events(calendar_name, max_capacity =20):
    """
    List events from a specific calendar until the total number of items reaches max_capacity.
    
    Parameters:
    - calendar_name (str): The name of the calendar to retrieve events from.
    - max_capacity (int or str optional): The maximum number of events to retrieve. Defaults to 20.
        if a string is provided, it will be converted to an integer.
    
    Returns:
    - list: a list of event from specified calendar.
    """
    if isinstance(max_capacity, str):
        max_capacity = int(max_capacity)

    calendar_id = get_CalenderId(calendar_name,list_calendar_list)
    all_events = []
    next_page_token = None
    capacity_tracker = 0
    while True:
        events_list = calendar_service.events().list(
            calendarId=calendar_id,
            maxResults = min(250, max_capacity - capacity_tracker),
            pageToken = next_page_token
        ).execute()
        events = events_list.get('items', [])
        all_events.extend(events)
        capacity_tracker += len(events)
        if capacity_tracker >= max_capacity:
            break
        next_page_token = events_list.get('nextPageToken')
        if not next_page_token:
            break
    return all_events



def insert_calendar_event(calendar_name, summary, start_datetime, description=None, end_datetime=None, time_zone='Asia/Jerusalem', **kwargs):
    """
    Insert an event into a specific calendar using only a start time.
    Google Calendar will automatically set the event duration (usually 1 hour).    
    Parameters:
    - service: The Google Calendar API service instance.
    - calender_name: the name of the calender you will get the id in the function.
    - calendar_id: The ID of the calendar where the events will be inserted you will get this as an argument in this function.
    - summary: Title of the event.
    - start_datetime: The start date and time (e.g., "2025-10-31T17:00:00+02:00").
    - description: Description of the event.
    - time_zone: The timezone for the event. Defaults to 'Asia/Jerusalem'.
    - **kwargs: Additional keyword arguments representing event details.
    
    Returns:
    - The created event.
    """
    try: 
        calendar_id = get_CalenderId(calendar_name,list_calendar_list)
    except ValueError as e:
        available_calendars = list_calendar_list()
        calendar_names = [cal['name'] for cal in available_calendars]
        error_msg = f"Calendar '{calendar_name}' not found. Available calendars: {', '.join(calendar_names)}"
        return {"error": error_msg, "available_calendars": calendar_names}
    
    if end_datetime is None:
        start_dt = datetime.fromisoformat(start_datetime.replace('+02:00', ''))
        end_dt = start_dt + timedelta(hours=1)
        end_datetime = end_dt.isoformat() + '+02:00'
    
        
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_datetime,
            'timeZone': time_zone,
        },
        'end': {
            'dateTime': end_datetime,
            'timeZone': time_zone,
        },
    }
    event.update(kwargs)
    event = calendar_service.events().insert(calendarId=calendar_id, body=event).execute()
    return event

def get_today_date():
    return date.today().strftime("%Y-%m-%d")
