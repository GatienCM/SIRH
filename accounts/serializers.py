from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer pour CustomUser"""
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'phone',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LoginSerializer(serializers.Serializer):
    """Serializer pour le login"""
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            raise serializers.ValidationError(
                'Vous devez fournir un nom d\'utilisateur et un mot de passe'
            )
        
        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError(
                'Identifiants invalides'
            )
        
        if not user.is_active:
            raise serializers.ValidationError(
                'Ce compte est désactivé'
            )
        
        data['user'] = user
        return data


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer pour l'enregistrement"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'password2',
            'phone'
        ]
    
    def validate(self, data):
        if data['password'] != data.pop('password2'):
            raise serializers.ValidationError({
                'password': 'Les mots de passe ne correspondent pas'
            })
        return data
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer pour changer le mot de passe"""
    
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password]
    )
    new_password2 = serializers.CharField(write_only=True)
    
    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({
                'new_password': 'Les mots de passe ne correspondent pas'
            })
        return data
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                'L\'ancien mot de passe est incorrect'
            )
        return value
