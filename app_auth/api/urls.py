
from django.urls import path
from .views import ProfileListView, ProfileDetailView, RegistrationView, LoginView, \
BusinessListView, CustomerListView


urlpatterns = [
    path('profile/', ProfileListView.as_view(), name="profile-list"),
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name="userprofile-detail"),
    path('profiles/business/', BusinessListView.as_view(), name='business-list'),
    path('profiles/customer/', CustomerListView.as_view(), name='customer-list'),
    path('registration/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name="login"),
]
