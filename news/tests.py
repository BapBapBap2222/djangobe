from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from news.models import News
from utils.factories import TestDataFactory


class NewsApiTests(APITestCase):
    def setUp(self):
        self.staff_user = TestDataFactory.create_user(is_staff=True)
        self.normal_user = TestDataFactory.create_user()
        self.other_user = TestDataFactory.create_user()
        self.super_user = User.objects.create_superuser(
            username="admin_news",
            email="admin_news@example.com",
            password="Pass123!",
        )

        self.published_news = TestDataFactory.create_news(
            author=self.staff_user,
            is_published=True,
            title="Published post",
        )
        self.own_draft_news = TestDataFactory.create_news(
            author=self.normal_user,
            is_published=False,
            title="Own draft post",
        )
        self.other_draft_news = TestDataFactory.create_news(
            author=self.other_user,
            is_published=False,
            title="Other draft post",
        )

        self.list_url = reverse("news-list")

    def _extract_results(self, data):
        if isinstance(data, dict) and "results" in data:
            return data["results"]
        if isinstance(data, list):
            return data
        return []

    def test_public_list_only_returns_published_news(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        items = self._extract_results(response.data)
        ids = {item["id"] for item in items}

        self.assertIn(self.published_news.id, ids)
        self.assertNotIn(self.own_draft_news.id, ids)
        self.assertNotIn(self.other_draft_news.id, ids)

    def test_authenticated_user_list_contains_public_and_own_draft(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        items = self._extract_results(response.data)
        ids = {item["id"] for item in items}

        self.assertIn(self.published_news.id, ids)
        self.assertIn(self.own_draft_news.id, ids)
        self.assertNotIn(self.other_draft_news.id, ids)

    def test_staff_list_contains_all_news(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        items = self._extract_results(response.data)
        ids = {item["id"] for item in items}

        self.assertIn(self.published_news.id, ids)
        self.assertIn(self.own_draft_news.id, ids)
        self.assertIn(self.other_draft_news.id, ids)

    def test_public_can_view_published_detail_and_view_count_increments(self):
        detail_url = reverse("news-detail", args=[self.published_news.id])
        before = self.published_news.views_count

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.published_news.refresh_from_db()
        self.assertEqual(self.published_news.views_count, before + 1)

    def test_public_cannot_view_draft_detail(self):
        detail_url = reverse("news-detail", args=[self.other_draft_news.id])
        before = self.other_draft_news.views_count

        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.other_draft_news.refresh_from_db()
        self.assertEqual(self.other_draft_news.views_count, before)

    def test_owner_can_view_own_draft_detail(self):
        detail_url = reverse("news-detail", args=[self.own_draft_news.id])

        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_non_staff_cannot_create_news(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post(
            self.list_url,
            {"title": "Unauthorized post", "content": "Should fail"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_create_news(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(
            self.list_url,
            {"title": "Market update", "content": "New article", "is_published": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Market update")
        self.assertEqual(response.data["author"], self.staff_user.id)

    def test_create_news_rejects_blank_title(self):
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(
            self.list_url,
            {"title": "   ", "content": "Some content", "is_published": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_author_can_patch_own_news(self):
        detail_url = reverse("news-detail", args=[self.published_news.id])

        self.client.force_authenticate(user=self.staff_user)
        response = self.client.patch(detail_url, {"title": "Updated title"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Updated title")

    def test_non_owner_cannot_patch_published_news(self):
        detail_url = reverse("news-detail", args=[self.published_news.id])

        self.client.force_authenticate(user=self.normal_user)
        response = self.client.patch(detail_url, {"title": "Hacked"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_owner_cannot_patch_other_user_draft(self):
        detail_url = reverse("news-detail", args=[self.other_draft_news.id])

        self.client.force_authenticate(user=self.normal_user)
        response = self.client.patch(detail_url, {"title": "Hacked"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_superuser_can_patch_any_news(self):
        detail_url = reverse("news-detail", args=[self.other_draft_news.id])

        self.client.force_authenticate(user=self.super_user)
        response = self.client.patch(detail_url, {"title": "Admin updated"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Admin updated")

    def test_non_owner_cannot_delete_published_news(self):
        detail_url = reverse("news-detail", args=[self.published_news.id])

        self.client.force_authenticate(user=self.normal_user)
        response = self.client.delete(detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_author_can_delete_own_news(self):
        own_news = TestDataFactory.create_news(author=self.normal_user, is_published=True)
        detail_url = reverse("news-detail", args=[own_news.id])

        self.client.force_authenticate(user=self.normal_user)
        response = self.client.delete(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(News.objects.filter(id=own_news.id).exists())

    def test_superuser_can_delete_any_news(self):
        detail_url = reverse("news-detail", args=[self.other_draft_news.id])

        self.client.force_authenticate(user=self.super_user)
        response = self.client.delete(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(News.objects.filter(id=self.other_draft_news.id).exists())
