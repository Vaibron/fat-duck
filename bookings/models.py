from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    table_number = models.PositiveIntegerField(verbose_name="Номер стола")
    booking_date = models.DateTimeField(verbose_name="Дата и время бронирования")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_active = models.BooleanField(default=True, verbose_name="Активно")
    order = models.OneToOneField('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Связанный заказ")

    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        unique_together = ('table_number', 'booking_date')

    def clean(self):
        if self.booking_date < timezone.now():
            raise ValidationError("Нельзя забронировать столик в прошлом!")
        if self.table_number < 1 or self.table_number > 20:
            raise ValidationError("Номер стола должен быть от 1 до 20.")

    def __str__(self):
        return f"Стол {self.table_number} на {self.booking_date} ({self.user.username})"
