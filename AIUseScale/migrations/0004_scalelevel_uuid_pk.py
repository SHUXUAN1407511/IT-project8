import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ai_use_scale", "0003_alter_scalerecord_options_aiuserscale"),
    ]

    operations = [
        migrations.RenameField(
            model_name="scalelevel",
            old_name="id",
            new_name="level_code",
        ),
        migrations.AddField(
            model_name="scalelevel",
            name="uid",
            field=models.UUIDField(default=uuid.uuid4, editable=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="scalelevel",
            name="level_code",
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name="scalelevel",
            name="uid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name="scalelevel",
            unique_together={("version", "level_code")},
        ),
    ]
