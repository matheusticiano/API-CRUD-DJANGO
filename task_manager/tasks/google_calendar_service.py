from googleapiclient.discovery import build
from datetime import timedelta, datetime
from task_manager.google_auth import get_credentials

class GoogleCalendarService:

    def __init__(self):
        self.creds = get_credentials()
        self.service = build('calendar', 'v3', credentials=self.creds)

    def create_event(self, task):
        start_datetime = datetime.combine(task.date, task.time)
        end_datetime = start_datetime + timedelta(hours=1)

        event = {
            'summary': task.title,
            'description': task.description,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
        }

        event = self.service.events().insert(calendarId='primary', body=event).execute()
        return event.get('id')

    def update_event(self, task):
        start_datetime = datetime.combine(task.date, task.time)
        end_datetime = start_datetime + timedelta(hours=1)

        event = {
            'summary': task.title,
            'description': task.description,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'America/Sao_Paulo',
            },
        }

        if task.google_event_id:
            self.service.events().update(
                calendarId='primary',
                eventId=task.google_event_id,
                body=event
            ).execute()

    def delete_event(self, google_event_id):
        if google_event_id:
            self.service.events().delete(calendarId='primary', eventId=google_event_id).execute()
