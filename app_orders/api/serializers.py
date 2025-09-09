from rest_framework import serializers
from app_orders.models import Order
from app_offers.models import OfferDetail

class OrdersListCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for listing and creating orders.
    Includes nested fields from related OfferDetail and Offer.
    """

    # Fields OfferDetail
    title = serializers.CharField(source='offer_detail.title', read_only=True)
    revisions = serializers.IntegerField(source='offer_detail.revisions', read_only=True)
    delivery_time_in_days = serializers.IntegerField(source='offer_detail.delivery_time_in_days', read_only=True)
    price = serializers.DecimalField(source='offer_detail.price', max_digits=10, decimal_places=2, read_only=True)
    features = serializers.JSONField(source='offer_detail.features', read_only=True)
    offer_type = serializers.CharField(source='offer_detail.offer_type', read_only=True)
    
    # Fields Offer
    business_user = serializers.PrimaryKeyRelatedField(source='offer_detail.offer.user', read_only=True)

    offer_detail_id = serializers.PrimaryKeyRelatedField(
        queryset = OfferDetail.objects.all(),
        source='offer_detail',
        write_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at',
            'offer_detail_id'
        ]
        read_only_fields = [
            'customer_user',
            'status',
            'created_at',
            'updated_at'
        ]

    def create(self, validated_data):
        """
        Create a new Order for the current authenticated user.
        The OfferDetail is required in the request data.
        """
        current_user = self.context['request'].user
        offer_detail = validated_data["offer_detail"]

        new_order = Order.objects.create(
            customer_user=current_user,
            offer_detail=offer_detail
        )
        return new_order

class OrderDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for updating or retrieving the status of an order.
    """
    class Meta:
        model = Order
        fields = ['status']
