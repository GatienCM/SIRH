from rest_framework import serializers
from .models import LeaveRequest, TimeOffBalance, Document, Notification
from employees.serializers import EmployeeSerializer


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.IntegerField(write_only=True, required=False)
    approved_by = EmployeeSerializer(read_only=True)
    
    labels = {
        'id': 'ID',
        'employee': 'Employé',
        'employee_id': 'ID Employé',
        'leave_type': 'Type de congé',
        'start_date': 'Date de début',
        'end_date': 'Date de fin',
        'days_requested': 'Nombre de jours',
        'reason': 'Motif',
        'status': 'Statut',
        'approved_by': 'Approuvé par',
        'approved_at': 'Approuvé le',
        'rejection_reason': 'Motif de refus',
        'created_at': 'Créé le',
        'updated_at': 'Mis à jour le',
    }
    
    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee', 'employee_id', 'leave_type',
            'start_date', 'end_date', 'days_requested', 'reason',
            'status', 'approved_by', 'approved_at', 'rejection_reason',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'approved_by', 'approved_at', 'created_at', 'updated_at'
        ]
    
    def validate(self, data):
        """Valider que la date de fin est après la date de début"""
        if 'start_date' in data and 'end_date' in data:
            if data['end_date'] < data['start_date']:
                raise serializers.ValidationError(
                    "La date de fin doit être après la date de début"
                )
        return data


class TimeOffBalanceSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.IntegerField(write_only=True)
    vacation_days_remaining = serializers.DecimalField(
        max_digits=5,
        decimal_places=1,
        read_only=True
    )
    
    labels = {
        'id': 'ID',
        'employee': 'Employé',
        'employee_id': 'ID Employé',
        'year': 'Année',
        'vacation_days_total': 'Total congés payés',
        'vacation_days_taken': 'Congés payés pris',
        'vacation_days_remaining': 'Congés payés restants',
        'sick_days_taken': 'Jours maladie pris',
        'other_days_taken': 'Autres jours pris',
        'created_at': 'Créé le',
        'updated_at': 'Mis à jour le',
    }
    
    class Meta:
        model = TimeOffBalance
        fields = [
            'id', 'employee', 'employee_id', 'year',
            'vacation_days_total', 'vacation_days_taken',
            'vacation_days_remaining', 'sick_days_taken',
            'other_days_taken', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'vacation_days_remaining']


class DocumentSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.IntegerField(write_only=True, required=False)
    uploaded_by = EmployeeSerializer(read_only=True)
    
    labels = {
        'id': 'ID',
        'employee': 'Employé',
        'employee_id': 'ID Employé',
        'document_type': 'Type de document',
        'title': 'Titre',
        'description': 'Description',
        'file': 'Fichier',
        'uploaded_by': 'Téléchargé par',
        'is_confidential': 'Confidentiel',
        'created_at': 'Créé le',
    }
    
    class Meta:
        model = Document
        fields = [
            'id', 'employee', 'employee_id', 'document_type',
            'title', 'description', 'file', 'uploaded_by',
            'is_confidential', 'created_at'
        ]
        read_only_fields = ['uploaded_by', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.IntegerField(write_only=True, required=False)
    
    labels = {
        'id': 'ID',
        'employee': 'Employé',
        'employee_id': 'ID Employé',
        'notification_type': 'Type',
        'title': 'Titre',
        'message': 'Message',
        'is_read': 'Lu',
        'read_at': 'Lu le',
        'created_at': 'Créé le',
    }
    
    class Meta:
        model = Notification
        fields = [
            'id', 'employee', 'employee_id', 'notification_type',
            'title', 'message', 'is_read', 'read_at', 'created_at'
        ]
        read_only_fields = ['read_at', 'created_at']
