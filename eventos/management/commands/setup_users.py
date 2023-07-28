from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group

from eventos.models import Usuario


class Command(BaseCommand):
    help = "Creates admin user."

    def handle(self, *args, **options):
        for username in ['admin', 'rrpp', 'entrada']:
            filter = Usuario.objects.filter(username=username)
            if not filter.exists():
                user = Usuario(username=username, first_name=username)
                user.set_password(username)
                user.is_superuser = True
                user.is_staff = True
                user.save()
            else:
                user = filter[0]
            if not user.groups.filter(name=username).exists():
                user.groups.add(Group.objects.filter(name=username).first())
            user.save()
