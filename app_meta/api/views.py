from rest_framework.views import APIView
from django.db.models import Avg
from rest_framework.response import Response

from app_reviews.models import Review
from app_auth.models import UserProfile
from app_offers.models import Offer
from .serializers import BaseInfoSerializer

class BaseInfoView(APIView):
    def get(self, request):
        average_rating =  Review.objects.aggregate(average=Avg('rating'))['average']
        serializer = BaseInfoSerializer({
            'review_count' : Review.objects.count(),
            'average_rating': average_rating,
            'business_profile_count': UserProfile.objects.filter(type='business').count(),
            'offer_count': Offer.objects.count()
            })
        
        return Response(serializer.data)