from rest_framework import serializers
from app_offers.models import Offer, OfferDetail
from django.contrib.auth.models import User


class OfferDetailNestedReadSerializer(serializers.HyperlinkedModelSerializer):
    """
    Serializer for nested representation of OfferDetail in read-only mode.
    Provides only the 'id' and hyperlink to the OfferDetail.
    """
    class Meta:
        model = OfferDetail
        fields = ['id','url']
        extra_kwargs = {
            'url': {'view_name': 'offerdetails-detail', 'lookup_field': 'pk'}
        }

class OfferDetailNestedDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed nested OfferDetail.
    Includes fields needed when reading or updating offer details.
    'revisions' and 'offer' are read-only.
    """
    class Meta:
        model = OfferDetail
        fields = [
            'id',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type'
            ]
        read_only_fields = [
            #'revisions',
            'offer']

class UserDetailsNestedSerializer(serializers.ModelSerializer):
    """
    Serializer for nested user information.
    Includes first name, last name, and username.
    """
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username'
        ]

class OfferListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing offers with aggregated min_price and min_delivery_time.
    Includes nested details and user information.
    """
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    min_delivery_time = serializers.IntegerField(read_only=True)
    details = OfferDetailNestedReadSerializer(many=True)
    user_details = UserDetailsNestedSerializer(source="user", read_only=True)

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
            "min_delivery_time",
            'user_details'
        ]

class OfferCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating offers.
    Handles nested creation and update of OfferDetails.
    Enforces validation rules for details (must include 'basic', 'standard', 'premium').
    Read-only fields: id, user, created_at, updated_at, min_price, min_delivery_time.
    """
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
        """
        Validate the 'details' field when creating a new Offer.
        Ensures exactly 3 items are provided with offer_types: 'basic', 'standard', 'premium'.
        Skips validation on update (instance exists).
        """
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
        """
        Create a new Offer instance along with its nested OfferDetails.
        The current authenticated user is automatically set as the offer owner.
        """
        details_list = validated_data.pop('details')
        current_user = self.context['request'].user

        # Create offer
        new_offer = Offer.objects.create(user=current_user, **validated_data)

        # Create details
        for single_detail in details_list:
            OfferDetail.objects.create(offer=new_offer, **single_detail)

        return new_offer


    def update(self, instance, validated_data):
        """
        Update an existing Offer instance and its nested OfferDetails.
        - Only updates provided fields in the details and increments revisions.
        - Updates offer fields: title, image, description if present.
        """
        details_list = validated_data.pop('details', [])

        # Update Details
        for single_detail in details_list:
            offer_type_to_update = single_detail.get('offer_type')
            
            if offer_type_to_update:
                detail = instance.details.get(offer_type=offer_type_to_update)

                for field in ['title', 'delivery_time_in_days', 'price', 'features', 'revisions']:
                    if field in single_detail:
                        setattr(detail, field, single_detail[field])

                # detail.revisions += 1
                detail.save()

        # Update main Offer fields
        for field in ['title', 'image', 'description']:
            if field in validated_data:
                setattr(instance, field, validated_data[field])

        instance.save()

        return instance

