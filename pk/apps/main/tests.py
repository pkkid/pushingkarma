import sys
from itertools import product
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings


@override_settings(ALLOWED_HOSTS=['testserver'])
class DebugSuperuserTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model().objects
        cls.ordinary_user = users.create_user(username='ordinary')
        users.create_user(username='inactive', is_superuser=True, is_active=False)
        cls.superuser = users.create_user(username='first', is_superuser=True, is_staff=True)
        users.create_user(username='second', is_superuser=True, is_staff=True)

    def test_auto_user_requires_all_development_guards(self):
        commands = [['manage.py', 'runserver'], ['daphne', 'pk.asgi:application'], ['gunicorn', 'pk.wsgi:application']]
        for debug, enabled, argv in product([False, True], [False, True], commands):
            with (
                self.subTest(debug=debug, enabled=enabled, command=argv[0]),
                override_settings(DEBUG=debug, DEBUG_SUPERUSER=enabled),
                patch.object(sys, 'argv', argv),
            ):
                response = self.client.get('/api/main/global_vars')
                self.assertEqual(response.status_code, 200)
                data = response.json()
                if debug and enabled and 'runserver' in argv:
                    self.assertEqual(data['user']['id'], self.superuser.pk)
                else:
                    self.assertIsNone(data['user'])
                self.assertNotIn('SHOW_ALL_NAV_LINKS', data)
                self.assertNotIn('DEBUG_SUPERUSER', data)

    @override_settings(DEBUG=True, DEBUG_SUPERUSER=True)
    def test_auto_user_can_access_budget_without_saving_a_login(self):
        with patch.object(sys, 'argv', ['manage.py', 'runserver']):
            response = self.client.get('/api/budget/accounts')
            self.assertEqual(response.status_code, 200)
            self.assertNotIn('_auth_user_id', self.client.session)
            with override_settings(DEBUG_SUPERUSER=False):
                self.assertEqual(self.client.get('/api/budget/accounts').status_code, 401)
            with override_settings(DEBUG=False):
                self.assertEqual(self.client.get('/api/budget/accounts').status_code, 401)
        self.assertEqual(self.client.get('/api/budget/accounts').status_code, 401)

    @override_settings(DEBUG=True, DEBUG_SUPERUSER=True)
    def test_existing_authenticated_user_is_preserved(self):
        self.client.force_login(self.ordinary_user)
        with patch.object(sys, 'argv', ['manage.py', 'runserver']):
            response = self.client.get('/api/main/global_vars')
        self.assertEqual(response.json()['user']['id'], self.ordinary_user.pk)

    @override_settings(DEBUG=True, DEBUG_SUPERUSER=True)
    def test_no_active_superuser_leaves_request_anonymous(self):
        get_user_model().objects.filter(is_superuser=True).update(is_active=False)
        with patch.object(sys, 'argv', ['manage.py', 'runserver']):
            response = self.client.get('/api/main/global_vars')
            self.assertIsNone(response.json()['user'])
            self.assertEqual(self.client.get('/api/budget/accounts').status_code, 401)
