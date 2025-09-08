from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated, AllowAny, SAFE_METHODS
from django_filters.rest_framework import DjangoFilterBackend

from django.db.models import Min

from .paginations import LargeResultsSetPagination
from .filters import OfferFilter
from app_offers.models import Offer, OfferDetail
from .serializers import OfferCreateUpdateSerializer, OfferDetailNestedDetailSerializer, OfferListSerializer
from .permissions import IsAssignedBusinessOrAdmin


def add_min_fields_to_offer():
    return Offer.objects.all().annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )


class OffersListCreateView(generics.ListCreateAPIView):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['updated_at', 'min_price']
    search_fields = ['title', 'description']
    filterset_class = OfferFilter
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        return add_min_fields_to_offer()
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return OfferCreateUpdateSerializer
        return OfferListSerializer
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated()]


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):

    def get_queryset(self):
        return add_min_fields_to_offer()
    
    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return OfferCreateUpdateSerializer
        return OfferListSerializer
    
    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsAssignedBusinessOrAdmin()]


class OfferDetailsDetailView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailNestedDetailSerializer
    permission_classes = [IsAuthenticated]