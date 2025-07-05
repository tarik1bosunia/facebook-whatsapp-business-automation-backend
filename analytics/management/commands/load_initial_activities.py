from django.core.management.base import BaseCommand
from django.utils import timezone
from analytics.models import Activity
from django.contrib.auth import get_user_model
import datetime

User = get_user_model()
# python manage.py load_initial_activities

class Command(BaseCommand):
    help = 'Load initial activities'

    def handle(self, *args, **kwargs):
        # Use the first user in the system (or None if no user exists)
        user = User.objects.first()

        Activity.objects.bulk_create([
            Activity(
                user=user,
                type="conversation",
                title="New conversation from Sarah Wilson",
                description="Asked about product return policy",
                source="Facebook",
                created_at=timezone.now() - datetime.timedelta(minutes=10)
            ),
            Activity(
                user=user,
                type="order",
                title="New order #1234 received",
                description="2 items: Blue T-shirt, Black Jeans - $89.97",
                source="WhatsApp",
                created_at=timezone.now() - datetime.timedelta(minutes=45)
            ),
            Activity(
                user=user,
                type="faq",
                title="FAQ updated: Shipping Policy",
                description="Admin Jane Doe updated the shipping policy FAQ",
                source=None,
                created_at=timezone.now() - datetime.timedelta(hours=2)
            ),
            Activity(
                user=user,
                type="conversation",
                title="New conversation from Mike Peterson",
                description="Asked about product availability",
                source="Facebook",
                created_at=timezone.now() - datetime.timedelta(hours=3)
            ),
            Activity(
                user=user,
                type="order",
                title="New order #1233 received",
                description="1 item: Red Dress - $49.99",
                source="WhatsApp",
                created_at=timezone.now() - datetime.timedelta(hours=5)
            ),
            Activity(
                user=user,
                type="conversation",
                title="New conversation from Linda Young",
                description="Inquired about express shipping options",
                source="Facebook",
                created_at=timezone.now() - datetime.timedelta(hours=7)
            ),
            Activity(
                user=user,
                type="faq",
                title="FAQ updated: Return & Refund Policy",
                description="Updated return policy for seasonal products",
                source=None,
                created_at=timezone.now() - datetime.timedelta(days=1)
            ),
                        Activity(
                user=user,
                type="conversation",
                title="New conversation from Sarah Wilson",
                description="Asked about product return policy",
                source="Facebook",
                created_at=timezone.now() - datetime.timedelta(minutes=10)
            ),
            Activity(
                user=user,
                type="order",
                title="New order #1234 received",
                description="2 items: Blue T-shirt, Black Jeans - $89.97",
                source="WhatsApp",
                created_at=timezone.now() - datetime.timedelta(minutes=45)
            ),
            Activity(
                user=user,
                type="faq",
                title="FAQ updated: Shipping Policy",
                description="Admin Jane Doe updated the shipping policy FAQ",
                source=None,
                created_at=timezone.now() - datetime.timedelta(hours=2)
            ),
            Activity(
                user=user,
                type="conversation",
                title="New conversation from Mike Peterson",
                description="Asked about product availability",
                source="Facebook",
                created_at=timezone.now() - datetime.timedelta(hours=3)
            ),
            Activity(
                user=user,
                type="order",
                title="New order #1233 received",
                description="1 item: Red Dress - $49.99",
                source="WhatsApp",
                created_at=timezone.now() - datetime.timedelta(hours=5)
            ),
            Activity(
                user=user,
                type="conversation",
                title="New conversation from Linda Young",
                description="Inquired about express shipping options",
                source="Facebook",
                created_at=timezone.now() - datetime.timedelta(hours=7)
            ),
            Activity(
                user=user,
                type="faq",
                title="FAQ updated: Return & Refund Policy",
                description="Updated return policy for seasonal products",
                source=None,
                created_at=timezone.now() - datetime.timedelta(days=1)
            ),
            Activity(
                user=user,
                type="conversation",
                title="New message from Kevin Tran",
                description="Asked for invoice copy",
                source="Messenger",
                created_at=timezone.now() - datetime.timedelta(minutes=25)
            ),
            Activity(
                user=user,
                type="order",
                title="New order #1235 received",
                description="3 items: Hoodie, Cap, Sneakers - $149.00",
                source="WhatsApp",
                created_at=timezone.now() - datetime.timedelta(hours=1, minutes=30)
            ),
            Activity(
                user=user,
                type="conversation",
                title="Chat started by Amanda Smith",
                description="Inquired about size chart for shoes",
                source="Instagram",
                created_at=timezone.now() - datetime.timedelta(hours=4)
            ),
            Activity(
                user=user,
                type="faq",
                title="FAQ updated: Payment Methods",
                description="Added Apple Pay and Google Pay options",
                source=None,
                created_at=timezone.now() - datetime.timedelta(days=2)
            ),
            Activity(
                user=user,
                type="conversation",
                title="New question from Tom Harris",
                description="Asked about loyalty points",
                source="Facebook",
                created_at=timezone.now() - datetime.timedelta(minutes=5)
            ),
            Activity(
                user=user,
                type="order",
                title="New order #1236 received",
                description="1 item: Leather Wallet - $39.95",
                source="WhatsApp",
                created_at=timezone.now() - datetime.timedelta(hours=6)
            ),
            Activity(
                user=user,
                type="faq",
                title="FAQ updated: Warranty Policy",
                description="Extended warranty period for electronics",
                source=None,
                created_at=timezone.now() - datetime.timedelta(days=3)
            ),
            Activity(
                user=user,
                type="conversation",
                title="Live chat initiated by Julia Roberts",
                description="Asked if the product is available in store",
                source="Website",
                created_at=timezone.now() - datetime.timedelta(minutes=2)
            ),
        ])

        self.stdout.write(self.style.SUCCESS("Initial activities loaded."))
