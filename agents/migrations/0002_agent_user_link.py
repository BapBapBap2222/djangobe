from django.conf import settings
from django.db import migrations, models
from django.utils.text import slugify


def build_agent_slug(Agent, user, current_agent=None):
    base_slug = slugify(user.username) or slugify(build_full_name(user)) or f"user-{user.pk}"
    candidate = base_slug
    suffix = 1

    while Agent.objects.exclude(pk=getattr(current_agent, "pk", None)).filter(slug=candidate).exists():
        candidate = f"{base_slug}-{suffix}"
        suffix += 1

    return candidate


def build_full_name(user):
    full_name = " ".join(part for part in [user.first_name, user.last_name] if part).strip()
    return full_name or user.username


def sync_existing_users(apps, schema_editor):
    Agent = apps.get_model("agents", "Agent")
    User = apps.get_model("auth", "User")
    UserProfile = apps.get_model("accounts", "UserProfile")

    profiles_by_user_id = {
        profile.user_id: profile
        for profile in UserProfile.objects.all()
    }

    for user in User.objects.all():
        profile = profiles_by_user_id.get(user.pk)
        existing_agent = Agent.objects.filter(user=user).first()
        defaults = {
            "full_name": build_full_name(user),
            "slug": build_agent_slug(Agent, user, existing_agent),
            "email": user.email,
            "phone": profile.phone if profile and profile.phone else "",
            "avatar_url": profile.avatar.url if profile and profile.avatar else "",
            "bio": profile.bio if profile and profile.bio else "",
        }

        if existing_agent is None:
            Agent.objects.create(user=user, is_verified=False, **defaults)
            continue

        for field, value in defaults.items():
            setattr(existing_agent, field, value)
        existing_agent.user = user
        existing_agent.save()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("agents", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="agent",
            name="user",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=models.SET_NULL,
                related_name="agent_profile",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(sync_existing_users, migrations.RunPython.noop),
    ]
