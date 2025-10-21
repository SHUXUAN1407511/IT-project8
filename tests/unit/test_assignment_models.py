from django.test import TestCase
from Assignment.models import Assignment
from courses.models import Course

class AssignmentModelTest(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            Course_name="Test Course",
            code="TEST101",
            semester="2025S1",
            Description="Test course",
            coordinator="test_coord"
        )
        
    def test_assignment_creation(self):
        assignment = Assignment.objects.create(
            course=self.course,
            name="Test Assignment",
            type="Homework",
            description="Test description"
        )
        self.assertEqual(assignment.name, "Test Assignment")
        self.assertEqual(assignment.type, "Homework")
        
    def test_assignment_str(self):
        assignment = Assignment.objects.create(
            course=self.course,
            name="Final Project",
            type="Project"
        )
        self.assertEqual(str(assignment), "TEST101 - Final Project")
