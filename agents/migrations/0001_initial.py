from django.db import migrations, models


def seed_agents(apps, schema_editor):
    Agent = apps.get_model("agents", "Agent")
    seed_data = [
        {
            "full_name": "Nguyen Van An",
            "slug": "nguyen-van-an",
            "avatar_url": "https://i.pravatar.cc/300?img=12",
            "email": "nguyenvanan@bluesky-agent.vn",
            "phone": "+84 901 234 001",
            "city": "Ho Chi Minh City",
            "specialization": "Luxury apartments and riverside homes",
            "tagline": "Trusted advisor for premium homes in the south of the city.",
            "years_experience": 8,
            "total_listings": 42,
            "deals_closed": 128,
            "rating": "4.90",
            "total_reviews": 128,
            "is_verified": True,
            "response_time": "Under 10 minutes",
            "areas": ["District 2", "District 7", "Binh Thanh"],
            "languages": ["Vietnamese", "English"],
            "bio": (
                "Nguyen Van An focuses on premium apartments and family homes in central "
                "and riverside neighborhoods. He is known for clear legal guidance, fast "
                "follow-up, and practical negotiation support."
            ),
        },
        {
            "full_name": "Tran Thi Mai",
            "slug": "tran-thi-mai",
            "avatar_url": "https://i.pravatar.cc/300?img=32",
            "email": "tranthimai@bluesky-agent.vn",
            "phone": "+84 901 234 002",
            "city": "Ho Chi Minh City",
            "specialization": "Inner-city resale homes and investment properties",
            "tagline": "Sharp market sense for buyers looking in central districts.",
            "years_experience": 7,
            "total_listings": 35,
            "deals_closed": 95,
            "rating": "4.80",
            "total_reviews": 95,
            "is_verified": True,
            "response_time": "Within 15 minutes",
            "areas": ["District 1", "District 3", "Phu Nhuan"],
            "languages": ["Vietnamese", "English"],
            "bio": (
                "Tran Thi Mai helps clients compare price, location, and liquidity before "
                "they commit. Her portfolio is strongest in central HCMC, especially for "
                "resale apartments and mixed-use investments."
            ),
        },
        {
            "full_name": "Le Minh Tuan",
            "slug": "le-minh-tuan",
            "avatar_url": "https://i.pravatar.cc/300?img=15",
            "email": "leminhtuan@bluesky-agent.vn",
            "phone": "+84 901 234 003",
            "city": "Thu Duc",
            "specialization": "Emerging districts and first-home consulting",
            "tagline": "Strong coverage for Thu Duc City and neighboring growth zones.",
            "years_experience": 6,
            "total_listings": 29,
            "deals_closed": 82,
            "rating": "4.70",
            "total_reviews": 82,
            "is_verified": True,
            "response_time": "Within 20 minutes",
            "areas": ["Thu Duc City", "District 9", "Di An"],
            "languages": ["Vietnamese", "English"],
            "bio": (
                "Le Minh Tuan works with buyers who want a realistic path to ownership in "
                "fast-growing districts. He combines on-site market updates with practical "
                "advice on financing, commute, and long-term appreciation."
            ),
        },
        {
            "full_name": "Pham Hoang Linh",
            "slug": "pham-hoang-linh",
            "avatar_url": "https://i.pravatar.cc/300?img=47",
            "email": "phamhoanglinh@bluesky-agent.vn",
            "phone": "+84 901 234 004",
            "city": "Ha Noi",
            "specialization": "Established residential districts in Hanoi",
            "tagline": "Reliable guidance for buyers seeking stable value in Hanoi.",
            "years_experience": 9,
            "total_listings": 51,
            "deals_closed": 156,
            "rating": "4.90",
            "total_reviews": 156,
            "is_verified": True,
            "response_time": "Under 10 minutes",
            "areas": ["Ba Dinh", "Cau Giay", "Dong Da"],
            "languages": ["Vietnamese", "English"],
            "bio": (
                "Pham Hoang Linh specializes in established Hanoi neighborhoods where legal "
                "clarity and neighborhood fit matter most. Clients value her direct advice, "
                "careful planning checks, and deep local network."
            ),
        },
    ]

    for item in seed_data:
        Agent.objects.update_or_create(slug=item["slug"], defaults=item)


def remove_seed_agents(apps, schema_editor):
    Agent = apps.get_model("agents", "Agent")
    Agent.objects.filter(
        slug__in=[
            "nguyen-van-an",
            "tran-thi-mai",
            "le-minh-tuan",
            "pham-hoang-linh",
        ]
    ).delete()


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Agent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=120)),
                ("slug", models.SlugField(unique=True)),
                ("avatar_url", models.URLField(blank=True, max_length=500)),
                ("email", models.EmailField(blank=True, max_length=254)),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("city", models.CharField(blank=True, max_length=120)),
                ("specialization", models.CharField(blank=True, max_length=200)),
                ("tagline", models.CharField(blank=True, max_length=255)),
                ("years_experience", models.PositiveSmallIntegerField(default=0)),
                ("total_listings", models.PositiveIntegerField(default=0)),
                ("deals_closed", models.PositiveIntegerField(default=0)),
                ("rating", models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ("total_reviews", models.PositiveIntegerField(default=0)),
                ("is_verified", models.BooleanField(default=False)),
                ("response_time", models.CharField(blank=True, max_length=100)),
                ("areas", models.JSONField(blank=True, default=list)),
                ("languages", models.JSONField(blank=True, default=list)),
                ("bio", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-is_verified", "-rating", "-total_reviews", "full_name"],
            },
        ),
        migrations.RunPython(seed_agents, remove_seed_agents),
    ]
