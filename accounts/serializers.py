from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_confirm', 'phone_number', 'date_of_birth']
        
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    # Accept either username or email for login
    username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    password = serializers.CharField()
    
    def validate(self, attrs):
        # Determine identifier from either username or email
        identifier = attrs.get('username') or attrs.get('email')
        password = attrs.get('password')
        
        if identifier and password:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            user = None
            try:
                # Try by username
                user_obj = User.objects.get(username=identifier)
                if user_obj.check_password(password):
                    user = user_obj
            except User.DoesNotExist:
                try:
                    # Try by email
                    user_obj = User.objects.get(email=identifier)
                    if user_obj.check_password(password):
                        user = user_obj
                except User.DoesNotExist:
                    pass
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
        
        raise serializers.ValidationError('Username/email and password are required')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'notification_preferences', 'security_settings']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'phone_number', 'role', 'is_verified', 
                 'date_of_birth', 'address', 'created_at', 'profile']
        read_only_fields = ['id', 'role', 'is_verified', 'created_at']


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Invalid old password')
        return value
