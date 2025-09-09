from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema, OpenApiResponse

from app_orders.models import Order
from app_auth.models import UserProfile
from .serializers import OrdersListCreateSerializer, OrderDetailSerializer
from .permissions import IsAssignedBusinessOrAdmin, IsCustomerUser


@extend_schema(
    description="List all orders for the authenticated user or create a new order.",
    responses=OrdersListCreateSerializer
)
class OrdersListCreateView(generics.ListCreateAPIView):
    """
    List orders for the current user (customer or business) or create a new order.
    Superusers can see all orders.
    """
    serializer_class = OrdersListCreateSerializer

    def get_queryset(self):
        """
        Return queryset based on user type:
        - Customers: only their own orders
        - Business users: orders for their offers
        - Superusers: all orders
        """
        user = self.request.user
        if not user.is_superuser:
            if user.profile.type == 'customer':
                return Order.objects.filter(customer_user=self.request.user)
            else:
                return Order.objects.filter(offer_detail__offer__user=user)
        else:
            return Order.objects.all()

    def get_permissions(self):
        """
        Assign permissions dynamically:
        - SAFE_METHODS: authenticated users
        - POST: customer users only
        """
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        else:
            return [IsAuthenticated(), IsCustomerUser()]


@extend_schema(
    description="Retrieve, update, or delete a specific order.",
    responses=OrderDetailSerializer
)
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific order.
    Only assigned business or admin users can modify orders.
    """
    queryset = Order.objects.all()
    serializer_class = OrderDetailSerializer
    http_method_names = ['put', 'patch', 'delete']
    permission_classes = [IsAuthenticated, IsAssignedBusinessOrAdmin]

    def update(self, request, *args, **kwargs):
        """
        Update the order and return serialized data using OrdersListCreateSerializer.
        """
        super().update(request, *args, **kwargs)
        instance = self.get_object()
        return Response(OrdersListCreateSerializer(instance).data)
    

@extend_schema(
    description="Return the number of orders for a given business user. Supports 'completed' or 'in_progress' filter.",
    responses={
        200: OpenApiResponse(description="Returns order count."),
        404: OpenApiResponse(description="Business user not found.")
    }
)
class OrderCountView(APIView):
    """
    Return the count of orders for a business user, filtered by status.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        """
        GET: Return order count for the specified business user.
        """
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
