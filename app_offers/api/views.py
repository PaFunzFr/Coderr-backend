from rest_framework import generics, filters
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django_filters.rest_framework import DjangoFilterBackend

from django.db.models import Min

from .paginations import LargeResultsSetPagination
from .filters import OfferFilter
from app_offers.models import Offer, OfferDetail
from .serializers import OfferCreateUpdateSerializer, OfferDetailNestedDetailSerializer, OfferListSerializer

class OffersListCreateView(generics.ListCreateAPIView):
    permission_classes = []
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['updated_at', 'min_price']
    search_fields = ['title', 'description']
    filterset_class = OfferFilter
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        queryset = Offer.objects.all().annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return OfferCreateUpdateSerializer
        return OfferListSerializer


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = []

    def get_queryset(self):
        queryset = Offer.objects.all().annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )
        return queryset
    
    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return OfferCreateUpdateSerializer
        return OfferListSerializer

class OfferDetailsDetailView(generics.ListAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailNestedDetailSerializer
    permission_classes = []

    def get_queryset(self):
        pk = self.kwargs["pk"]
        queryset = OfferDetail.objects.filter(pk=pk)
        return queryset