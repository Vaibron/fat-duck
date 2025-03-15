from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'table_number', 'booking_date', 'is_active')
    list_filter = ('is_active', 'booking_date')
    search_fields = ('user__username', 'table_number')