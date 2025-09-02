from django.urls import path
from .views import OffersListCreateView, OfferDetailView, OfferDetailsDetailView


urlpatterns = [
    path('offers/', OffersListCreateView.as_view(), name="offers-list"),
    path('offers/<int:pk>/', OfferDetailView.as_view(), name="offer-detail"),
    path('offerdetails/<int:pk>/', OfferDetailsDetailView.as_view(), name="offerdetails-detail"),
]