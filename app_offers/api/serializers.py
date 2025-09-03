from rest_framework import serializers
from app_offers.models import Offer, OfferDetail


class OfferDetailNestedReadSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = OfferDetail
        fields = ['id','url']
        extra_kwargs = {
            'url': {'view_name': 'offerdetails-detail', 'lookup_field': 'pk'}
        }

class OfferDetailNestedDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = OfferDetail
        fields = [
            'id',
            'offer',
            'title',
            'revisions',
            'delivery_time_in_days',
            'features',
            'offer_type',
            'price'
            ]
        read_only_fields = ['revisions', 'offer']


class OfferListSerializer(serializers.ModelSerializer):
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)
    details = OfferDetailNestedReadSerializer(many=True)

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

class OfferCreateUpdateSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)
    details = OfferDetailNestedDetailSerializer(many=True)

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
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
            "min_price",
            "min_delivery_time"
        ]

    def validate_details(self, value):
        if not self.instance: # only validates for POST Methode (no instance existant)
            if len(value) < 3:
                raise serializers.ValidationError("Details must contain exactly 3 items (basic, standard, premium).")
            
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
    

    def update(self, instance, validated_data):
        details_list = validated_data.pop('details', [])

        # Update Details
        for single_detail in details_list:
            offer_type_to_update = single_detail.get('offer_type')
            
            if offer_type_to_update:
                detail = instance.details.get(offer_type=offer_type_to_update)

                for field in ['title', 'delivery_time_in_days', 'price', 'features']:
                    if field in single_detail:
                        setattr(detail, field, single_detail[field])

                # detail.title = single_detail.get('title', detail.title)
                # detail.delivery_time_in_days = single_detail.get(
                #     'delivery_time_in_days', detail.delivery_time_in_days
                # )
                # detail.price = single_detail.get('price', detail.price)
                # detail.features = single_detail.get('features', detail.features)
                detail.revisions += 1
                detail.save()

        # Update Offer
        for field in ['title', 'image', 'description']:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        # instance.title = validated_data.get('title', instance.title)
        # instance.image = validated_data.get('image', instance.image)
        # instance.description = validated_data.get('description', instance.description)
        instance.save()

        return instance

