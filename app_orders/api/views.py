from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


from app_orders.models import Order
from app_auth.models import UserProfile
from .serializers import OrdersListCreateSerializer, OrderDetailSerializer
from .permissions import IsAssignedBusinessOrAdmin

class OrdersListCreateView(generics.ListCreateAPIView):

    serializer_class = OrdersListCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_superuser:
            if user.profile.type == 'customer':
                return Order.objects.filter(customer_user=self.request.user)
            else:
                return Order.objects.filter(offer_detail__offer__user=user)
        else:
            return Order.objects.all()


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
            return Response({"detail": "User is not a business."}, status=status.HTTP_400_BAD_REQUEST)
        
        status_filter = 'completed' if 'completed' in request.path else 'in_progress'

        count = Order.objects.filter(
            offer_detail__offer__user_id=business_user_id,
            status=status_filter
        ).count()

        if status_filter == 'completed':
            return Response({"completed_order_count": count})
        else:
            return Response({"order_count": count})
