from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Creates required initial groups."

    def handle(self, *args, **options):
        LABELS = {
            'admin': 'Admin',
            'entrada': 'Entrada',
            'rrpp': 'R.R.P.P.'
        }
        for name in ['admin', 'entrada', 'rrpp']:
            if not Group.objects.filter(name=name).exists():
                grp = Group(name=name, label=LABELS[name])
                grp.save()

                self.stdout.write(
                    self.style.SUCCESS('Successfully created group "%s"' % name)
                )
            self.stdout.write(
                self.style.SUCCESS('"%s" Already exists' % name)
            )
