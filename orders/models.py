from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название категории")
    priority = models.PositiveIntegerField(default=0, verbose_name="Приоритет (чем меньше, тем выше)")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['priority', 'name']

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Категория")
    name = models.CharField(max_length=100, verbose_name="Название блюда")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Цена")
    description = models.TextField(blank=True, verbose_name="Описание")
    is_available = models.BooleanField(default=True, verbose_name="Доступно")
    image = models.ImageField(upload_to='menu_images/', null=True, blank=True, verbose_name="Изображение")

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"

    def __str__(self):
        return f"{self.name} ({self.price} руб.)"

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'В ожидании'),
        ('ready', 'Готово'),
        ('paid', 'Оплачено'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")
    table_number = models.PositiveIntegerField(verbose_name="Номер стола")
    items = models.ManyToManyField(MenuItem, through='OrderItem', verbose_name="Блюда")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая стоимость", default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def update_total_price(self):
        self.total_price = sum(item.menu_item.price * item.quantity for item in self.orderitem_set.all())
        self.save(update_fields=['total_price'])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.total_price = sum(item.menu_item.price * item.quantity for item in self.orderitem_set.all())
        super().save(update_fields=['total_price'])

    def __str__(self):
        return f"Заказ #{self.id} - Стол {self.table_number} ({self.status})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"

    def __str__(self):
        return f"{self.menu_item.name} x{self.quantity}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.order.update_total_price()
