from django.core.exceptions import PermissionDenied

from .repositories import NewsRepository


class NewsService:
    """
    Service layer containing business logic for News.
    """

    @staticmethod
    def increment_view_count(news_id: int):
        NewsRepository.increment_view_count(news_id)

    @staticmethod
    def create_news(user, validated_data: dict):
        # Defense in depth even when POST permission is protected at the view layer.
        if not getattr(user, "is_staff", False) and not getattr(user, "is_superuser", False):
            raise PermissionDenied("Ban khong co quyen tao bai viet.")

        validated_data["author"] = user
        return NewsRepository.create_news(validated_data)

    @staticmethod
    def update_news(user, news_id: int, validated_data: dict):
        news = NewsRepository.get_by_id(news_id)

        if news.author != user and not user.is_superuser:
            raise PermissionDenied("Ban khong co quyen sua bai viet nay.")

        for key, value in validated_data.items():
            setattr(news, key, value)

        news.save()
        return news

    @staticmethod
    def delete_news(user, news_id: int):
        news = NewsRepository.get_by_id(news_id)

        if news.author != user and not user.is_superuser:
            raise PermissionDenied("Ban khong co quyen xoa bai viet nay.")

        news.delete()
