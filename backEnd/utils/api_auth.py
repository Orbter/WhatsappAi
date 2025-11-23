import os
from database.get_from_data import get_user_google_creds
from database.validation_data import is_token_valid
from datetime import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

def refresh_user_token(user_id, service_name):
    """
    Refreshes an expired Google OAuth token using the refresh token.
    
    Parameters:
    - user_id (int): The ID of the user.
    - service_name (str): The name of the service (e.g., 'calendar').
    
    Returns:
    - Credentials object: The newly refreshed Credentials object, or None on failure.
    """
    db_service_name = f'google_{service_name}'
    
    # 1. Retrieve the stored credentials including the refresh token
    creds_data = get_user_google_creds(user_id, db_service_name)
    
    if not creds_data or not creds_data.get('refresh_token'):
        print(f"No refresh token found for user {user_id} and service {db_service_name}.")
        return None

    try:
        # 2. Create a Credentials object from the stored data
        creds = Credentials(
            token=creds_data['access_token'],
            refresh_token=creds_data['refresh_token'],
            token_uri='https://oauth2.googleapis.com/token',
            scopes=creds_data['scopes']
        )
        
        # Force the refresh flow by setting expired=True
        creds.expired = True 
        
        # 3. Perform the token refresh using a Request object
        creds.refresh(Request())
        
        # 4. Save the new access token and expiry time back to the database
        # creds.expiry is a datetime object, converting to ISO format for database TIMESTAMP storage.
        token_expiry_str = creds.expiry.isoformat()
        
        success = get_user_google_creds(
            user_id=user_id,
            service_name=db_service_name,
            access_token=creds.token,
            # Refresh token may or may not be returned on refresh, so we reuse the original one
            refresh_token=creds.refresh_token, 
            token_expiry=token_expiry_str,
            scopes=creds.scopes
        )
        
        if success:
            print(f"Token for user {user_id} and service {db_service_name} refreshed and saved successfully.")
            return creds
        else:
            print(f"Failed to save refreshed token for user {user_id} and service {db_service_name}.")
            return None
            
    except Exception as e:
        print(f"Error refreshing token for user {user_id}: {e}")
        return None



def create_google_calendar_service(user_id, service_name='calendar', service_version='v3',scopes=None):

    # 1. Fetch stored credentials
    creds_data = get_user_google_creds(user_id)
    if not creds_data:
        return None

    # 2. Refresh token if needed
    if not is_token_valid(user_id, f'google_{service_name}'):
        creds = refresh_user_token(user_id, service_name)
        if not creds:
            return None
    else:
        # 3. Build credentials object
        creds = Credentials(
            token=creds_data["access_token"],
            refresh_token=creds_data["refresh_token"],
            token_uri="https://oauth2.googleapis.com/token",
            scopes=creds_data["scopes"]
        )

    # 4. Build and return calendar service
    try:
        service = build(service_name, service_version, credentials=creds)
        return service
    except Exception as e:
        print(f"Error creating Google Calendar service: {e}")
        return None