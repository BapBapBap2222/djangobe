from __future__ import annotations

from datetime import date, time, timedelta

from django.contrib.auth.models import User

from appointments.models import Appointment, AppointmentStatus
from news.models import News
from properties.models import ListingType, Property, PropertyStatus, PropertyType


class TestDataFactory:
    """Small in-project factory helpers for tests and seed commands."""

    _counter = 0

    @classmethod
    def _next(cls) -> int:
        cls._counter += 1
        return cls._counter

    @classmethod
    def create_user(cls, *, is_staff: bool = False, password: str = "Pass123!"):
        idx = cls._next()
        user = User.objects.create_user(
            username=f"user_{idx}",
            email=f"user_{idx}@example.com",
            password=password,
            first_name="Test",
            last_name=f"User{idx}",
            is_staff=is_staff,
        )
        return user

    @classmethod
    def create_property(cls, *, owner=None, **overrides):
        owner = owner or cls.create_user()
        idx = cls._next()
        defaults = {
            "title": f"Property {idx}",
            "description": "Factory generated property",
            "property_type": PropertyType.HOUSE,
            "listing_type": ListingType.FOR_SALE,
            "status": PropertyStatus.ACTIVE,
            "price": 2_500_000_000,
            "area": 120,
            "bedrooms": 3,
            "bathrooms": 2,
            "floors": 2,
            "city": "Ho Chi Minh City",
            "district": "District 1",
            "ward": "Ben Nghe",
            "address": f"{idx} Nguyen Hue",
            "is_active": True,
        }
        defaults.update(overrides)
        return Property.objects.create(owner=owner, **defaults)

    @classmethod
    def create_news(cls, *, author=None, **overrides):
        author = author or cls.create_user(is_staff=True)
        idx = cls._next()
        defaults = {
            "title": f"News {idx}",
            "content": "Factory generated news content",
            "author": author,
            "is_published": True,
        }
        defaults.update(overrides)
        return News.objects.create(**defaults)

    @classmethod
    def create_appointment(cls, *, user=None, property_obj=None, **overrides):
        user = user or cls.create_user()
        property_obj = property_obj or cls.create_property()
        idx = cls._next()
        defaults = {
            "user": user,
            "property": property_obj,
            "date": date.today() + timedelta(days=idx),
            "time": time(hour=10, minute=0),
            "name": f"Visitor {idx}",
            "phone": "0900000000",
            "message": "Factory appointment",
            "status": AppointmentStatus.PENDING,
        }
        defaults.update(overrides)
        return Appointment.objects.create(**defaults)
