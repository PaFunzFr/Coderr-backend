from django.urls import path
from .views import OrdersListCreateView, OrderDetailView

urlpatterns = [
    path('', OrdersListCreateView.as_view(), name="orders-list"),
    path('<int:pk>/', OrderDetailView.as_view(), name="order-detail"),
]