from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from business.models import ProductCategory, Product 
from decimal import Decimal

User = get_user_model()
"""
python manage.py seed_products
"""
class Command(BaseCommand):
    help = "Seeds the database with real product categories and 15 products"

    def handle(self, *args, **kwargs):
        # Get first user (or modify this to get a specific user)
        user = User.objects.get(email="t@t.com")
        if not user:
            self.stderr.write(self.style.ERROR("No user found. Please create a user first."))
            return

        self.stdout.write(self.style.SUCCESS(f"Seeding data for user: {user.email}"))

        # --- Category and Product Data ---
        product_data = {
            "Electronics": [
                {
                    "name": "Apple iPhone 14",
                    "description": "Latest Apple smartphone with A15 Bionic chip and dual-camera system.",
                    "price": "999.00",
                    "stock": 25
                },
                {
                    "name": "Samsung Galaxy A54",
                    "description": "Mid-range Android phone with AMOLED display and 5G support.",
                    "price": "349.99",
                    "stock": 30
                },
                {
                    "name": "Sony WH-1000XM4",
                    "description": "Industry-leading noise cancelling wireless headphones.",
                    "price": "278.00",
                    "stock": 15
                },
                {
                    "name": "Anker PowerCore 10000",
                    "description": "Portable power bank with fast charging technology.",
                    "price": "29.99",
                    "stock": 100
                }
            ],
            "Clothing": [
                {
                    "name": "Levi's 511 Slim Jeans",
                    "description": "Modern slim-fit jeans with a clean, tailored look.",
                    "price": "59.99",
                    "stock": 40
                },
                {
                    "name": "Nike Dri-FIT T-Shirt",
                    "description": "Moisture-wicking tee for sports and training.",
                    "price": "24.99",
                    "stock": 60
                },
                {
                    "name": "H&M Cotton Hoodie",
                    "description": "Basic hoodie made from soft organic cotton.",
                    "price": "35.00",
                    "stock": 50
                },
                {
                    "name": "Adidas Track Jacket",
                    "description": "Classic Adidas jacket with signature 3-stripe design.",
                    "price": "65.00",
                    "stock": 20
                }
            ],
            "Groceries": [
                {
                    "name": "Bashundhara Fortified Rice 5kg",
                    "description": "High-quality Bangladeshi rice fortified with vitamins.",
                    "price": "480.00",
                    "stock": 80
                },
                {
                    "name": "Fresh Soyabean Oil 1L",
                    "description": "Refined soyabean cooking oil for daily use.",
                    "price": "160.00",
                    "stock": 150
                },
                {
                    "name": "ACI Pure Salt 1kg",
                    "description": "Free-flowing iodized salt for healthy cooking.",
                    "price": "35.00",
                    "stock": 200
                },
                {
                    "name": "Brooke Bond Taaza Tea 400g",
                    "description": "Premium black tea for refreshing mornings.",
                    "price": "110.00",
                    "stock": 100
                }
            ],
            "Books": [
                {
                    "name": "Atomic Habits by James Clear",
                    "description": "Bestseller about building good habits and breaking bad ones.",
                    "price": "450.00",
                    "stock": 25
                },
                {
                    "name": "The Alchemist by Paulo Coelho",
                    "description": "Inspirational novel about finding your destiny.",
                    "price": "300.00",
                    "stock": 40
                },
                {
                    "name": "English Grammar in Use",
                    "description": "Reference and practice book for learners of English.",
                    "price": "580.00",
                    "stock": 15
                }
            ]
        }

        # --- Create categories and products ---
        for category_name, products in product_data.items():
            category, created = ProductCategory.objects.get_or_create(
                user=user,
                name=category_name,
                defaults={"description": f"{category_name} related items."}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created category: {category.name}"))

            for product in products:
                prod, created = Product.objects.get_or_create(
                    user=user,
                    name=product["name"],
                    category=category,
                    defaults={
                        "description": product["description"],
                        "price": Decimal(product["price"]),
                        "stock": product["stock"],
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created product: {prod.name}"))
                else:
                    self.stdout.write(f"Product already exists: {prod.name}")

        self.stdout.write(self.style.SUCCESS("✅ Seeding complete with real data!"))
