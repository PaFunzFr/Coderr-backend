from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS

from django_filters.rest_framework import DjangoFilterBackend

from drf_spectacular.utils import extend_schema, OpenApiResponse

from app_reviews.models import Review
from .serializers import ReviewListCreateSerializer, ReviewUpdateDeleteSerializer
from .permissions import IsOwnerOrAdmin
from app_orders.api.permissions import IsCustomerUser
from .filters import ReviewFilter


@extend_schema(
    description="List all reviews or create a new review. Authenticated users only. Only customers can create.",
    responses={
        200: OpenApiResponse(response=ReviewListCreateSerializer, description="List of reviews"),
        201: OpenApiResponse(response=ReviewListCreateSerializer, description="Created review successfully"),
        400: OpenApiResponse(description="Invalid input data or validation errors")
    }
)
class ReviewListCreateView(generics.ListCreateAPIView):
    """
    List existing reviews or create a new review.
    GET: List reviews for authenticated users.
    POST: Create a new review for authenticated customers.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewListCreateSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['updated_at', 'rating']

    def get_permissions(self):
        """
        Apply different permissions for safe vs write methods.
        Safe methods: authenticated users.
        POST: authenticated customer users only.
        """
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        else:
            return [IsAuthenticated(), IsCustomerUser()]


@extend_schema(
    description="Update, or delete a review. Only owner or admin can modify.",
    responses={
        200: OpenApiResponse(response=ReviewListCreateSerializer, description="Updated review successfully"),
        204: OpenApiResponse(description="Review deleted successfully"),
        400: OpenApiResponse(description="Invalid input data"),
        403: OpenApiResponse(description="Permission denied"),
        404: OpenApiResponse(description="Review not found")
    }
)
class ReviewUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    Update, or delete a specific review.
    PUT/PATCH: Update review (owner/admin only).
    DELETE: Delete review (owner/admin only).
    """
    queryset = Review.objects.all()
    serializer_class = ReviewUpdateDeleteSerializer
    http_method_names = ['put', 'patch', 'delete']
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def update(self, request, *args, **kwargs):
        """
        Override update to return serialized review data after update.
        """
        super().update(request, *args, **kwargs)
        instance = self.get_object()
        return Response(ReviewListCreateSerializer(instance).data)
    