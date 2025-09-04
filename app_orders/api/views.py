from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response


from app_orders.models import Order
from app_auth.models import UserProfile
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
    
class OrderCountView(APIView):

    def get(self, request, business_user_id):
        try:
            profile = UserProfile.objects.get(user_id=business_user_id)
        except UserProfile.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if profile.type != 'business':
            return Response({"detail": "User is not a business."}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'completed' in request.path:
            status_filter = 'completed'
        else:
            status_filter = 'in_progress'

        count = Order.objects.filter(
            offer_detail__offer__user_id=business_user_id,
            status=status_filter
        ).count()

        return Response({"order_count": count}, status=status.HTTP_200_OK)
