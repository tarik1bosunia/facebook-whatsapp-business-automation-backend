from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from business.models import Promotion  # Adjust path if Promotion model is elsewhere

User = get_user_model()

"""
Usage:
    python manage.py seed_promotions
"""

class Command(BaseCommand):
    help = "Seeds the database with sample promotions"

    def handle(self, *args, **kwargs):
        # Fetch the user (modify email as needed or make it configurable)
        try:
            user = User.objects.get(email="t@t.com")
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR("No user found. Please create a user first."))
            return

        self.stdout.write(self.style.SUCCESS(f"Seeding promotions for user: {user.email}"))

        # Sample promotions
        promotions_data = [
            {
                "title": "Winter Sale - 20% Off Electronics",
                "description": "Enjoy 20% discount on all electronic items during winter sale!",
                "discount_percent": 20,
                "start_date": timezone.now(),
                "end_date": timezone.now() + timezone.timedelta(days=30),
            },
            {
                "title": "Buy 1 Get 1 Free on Books",
                "description": "Limited time offer on select books — buy one, get one free!",
                "discount_percent": None,  # Not percentage-based
                "start_date": timezone.now(),
                "end_date": timezone.now() + timezone.timedelta(days=15),
            },
            {
                "title": "Flash Sale: 50% Off Accessories",
                "description": "Massive discount on accessories for 48 hours only.",
                "discount_percent": 50,
                "start_date": timezone.now(),
                "end_date": timezone.now() + timezone.timedelta(days=2),
            },
        ]

        # Insert promotions
        for promo in promotions_data:
            obj, created = Promotion.objects.get_or_create(
                user=user,
                title=promo["title"],
                defaults={
                    "description": promo["description"],
                    "discount_percent": promo["discount_percent"],
                    "start_date": promo["start_date"],
                    "end_date": promo["end_date"],
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created promotion: {obj.title}"))
            else:
                self.stdout.write(f"Promotion already exists: {obj.title}")

        self.stdout.write(self.style.SUCCESS("✅ Promotion seeding complete!"))
