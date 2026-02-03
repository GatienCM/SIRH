from rest_framework import serializers
from .models import SalaryScale, Payroll, PayrollItem
from employees.serializers import EmployeeSerializer


class SalaryScaleSerializer(serializers.ModelSerializer):
    labels = {
        'id': 'ID',
        'name': 'Nom de la grille',
        'level': 'Niveau',
        'base_rate': 'Taux horaire de base (€)',
        'night_multiplier': 'Multiplicateur nuit',
        'sunday_multiplier': 'Multiplicateur dimanche',
        'holiday_multiplier': 'Multiplicateur férié',
        'overtime_multiplier': 'Multiplicateur heures supplémentaires',
        'created_at': 'Créé le',
        'updated_at': 'Mis à jour le',
    }
    
    class Meta:
        model = SalaryScale
        fields = [
            'id', 'name', 'level', 'base_rate',
            'night_multiplier', 'sunday_multiplier',
            'holiday_multiplier', 'overtime_multiplier',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class PayrollItemSerializer(serializers.ModelSerializer):
    labels = {
        'id': 'ID',
        'payroll': 'Fiche de paie',
        'item_type': 'Type',
        'description': 'Description',
        'amount': 'Montant',
        'created_at': 'Créé le',
    }
    
    class Meta:
        model = PayrollItem
        fields = ['id', 'payroll', 'item_type', 'description', 'amount', 'created_at']
        read_only_fields = ['created_at']


class PayrollSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.IntegerField(write_only=True)
    items = PayrollItemSerializer(many=True, read_only=True)
    
    labels = {
        'id': 'ID',
        'employee': 'Employé',
        'employee_id': 'ID Employé',
        'period': 'Période (YYYY-MM)',
        'year': 'Année',
        'month': 'Mois',
        'status': 'Statut',
        'total_hours': 'Total heures',
        'normal_hours': 'Heures normales',
        'night_hours': 'Heures de nuit',
        'sunday_hours': 'Heures dimanche',
        'holiday_hours': 'Heures féries',
        'overtime_hours': 'Heures supplémentaires',
        'gross_salary': 'Salaire brut',
        'normal_salary': 'Salaire normal',
        'night_salary': 'Salaire nuit',
        'sunday_salary': 'Salaire dimanche',
        'holiday_salary': 'Salaire féries',
        'overtime_salary': 'Salaire heures supplémentaires',
        'total_deductions': 'Total déductions',
        'social_security': 'Cotisations sociales',
        'taxes': 'Impôts',
        'other_deductions': 'Autres déductions',
        'net_salary': 'Salaire net',
        'calculated_at': 'Calculée le',
        'validated_at': 'Validée le',
        'validated_by': 'Validée par',
        'paid_at': 'Payée le',
        'created_at': 'Créé le',
        'updated_at': 'Mis à jour le',
        'notes': 'Notes',
        'items': 'Éléments de paie',
    }
    
    class Meta:
        model = Payroll
        fields = [
            'id', 'employee', 'employee_id', 'period', 'year', 'month', 'status',
            'total_hours', 'normal_hours', 'night_hours', 'sunday_hours',
            'holiday_hours', 'overtime_hours', 'gross_salary', 'normal_salary',
            'night_salary', 'sunday_salary', 'holiday_salary', 'overtime_salary',
            'total_deductions', 'social_security', 'taxes', 'other_deductions',
            'net_salary', 'calculated_at', 'validated_at', 'validated_by',
            'paid_at', 'created_at', 'updated_at', 'notes', 'items'
        ]
        read_only_fields = [
            'calculated_at', 'validated_at', 'validated_by', 'paid_at',
            'created_at', 'updated_at', 'gross_salary', 'net_salary',
            'normal_salary', 'night_salary', 'sunday_salary',
            'holiday_salary', 'overtime_salary', 'total_deductions'
        ]
