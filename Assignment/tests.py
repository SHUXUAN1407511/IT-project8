from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from courses.models import Course
from .models import Assignment
from template.models import AssignmentTemplate


class AssignmentTemplateAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.course = Course.objects.create(
            Course_name="Intro to AI",
            code="AI101",
            semester="2024",
            Description="Test course",
            coordinator="SC001",
        )
        self.assignment = Assignment.objects.create(
            course=self.course,
            name="Essay 1",
            type="essay",
            description="Write about AI ethics.",
        )

    def test_save_template_creates_record(self):
        url = reverse("Assignment:assignments-template", args=[self.assignment.id])
        payload = {
            "rows": [
                {
                    "task": "Draft outline",
                    "levelId": "level-1",
                    "levelLabel": "Limited",
                    "instructions": "Do not use AI to draft the outline.",
                    "examples": "",
                }
            ],
            "publish": False,
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assignment.refresh_from_db()
        template = AssignmentTemplate.objects.get(assignment=self.assignment)
        self.assertTrue(self.assignment.has_template)
        self.assertEqual(template.rows[0]["task"], "Draft outline")
        self.assertEqual(
            self.assignment.ai_declaration_status, Assignment.STATUS_DRAFT
        )

    def test_save_template_publish_updates_status(self):
        url = reverse("Assignment:assignments-template", args=[self.assignment.id])
        payload = {
            "rows": [
                {
                    "task": "Submit final report",
                    "levelId": "level-2",
                    "levelLabel": "Extensive",
                    "instructions": "Document how AI tools were used.",
                    "examples": "",
                }
            ],
            "publish": True,
        }

        response = self.client.post(url, payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assignment.refresh_from_db()
        template = AssignmentTemplate.objects.get(assignment=self.assignment)
        self.assertTrue(template.is_published)
        self.assertEqual(
            self.assignment.ai_declaration_status, Assignment.STATUS_PUBLISHED
        )

    def test_unpublish_template_sets_draft_status(self):
        create_url = reverse(
            "Assignment:assignments-template", args=[self.assignment.id]
        )
        payload = {
            "rows": [
                {
                    "task": "Peer review",
                    "levelId": "level-3",
                    "levelLabel": "Moderate",
                    "instructions": "Use AI only for grammar suggestions.",
                    "examples": "",
                }
            ],
            "publish": True,
        }
        create_response = self.client.post(create_url, payload, format="json")
        self.assertEqual(create_response.status_code, 201)

        unpublish_url = reverse(
            "Assignment:assignments-template-unpublish", args=[self.assignment.id]
        )
        response = self.client.post(unpublish_url, {}, format="json")
        self.assertEqual(response.status_code, 200)

        self.assignment.refresh_from_db()
        template = AssignmentTemplate.objects.get(assignment=self.assignment)
        self.assertFalse(template.is_published)
        self.assertEqual(
            self.assignment.ai_declaration_status, Assignment.STATUS_DRAFT
        )
