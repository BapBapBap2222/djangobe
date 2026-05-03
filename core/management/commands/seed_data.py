from django.core.management.base import BaseCommand

from utils.factories import TestDataFactory


class Command(BaseCommand):
    help = "Seed demo data for local development and FE smoke tests."

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=5, help="Number of users to create")
        parser.add_argument(
            "--properties", type=int, default=10, help="Number of properties to create"
        )
        parser.add_argument("--news", type=int, default=6, help="Number of news posts to create")
        parser.add_argument(
            "--appointments", type=int, default=8, help="Number of appointments to create"
        )

    def handle(self, *args, **options):
        users = [TestDataFactory.create_user() for _ in range(max(0, options["users"]))]
        staff_user = TestDataFactory.create_user(is_staff=True)

        properties = []
        for idx in range(max(0, options["properties"])):
            owner = users[idx % len(users)] if users else staff_user
            properties.append(TestDataFactory.create_property(owner=owner))

        for idx in range(max(0, options["news"])):
            TestDataFactory.create_news(author=staff_user, title=f"Market update #{idx + 1}")

        for idx in range(max(0, options["appointments"])):
            if not users or not properties:
                break
            requester = users[idx % len(users)]
            target_property = properties[idx % len(properties)]
            if requester == target_property.owner:
                continue
            TestDataFactory.create_appointment(user=requester, property_obj=target_property)

        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))
