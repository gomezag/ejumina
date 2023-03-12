from django.test import TestCase
from eventos.models import Usuario
from django.contrib.auth.models import Group
from rest_framework.test import APIClient
from rest_framework import status

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

    def test_login_responds_with_token(self):
        client = APIClient()
        response = client.post('/api/user/login', data={'CI': 'admin',
                                                        'password': 'admin'})
        data = response.json()
        assert data['_id'] == 1
        assert data['rol'] == 'Admin'
        assert data['access'] != ''

    def test_login_with_invalid_returns_400(self):
        client = APIClient()
        response = client.post('/api/user/login', data={'CI': 'admino',
                                                        'password': 'admin'})
        assert response.status_code == 400
