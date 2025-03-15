from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from bookings.models import Booking
from bookings.forms import BookingForm
from orders.models import Order, MenuItem, Category

class BookingsTests(TestCase):
    def setUp(self):
        """Настройка перед каждым тестом."""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name="Еда")
        self.menu_item = MenuItem.objects.create(
            name="Пицца",
            category=self.category,
            price=500,
            is_available=True
        )
        self.booking = Booking.objects.create(
            user=self.user,
            table_number=1,
            booking_date=timezone.now() + timezone.timedelta(hours=1),
            is_active=True
        )

    def test_booking_model(self):
        """Тест модели Booking."""
        booking = self.booking
        self.assertEqual(str(booking), f"Стол 1 на {booking.booking_date} (testuser)")
        self.assertTrue(booking.is_active)

    def test_booking_form_valid(self):
        """Тест валидации формы бронирования."""
        booking_time = timezone.now().replace(hour=12, minute=0, second=0, microsecond=0) + timezone.timedelta(days=1)
        data = {
            'table_number': 2,
            'booking_date': booking_time.strftime('%Y-%m-%dT%H:%M'),
            f'item_{self.menu_item.id}': 1
        }
        form = BookingForm(data=data, user=self.user)
        self.assertTrue(form.is_valid(), form.errors)
        booking = form.save()
        self.assertEqual(booking.table_number, 2)
        self.assertEqual(booking.order.orderitem_set.count(), 1)

    def test_book_table_view_authenticated(self):
        """Тест страницы бронирования для авторизованного пользователя."""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('book_table'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_table.html')
        self.assertIn('form', response.context)

    def test_booking_list_view(self):
        """Тест списка бронирований."""
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('booking_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'booking_list.html')
        self.assertIn(self.booking, response.context['bookings'])

    def test_cancel_booking(self):
        """Тест отмены бронирования."""
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('cancel_booking', args=[self.booking.id]))
        self.assertEqual(response.status_code, 302)
        self.booking.refresh_from_db()
        self.assertFalse(self.booking.is_active)