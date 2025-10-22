from django.test import TestCase
from usersystem.models import User

class UserPermissionTests(TestCase):
    def test_user_roles(self):
        admin_user = User.objects.create(
            username="admin1",
            password="adminpass",
            role="admin"
        )
        self.assertEqual(admin_user.role, "admin")
