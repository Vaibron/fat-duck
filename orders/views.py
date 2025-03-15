from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Order, OrderItem, MenuItem, Category
from .forms import OrderForm, OrderEditForm
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from bookings.models import Booking
from django.contrib import messages

def check_booking_permission(request):
    """Проверяет наличие активного бронирования для создания заказа."""
    if request.user.is_staff:
        return True
    current_time = timezone.now()
    booking = Booking.objects.filter(
        user=request.user,
        is_active=True,
        booking_date__gte=current_time
    ).first()
    return booking if booking else False

@login_required
def create_order(request):
    booking = check_booking_permission(request)
    if not booking and not request.user.is_staff:
        messages.error(request, "Вы не можете создать заказ без активного бронирования на будущее время.")
        return redirect('order_list')

    if request.method == 'POST':
        print("POST data:", dict(request.POST))
        form = OrderForm(request.POST, user=request.user)
        if form.is_valid():
            print("Cleaned data:", form.cleaned_data)
            order = form.save(commit=True)
            if not request.user.is_staff and booking:
                order.table_number = booking.table_number
                booking.order = order
                booking.save()
            print("Order saved:", order.id, "OrderItems:", list(order.orderitem_set.all()))
            messages.success(request, "Заказ успешно создан!")
            return redirect('order_list')
        else:
            print("Form errors:", form.errors)
            messages.error(request, "Ошибка при создании заказа. Проверьте введенные данные.")
    else:
        form = OrderForm(user=request.user)

    categories = Category.objects.all()
    return render(request, 'create_order.html', {'form': form, 'categories': categories})


@login_required
def order_list(request):
    if not request.user.is_staff:
        return redirect('booking_list')

    status_filter = request.GET.get('status', '')
    query = request.GET.get('q', '')
    date_filter = request.GET.get('date', timezone.now().date().isoformat())
    try:
        date_filter = datetime.strptime(date_filter, '%Y-%m-%d').date()
    except ValueError:
        date_filter = timezone.now().date()

    orders = Order.objects.all()
    if status_filter in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status_filter)
    if query:
        orders = orders.filter(table_number__icontains=query) | orders.filter(status__icontains=query)
    if date_filter:
        orders = orders.filter(created_at__date=date_filter)

    orders_with_permissions = [{'order': order, 'can_manage': True} for order in orders]

    context = {
        'orders_with_permissions': orders_with_permissions,
        'status_filter': status_filter,
        'query': query,
        'date_filter': date_filter.isoformat(),
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'order_list.html', context)


@login_required
def order_detail(request, order_id):
    if request.user.is_staff:
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})


@login_required
@staff_member_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Order.STATUS_CHOICES):
            order.status = status
            order.save()
            messages.success(request, "Статус заказа обновлён!")
            return redirect('order_list')
    return render(request, 'update_order_status.html', {'order': order})


@login_required
@staff_member_required
def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderEditForm(request.POST, instance=order, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Заказ успешно обновлён!")
            return redirect('order_list')
        else:
            messages.error(request, "Ошибка при редактировании заказа. Проверьте введенные данные.")
    else:
        form = OrderEditForm(instance=order, user=request.user)

    categories = Category.objects.all()
    return render(request, 'edit_order.html', {'form': form, 'order': order, 'categories': categories})


@login_required
@staff_member_required
def delete_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        Booking.objects.filter(order=order).update(order=None)
        order.delete()
        messages.success(request, "Заказ удалён!")
        return redirect('order_list')
    return render(request, 'delete_order.html', {'order': order})


@login_required
@staff_member_required
def analytics(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status_filter = request.GET.get('status', '')
    show_all_time = request.GET.get('all_time', 'false') == 'true'
    if show_all_time:
        orders = Order.objects.all()
        bookings = Booking.objects.filter(is_active=True)
        date_range_label = "За всё время"
    else:
        if start_date and end_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            except ValueError:
                start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        else:
            start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        orders = Order.objects.filter(created_at__range=(start_date, end_date))
        bookings = Booking.objects.filter(booking_date__range=(start_date, end_date), is_active=True)
        date_range_label = f"{start_date.strftime('%Y-%m-%d')} - {end_date.strftime('%Y-%m-%d')}"
    if status_filter in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status_filter)
    total_revenue = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_orders = orders.count()
    total_clients = bookings.count()
    popular_items = OrderItem.objects.filter(
        order__in=orders
    ).values('menu_item__name').annotate(total=Sum('quantity')).order_by('-total')[:5]
    context = {
        'start_date': start_date.strftime('%Y-m-d') if not show_all_time else '',
        'end_date': end_date.strftime('%Y-%m-%d') if not show_all_time else '',
        'status_filter': status_filter,
        'show_all_time': show_all_time,
        'date_range_label': date_range_label,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_clients': total_clients,
        'popular_items': popular_items,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'analytics.html', context)
