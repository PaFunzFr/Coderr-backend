from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django.db.models import Min

from app_orders.models import Order
from .serializers import OrdersListCreateSerializer, OrderDetailSerializer

class OrdersListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrdersListCreateSerializer

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderDetailSerializer