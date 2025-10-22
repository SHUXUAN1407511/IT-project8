from django.test import TestCase
from courses.models import Course

class CourseModelTest(TestCase):
    def test_course_creation(self):
        """测试课程模型创建"""
        course = Course.objects.create(
            Course_name="Software Engineering",
            code="COMP30022",
            semester="2025S1",
            Description="Software engineering fundamentals",
            coordinator="coord123"
        )
        self.assertEqual(course.code, "COMP30022")
        self.assertEqual(course.Course_name, "Software Engineering")
        self.assertEqual(course.semester, "2025S1")
        
    def test_course_str_representation(self):
        """测试课程字符串表示"""
        course = Course.objects.create(
            Course_name="AI Fundamentals",
            code="COMP30025", 
            semester="2025S1",
            Description="AI basics",
            coordinator="ai_coord"
        )
        expected_str = "COMP30025 - AI Fundamentals (2025S1)"
        self.assertEqual(str(course), expected_str)
