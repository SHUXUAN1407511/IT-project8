from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Assignment
from .forms import AssignmentForm

User = get_user_model()

class AssignmentModelTest(TestCase):
    def setUp(self):
        self.assignment = Assignment.objects.create(
            subject="COMP30022",
            assignment_title="IT Project 8",
            due_date=timezone.now() + timezone.timedelta(days=7),
            assignment_type="1"
        )
    
    def test_assignment_creation(self):
        self.assertEqual(self.assignment.subject, "COMP30022")
        self.assertEqual(self.assignment.assignment_title, "IT Project 8")
        self.assertTrue(self.assignment.due_date > timezone.now())
    
    def test_assignment_str_representation(self):
        self.assertEqual(str(self.assignment), "COMP30022 - IT Project 8")
    
    def test_created_at_auto_add(self):
        self.assertIsNotNone(self.assignment.created_at)

class AssignmentFormTest(TestCase):
    def test_valid_assignment_form(self):
        form_data = {
            'subject': 'COMP30022',
            'assignment_title': 'Test Assignment',
            'due_date': timezone.now() + timezone.timedelta(days=1),
            'assignment_type': '1'
        }
        form = AssignmentForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_past_due_date(self):
        form_data = {
            'subject': 'COMP30022',
            'assignment_title': 'Test Assignment',
            'due_date': timezone.now() - timezone.timedelta(days=1),
            'assignment_type': '1'
        }
        form = AssignmentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('due_date', form.errors)
    
    def test_missing_required_fields(self):
        form_data = {
            'subject': '',
            'assignment_title': 'Test Assignment',
            'due_date': timezone.now() + timezone.timedelta(days=1),
            'assignment_type': '1'
        }
        form = AssignmentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('subject', form.errors)

class AssignmentViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
        self.assignment = Assignment.objects.create(
            subject="COMP30022",
            assignment_title="Existing Assignment",
            due_date=timezone.now() + timezone.timedelta(days=7),
            assignment_type="1"
        )
    
    def test_create_assignment_get(self):
        response = self.client.get(reverse('Assignment:create_assignment'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Assignment.html')
        self.assertContains(response, 'form')
    
    def test_create_assignment_post_valid(self):
        response = self.client.post(reverse('Assignment:create_assignment'), {
            'subject': 'COMP30022',
            'assignment_title': 'New Test Assignment',
            'due_date': '2024-12-31T23:59',
            'assignment_type': '1'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'good')
        self.assertEqual(Assignment.objects.count(), 2)
    
    def test_create_assignment_post_invalid(self):
        response = self.client.post(reverse('Assignment:create_assignment'), {
            'subject': '',
            'assignment_title': 'New Test Assignment',
            'due_date': '2024-12-31T23:59',
            'assignment_type': '1'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form')
    
    def test_query_assignment(self):
        response = self.client.get(reverse('Assignment:query_assignment'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'query completed')
    
    def test_ai_use_scale_view(self):
        response = self.client.get(reverse('Assignment:AIUseScale'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'AIUseScale.html')

class AssignmentURLTest(TestCase):
    def test_assignment_urls(self):
        url = reverse('Assignment:create_assignment')
        self.assertEqual(url, '/Assignment')
        
        url = reverse('Assignment:query_assignment')
        self.assertEqual(url, '/Assignment/query')
        
        url = reverse('Assignment:AIUseScale')
        self.assertEqual(url, '/Assignment/AIUseScale')
