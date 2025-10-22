from django.test import TestCase
from Assignment.models import Assignment
from courses.models import Course

class TemplateDistributionTests(TestCase):
    def test_template_sharing_preparation(self):
        course = Course.objects.create(
            Course_name="Distribution Course",
            code="DIST101",
            semester="2025S1",
            Description="Template distribution testing",
            coordinator="dist_coord"
        )
        
        template = Assignment.objects.create(
            course=course,
            name="Shareable Template",
            type="Project",
            description="Template ready for sharing with students"
        )
        
        self.assertEqual(template.name, "Shareable Template")
        self.assertIsNotNone(template.description)
        
    def test_template_accessibility(self):
        template = Assignment.objects.create(
            name="Accessible Template",
            type="Homework",
            description="Students can access this template"
        )
        
        self.assertEqual(template.name, "Accessible Template")
        self.assertTrue(len(template.description) > 0)
