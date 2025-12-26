import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Ensure admin user exists with password from ADMIN_PASSWORD env var'

    def handle(self, *args, **options):
        User = get_user_model()
        password = os.environ.get('ADMIN_PASSWORD')
        
        if not password:
            self.stdout.write(self.style.WARNING('ADMIN_PASSWORD not set, skipping'))
            return
        
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={'is_staff': True, 'is_superuser': True}
        )
        admin.set_password(password)
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        else:
            self.stdout.write(self.style.SUCCESS('Updated admin password'))
