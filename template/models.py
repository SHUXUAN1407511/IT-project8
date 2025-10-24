from django.db import models


class AssignmentTemplate(models.Model):
    """
    Stores the AI declaration template for a particular assignment.
    Each assignment can have at most one template (enforced by OneToOne relation).
    """

    assignment = models.OneToOneField(
        "assignment.Assignment",
        on_delete=models.CASCADE,
        related_name="ai_template",
    )
    rows = models.JSONField(default=list, blank=True)
    is_published = models.BooleanField(default=False)
    updated_by = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Template for assignment {self.assignment_id}"
