# jobsboard/notifications/tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from notifications.models import Notification

User = get_user_model()

class NotificationModelTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )

    def test_notification_creation(self):
        notification = Notification.objects.create(
            user=self.user,
            title='Test Notification',
            message='This is a test notification',
            type='info'
        )
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.title, 'Test Notification')
        self.assertEqual(notification.message, 'This is a test notification')
        self.assertEqual(notification.type, 'info')
        self.assertFalse(notification.is_read)
        self.assertIsNone(notification.link)

    def test_notification_str_unread(self):
        notification = Notification.objects.create(
            user=self.user,
            title='Unread Notification',
            message='Message',
        )
        self.assertEqual(str(notification), f"{self.user} - Unread Notification (Unread)")

    def test_notification_str_read(self):
        notification = Notification.objects.create(
            user=self.user,
            title='Read Notification',
            message='Message',
            is_read=True
        )
        self.assertEqual(str(notification), f"{self.user} - Read Notification (Read)")

    def test_mark_notification_as_read(self):
        notification = Notification.objects.create(
            user=self.user,
            title='Mark Read Test',
            message='Message'
        )
        notification.is_read = True
        notification.save()
        updated = Notification.objects.get(id=notification.id)
        self.assertTrue(updated.is_read)
