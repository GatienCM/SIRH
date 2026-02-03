from rest_framework import serializers
from .models import Contract
from employees.serializers import EmployeeSerializer


class ContractSerializer(serializers.ModelSerializer):
    """Serializer pour les contrats"""
    
    employee_detail = EmployeeSerializer(source='employee', read_only=True)
    is_trial_period = serializers.SerializerMethodField()
    duration_days = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = Contract
        fields = [
            'id',
            'employee',
            'employee_detail',
            'contract_number',
            'contract_type',
            'status',
            'contract_status',
            'start_date',
            'end_date',
            'trial_end_date',
            'working_hours_per_week',
            'hourly_rate',
            'monthly_salary',
            'collective_agreement',
            'is_trial_period',
            'duration_days',
            'days_remaining',
            'notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'is_trial_period',
            'duration_days',
            'days_remaining'
        ]
    
    def get_is_trial_period(self, obj):
        return obj.is_trial_period
    
    def get_duration_days(self, obj):
        return obj.duration_days
    
    def get_days_remaining(self, obj):
        return obj.days_remaining
