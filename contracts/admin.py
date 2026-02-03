from django.contrib import admin
from django.utils.html import format_html
from .models import Contract


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    """Admin pour les contrats"""
    
    list_display = [
        'contract_number',
        'employee_name',
        'contract_type',
        'status_badge',
        'start_date',
        'end_date',
        'is_trial_period_display',
        'occupational_health_service',
    ]
    
    list_filter = [
        'contract_type',
        'status',
        'contract_status',
        'start_date',
        'created_at'
    ]
    
    search_fields = [
        'contract_number',
        'employee__employee_id',
        'employee__user__first_name',
        'employee__user__last_name'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'duration_days',
        'days_remaining',
        'is_active',
        'is_trial_period_display'
    ]
    
    fieldsets = (
        ('Identification', {
            'fields': ('employee', 'contract_number', 'contract_file')
        }),
        ('Type et statut', {
            'fields': ('contract_type', 'status', 'contract_status')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'trial_end_date')
        }),
        ('Conditions de travail', {
            'fields': (
                'working_hours_per_week',
                'hourly_rate',
                'monthly_salary'
            )
        }),
        ('Médecine du travail', {
            'fields': ('occupational_health_service',)
        }),
        ('Convention collective', {
            'fields': ('collective_agreement', 'collective_agreement_date')
        }),
        ('Informations supplémentaires', {
            'fields': ('notes',)
        }),
        ('Propriétés calculées', {
            'fields': (
                'is_active',
                'is_trial_period_display',
                'duration_days',
                'days_remaining'
            ),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def employee_name(self, obj):
        return obj.employee.user.get_full_name()
    employee_name.short_description = 'Salarié'
    
    def status_badge(self, obj):
        """Affiche le statut avec une couleur"""
        colors = {
            'active': 'green',
            'suspended': 'orange',
            'terminated': 'red',
            'expired': 'gray',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    def is_trial_period_display(self, obj):
        return obj.is_trial_period
    is_trial_period_display.boolean = True
    is_trial_period_display.short_description = 'En période d\'essai'
