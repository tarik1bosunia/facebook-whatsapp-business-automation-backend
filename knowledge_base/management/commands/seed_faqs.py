from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from knowledge_base.models import Category, FAQ 

User = get_user_model()
"""
python manage.py seed_faqs
"""
class Command(BaseCommand):
    help = "Seed the database with product and business-related FAQs"

    def handle(self, *args, **kwargs):
        user = User.objects.get(email="t@t.com")
        if not user:
            self.stderr.write(self.style.ERROR("❌ No user found. Please create  user with email t@t.com. "))
            return

        self.stdout.write(self.style.SUCCESS(f"Seeding product and business FAQs for user: {user.email}"))

        faq_data = {
            "Product": [
                {
                    "question": "Are your products authentic?",
                    "answer": "Yes, we source all products directly from verified manufacturers and suppliers."
                },
                {
                    "question": "Do you offer product warranties?",
                    "answer": "Yes, selected products come with official manufacturer warranties."
                },
                {
                    "question": "Can I request a product that is out of stock?",
                    "answer": "Yes, please contact support with the product name and we’ll try to restock it for you."
                },
                {
                    "question": "How do I find the right size or variant?",
                    "answer": "Product pages include detailed size guides and variant options. If unsure, contact us for help."
                }
            ],
            "Business": [
                {
                    "question": "How do I register my business on your platform?",
                    "answer": "Visit the 'Business Signup' page and fill out the required information to get started."
                },
                {
                    "question": "Is there a fee for listing products?",
                    "answer": "Basic product listings are free. Premium features may require a subscription."
                },
                {
                    "question": "Can I manage inventory and pricing myself?",
                    "answer": "Yes, you can fully manage products, pricing, and stock from your business dashboard."
                },
                {
                    "question": "Do you provide sales reports?",
                    "answer": "Yes, detailed analytics and sales reports are available in your business account."
                }
            ]
        }

        for category_name, faqs in faq_data.items():
            category, created = Category.objects.get_or_create(
                user=user,
                name=category_name
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category: {category.name}"))

            for item in faqs:
                faq, created = FAQ.objects.get_or_create(
                    question=item["question"],
                    category=category,
                    defaults={"answer": item["answer"]}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"✅ Created FAQ: {faq.question}"))
                else:
                    self.stdout.write(f"FAQ already exists: {faq.question}")

        self.stdout.write(self.style.SUCCESS("Product & Business FAQ seeding complete!"))
