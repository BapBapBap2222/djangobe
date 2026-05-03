from rest_framework import generics, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .repositories import NewsRepository
from .serializers import NewsSerializer
from .services import NewsService


class NewsPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class IsStaffOrReadOnly(IsAuthenticatedOrReadOnly):
    """Allow read for everyone, allow create only for staff/superuser."""

    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class NewsListView(generics.ListCreateAPIView):
    """
    GET: list news by actor scope.
    POST: create news for staff/superuser.
    """

    permission_classes = [IsStaffOrReadOnly]
    serializer_class = NewsSerializer
    pagination_class = NewsPagination

    def get_queryset(self):
        return NewsRepository.get_actor_scope(self.request.user)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        news_item = NewsService.create_news(
            user=request.user,
            validated_data=serializer.validated_data,
        )
        return Response(
            self.get_serializer(news_item).data,
            status=status.HTTP_201_CREATED,
        )


class NewsDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: retrieve by actor scope and increase view count.
    PUT/PATCH: update own post or superuser.
    DELETE: delete own post or superuser.
    """

    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = NewsSerializer

    def get_queryset(self):
        return NewsRepository.get_actor_scope(self.request.user)

    def get_object(self):
        obj = super().get_object()

        if self.request.method == "GET":
            NewsService.increment_view_count(obj.id)
            obj.refresh_from_db(fields=["views_count"])

        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        current = self.get_object()

        serializer = self.get_serializer(current, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        news_item = NewsService.update_news(
            user=request.user,
            news_id=current.id,
            validated_data=serializer.validated_data,
        )
        return Response(self.get_serializer(news_item).data)

    def delete(self, request, *args, **kwargs):
        current = self.get_object()
        NewsService.delete_news(user=request.user, news_id=current.id)
        return Response({"message": "Da xoa bai viet thanh cong"}, status=status.HTTP_200_OK)
