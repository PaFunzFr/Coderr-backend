from rest_framework import serializers
from django.contrib.auth import authenticate
from app_auth.models import UserProfile
from django.contrib.auth.models import User
from app_auth.models import UserProfile, USER_TYPES

MAX_FILE_SIZE = 2 * 1024 * 1024

class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=USER_TYPES, write_only=True)

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

class BusinessSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    file = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile 
        fields = [
            'id',
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
            #return obj.file.name.split('/')[-1]  # only show filename
        return None

class CustomerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    file = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile 
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'file',
            'type'
        ]
        read_only_fields = ['type']

    def get_file(self, obj):
        if obj.file:
            #return obj.file.name.split('/')[-1]  # only show filename
            return obj.file.url
        return None

class UserDetailSerializer(serializers.HyperlinkedModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    email = serializers.EmailField(source='user.email')
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    file = serializers.ImageField(required=False)

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
        """Override representation to show only filename for `file`."""
        return_value = super().to_representation(instance)
        if instance.file:
            return_value['file'] = instance.file.url.lstrip('/')
            #return_value['file'] = instance.file.name.split('/')[-1]
        else:
            return_value['file'] = None
        return return_value


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