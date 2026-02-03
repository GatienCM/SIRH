from rest_framework import serializers
from .models import AuditLog, SystemSetting
from accounts.serializers import CustomUserSerializer


class AuditLogSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    labels = {
        'id': 'ID',
        'user': 'Utilisateur',
        'action': 'Action',
        'action_display': 'Action',
        'content_type': 'Type de contenu',
        'object_id': 'ID de l\'objet',
        'object_repr': 'Représentation',
        'changes': 'Modifications',
        'ip_address': 'Adresse IP',
        'user_agent': 'User Agent',
        'timestamp': 'Horodatage',
    }
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'action', 'action_display',
            'content_type', 'object_id', 'object_repr',
            'changes', 'ip_address', 'user_agent', 'timestamp'
        ]
        read_only_fields = fields


class SystemSettingSerializer(serializers.ModelSerializer):
    labels = {
        'id': 'ID',
        'key': 'Clé',
        'value': 'Valeur',
        'setting_type': 'Type',
        'description': 'Description',
        'is_sensitive': 'Sensible',
        'created_at': 'Créé le',
        'updated_at': 'Mis à jour le',
    }
    
    class Meta:
        model = SystemSetting
        fields = [
            'id', 'key', 'value', 'setting_type',
            'description', 'is_sensitive', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def to_representation(self, instance):
        """Masquer les valeurs sensibles"""
        data = super().to_representation(instance)
        if instance.is_sensitive:
            data['value'] = '***'
        return data
