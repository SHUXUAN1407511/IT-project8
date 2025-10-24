import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('usersystem', '0007_user_bio_user_email_user_last_login_at_user_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField(blank=True)),
                ('body', models.TextField(blank=True)),
                ('related_type', models.CharField(blank=True, max_length=50)),
                ('related_id', models.CharField(blank=True, max_length=128)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='usersystem.user')),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['recipient', 'is_read'], name='notificatio_recipie_4e3567_idx'), models.Index(fields=['related_type', 'related_id'], name='notificatio_related_33f11d_idx')],
            },
        ),
    ]
