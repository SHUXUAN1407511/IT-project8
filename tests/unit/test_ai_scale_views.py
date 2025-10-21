from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from AIUseScale.models import AIUserScale

class AIUserScaleViewTest(APITestCase):
    def setUp(self):
        self.ai_scale = AIUserScale.objects.create(
            username="testuser",
            name="Test Assignment",
            level="R2"
        )
        
    def test_list_ai_scales(self):
        url = "/aiusescale/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
    def test_create_ai_scale(self):
        url = "/aiusescale/"
        data = {
            "username": "newuser",
            "name": "New Assignment",
            "level": "R1"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        
    def test_filter_by_username(self):
        url = "/aiusescale/?username=testuser"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
