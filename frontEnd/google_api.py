import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

def create_google_calendar_service(client_secrets_file, api_name,api_version,*scopes, prefix=''):
    CLIENT_SECRETS_FILE = client_secrets_file
    API_NAME = api_name
    API_VERSION = api_version
    SCOPES = [scope for scope in scopes]

    creds =None
    working_dir = os.getcwd()
    token_dir = 'token_files'
    token_file = f'token_{API_NAME}_{API_VERSION}{prefix}.json'
    if not os.path.exists(os.path.join(working_dir, token_dir)):
        os.mkdir(os.path.join(working_dir, token_dir))
    
    if os.path.exists(os.path.join(working_dir, token_dir, token_file)):
        creds = Credentials.from_authorized_user_file(os.path.join(working_dir, token_dir, token_file), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(os.path.join(working_dir, token_dir, token_file), 'w') as token:
            token.write(creds.to_json())
    try:
        service = build(API_NAME, API_VERSION, credentials=creds, static_discovery=False)
        print(API_NAME,API_VERSION,'service created successfully')
        return service
    except Exception as e:
        print('Unable to connect.')
        print(e)
        print(f'Failed to create service for {API_NAME} ')
        os.remove(os.path.join(working_dir, token_dir, token_file))
        return None


# from swarms.models import Gemini
# from swarms.agents import Agent
# gemini_model = Gemini(
#     gemini_api_key=os.getenv("GEMINI_API_KEY") 
# )