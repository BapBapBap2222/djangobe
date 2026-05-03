from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_userprofile_short_intro"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="activity_visible",
            field=models.BooleanField(default=True),
        ),
    ]
