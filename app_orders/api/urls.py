from django.urls import path
from .views import OrdersListCreateView, OrderDetailView

urlpatterns = [
    path('', OrdersListCreateView.as_view(), name="offers-list"),
    path('<int:pk>/', OrderDetailView.as_view(), name="offer-detail"),
]