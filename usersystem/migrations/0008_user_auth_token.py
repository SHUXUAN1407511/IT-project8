from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usersystem', '0007_user_bio_user_email_user_last_login_at_user_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='auth_token',
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
    ]

