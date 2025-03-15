from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import BookingForm
from .models import Booking
from orders.models import Category
from django.contrib import messages
from django.utils import timezone
from orders.forms import OrderForm, OrderEditForm

@login_required
def bookings_list(request):
    if request.user.is_staff:
        bookings = Booking.objects.filter(is_active=True).order_by('booking_date')
    else:
        bookings = Booking.objects.filter(user=request.user, is_active=True).order_by('booking_date')
    context = {
        'bookings': bookings,
        'user': request.user,
    }
    return render(request, 'booking_list.html', context)


@login_required
def edit_booking(request, booking_id):
    if request.user.is_staff:
        booking = get_object_or_404(Booking, id=booking_id)
    else:
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.booking_date < timezone.now():
        messages.error(request, "Нельзя редактировать бронирование после его начала.")
        return redirect('booking_list')

    if request.method == 'POST':
        booking_form = BookingForm(request.POST, user=request.user, instance=booking)
        order_form = OrderEditForm(user=request.user, instance=booking.order if booking.order and booking.order.id else None)

        if 'update_booking' in request.POST:
            if booking_form.is_valid():
                booking_form.save()
                messages.success(request, "Бронирование обновлено!")
                return redirect('booking_list')
        elif 'update_order' in request.POST and booking.order:
            order_form = OrderEditForm(request.POST, user=request.user, instance=booking.order)
            if order_form.is_valid():
                order_form.save()
                messages.success(request, "Заказ в бронировании обновлён!")
                return redirect('booking_list')
        elif 'delete_order' in request.POST and booking.order:
            booking.order.delete()
            booking.order = None
            booking.save()
            messages.success(request, "Заказ удалён из бронирования!")
            return redirect('booking_list')
        elif 'create_order' in request.POST and not booking.order:
            order_form = OrderEditForm(request.POST, user=request.user)
            if order_form.is_valid():
                order = order_form.save(commit=False)
                order.user = request.user
                order.table_number = booking.table_number
                order.save()
                order_form.save_m2m()
                booking.order = order
                booking.save()
                messages.success(request, "Заказ добавлен к бронированию!")
                return redirect('booking_list')
            else:
                messages.error(request, "Ошибка при создании заказа. Проверьте данные.")
    else:
        booking_form = BookingForm(user=request.user, instance=booking)
        order_form = OrderEditForm(user=request.user, instance=booking.order if booking.order and booking.order.id else None)

    categories = Category.objects.all()
    return render(request, 'edit_booking.html', {
        'booking': booking,
        'booking_form': booking_form,
        'order_form': order_form,
        'categories': categories
    })


@login_required
def book_table(request):
    if request.method == 'POST':
        form = BookingForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Столик успешно забронирован!")
            return redirect('profile')
    else:
        form = BookingForm(user=request.user)

    booking_date = request.GET.get('booking_date')
    if booking_date:
        try:
            booking_date = timezone.datetime.fromisoformat(booking_date)
        except ValueError:
            booking_date = timezone.now()
    else:
        booking_date = timezone.now()

    all_tables = range(1, 21)
    booked_tables = Booking.objects.filter(
        is_active=True,
        booking_date__range=(booking_date - timedelta(hours=2), booking_date + timedelta(hours=2))
    ).values_list('table_number', flat=True)
    free_tables = [table for table in all_tables if table not in booked_tables]

    categories = Category.objects.all()
    return render(request, 'book_table.html', {
        'form': form,
        'free_tables': free_tables,
        'booking_date': booking_date,
        'categories': categories
    })

@login_required
def cancel_booking(request, booking_id):
    if request.user.is_staff:
        booking = get_object_or_404(Booking, id=booking_id)
    else:
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.booking_date < timezone.now():
        messages.error(request, "Нельзя отменить бронирование после его начала.")
        return redirect('booking_list')

    if request.method == 'POST':
        if booking.order:
            booking.order.delete()
        booking.is_active = False
        booking.save()
        messages.success(request, "Бронирование отменено!")
        return redirect('booking_list' if not request.user.is_staff else 'all_bookings')

    return render(request, 'cancel_booking.html', {'booking': booking})


@login_required
def cancel_booking(request, booking_id):
    try:
        if request.user.is_staff:
            booking = Booking.objects.get(id=booking_id, is_active=True)
        else:
            booking = Booking.objects.get(id=booking_id, user=request.user, is_active=True)
    except Booking.DoesNotExist:
        messages.error(request, "Бронирование не найдено или уже отменено.")
        return redirect('booking_list')

    if booking.booking_date < timezone.now():
        messages.error(request, "Нельзя отменить бронирование после его начала.")
        return redirect('booking_list')

    if request.method == 'POST':
        booking.is_active = False
        if booking.order:
            order = booking.order
            booking.order = None
            booking.save()
            order.delete()
        else:
            booking.save()
        updated_booking = Booking.objects.get(id=booking_id)
        if updated_booking.is_active:
            raise ValueError("Failed to update is_active to False")
        messages.success(request, "Бронирование отменено!")
        return redirect('booking_list')

    return render(request, 'cancel_booking.html', {'booking': booking})

