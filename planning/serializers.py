from rest_framework import serializers
from .models import ShiftType, Shift, Assignment
from employees.serializers import EmployeeSerializer
from vehicles.serializers import VehicleSerializer
from accounts.serializers import CustomUserSerializer


class ShiftTypeSerializer(serializers.ModelSerializer):
    """Serializer pour ShiftType"""
    
    class Meta:
        model = ShiftType
        fields = [
            'id',
            'name',
            'description',
            'start_hour',
            'end_hour',
            'base_hours',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ShiftSerializer(serializers.ModelSerializer):
    """Serializer pour Shift"""
    
    shift_type = ShiftTypeSerializer(read_only=True)
    shift_type_id = serializers.IntegerField(write_only=True)
    created_by = CustomUserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    duration_hours = serializers.SerializerMethodField(read_only=True)
    is_past = serializers.SerializerMethodField(read_only=True)
    is_ongoing = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Shift
        fields = [
            'id',
            'shift_type',
            'shift_type_id',
            'date',
            'start_time',
            'end_time',
            'status',
            'status_display',
            'notes',
            'created_by',
            'duration_hours',
            'is_past',
            'is_ongoing',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']
    
    def get_duration_hours(self, obj):
        """Calculer la durée en heures"""
        return obj.duration_hours
    
    def get_is_past(self, obj):
        """Vérifier si le shift est passé"""
        return obj.is_past
    
    def get_is_ongoing(self, obj):
        """Vérifier si le shift est en cours"""
        return obj.is_ongoing


class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer pour Assignment"""
    
    shift = ShiftSerializer(read_only=True)
    shift_id = serializers.IntegerField(write_only=True)
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.IntegerField(write_only=True)
    vehicle = VehicleSerializer(read_only=True)
    vehicle_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_confirmed = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Assignment
        fields = [
            'id',
            'shift',
            'shift_id',
            'employee',
            'employee_id',
            'vehicle',
            'vehicle_id',
            'status',
            'status_display',
            'notes',
            'confirmed_at',
            'is_confirmed',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'confirmed_at', 'created_at', 'updated_at']
    
    def get_is_confirmed(self, obj):
        """Vérifier si l'assignment est confirmé"""
        return obj.is_confirmed
    
    def create(self, validated_data):
        """Créer un assignment avec validation"""
        validated_data['shift_id'] = validated_data.pop('shift_id')
        validated_data['employee_id'] = validated_data.pop('employee_id')
        vehicle_id = validated_data.pop('vehicle_id', None)
        if vehicle_id:
            validated_data['vehicle_id'] = vehicle_id
        
        assignment = Assignment(**validated_data)
        assignment.full_clean()
        assignment.save()
        return assignment
