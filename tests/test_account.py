from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

class AccountsTests(TestCase):
    def setUp(self):
        """Настройка перед каждым тестом."""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345', email='test@example.com')

    def test_login_view(self):
        """Тест страницы логина."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': '12345'
        })
        self.assertEqual(response.status_code, 302)

    def test_profile_view(self):
        """Тест страницы профиля."""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertEqual(response.context['user'], self.user)

    def test_logout(self):
        """Тест выхода из системы."""
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse('_auth_user_id' in self.client.session)