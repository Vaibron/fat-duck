from django.test import TestCase, Client
from django.urls import reverse
from orders.models import Category, MenuItem


class BaseTests(TestCase):
    def setUp(self):
        """Настройка перед каждым тестом."""
        self.client = Client()
        self.category = Category.objects.create(name="Напитки")
        self.menu_item = MenuItem.objects.create(
            name="Кофе",
            category=self.category,
            price=150,
            is_available=True,
            description="Вкусный кофе"
        )

    def test_home_page(self):
        """Тест главной страницы."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_menu_view(self):
        """Тест страницы меню с фильтрацией."""
        response = self.client.get(reverse('menu'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'menu.html')
        self.assertIn('menu_data', response.context)
        self.assertIn(self.category, response.context['menu_data'])
        self.assertEqual(response.context['menu_data'][self.category].count(), 1)

    def test_menu_search(self):
        """Тест поиска в меню."""
        response = self.client.get(reverse('menu'), {'q': 'Кофе'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.menu_item, response.context['menu_data'][self.category])

        response = self.client.get(reverse('menu'), {'q': 'Чай'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['menu_data']), 0)

    def test_contacts_view(self):
        """Тест страницы контактов."""
        response = self.client.get(reverse('contacts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contacts.html')