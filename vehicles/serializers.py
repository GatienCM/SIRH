from rest_framework import serializers
from .models import Vehicle


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer pour les véhicules"""
    
    age_years = serializers.SerializerMethodField()
    total_mileage = serializers.SerializerMethodField()
    is_maintenance_needed = serializers.SerializerMethodField()
    is_inspection_needed = serializers.SerializerMethodField()
    is_insurance_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehicle
        fields = [
            'id',
            'vehicle_id',
            'registration_number',
            'vehicle_type',
            'brand',
            'model',
            'year',
            'color',
            'seats_count',
            'stretcher_capacity',
            'initial_mileage',
            'current_mileage',
            'total_mileage',
            'fuel_type',
            'consumption_per_100km',
            'purchase_date',
            'entry_date',
            'exit_date',
            'status',
            'last_maintenance_date',
            'next_maintenance_date',
            'is_maintenance_needed',
            'last_inspection_date',
            'next_inspection_date',
            'is_inspection_needed',
            'insurance_policy_number',
            'insurance_expiry_date',
            'is_insurance_valid',
            'age_years',
            'notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'age_years',
            'total_mileage',
            'is_maintenance_needed',
            'is_inspection_needed',
            'is_insurance_valid'
        ]
    
    def get_age_years(self, obj):
        return obj.age_years
    
    def get_total_mileage(self, obj):
        return obj.total_mileage
    
    def get_is_maintenance_needed(self, obj):
        return obj.is_maintenance_needed
    
    def get_is_inspection_needed(self, obj):
        return obj.is_inspection_needed
    
    def get_is_insurance_valid(self, obj):
        return obj.is_insurance_valid
