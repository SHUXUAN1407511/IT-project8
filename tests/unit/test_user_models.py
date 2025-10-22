from django.test import TestCase
from usersystem.models import User

class UserModelTest(TestCase):
    def test_user_creation(self):
        user = User.objects.create(
            username="testuser",
            password="testpass123",
            role="tutor",
            name="Test User",
            email="test@example.com"
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.role, "tutor")
        
    def test_user_str_representation(self):
        user = User.objects.create(
            username="adminuser",
            password="adminpass",
            role="admin",
            name="Admin User"
        )
        self.assertEqual(str(user), "Admin User (admin)")
        
    def test_user_without_name(self):
        user = User.objects.create(
            username="usernameonly",
            password="pass123", 
            role="sc"
        )
        self.assertEqual(str(user), "usernameonly (sc)")
