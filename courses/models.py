from django.db import models

class Course(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, db_index=True)
    teacher = models.CharField(max_length=120, blank=True)
    semester = models.CharField(max_length=20, db_index=True)
    credits = models.PositiveIntegerField(default=0)

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
        return f"{self.code} - {self.name} ({self.semester})"
