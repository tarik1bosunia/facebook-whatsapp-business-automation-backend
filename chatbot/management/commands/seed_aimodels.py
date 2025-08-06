from django.core.management.base import BaseCommand
from chatbot.models import AIModel

"""python manage.py seed_aimodels"""
class Command(BaseCommand):
    help = 'Seeds initial AI model data into the database.'

    def handle(self, *args, **options):
        models_to_seed = [
            {'code': 'gemini-2.0-flash', 'name': 'Gemini 2.0 Flash', 'is_custom': False},
            # Add other models here if needed in the future
        ]

        self.stdout.write(self.style.SUCCESS('Seeding AI models...'))

        for model_data in models_to_seed:
            ai_model, created = AIModel.objects.update_or_create(
                code=model_data['code'],
                defaults={
                    'name': model_data['name'],
                    'is_custom': model_data['is_custom']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Successfully created AIModel: {ai_model.name} ({ai_model.code})"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Successfully updated AIModel: {ai_model.name} ({ai_model.code})"))

        self.stdout.write(self.style.SUCCESS('AI model seeding completed.'))