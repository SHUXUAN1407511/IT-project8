from django.db import migrations, models
import django.db.models.deletion


def forwards_assign_coordinator(apps, schema_editor):
    Course = apps.get_model('courses', 'Course')
    User = apps.get_model('usersystem', 'User')

    for course in Course.objects.all():
        legacy = getattr(course, 'coordinator_legacy', None)
        if not legacy:
            continue

        user = None
        try:
            user = User.objects.filter(pk=int(legacy)).first()
        except (TypeError, ValueError):
            user = None
        if user is None:
            user = (
                User.objects.filter(username=legacy)
                .order_by('id')
                .first()
            )
        if user is None:
            continue
        course.coordinator = user
        course.save(update_fields=['coordinator'])


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_rename_course_fields'),
        ('usersystem', '0009_passwordresettoken'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='coordinator',
            new_name='coordinator_legacy',
        ),
        migrations.AddField(
            model_name='course',
            name='coordinator',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='coordinated_courses',
                to='usersystem.user',
            ),
        ),
        migrations.RunPython(forwards_assign_coordinator, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='course',
            name='coordinator_legacy',
        ),
    ]
