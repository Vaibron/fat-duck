from django.urls import path
from . import views

urlpatterns = [
    path('', views.bookings_list, name='booking_list'),
    path('edit/<int:booking_id>/', views.edit_booking, name='edit_booking'),
    path('book/', views.book_table, name='book_table'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
]