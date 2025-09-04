from rest_framework import generics
from rest_framework.response import Response

from app_reviews.models import Review
from .serializers import ReviewListCreateSerializer, ReviewUpdateDeleteSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewListCreateSerializer

class ReviewUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewUpdateDeleteSerializer
    http_method_names = ['put', 'patch', 'delete']
    permission_classes = []

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        instance = self.get_object()
        return Response(ReviewListCreateSerializer(instance).data)
    