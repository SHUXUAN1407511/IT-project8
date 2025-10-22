from django.test import TestCase
from AIUseScale.models import AIUserScale
from AIUseScale.serializer import AIUserScaleSerializer

class AIUserScaleSerializerTest(TestCase):
    def test_serializer_valid_data(self):
        data = {
            "username": "student123",
            "name": "Test Assignment",
            "level": "R2",
            "notes": "Test notes"
        }
        serializer = AIUserScaleSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
    def test_serializer_invalid_empty_name(self):
        data = {
            "username": "student123",
            "name": "",
            "level": "R2"
        }
        serializer = AIUserScaleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        
    def test_serializer_duplicate_validation(self):
        AIUserScale.objects.create(
            username="user1",
            name="Assignment1",
            level="N"
        )
        data = {
            "username": "user1",
            "name": "Assignment1",
            "level": "R1"
        }
        serializer = AIUserScaleSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        
    def test_serializer_update(self):
        ai_scale = AIUserScale.objects.create(
            username="user1",
            name="Old Assignment",
            level="N"
        )
        data = {
            "username": "user1",
            "name": "Updated Assignment",
            "level": "R2"
        }
        serializer = AIUserScaleSerializer(instance=ai_scale, data=data)
        self.assertTrue(serializer.is_valid())
        updated = serializer.save()
        self.assertEqual(updated.name, "Updated Assignment")
