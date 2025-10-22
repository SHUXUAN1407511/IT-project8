from django.test import TestCase
from Assignment.models import Assignment
from courses.models import Course
from usersystem.models import User

class TemplateSharingWorkflowTests(TestCase):
    def test_complete_template_sharing_workflow(self):
        coordinator = User.objects.create(
            username="sharing_coord",
            password="sharepass",
            role="sc",
            name="Sharing Coordinator"
        )
        
        course = Course.objects.create(
            Course_name="Sharing Workflow Course",
            code="SHARE201",
            semester="2025S1",
            Description="Complete template sharing workflow test",
            coordinator="sharing_coord"
        )
        
        template = Assignment.objects.create(
            course=course,
            name="Complete Sharing Template",
            type="Final Project",
            description="Template with complete information for sharing: AI guidelines, instructions, and requirements"
        )
        
        self.assertEqual(template.course.coordinator, "sharing_coord")
        self.assertIn("ai guidelines", template.description.lower())
        self.assertTrue(len(template.name) > 0)
        
    def test_template_with_detailed_ai_instructions(self):
        template = Assignment.objects.create(
            name="Detailed AI Instructions Template",
            type="Research Paper",
            description="""
            AI Use Guidelines:
            - R1: Grammar and spelling check only
            - R2: Research assistance and data analysis
            - R3: Content generation with proper citation
            - G: Full AI collaboration with disclosure
            
            Students must declare AI usage level.
            """
        )
        
        self.assertIn("ai use guidelines", template.description.lower())
        self.assertIn("r1", template.description.lower())
        self.assertIn("r2", template.description.lower())
        self.assertIn("declare", template.description.lower())
