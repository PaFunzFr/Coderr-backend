from rest_framework import serializers
from app_offers.models import Offer, OfferDetail


class OfferdetailDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = OfferDetail
        fields = ['id']

class OfferSerializer(serializers.ModelSerializer):
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)
    details = OfferdetailDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time"
        ]

    def validate_details(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Details must have at least 3 items")
        
        all_types = []
        for detail in value:
            all_types.append(detail['offer_type'])

        required_types = ['basic', 'standard', 'premium']
        for required in required_types:
            if required not in all_types:
                raise serializers.ValidationError(f"Missing offer_type: {required}")
            
        return value


    def create(self, validated_data):
        details_list = validated_data.pop('details')
        current_user = self.context['request'].user

        #create offer
        new_offer = Offer.objects.create(user=current_user, **validated_data)

        # create details
        for single_detail in details_list:
            OfferDetail.objects.create(offer=new_offer, **single_detail)

        return new_offer
        

class OfferDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Offer
        fields = ['id']

    # for update / save revisions
    # def save(self, *args, **kwargs):
    #     if self.pk:
    #         self.revisions += 1
    #     super().save(*args, **kwargs)

