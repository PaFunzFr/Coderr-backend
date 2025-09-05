from rest_framework import serializers

class BaseInfoSerializer(serializers.Serializer):
    review_count = serializers.IntegerField(read_only=True)
    average_rating = serializers.DecimalField(read_only=True, max_digits=2, decimal_places=1)
    business_profile_count = serializers.IntegerField(read_only=True)
    offer_count = serializers.IntegerField(read_only=True)