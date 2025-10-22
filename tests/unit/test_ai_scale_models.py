from django.test import TestCase
from AIUseScale.models import AIUserScale

class AIUseScaleModelTest(TestCase):
    def test_ai_scale_creation(self):
        scale = AIUserScale.objects.create(
            username="student1",
            name="Assignment 1",
            level="R2",
            notes="Some notes"
        )
        self.assertEqual(scale.username, "student1")
        self.assertEqual(scale.name, "Assignment 1")
        self.assertEqual(scale.level, "R2")
        
    def test_ai_scale_str_representation(self):
        scale = AIUserScale.objects.create(
            username="student2",
            name="Final Project",
            level="R3"
        )
        self.assertEqual(str(scale), "student2 - Final Project")
        
    def test_ai_scale_ordering(self):
        scale1 = AIUserScale.objects.create(username="user1", name="Task1", level="R1")
        scale2 = AIUserScale.objects.create(username="user2", name="Task2", level="R2")
        scales = list(AIUserScale.objects.all())
        self.assertEqual(scales[0], scale2)
        self.assertEqual(scales[1], scale1)
        
    def test_ai_scale_unique_constraint(self):
        scale1 = AIUserScale.objects.create(
            username="sameuser",
            name="sametask",
            level="R1"
        )
        
        with self.assertRaises(Exception):
            AIUserScale.objects.create(
                username="sameuser",
                name="sametask",
                level="R2"
            )
