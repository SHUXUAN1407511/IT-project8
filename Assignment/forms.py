from django import forms
from django.utils import timezone

ASSIGNMENT_TYPE_CHOICES = [
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
]

class AssignmentForm(forms.Form):
    subject = forms.CharField(
        label="Subject",
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "Subject",
            "placeholder": "e.g. IT Project (COMP30022)",
            "name": "subject",
        })
    )

    assignment_title = forms.CharField(
        label="Assignment Title",
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "id": "AssignmentTitle",
            "placeholder": "Assignment Title",
            "name": "assignment_title",
        })
    )

    due_date = forms.DateTimeField(
        label="Due date",
        required=True,
        widget=forms.DateTimeInput(attrs={
            "class": "form-control",
            "id": "DueDate",
            "name": "due_date",
            "type": "datetime-local",
        }),
    )

    assignment_type = forms.ChoiceField(
        label="Assignment Type",
        choices=ASSIGNMENT_TYPE_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-control",
            "id": "AssignmentType",
            "name": "assignment_type",
        })
    )

    def clean_due_date(self):
        dt = self.cleaned_data["due_date"]
        if dt <= timezone.now():
            raise forms.ValidationError("Due date must be in the future.")
        return dt
