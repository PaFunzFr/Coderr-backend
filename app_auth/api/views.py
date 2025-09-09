from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS, IsAdminUser
from rest_framework.authtoken.models import Token

from drf_spectacular.utils import extend_schema, OpenApiResponse

from app_auth.models import UserProfile
from .serializers import (
    UserDetailSerializer,
    RegistrationSerializer,
    LoginSerializer,
    BusinessSerializer,
    CustomerSerializer,
    RegistrationOrLoginResponseSerializer
)
from .permissions import IsProfileOwnerOrAdmin

@extend_schema(
    description="List all user profiles. Admin-only endpoint.",
    responses=UserDetailSerializer
)
class ProfileListView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAdminUser]


@extend_schema(
    description="List all business profiles. Authenticated users only.",
    responses=BusinessSerializer
)
class BusinessListView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(type="business")


@extend_schema(
    description="List all customer profiles. Authenticated users only.",
    responses=CustomerSerializer
)
class CustomerListView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(type="customer")


@extend_schema(
    description="Retrieve or update a user profile. Only the profile owner or admin can update.",
    responses=UserDetailSerializer
)
class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated, IsProfileOwnerOrAdmin]

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        return [IsProfileOwnerOrAdmin()]


@extend_schema(
    description="Login endpoint. Returns authentication token along with user info.",
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(
            response=RegistrationOrLoginResponseSerializer,
            description="Successfully logged in. Returns token, username, email, and user ID."
        ),
        400: OpenApiResponse(description="Invalid username or password.")
    }
)
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

@extend_schema(
    description="Register a new user. Returns authentication token and user info upon success.",
    request=RegistrationSerializer,
    responses={
        201: OpenApiResponse(
            response=RegistrationOrLoginResponseSerializer,
            description="User successfully created. Returns token, username, email, and user ID."
        ),
        400: OpenApiResponse(description="Invalid input data or validation errors.")
    }
)
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