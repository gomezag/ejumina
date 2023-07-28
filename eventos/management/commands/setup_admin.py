from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group

from eventos.models import Usuario


class Command(BaseCommand):
    help = "Creates admin user."

    def handle(self, *args, **options):
        filter = Usuario.objects.filter(username='admin')
        if not filter.exists():
            user = Usuario(username='admin', first_name='Admin')
            user.set_password('admin')
            user.is_superuser = True
            user.is_staff = True
            user.save()
        else:
            user = filter[0]
        if not user.groups.filter(name='admin').exists():
            user.groups.add(Group.objects.filter(name='admin').first())
        user.save()
