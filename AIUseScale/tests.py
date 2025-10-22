from django.test import TestCase
from AIUseScale.models import AIUserScale

class AIUserScaleModelTest(TestCase):
    def test_ai_user_scale_creation(self):
        ai_scale = AIUserScale.objects.create(
            username="student123",
            name="Research Assignment",
            level="R2",
            notes="Research paper with AI assistance"
        )
        self.assertEqual(ai_scale.username, "student123")
        self.assertEqual(ai_scale.name, "Research Assignment")
        self.assertEqual(ai_scale.level, "R2")
        
    def test_ai_user_scale_str_representation(self):
        ai_scale = AIUserScale.objects.create(
            username="tutor456",
            name="Grammar Check", 
            level="R1",
            notes="Basic grammar assistance"
        )
        self.assertEqual(str(ai_scale), "tutor456 - Grammar Check")
        
    def test_unique_constraint(self):
        AIUserScale.objects.create(
            username="user1",
            name="Assignment1",
            level="N"
        )
        with self.assertRaises(Exception):
            AIUserScale.objects.create(
                username="user1",
                name="Assignment1", 
                level="R1"
            )
            
    def test_level_choices_validation(self):
        valid_levels = ["N", "R1", "R2", "G"]
        ai_scale = AIUserScale.objects.create(
            username="testuser",
            name="Test Assignment",
            level="R1"
        )
        self.assertIn(ai_scale.level, valid_levels)
