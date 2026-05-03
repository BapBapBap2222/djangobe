from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

from agents.models import Agent

from .models import UserProfile


def _build_agent_slug(user: User, existing_agent: Agent | None = None) -> str:
    base_slug = slugify(user.username) or slugify(user.get_full_name()) or f"user-{user.pk}"
    candidate = base_slug
    suffix = 1

    while Agent.objects.exclude(pk=getattr(existing_agent, "pk", None)).filter(slug=candidate).exists():
        candidate = f"{base_slug}-{suffix}"
        suffix += 1

    return candidate


def sync_user_agent(user: User) -> None:
    if user.is_staff or user.is_superuser:
        Agent.objects.filter(user=user).delete()
        return

    profile = getattr(user, "profile", None)
    existing_agent = Agent.objects.filter(user=user).first()

    defaults = {
        "full_name": user.get_full_name() or user.username,
        "slug": _build_agent_slug(user, existing_agent),
        "email": user.email,
        "phone": profile.phone if profile and profile.phone else "",
        "avatar_url": profile.avatar.url if profile and profile.avatar else "",
        "bio": profile.bio if profile and profile.bio else "",
    }

    if existing_agent is None:
        Agent.objects.create(
            user=user,
            is_verified=False,
            **defaults,
        )
        return

    for field, value in defaults.items():
        setattr(existing_agent, field, value)
    existing_agent.user = user
    existing_agent.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def ensure_agent_for_user(sender, instance, **kwargs):
    sync_user_agent(instance)


@receiver(post_save, sender=UserProfile)
def sync_agent_from_profile(sender, instance, **kwargs):
    sync_user_agent(instance.user)
