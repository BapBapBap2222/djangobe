from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_verificationrequest"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="short_intro",
            field=models.CharField(blank=True, max_length=280, null=True),
        ),
    ]
