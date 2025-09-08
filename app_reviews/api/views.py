from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend

from app_reviews.models import Review
from .serializers import ReviewListCreateSerializer, ReviewUpdateDeleteSerializer
from .permissions import IsOwnerOrAdmin
from .filters import ReviewFilter


class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewListCreateSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['updated_at', 'rating']
    permission_classes = [IsAuthenticated]

class ReviewUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewUpdateDeleteSerializer
    http_method_names = ['put', 'patch', 'delete']
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        instance = self.get_object()
        return Response(ReviewListCreateSerializer(instance).data)
    