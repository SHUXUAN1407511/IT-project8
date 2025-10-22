from django.test import TestCase
from Assignment.models import Assignment

class SimpleAPITest(TestCase):
    def test_assignment_creation(self):
        assignment = Assignment.objects.create(
            name="API Test Assignment",
            type="Research"
        )
        self.assertEqual(assignment.name, "API Test Assignment")
        self.assertEqual(assignment.type, "Research")
