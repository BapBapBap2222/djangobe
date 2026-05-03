from django.db.models import Q
from django.db.models import F
from rest_framework.exceptions import NotFound

from .models import News


class NewsRepository:
    """
    Repository layer for News queries.
    """

    @staticmethod
    def _base_queryset():
        return News.objects.select_related("author")

    @staticmethod
    def get_published_news():
        return NewsRepository._base_queryset().filter(is_published=True)

    @staticmethod
    def get_all_news():
        return NewsRepository._base_queryset()

    @staticmethod
    def get_actor_scope(user):
        """
        Scope visible news by actor role.
        - Anonymous: published only
        - Staff/superuser: all
        - Authenticated non-staff: published + own drafts
        """
        if not getattr(user, "is_authenticated", False):
            return NewsRepository.get_published_news()
        if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
            return NewsRepository.get_all_news()
        return NewsRepository._base_queryset().filter(Q(is_published=True) | Q(author=user))

    @staticmethod
    def get_by_id(pk: int):
        try:
            return NewsRepository._base_queryset().get(pk=pk)
        except News.DoesNotExist as exc:
            raise NotFound("News item not found.") from exc

    @staticmethod
    def get_by_id_for_actor(pk: int, user):
        try:
            return NewsRepository.get_actor_scope(user).get(pk=pk)
        except News.DoesNotExist as exc:
            raise NotFound("News item not found or not accessible.") from exc

    @staticmethod
    def create_news(data: dict):
        return News.objects.create(**data)

    @staticmethod
    def increment_view_count(news_id: int):
        updated = News.objects.filter(pk=news_id).update(views_count=F("views_count") + 1)
        if not updated:
            raise NotFound("News item not found.")
