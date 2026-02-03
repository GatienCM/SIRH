from rest_framework import serializers
from .models import Profession, Employee
from accounts.serializers import CustomUserSerializer


class ProfessionSerializer(serializers.ModelSerializer):
    """Serializer pour les professions"""
    
    class Meta:
        model = Profession
        fields = ['id', 'code', 'label', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer pour les salariés"""
    
    user = CustomUserSerializer(read_only=True)
    profession_detail = ProfessionSerializer(source='profession', read_only=True)
    age = serializers.SerializerMethodField()
    years_of_service = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id',
            'employee_id',
            'user',
            'birth_date',
            'birth_place',
            'nationality',
            'address',
            'postal_code',
            'city',
            'country',
            'phone',
            'emergency_contact',
            'emergency_phone',
            'social_security_number',
            'rib',
            'profession',
            'profession_detail',
            'qualification',
            'status',
            'date_entry',
            'date_exit',
            'age',
            'years_of_service',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'age', 'years_of_service']
    
    def get_age(self, obj):
        return obj.age
    
    def get_years_of_service(self, obj):
        return round(obj.years_of_service, 2)
