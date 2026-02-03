from rest_framework import serializers
from .models import TimeSheet, TimeSheetEntry, AbsenceRecord
from employees.serializers import EmployeeSerializer
from planning.serializers import AssignmentSerializer
from accounts.serializers import CustomUserSerializer


class TimeSheetEntrySerializer(serializers.ModelSerializer):
    """Serializer pour TimeSheetEntry"""
    
    assignment = AssignmentSerializer(read_only=True)
    assignment_id = serializers.IntegerField(write_only=True, required=False, allow_null=True, label='Assignment ID')
    hour_type_display = serializers.CharField(source='get_hour_type_display', read_only=True, label='Type d\'heures (texte)')
    amount = serializers.SerializerMethodField(read_only=True, label='Montant')
    
    class Meta:
        model = TimeSheetEntry
        fields = [
            'id',
            'timesheet',
            'assignment',
            'assignment_id',
            'date',
            'hour_type',
            'hour_type_display',
            'hours_worked',
            'hourly_rate',
            'amount',
            'notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'timesheet', 'created_at', 'updated_at']
        labels = {
            'id': 'ID',
            'timesheet': 'Feuille de temps',
            'assignment': 'Assignment',
            'date': 'Date',
            'hour_type': 'Type d\'heures',
            'hours_worked': 'Heures travaillées',
            'hourly_rate': 'Taux horaire',
            'notes': 'Notes',
            'created_at': 'Créé le',
            'updated_at': 'Mis à jour le'
        }
    
    def get_amount(self, obj):
        """Calculer le montant"""
        return obj.amount


class TimeSheetSerializer(serializers.ModelSerializer):
    """Serializer pour TimeSheet"""
    
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.IntegerField(write_only=True, label='Employé ID')
    approved_by = CustomUserSerializer(read_only=True)
    entries = TimeSheetEntrySerializer(read_only=True, many=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True, label='Statut (texte)')
    total_hours = serializers.SerializerMethodField(read_only=True, label='Total heures')
    total_normal_hours = serializers.SerializerMethodField(read_only=True, label='Heures normales')
    total_night_hours = serializers.SerializerMethodField(read_only=True, label='Heures de nuit')
    total_sunday_hours = serializers.SerializerMethodField(read_only=True, label='Heures dimanche')
    total_holiday_hours = serializers.SerializerMethodField(read_only=True, label='Heures féries')
    total_overtime_hours = serializers.SerializerMethodField(read_only=True, label='Heures supplémentaires')
    is_submitted = serializers.SerializerMethodField(read_only=True, label='Est soumis')
    
    class Meta:
        model = TimeSheet
        fields = [
            'id',
            'employee',
            'employee_id',
            'year',
            'month',
            'status',
            'status_display',
            'entries',
            'total_hours',
            'total_normal_hours',
            'total_night_hours',
            'total_sunday_hours',
            'total_holiday_hours',
            'total_overtime_hours',
            'is_submitted',
            'notes',
            'submitted_at',
            'approved_at',
            'approved_by',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'approved_at', 'approved_by', 'submitted_at', 'created_at', 'updated_at', 'entries']
        labels = {
            'id': 'ID',
            'employee': 'Employé',
            'year': 'Année',
            'month': 'Mois',
            'status': 'Statut',
            'entries': 'Entrées',
            'notes': 'Notes',
            'submitted_at': 'Soumis le',
            'approved_at': 'Approuvé le',
            'approved_by': 'Approuvé par',
            'created_at': 'Créé le',
            'updated_at': 'Mis à jour le'
        }
    
    def get_total_hours(self, obj):
        return obj.total_hours
    
    def get_total_normal_hours(self, obj):
        return obj.total_normal_hours
    
    def get_total_night_hours(self, obj):
        return obj.total_night_hours
    
    def get_total_sunday_hours(self, obj):
        return obj.total_sunday_hours
    
    def get_total_holiday_hours(self, obj):
        return obj.total_holiday_hours
    
    def get_total_overtime_hours(self, obj):
        return obj.total_overtime_hours
    
    def get_is_submitted(self, obj):
        return obj.is_submitted


class AbsenceRecordSerializer(serializers.ModelSerializer):
    """Serializer pour AbsenceRecord"""
    
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.IntegerField(write_only=True, label='Employé ID')
    absence_type_display = serializers.CharField(source='get_absence_type_display', read_only=True, label='Type d\'absence (texte)')
    duration_days = serializers.SerializerMethodField(read_only=True, label='Durée (jours)')
    
    class Meta:
        model = AbsenceRecord
        fields = [
            'id',
            'employee',
            'employee_id',
            'date_start',
            'date_end',
            'duration_days',
            'absence_type',
            'absence_type_display',
            'notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        labels = {
            'id': 'ID',
            'employee': 'Employé',
            'date_start': 'Date de début',
            'date_end': 'Date de fin',
            'absence_type': 'Type d\'absence',
            'notes': 'Notes',
            'created_at': 'Créé le',
            'updated_at': 'Mis à jour le'
        }
    
    def get_duration_days(self, obj):
        return obj.duration_days
