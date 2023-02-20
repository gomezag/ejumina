
from django.test import TestCase
from eventos.models import Evento
from django.contrib.auth.models import User
# Create your tests here.


class APITests(TestCase):
    def setUp(self):
        Evento.objects.create(name="TestoEvento", estado='PUB')
        user = User.objects.create(username='admin')

    def test_user_exists(self):
        assert User.objects.count()>0
