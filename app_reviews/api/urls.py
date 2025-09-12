
from django.urls import path
from app_reviews.api.views import ReviewListCreateView, ReviewUpdateDeleteView

urlpatterns = [
    path('', ReviewListCreateView.as_view(), name='review-list'),
    path('<int:pk>/', ReviewUpdateDeleteView.as_view(), name='review-detail')
]