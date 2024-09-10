from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Task
from .serializers import TaskSerializer
from task_manager.google_auth import get_credentials
from .google_calendar_service import GoogleCalendarService  # Importe o serviço
from datetime import datetime, timedelta

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    google_calendar_service = GoogleCalendarService()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        task = serializer.instance

        google_event_id = self.google_calendar_service.create_event(task)
        task.google_event_id = google_event_id
        task.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        task = serializer.instance

        self.google_calendar_service.update_event(task)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        self.google_calendar_service.delete_event(task.google_event_id)
        self.perform_destroy(task)
        return Response(status=status.HTTP_204_NO_CONTENT)
