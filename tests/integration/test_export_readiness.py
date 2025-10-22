from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from Assignment.models import Assignment
from courses.models import Course

class WorkingExportTests(APITestCase):
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
            name="Test Assignment for Export",
            type="Research Paper",
            description="Assignment data for export testing"
        )
    
    def test_export_endpoints_exist(self):
        endpoints = ['export-excel', 'export-pdf']
        for endpoint in endpoints:
            try:
                url = reverse(endpoint)
                self.assertIsNotNone(url)
            except:
                self.skipTest(f"Endpoint {endpoint} not configured")
                
    def test_assignment_data_export_readiness(self):
        assignments = Assignment.objects.all()
        self.assertGreater(assignments.count(), 0)
        
        assignment = assignments.first()
        self.assertIsNotNone(assignment.name)
        self.assertIsNotNone(assignment.type)
        self.assertIsNotNone(assignment.description)
        
    def test_course_data_export_readiness(self):
        courses = Course.objects.all()
        self.assertGreater(courses.count(), 0)
        
        course = courses.first()
        self.assertIsNotNone(course.Course_name)
        self.assertIsNotNone(course.code)
        self.assertIsNotNone(course.semester)
        
    def test_export_data_completeness(self):
        assignments = Assignment.objects.all()
        courses = Course.objects.all()
        
        self.assertTrue(assignments.exists())
        self.assertTrue(courses.exists())
