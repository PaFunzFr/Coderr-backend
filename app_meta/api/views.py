from rest_framework.views import APIView
from django.db.models import Avg
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from drf_spectacular.utils import extend_schema

from app_reviews.models import Review
from app_auth.models import UserProfile
from app_offers.models import Offer
from .serializers import BaseInfoSerializer

@extend_schema(
    description="Retrieve basic platform statistics, including total reviews, average rating, number of business profiles, and total offers.",
    responses=BaseInfoSerializer
)
class BaseInfoView(APIView):
    """Provide aggregated base information about the platform for dashboard or overview purposes."""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Return total counts and average rating for reviews, business profiles, and offers."""
        average_rating =  Review.objects.aggregate(average=Avg('rating'))['average']
        serializer = BaseInfoSerializer({
            'review_count' : Review.objects.count(),
            'average_rating': average_rating,
            'business_profile_count': UserProfile.objects.filter(type='business').count(),
            'offer_count': Offer.objects.count()
            })
        
        return Response(serializer.data)
