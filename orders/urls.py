from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, api_views

router = DefaultRouter()
router.register(r'orders', api_views.OrderViewSet)

urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('list/', views.order_list, name='order_list'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('update/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('edit/<int:order_id>/', views.edit_order, name='edit_order'),
    path('delete/<int:order_id>/', views.delete_order, name='delete_order'),
    path('analytics/', views.analytics, name='analytics'),
    path('api/', include(router.urls)),
]