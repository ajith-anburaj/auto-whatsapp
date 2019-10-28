import datetime
import os.path
import pickle
from collections import namedtuple

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class Calender:

    def __init__(self):
        self.service = Calender.get_service()

    @staticmethod
    def get_service():
        scopes = ['https://www.googleapis.com/auth/calendar']
        credentials_file = f'{os.getenv("PROJECT_DIRECTORY")}/config/credentials.json'
        credentials = None
        token_path = f'{os.getenv("PROJECT_DIRECTORY")}/calender/token.pickle'
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                credentials = pickle.load(token)
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, scopes=scopes)
                credentials = flow.run_local_server(port=0)
            with open(token_path, 'wb') as token:
                pickle.dump(credentials, token)
        service = build('calendar', 'v3', credentials=credentials, cache_discovery=False)
        return service

    def get_calenders(self):
        calendars_result = self.service.calendarList().list().execute()
        calendars = calendars_result.get('items', [])
        calendars_summary = []
        summary = namedtuple('calenders', ['id', 'description', 'primary'])
        for calendar in calendars:
            calendars_summary.append(summary(
                id=calendar['id'], description=calendar['summary'],
                primary=True if calendar.get('primary') else False
            ))
        return calendars_summary

    def get_events(self, calender_id='primary', upcoming=True, max_result=10):
        payload = {
            'calendarId': calender_id,
            'maxResults': max_result,
            'singleEvents': True,
            'orderBy': 'startTime'
        }
        if upcoming:
            payload['timeMin'] = f'{datetime.datetime.utcnow().isoformat()}Z'
        events_result = self.service.events().list(**payload).execute()
        events = events_result.get('items', [])
        events_summary = []
        event_summary = namedtuple('events', ['startDate', 'description'])
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            events_summary.append(event_summary(startDate=start, description=event['summary']))
        return events_summary
