from django.db import models

class Roles(models.TextChoices):
    SUPERADMIN = 'superadmin', 'Super Admin'
    BUSINESSMAN = 'businessman', 'Businessman'


class AuthProvider(models.TextChoices):
    EMAIL = 'email', 'Email'
    GOOGLE = 'google', 'Google'
    GITHUB = 'github', 'GitHub'
    FACEBOOK = 'facebook', 'Facebook'