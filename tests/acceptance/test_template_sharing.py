from django.test import TestCase
from Assignment.models import Assignment
from courses.models import Course

class TemplateSharingTests(TestCase):
    def test_shareable_template_creation(self):
        course = Course.objects.create(
            Course_name="Sharing Test Course",
            code="SHARE101",
            semester="2025S1",
            Description="Testing template sharing",
            coordinator="share_coord"
        )
        
        template = Assignment.objects.create(
            course=course,
            name="Shareable Template with AI Rules",
            type="Project",
            description="This template should be shareable with students and include clear AI guidelines"
        )
        
        self.assertTrue(len(template.name) > 0)
        self.assertTrue(len(template.description) > 0)
        self.assertIsNotNone(template.course)
        
    def test_template_ai_guidelines_clarity(self):
        template = Assignment.objects.create(
            name="AI Guidelines Template",
            type="Research",
            description="Clear AI use guidelines: R1 - Grammar check only, R2 - Research assistance"
        )
        
        self.assertIn("AI use guidelines", template.description)
        self.assertIn("R1", template.description)
        self.assertIn("R2", template.description)
