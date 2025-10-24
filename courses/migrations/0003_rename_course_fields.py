from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0002_rename_name_course_course_name_remove_course_credits_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="course",
            old_name="Course_name",
            new_name="course_name",
        ),
        migrations.RenameField(
            model_name="course",
            old_name="Description",
            new_name="description",
        ),
    ]
