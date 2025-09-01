
from django.urls import path
from .views import ProfileListView, ProfileDetailView, RegistrationView, LoginView

urlpatterns = [
    path('profile/', ProfileListView.as_view(), name="profile-list"),
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name="profile-detail"),
    path('registration/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name="login")
]
