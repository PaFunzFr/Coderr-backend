from rest_framework import serializers
from app_offers.models import Offer, OfferDetail

class OfferSerializer(serializers.ModelSerializer):

    class Meta:
        model = Offer
        fields = ['id']

class OfferDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Offer
        fields = ['id']

class OfferdetailDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = OfferDetail
        fields = ['id']