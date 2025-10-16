from django.db import models


class Assignment(models.Model):
    STATUS_MISSING = 'missing'
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'

    STATUS_CHOICES = [
        (STATUS_MISSING, 'Not created'),
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
    ]

    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='assignments',
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=60)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    tutors = models.ManyToManyField(
        'usersystem.User',
        related_name='assignments',
        blank=True,
    )
    ai_declaration_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_MISSING,
    )
    has_template = models.BooleanField(default=False)
    template_updated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        course_code = getattr(self.course, 'code', 'Unknown course')
        return f"{course_code} - {self.name}"
