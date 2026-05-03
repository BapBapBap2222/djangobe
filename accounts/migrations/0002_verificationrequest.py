from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="VerificationRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=120)),
                ("date_of_birth", models.DateField()),
                ("address", models.TextField()),
                ("gender", models.CharField(choices=[("male", "Male"), ("female", "Female"), ("other", "Other")], max_length=10)),
                ("national_id_number", models.CharField(max_length=32)),
                ("id_card_front", models.ImageField(upload_to="verification/id_cards/")),
                ("id_card_back", models.ImageField(upload_to="verification/id_cards/")),
                ("status", models.CharField(choices=[("pending", "Pending"), ("approved", "Approved"), ("denied", "Denied")], default="pending", max_length=20)),
                ("denial_reason", models.TextField(blank=True)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("reviewed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reviewed_verification_requests", to=settings.AUTH_USER_MODEL)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="verification_requests", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
