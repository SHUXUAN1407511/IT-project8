from django.test import TestCase
from usersystem.models import User
from courses.models import Course
from Assignment.models import Assignment

class EnhancedPermissionTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create(
            username="admin_test", 
            password="adminpass", 
            role="admin",
            name="Admin User"
        )
        self.coordinator = User.objects.create(
            username="coord_test",
            password="coordpass",
            role="sc", 
            name="Coordinator User"
        )
        self.tutor = User.objects.create(
            username="tutor_test",
            password="tutorpass",
            role="tutor",
            name="Tutor User"
        )
        self.course = Course.objects.create(
            Course_name="Permission Test Course",
            code="PERM101",
            semester="2025S1",
            Description="Testing enhanced permissions",
            coordinator="coord_test"
        )
        
    def test_admin_user_creation(self):
        self.assertEqual(self.admin.role, "admin")
        self.assertEqual(self.admin.username, "admin_test")
        
    def test_coordinator_course_relationship(self):
        self.assertEqual(self.course.coordinator, "coord_test")
        self.assertEqual(self.coordinator.role, "sc")
        
    def test_tutor_assignment_permissions(self):
        assignment = Assignment.objects.create(
            course=self.course,
            name="Tutor Permission Test",
            type="Exercise"
        )
        assignment.tutors.add(self.tutor)
        
        self.assertEqual(assignment.tutors.count(), 1)
        self.assertEqual(assignment.tutors.first().username, "tutor_test")
        
    def test_user_role_validation(self):
        valid_roles = ["admin", "sc", "tutor"]
        self.assertIn(self.admin.role, valid_roles)
        self.assertIn(self.coordinator.role, valid_roles)
        self.assertIn(self.tutor.role, valid_roles)
