from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Task
from .serializers import TaskSerializer
from task_manager.google_auth import get_credentials
from .google_calendar_service import GoogleCalendarService
from rest_framework.permissions import IsAuthenticated

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filtrar as tarefas para o usuário logado
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Salvar a tarefa associada ao usuário logado
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        task = serializer.instance

        # Integração com o Google Calendar (opcional)
        google_calendar_service = GoogleCalendarService()
        google_event_id = google_calendar_service.create_event(task)
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

        # Atualizar evento no Google Calendar (opcional)
        google_calendar_service = GoogleCalendarService()
        google_calendar_service.update_event(task)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()

        # Deletar o evento do Google Calendar (opcional)
        google_calendar_service = GoogleCalendarService()
        google_calendar_service.delete_event(task.google_event_id)

        self.perform_destroy(task)
        return Response(status=status.HTTP_204_NO_CONTENT)
