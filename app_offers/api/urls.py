from django.urls import path
from .views import OffersListCreateView, OfferDetailView


urlpatterns = [
    path('', OffersListCreateView.as_view(), name="offers-list"),
    path('<int:pk>/', OfferDetailView.as_view(), name="offer-detail"),
]