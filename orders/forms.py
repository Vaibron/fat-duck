from django import forms
from .models import Order, MenuItem, OrderItem, Category


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['table_number']
        widgets = {
            'table_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'style': 'width: 100px;'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['table_number'].initial = 1
        print(f"User: {user}, Is staff: {user.is_staff if user else 'No user'}")

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
                            'style': 'width: 100px;',
                            'data_category': category.name
                        })
                    )

        if user and not user.is_staff:
            self.fields['table_number'].widget = forms.HiddenInput()

    def save(self, commit=True):
        order = super().save(commit=False)
        order.user = self.initial.get('user', None)
        if commit:
            order.save()
            print("Saving order with cleaned data:", self.cleaned_data)
            for field_name, quantity in self.cleaned_data.items():
                if field_name.startswith('item_') and quantity and int(quantity) > 0:
                    item_id = int(field_name.replace('item_', ''))
                    menu_item = MenuItem.objects.get(id=item_id)
                    OrderItem.objects.create(order=order, menu_item=menu_item, quantity=quantity)
                    print(f"Created OrderItem: {menu_item.name} x {quantity}")
            order.update_total_price()
        return order


class OrderEditForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['table_number']
        widgets = {
            'table_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'style': 'width: 100px;'})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and not user.is_staff:
            self.fields.pop('table_number', None)
        elif 'table_number' in self.fields:
            self.fields['table_number'].label = "Номер стола"

        current_items = {}
        if self.instance and self.instance.id:
            current_items = {item.menu_item.id: item.quantity for item in self.instance.orderitem_set.all()}

        categories = Category.objects.all()
        for category in categories:
            menu_items = MenuItem.objects.filter(category=category, is_available=True)
            if menu_items.exists():
                for item in menu_items:
                    initial_quantity = current_items.get(item.id, 0)
                    self.fields[f'item_{item.id}'] = forms.IntegerField(
                        label=f"{item.name} ({item.price} руб.)",
                        required=False,
                        min_value=0,
                        initial=initial_quantity,
                        widget=forms.NumberInput(attrs={
                            'class': 'form-control',
                            'style': 'width: 100px;',
                            'data_category': category.name
                        })
                    )

    def save(self, commit=True):
        order = super().save(commit=False)
        if commit:
            order.save()
            order.orderitem_set.all().delete()
            for field_name, quantity in self.cleaned_data.items():
                if field_name.startswith('item_') and quantity > 0:
                    item_id = int(field_name.replace('item_', ''))
                    menu_item = MenuItem.objects.get(id=item_id)
                    OrderItem.objects.create(order=order, menu_item=menu_item, quantity=quantity)
            order.update_total_price()
        return order