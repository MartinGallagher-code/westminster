from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Create the initial admin user with default password "hello"'

    def handle(self, *args, **options):
        if User.objects.filter(username='admin').exists():
            self.stdout.write(self.style.WARNING('Admin user already exists.'))
            return

        user = User.objects.create_superuser(
            username='admin',
            email='admin@studyreformed.com',
            password='hello',
        )
        UserProfile.objects.get_or_create(user=user)
        self.stdout.write(self.style.SUCCESS(
            'Admin user created (username: admin, password: hello). '
            'Please change the password after first login.'
        ))
