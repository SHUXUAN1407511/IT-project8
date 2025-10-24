import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ai_use_scale', '0004_scalelevel_uuid_pk'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scalelevel',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
