from django.db import models

class Course(models.Model):
    Course_name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, db_index=True)
    semester = models.CharField(max_length=20, db_index=True)
    Description = models.TextField(max_length=160)
    coordinator = models.CharField(max_length=20, db_index=True)


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
        return f"{self.code} - {self.Course_name} ({self.semester})"
