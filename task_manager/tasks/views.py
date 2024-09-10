from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Task
from .serializers import TaskSerializer
from googleapiclient.discovery import build
from task_manager.google_auth import get_credentials
from datetime import datetime, timedelta

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def create(self, request, *args, **kwargs):
        # Cria a tarefa no banco de dados
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        task = serializer.instance

        # Cria o evento no Google Calendar
        self.create_google_calendar_event(task)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        # Atualiza a tarefa no banco de dados
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        task = serializer.instance

        # Atualiza o evento no Google Calendar
        self.update_google_calendar_event(task)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()

        # Excluir o evento do Google Calendar
        self.delete_google_calendar_event(task)

        # Excluir a tarefa da base de dados
        self.perform_destroy(task)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create_google_calendar_event(self, task):
        creds = get_credentials()
        service = build('calendar', 'v3', credentials=creds)

        # Converta `task.date` e `task.time` para um objeto `datetime`
        start_datetime = datetime.combine(task.date, task.time)
        end_datetime = start_datetime + timedelta(hours=1)  # Adicione uma hora para o final do evento

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

        event = service.events().insert(calendarId='primary', body=event).execute()

        # Salvar o eventId no modelo
        task.google_event_id = event.get('id')
        task.save()

    def update_google_calendar_event(self, task):
        creds = get_credentials()
        service = build('calendar', 'v3', credentials=creds)

        # Converta `task.date` e `task.time` para um objeto `datetime`
        start_datetime = datetime.combine(task.date, task.time)
        end_datetime = start_datetime + timedelta(hours=1)  # Adicione uma hora para o final do evento

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
            service.events().update(
                calendarId='primary',
                eventId=task.google_event_id,
                body=event
            ).execute()

    def delete_google_calendar_event(self, task):
        creds = get_credentials()
        service = build('calendar', 'v3', credentials=creds)

        # Obter o ID do evento do Google Calendar
        google_event_id = task.google_event_id

        if google_event_id:
            service.events().delete(calendarId='primary', eventId=google_event_id).execute()
