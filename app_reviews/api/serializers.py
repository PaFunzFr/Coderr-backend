from rest_framework import serializers

from app_reviews.models import Review

class ReviewListCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at"
        ]
        read_only_fields = [
            "id",
            "reviewer",
            "created_at",
            "updated_at"
        ]
    
    def validate(self, attrs):
        request = self.context.get("request")
        if request and request.method != "POST":
            return attrs

        current_user = self.context["request"].user
        business_user = attrs["business_user"]

        if business_user.profile.type != "business":
            raise serializers.ValidationError("Selected user is not a business.")
        
        if Review.objects.filter(reviewer=current_user, business_user=business_user).exists():
            raise serializers.ValidationError("You have already reviewed this business.")

        return attrs
        

    def create(self, validated_data):
        validated_data["reviewer"] = self.context["request"].user
        return Review.objects.create(**validated_data)
    


class ReviewUpdateDeleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = [
            "rating",
            "description",
        ]