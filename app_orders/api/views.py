from rest_framework import generics
from rest_framework.response import Response

from app_orders.models import Order
from .serializers import OrdersListCreateSerializer, OrderDetailSerializer

class OrdersListCreateView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrdersListCreateSerializer

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderDetailSerializer
    http_method_names = ['put', 'patch', 'delete']

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        instance = self.get_object()
        return Response(OrdersListCreateSerializer(instance).data)