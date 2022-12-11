from django.contrib.auth.models import User
from django.core.management import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', email='', password='admin')
            print("Superuser created with credentials:\n\tusername: admin\n\tpassword: admin")

        else:
            print('Superuser already exists')