from django.test import TestCase
from eventos.models import *
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
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
        self.client = APIClient()

    def test_login_responds_with_token(self):
        response = self.client.post('/api/user/login', data={'CI': 'admin',
                                                             'password': 'admin'})
        data = response.json()

        self.assertEqual(data['_id'], 1, 'ID not what is expected.')
        self.assertEqual(data['rol'], 'Admin', 'rol not what is expected.')
        self.assertNotEqual(data['access'], '', 'token is empty.')

    def test_login_with_invalid_returns_400(self):
        client = APIClient()
        response = client.post('/api/user/login', data={'CI': 'admino',
                                                        'password': 'admin'})
        self.assertEqual(response.status_code, 400, 'Status code not what is expected.')


class AdminTestCase(TestCase):

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
        self.client = APIClient()
        self.login(client=self.client)

    def login(self, client):
        response = client.post('/api/user/login', data={'CI': 'admin',
                                                        'password': 'admin'})
        data = response.json()

        access_token = data['access']
        client.credentials(HTTP_AUTHORIZATION=f'JWT {access_token}')
        return data

    def test_get_all_eventos(self):
        res = self.client.get('/api/evento/all')
        expected = Evento.objects.all().count()
        self.assertEqual(res.status_code, 200, 'Status code not OK')
        self.assertEqual(len(res.data), expected, 'Len of people not what expected')

    def test_find_persona(self):
        persona = Persona.objects.first()
        res = self.client.get(f'/api/invitado/ci/{persona.cedula}')
        self.assertEqual(res.data.get('nombre'), persona.nombre, 'Nombre is not what expected')
