from django.test import TestCase
from Assignment.models import Assignment

class AcceptanceTests(TestCase):
    def test_template_creation_acceptance(self):
        assignment = Assignment.objects.create(
            name="Acceptance Test Template",
            type="Research Paper"
        )
        self.assertEqual(assignment.name, "Acceptance Test Template")
