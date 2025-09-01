
from django.urls import path
from .views import ProfileListView, ProfileDetailView, RegistrationView

urlpatterns = [
    path('profiles/', ProfileListView.as_view(), name="list-view"),
    path('profiles/<int:pk>/', ProfileDetailView.as_view(), name="profile-detail"),
    path('registration/', RegistrationView.as_view(), name='register'),
]
