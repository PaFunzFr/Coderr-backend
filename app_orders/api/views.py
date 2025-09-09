from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from django.shortcuts import get_object_or_404


from app_orders.models import Order
from app_auth.models import UserProfile
from .serializers import OrdersListCreateSerializer, OrderDetailSerializer
from .permissions import IsAssignedBusinessOrAdmin, IsCustomerUser

class OrdersListCreateView(generics.ListCreateAPIView):

    serializer_class = OrdersListCreateSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_superuser:
            if user.profile.type == 'customer':
                return Order.objects.filter(customer_user=self.request.user)
            else:
                return Order.objects.filter(offer_detail__offer__user=user)
        else:
            return Order.objects.all()

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        else:
            return [IsAuthenticated(), IsCustomerUser()]

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderDetailSerializer
    http_method_names = ['put', 'patch', 'delete']
    permission_classes = [IsAuthenticated, IsAssignedBusinessOrAdmin]

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        instance = self.get_object()
        return Response(OrdersListCreateSerializer(instance).data)
    
class OrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        profile = get_object_or_404(UserProfile, user_id=business_user_id)
        
        if profile.type != 'business':
            return Response({"detail": "Business user not found"}, status=status.HTTP_404_NOT_FOUND)
        
        status_filter = 'completed' if 'completed' in request.path else 'in_progress'

        count = Order.objects.filter(
            offer_detail__offer__user_id=business_user_id,
            status=status_filter
        ).count()

        if status_filter == 'completed':
            return Response({"completed_order_count": count})
        else:
            return Response({"order_count": count})
