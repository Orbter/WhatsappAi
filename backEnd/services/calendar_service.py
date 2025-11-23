import json 
from utils.api_auth import create_google_calendar_service
from datetime import datetime, timedelta, date

# DELETED: Global client_secret and global service construction.
# These cannot exist globally in a multi-user app.

def get_service(user_id):
    """Helper to get authorized service for a specific user"""
    return create_google_calendar_service(user_id, 'calendar', 'v3')

def create_calendar(user_id, name):
    """Create a new calendar for the specific user."""
    service = get_service(user_id)
    if not service: return {"error": "Could not authenticate user"}

    calendar_list = {'summary': name}
    created_calendar = service.calendars().insert(body=calendar_list).execute()
    return created_calendar

def get_CalenderId(user_id, calender_name):
    # We reuse list_calendar_list but pass the user_id
    allCalenders = list_calendar_list(user_id)
    for calender in allCalenders:
        if calender['name'].lower() == calender_name.lower(): # Added case-insensitivity
            return calender['id']
    return None
 
def list_calendar_list(user_id, max_capacity=200):
    """List calendars for the specific user."""
    service = get_service(user_id)
    if not service: return []

    if isinstance(max_capacity, str):
        max_capacity = int(max_capacity)
        
    all_calendars = []
    all_calendars_cleaned = []
    next_page_token = None
    capacity_tracker = 0

    while True:
        calendar_list = service.calendarList().list(
            maxResults=min(200, max_capacity - capacity_tracker),
            pageToken=next_page_token
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
        all_calendars_cleaned.append({
            'id': calendar.get('id'),
            'name': calendar.get('summary'),
            'description': calendar.get('description', ''),
        })
    return all_calendars_cleaned

def list_calendar_events(user_id, calendar_name, max_capacity=20):
    """List events for specific user and calendar."""
    service = get_service(user_id)
    if not service: return []

    if isinstance(max_capacity, str):
        max_capacity = int(max_capacity)

    calendar_id = get_CalenderId(user_id, calendar_name)
    if not calendar_id:
        return [{"error": f"Calendar {calendar_name} not found"}]

    all_events = []
    next_page_token = None
    capacity_tracker = 0
    
    while True:
        events_list = service.events().list(
            calendarId=calendar_id,
            maxResults=min(250, max_capacity - capacity_tracker),
            pageToken=next_page_token
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

def insert_calendar_event(user_id, calendar_name, summary, start_datetime, description=None, end_datetime=None, time_zone='Asia/Jerusalem', **kwargs):
    """Insert event for specific user."""
    service = get_service(user_id)
    if not service: return {"error": "Could not authenticate user"}

    try: 
        calendar_id = get_CalenderId(user_id, calendar_name)
        if not calendar_id:
             # If not found, return available ones to help the AI
            available = list_calendar_list(user_id)
            names = [c['name'] for c in available]
            return {"error": f"Calendar '{calendar_name}' not found.", "available_calendars": names}
    except Exception as e:
        return {"error": str(e)}
    
    if end_datetime is None:
        try:
            # Handle timezone removal safely
            clean_start = start_datetime.split('+')[0]
            start_dt = datetime.fromisoformat(clean_start)
            end_dt = start_dt + timedelta(hours=1)
            end_datetime = end_dt.isoformat() + '+02:00'
        except Exception as e:
             return {"error": f"Date format error: {e}"}
        
    event = {
        'summary': summary,
        'description': description,
        'start': {'dateTime': start_datetime, 'timeZone': time_zone},
        'end': {'dateTime': end_datetime, 'timeZone': time_zone},
    }
    event.update(kwargs)
    
    try:
        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        return created_event
    except Exception as e:
        return {"error": f"Google API Error: {e}"}

def get_today_date():
    return date.today().strftime("%Y-%m-%d")