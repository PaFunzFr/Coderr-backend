from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from app_auth.models import UserProfile
from app_offers.models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferDetailSerializer, OfferdetailDetailSerializer

class OffersListCreateView(generics.ListCreateAPIView):
    queryset = Offer
    serializer_class = OfferSerializer
    permission_classes = []


class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer
    serializer_class = OfferDetailSerializer
    permission_classes = []


class OfferDetailsDetailView(generics.ListAPIView):
    queryset = OfferDetail
    serializer_class = OfferdetailDetailSerializer
    permission_classes = []