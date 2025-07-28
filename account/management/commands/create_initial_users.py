# your_app/management/commands/create_initial_users.py

from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string

from account.models import User  
from account.enums import Roles 


class Command(BaseCommand):
    """
    run:
    python manage.py create_initial_users
    """
    help = 'Create 15 initial users and a superuser'

    def handle(self, *args, **kwargs):
        # create a superuser
        def createsuperuser(email="t@t.com", password="t"):
            if User.objects.filter(email=email).exists():
                self.stdout.write(self.style.WARNING(f"User {email} already exists. Skipping."))
                return
            
            User.objects.create_superuser(
                email=email,
                password=password,
                first_name='Tarik',
                last_name='Bosunia',
                role=Roles.SUPERADMIN,
                is_active=True,
                is_email_verified=True,
                auth_provider='email',
            )
            
                
        createsuperuser()

        for i in range(1, 16):
            email = f'user{i}@example.com'
            if User.objects.filter(email=email).exists():
                self.stdout.write(self.style.WARNING(f"User {email} already exists. Skipping."))
                continue

            password = get_random_string(8)
            user = User.objects.create_user(
                email=email,
                password=password,
                first_name=f'User{i}',
                last_name='Test',
                role=Roles.BUSINESSMAN,  # Or any role you want
                is_active=True,
                is_email_verified=True,
                auth_provider='email',
            )

            self.stdout.write(self.style.SUCCESS(f"Created {email} with password: {password}"))
