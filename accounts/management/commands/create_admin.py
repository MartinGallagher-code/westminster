import os
import secrets

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from accounts.models import UserProfile


class Command(BaseCommand):
    help = (
        'Create the initial admin user. Reads credentials from the '
        'DJANGO_ADMIN_USERNAME/DJANGO_ADMIN_EMAIL/DJANGO_ADMIN_PASSWORD '
        'environment variables; generates a random password if none is set.'
    )

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_ADMIN_USERNAME', 'admin')
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING('Admin user already exists.'))
            return

        email = os.environ.get('DJANGO_ADMIN_EMAIL', 'admin@studyreformed.com')
        password = os.environ.get('DJANGO_ADMIN_PASSWORD')
        generated = password is None
        if generated:
            password = secrets.token_urlsafe(18)

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        UserProfile.objects.get_or_create(user=user)

        if generated:
            self.stdout.write(self.style.SUCCESS(
                f'Admin user created (username: {username}). '
                f'Generated password: {password}\n'
                'Store this securely and change it after first login — '
                'it will not be shown again.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'Admin user created (username: {username}) using the '
                'supplied DJANGO_ADMIN_PASSWORD.'
            ))
