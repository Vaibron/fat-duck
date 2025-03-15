from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from orders.models import Order, OrderItem, MenuItem, Category

class OrdersTests(TestCase):
    def setUp(self):
        """Настройка перед каждым тестом."""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name="Еда")
        self.menu_item = MenuItem.objects.create(
            name="Бургер",
            category=self.category,
            price=300,
            is_available=True
        )
        self.order = Order.objects.create(
            user=self.user,
            table_number=1,
            status='pending'
        )
        self.order_item = OrderItem.objects.create(
            order=self.order,
            menu_item=self.menu_item,
            quantity=2
        )

    def test_order_model(self):
        """Тест модели Order."""
        self.assertEqual(self.order.total_price, 600)
        self.assertEqual(self.order.orderitem_set.count(), 1)

    def test_order_detail_view(self):
        """Тест страницы деталей заказа."""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('order_detail', args=[self.order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'order_detail.html')
        self.assertEqual(response.context['order'], self.order)

    def test_order_list_view(self):
        """Тест списка заказов."""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('order_list'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('booking_list'))
