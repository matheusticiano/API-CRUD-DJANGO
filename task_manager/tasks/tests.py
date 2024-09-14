# tasks/tests/test_views.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from tasks.models import Task
from django.contrib.auth.models import User

class TaskTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')

        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.cookies['access'] = response.data['access']

    def test_create_task(self):
        url = reverse('task-list')
        data = {
            'title': 'Test Task',
            'description': 'This is a test task',
            'date': '2024-09-15',
            'time': '14:30:00'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_tasks(self):
        Task.objects.create(
            user=self.user, title='Task 1', description='Test task', date='2024-09-15'
        )

        url = reverse('task-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_task(self):
        task = Task.objects.create(
            user=self.user, title='Task 1', description='Test task', date='2024-09-15', time='14:30:00'
        )

        url = reverse('task-detail', args=[task.id])
        data = {
            'title': 'Updated Task',
            'description': 'Updated description',
            'date': '2024-09-15',
            'time': '15:30:00'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_task(self):
        task = Task.objects.create(
            user=self.user, title='Task 1', description='Test task', date='2024-09-15'
        )

        url = reverse('task-detail', args=[task.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
