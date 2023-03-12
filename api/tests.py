from django.test import TestCase
from eventos.models import *
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from rest_framework import status
from datetime import date


class AuthTestCase(TestCase):

    def setUp(self):
        gadmin = Group(name='admin', label='Admin')
        gadmin.save()
        grrpp = Group(name='rrpp', label='RRPP')
        grrpp.save()
        gbouncer = Group(name='entrada', label='Bouncer')
        gbouncer.save()
        suser = Usuario.objects.create_superuser(username='admin',
                                                password='admin',
                                                first_name='Admin',
                                                email='testadmin@admin.co')
        suser.groups.add(gadmin)
        suser.save()

        evento1 = Evento(name='Test1', fecha=date.today())
        evento1.save()

        evento2 = Evento(name='Test2', fecha=date.today())
        evento2.save()

        persona1 = Persona(nombre='Raul', cedula='0000')
        persona1.save()

    def login(self, client):
        response = client.post('/api/user/login', data={'CI': 'admin',
                                                        'password': 'admin'})
        data = response.json()

        access_token = data['access']
        client.credentials(HTTP_AUTHORIZATION=f'JWT {access_token}')
        return data

    def test_login_responds_with_token(self):
        client = APIClient()
        data = self.login(client)
        assert data['_id'] == 1
        assert data['rol'] == 'Admin'
        assert data['access'] != ''

    def test_login_with_invalid_returns_400(self):
        client = APIClient()
        response = client.post('/api/user/login', data={'CI': 'admino',
                                                        'password': 'admin'})
        assert response.status_code == 400

    def test_login_and_get_all_eventos(self):
        client = APIClient()
        data = self.login(client)
        res = client.get('/api/evento/all')

        assert res.status_code == 200
        assert len(res.data) == 2

    def test_login_and_find_persona(self):
        client = APIClient()
        self.login(client)
        res = client.get('/api/invitado/ci/0000')
        assert res.data.get('nombre') == 'Raul'

