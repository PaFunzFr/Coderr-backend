from rest_framework import serializers
from django.contrib.auth import authenticate
from app_auth.models import UserProfile
from django.contrib.auth.models import User
from app_auth.models import UserProfile, USER_TYPES


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=USER_TYPES, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'password': {'write_only': True}, # password write-only
            'username': {'write_only': True},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def validate(self, data):
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


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')

    file = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile 
        fields = ['id', 'username', 'type', 'first_name', 'last_name', 'email', 'file', 'location', 'tel',
                'description', 'working_hours', 'created_at']
        read_only_fields = ['type']

    def update(self, instance, validated_data):
        # get all User-Data & Update User
        user_data = validated_data.pop('user', {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()

        # Update Profile
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
    
    def get_file(self, obj):
        if obj.file:
            return obj.file.name.split('/')[-1]  # only show filename
        return None


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
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