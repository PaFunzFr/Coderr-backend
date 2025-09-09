from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS

from django_filters.rest_framework import DjangoFilterBackend

from app_reviews.models import Review
from .serializers import ReviewListCreateSerializer, ReviewUpdateDeleteSerializer
from .permissions import IsOwnerOrAdmin
from app_orders.api.permissions import IsCustomerUser
from .filters import ReviewFilter


class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewListCreateSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['updated_at', 'rating']

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        else:
            return [IsAuthenticated(), IsCustomerUser()]

class ReviewUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewUpdateDeleteSerializer
    http_method_names = ['put', 'patch', 'delete']
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        instance = self.get_object()
        return Response(ReviewListCreateSerializer(instance).data)
    