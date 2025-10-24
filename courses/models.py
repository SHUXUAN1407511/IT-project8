from django.db import models

class Course(models.Model):
    course_name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, db_index=True)
    semester = models.CharField(max_length=20, db_index=True)
    description = models.TextField(max_length=160)
    coordinator = models.ForeignKey(
        'usersystem.User',
        on_delete=models.SET_NULL,
        related_name='coordinated_courses',
        null=True,
        blank=True,
    )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "courses_course"
        constraints = [
            models.UniqueConstraint(
                fields=["code", "semester"],
                name="uq_course_code_semester"
            )
        ]
        ordering = ["-created_at"]

    def __str__(self):
        coordinator = getattr(self.coordinator, "username", "")
        return f"{self.code} - {self.course_name} ({self.semester}){f' [{coordinator}]' if coordinator else ''}"
