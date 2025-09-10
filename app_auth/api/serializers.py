from rest_framework import serializers
from django.contrib.auth import authenticate
from app_auth.models import UserProfile
from django.contrib.auth.models import User
from app_auth.models import UserProfile, USER_TYPES

MAX_FILE_SIZE = 2 * 1024 * 1024


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.

    Handles creation of a User and associated UserProfile. 
    Validates that passwords match and that the email is unique.
    """
    repeated_password = serializers.CharField(
        write_only=True,
        help_text="Repeat the password for confirmation."
    )
    type = serializers.ChoiceField(
        choices=USER_TYPES, 
        write_only=True,
        help_text="Select the type of user: 'business' or 'customer'."
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'repeated_password',
            'type'
        ]
        extra_kwargs = {
            'password': {'write_only': True}, # password write-only
            'username': {'write_only': True},
        }

    def validate_email(self, value):
        """Ensure email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def validate(self, data):
        """Ensure passwords match."""
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        profile_type = validated_data.pop('type')

        user = User(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()

        UserProfile.objects.create(user=user, type=profile_type)

        return user


class BusinessSerializer(serializers.ModelSerializer):
    """
    Serializer for business user profiles.

    Returns user info (username, first_name, last_name) and profile details.
    """
    username = serializers.CharField(
        source="user.username",
        read_only=True,
        help_text="User's username"
    )
    first_name = serializers.CharField(
        source='user.first_name',
        read_only=True,
        help_text="User's first name"
    )
    last_name = serializers.CharField(
        source='user.last_name',
        read_only=True,
        help_text="User's last name"
    )
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    file = serializers.SerializerMethodField(help_text="URL to the profile picture")

    class Meta:
        model = UserProfile 
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file', 
            'location',
            'tel',
            'description',
            'working_hours',
            'type'
        ]
        read_only_fields = ['type']

    def get_file(self, obj):
        if obj.file:
            return obj.file.url
        return None

class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer for customer user profiles.

    Returns user info (username, first_name, last_name) and profile ID.
    """
    username = serializers.CharField(
        source="user.username",
        read_only=True,
        help_text="User's username"
    )
    first_name = serializers.CharField(
        source='user.first_name',
        read_only=True,
        help_text="User's first name"
    )
    last_name = serializers.CharField(
        source='user.last_name',
        read_only=True,
        help_text="User's last name"
    )
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    file = serializers.SerializerMethodField(help_text="URL to the profile picture")

    class Meta:
        model = UserProfile 
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'type'
        ]
        read_only_fields = ['type']

    def get_file(self, obj):
        if obj.file:
            return obj.file.url
        return None

class UserDetailSerializer(serializers.HyperlinkedModelSerializer):
    """
    Detailed serializer for user profiles.

    Includes user info (username, first_name, last_name, email) and profile fields.
    Supports updating user info and profile picture.
    """
    username = serializers.CharField(
        source="user.username",
        read_only=True,
        help_text="User's username"
    )
    first_name = serializers.CharField(
        source='user.first_name',
        required=False,
        help_text="User's first name"
    )
    last_name = serializers.CharField(
        source='user.last_name',
        required=False,
        help_text="User's last name"
    )
    email = serializers.EmailField(source='user.email', help_text="User email address")
    user = serializers.PrimaryKeyRelatedField(read_only=True, help_text="User ID")
    file = serializers.ImageField(required=False, help_text="Profile picture URL")

    class Meta:
        model = UserProfile 
        fields = [
            'user',
            'url',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
            'email',
            'created_at'
        ]
        read_only_fields = ['type']

    def validate_file(self, value):
        if value.size > MAX_FILE_SIZE:
            raise serializers.ValidationError("Image file too large (max 2MB)")
        return value
        
    def update(self, instance, validated_data):
        """
        Update user and profile information.

        Handles updating user fields, profile fields, and file upload.
        """

        # upload image:
        file = validated_data.pop('file', None)
        if file:
            instance.file = file
        
        # get all User-Data & Update User
        user_data = validated_data.pop('user', {})
        if user_data:
            user = instance.user
            user.first_name = user_data.get('first_name', instance.user.first_name)
            user.last_name = user_data.get('last_name', instance.user.last_name)
            user.email = user_data.get('email', instance.user.email)
            user.save()

        # Update Profile
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
    
    def to_representation(self, instance):
        """Override representation to show correct path to `file` ( 1x / less )."""
        return_value = super().to_representation(instance)
        if instance.file:
            return_value['file'] = instance.file.url.lstrip('/')
        else:
            return_value['file'] = None
        return return_value


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.

    Validates username and password, authenticates user.
    """
    username = serializers.CharField(write_only=True, help_text="Username for Login")
    password = serializers.CharField(write_only=True, help_text="Password for Login")

    def validate(self, data):
        """Authenticate user credentials."""
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError("Invalid email or password")
            
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled")
            
            data['user'] = user  # Authenticated user
            return data
        else:
            raise serializers.ValidationError("Must include email and password")
        

class RegistrationOrLoginResponseSerializer(serializers.Serializer):
    """
    Serializer for responses after registration or login. Only used for api/schema/swagger-ui/

    Returns authentication token and basic user info.
    """
    token = serializers.CharField(help_text="Authentication token")
    username = serializers.CharField(help_text="Username of the logged-in user")
    email = serializers.EmailField(help_text="Email of the logged-in user")
    user_id = serializers.IntegerField(help_text="ID of the logged-in user")