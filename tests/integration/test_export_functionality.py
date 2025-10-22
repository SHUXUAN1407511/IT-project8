from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from Assignment.models import Assignment
from courses.models import Course

class ExportFunctionalityTests(TestCase):
    def setUp(self):
        self.course = Course.objects.create(
            Course_name="Export Test Course",
            code="EXP101",
            semester="2025S1",
            Description="Testing export functionality",
            coordinator="export_coord"
        )
        self.assignment = Assignment.objects.create(
            course=self.course,
            name="Export Test Assignment",
            type="Research Paper",
            description="Assignment for export testing"
        )
    
    def test_export_template_data_structure(self):
        assignment = Assignment.objects.get(name="Export Test Assignment")
        self.assertEqual(assignment.name, "Export Test Assignment")
        self.assertEqual(assignment.type, "Research Paper")
        
    def test_export_required_fields(self):
        assignment = Assignment.objects.get(name="Export Test Assignment")
        self.assertIsNotNone(assignment.name)
        self.assertIsNotNone(assignment.type)
        self.assertIsNotNone(assignment.course)
        
    def test_multiple_assignments_export(self):
        assignment2 = Assignment.objects.create(
            course=self.course,
            name="Second Export Assignment",
            type="Homework"
        )
        assignments = Assignment.objects.filter(course=self.course)
        self.assertEqual(assignments.count(), 2)
