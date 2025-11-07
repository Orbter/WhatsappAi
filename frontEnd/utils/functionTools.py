create_calendar_function = {
    "name": "create_calendar",
    "description": "creates a google calendar with the given name.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Name of the calendar to be created.",
            },
        },
        "required": ["name"],
    },
}

create_calendar_event_function = {
    "name": "insert_calendar_event",
    "description": (
        "Creates and inserts a new event into a specific Google Calendar. "
        "The function locates the calendar by its name, then schedules an event "
        "on the specified date and time. It can include an event title and a detailed description "
    ),    
    "parameters": {
        "type": "object",
        "properties": {
            "calendar_name": {
                "type": "string",
                "description": "The name of the event (e.g., 'Cal-work')",
            },
            "summary": {
                "type": "string",
                "description": "Title of the event (e.g., 'Meeting about stocks')",
            },
            "description": {
                "type": "string",
                "description": "The description of the event (e.g., 'Going to meet Yotam and Omer in bank Leomi')",
            },
            "start_datetime": {
                "type": "string",
                "description": "The start Date of the meeting (e.g., '2025-10-31T17:00:00+02:00')",
            },
            "end_datetime": {
                "type": "string",
                "description": "The end Date of the meeting (e.g., '2025-10-31T17:70:00+02:00')",
            },
        },
        "required": ["calendar_name", "summary", "start_datetime"],
    }
}

list_calendar_events_function = {
    "name": "list_calendar_events",
    "description": "get the events of a single calendar",
    "parameters": {
        "type": "object",
        "properties": {
            "calendar_name": {
                "type": "string",
                "description": "Name of the calendar to get all the events from.",
            },
        },
        "required": ["calendar_name"],
    },
}

list_calendar_list_function = {
    "name": 'list_calendar_list',
    "description": "get all the calendars",
    "parameters": {
        "type": "object",
        "properties": {},
    },
}


