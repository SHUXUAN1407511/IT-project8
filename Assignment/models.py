from django.db import models

# Create your models here.
# app/models.py
from django.db import models

class Assignment(models.Model):
    subject = models.CharField(max_length=200)
    assignment_title = models.CharField(max_length=200)
    due_date = models.DateTimeField()
    assignment_type = models.CharField(max_length=20)  # 或 IntegerField/SmallIntegerField

    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.subject} - {self.assignment_title}"
