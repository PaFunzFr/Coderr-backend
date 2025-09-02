from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from django_filters.rest_framework import DjangoFilterBackend

from django.db.models import Min

from app_auth.models import UserProfile
from app_offers.models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferDetailSerializer, OfferdetailDetailSerializer

class OffersListCreateView(generics.ListCreateAPIView):
    queryset = Offer
    serializer_class = OfferSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend]


    def get_queryset(self):
        queryset = Offer.objects.all().annotate(
            min_price=Min("details__price"),
            min_delivery_time=Min("details__delivery_time_in_days"),
        )
        return queryset


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer
    serializer_class = OfferDetailSerializer
    permission_classes = []

class OfferDetailsDetailView(generics.ListAPIView):
    queryset = OfferDetail
    serializer_class = OfferdetailDetailSerializer
    permission_classes = []