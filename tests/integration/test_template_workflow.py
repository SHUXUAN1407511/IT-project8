from django.test import TestCase
from courses.models import Course
from Assignment.models import Assignment
from usersystem.models import User

class TemplateManagementIntegrationTest(TestCase):
    def setUp(self):
        self.coordinator = User.objects.create(
            username="coordinator1",
            password="testpass123",
            role="sc",
            name="Test Coordinator"
        )
        self.tutor = User.objects.create(
            username="tutor1",
            password="testpass123", 
            role="tutor",
            name="Test Tutor"
        )
        
        self.course = Course.objects.create(
            Course_name="Integration Test Course",
            code="INT101",
            semester="2025S1",
            Description="Course for integration testing",
            coordinator="coordinator1"
        )
        
    def test_template_creation_with_course_and_tutor(self):
        assignment = Assignment.objects.create(
            course=self.course,
            name="Integration Test Assignment",
            type="Research Project",
            description="Testing integrated workflow"
        )
        
        assignment.tutors.add(self.tutor)
        
        self.assertEqual(assignment.course, self.course)
        self.assertEqual(assignment.tutors.count(), 1)
        self.assertEqual(assignment.tutors.first(), self.tutor)
        self.assertEqual(assignment.name, "Integration Test Assignment")
        
    def test_user_role_integration(self):
        self.assertEqual(self.coordinator.role, "sc")
        self.assertEqual(self.tutor.role, "tutor")
        
        assignment = Assignment.objects.create(
            course=self.course,
            name="Role Test Assignment",
            type="Homework"
        )
        
        self.assertEqual(assignment.course.coordinator, "coordinator1")
