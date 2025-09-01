from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken

from app_auth.models import UserProfile
from .serializers import UserDetailSerializer, RegistrationSerializer, LoginSerializer, BusinessSerializer, CustomerSerializer

class ProfileListView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserDetailSerializer

class BusinessListView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = BusinessSerializer

    def get_queryset(self):
        return UserProfile.objects.filter(type="business")
    
class CustomerListView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = CustomerSerializer

    def get_queryset(self):
        return UserProfile.objects.filter(type="customer")

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserDetailSerializer

    # def get_serializer_class(self):
    #     obj = self.get_object()
    #     if obj.type == 'business':
    #         return BusinessSerializer
    #     else:
    #         return CustomerSerializer

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.id
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            data = {
                'token':token.key,
                'username': saved_account.username,
                'email':saved_account.email,
                'user_id': saved_account.pk
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)