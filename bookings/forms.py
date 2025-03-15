from django import forms
from .models import Booking
from orders.models import MenuItem, Order, OrderItem, Category
from django.utils import timezone
from datetime import timedelta

class BookingForm(forms.ModelForm):
    table_number = forms.IntegerField(
        label="Номер стола",
        min_value=1,
        max_value=20,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Booking
        fields = ['table_number', 'booking_date']
        widgets = {
            'booking_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        categories = Category.objects.all()
        for category in categories:
            menu_items = MenuItem.objects.filter(category=category, is_available=True)
            if menu_items.exists():
                for item in menu_items:
                    self.fields[f'item_{item.id}'] = forms.IntegerField(
                        label=f"{item.name} ({item.price} руб.)",
                        required=False,
                        min_value=0,
                        initial=0,
                        widget=forms.NumberInput(attrs={
                            'class': 'form-control',
                            'data_category': category.name
                        })
                    )

    def clean(self):
        cleaned_data = super().clean()
        booking_date = cleaned_data.get('booking_date')
        table_number = cleaned_data.get('table_number')

        if booking_date and table_number:
            booking_time = booking_date.time()
            if booking_time < timezone.datetime.strptime('08:00', '%H:%M').time() or booking_time > timezone.datetime.strptime('22:00', '%H:%M').time():
                raise forms.ValidationError("Ресторан работает с 8:00 до 22:00. Выберите время в этом диапазоне.")
            start_time = booking_date - timedelta(hours=2)
            end_time = booking_date + timedelta(hours=2)
            if Booking.objects.filter(
                table_number=table_number,
                booking_date__range=(start_time, end_time),
                is_active=True
            ).exclude(id=self.instance.id if self.instance else None).exists():
                raise forms.ValidationError("Этот стол уже забронирован в указанный период.")

        return cleaned_data

    def save(self, commit=True):
        booking = super().save(commit=False)
        if self.user:
            booking.user = self.user
        if commit:
            booking.save()
            items_selected = False
            order = None
            for field_name, quantity in self.cleaned_data.items():
                if field_name.startswith('item_') and quantity > 0:
                    if not order:
                        order = Order.objects.create(
                            table_number=booking.table_number,
                            status='pending',
                            user=self.user
                        )
                    item_id = int(field_name.replace('item_', ''))
                    menu_item = MenuItem.objects.get(id=item_id)
                    OrderItem.objects.create(order=order, menu_item=menu_item, quantity=quantity)
                    items_selected = True
            if items_selected and order:
                booking.order = order
                booking.save()
        return booking