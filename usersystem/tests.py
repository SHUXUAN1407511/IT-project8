from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .forms import LoginForm, RegisterForm

User = get_user_model()

class UserSystemFormsTest(TestCase):
    def test_valid_login_form(self):
        form_data = {'username': 'testuser', 'password': 'testpass123'}
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_invalid_login_form_missing_fields(self):
        form_data = {'username': '', 'password': ''}
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_valid_register_form(self):
        form_data = {
            'username': 'newuser',
            'password': 'testpass123',
            'confirmpassword': 'testpass123'
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_register_form_password_mismatch(self):
        form_data = {
            'username': 'newuser',
            'password': 'testpass123',
            'confirmpassword': 'differentpass'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('confirmpassword', form.errors)
    
    def test_register_form_duplicate_username(self):
        User.objects.create_user(username='existinguser', password='testpass123')
        
        form_data = {
            'username': 'existinguser',
            'password': 'testpass123',
            'confirmpassword': 'testpass123'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

class UserSystemViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_login_view_get(self):
        response = self.client.get(reverse('usersystem:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
    
    def test_successful_login(self):
        response = self.client.post(reverse('usersystem:login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
    
    def test_failed_login_wrong_password(self):
        response = self.client.post(reverse('usersystem:login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
    
    def test_failed_login_nonexistent_user(self):
        response = self.client.post(reverse('usersystem:login'), {
            'username': 'nonexistentuser',
            'password': 'somepassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
    
    def test_register_view_get(self):
        response = self.client.get(reverse('usersystem:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
    
    def test_successful_registration(self):
        response = self.client.post(reverse('usersystem:register'), {
            'username': 'newuser123',
            'password': 'newpass123',
            'confirmpassword': 'newpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser123').exists())
    
    def test_registration_password_mismatch(self):
        response = self.client.post(reverse('usersystem:register'), {
            'username': 'newuser123',
            'password': 'newpass123',
            'confirmpassword': 'differentpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
