from django.contrib import admin
from .models import SalaryScale, Payroll, PayrollItem, PayrollVariable, PayrollContribution


@admin.register(PayrollVariable)
class PayrollVariableAdmin(admin.ModelAdmin):
    list_display = ['name', 'value', 'unit', 'is_active', 'updated_at']
    list_filter = ['is_active', 'updated_at']
    search_fields = ['name', 'description']
    readonly_fields = ['updated_at']


@admin.register(PayrollContribution)
class PayrollContributionAdmin(admin.ModelAdmin):
    list_display = ['name', 'rate', 'ceiling', 'is_active', 'updated_at']
    list_filter = ['is_active', 'updated_at']
    search_fields = ['name', 'description']
    readonly_fields = ['updated_at']


@admin.register(SalaryScale)
class SalaryScaleAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'base_rate', 'night_multiplier', 'sunday_multiplier']
    list_filter = ['level', 'created_at']
    search_fields = ['name', 'level']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'level', 'base_rate')
        }),
        ('Multiplicateurs', {
            'fields': ('night_multiplier', 'sunday_multiplier', 'holiday_multiplier', 'overtime_multiplier')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class PayrollItemInline(admin.TabularInline):
    model = PayrollItem
    extra = 0
    readonly_fields = ['created_at']
    fields = ['item_type', 'description', 'amount', 'created_at']


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['employee', 'period', 'status', 'gross_salary', 'net_salary', 'paid_at']
    list_filter = ['status', 'period', 'year', 'month', 'paid_at']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'period']
    readonly_fields = [
        'calculated_at', 'validated_at', 'paid_at', 'created_at', 'updated_at',
        'gross_salary', 'net_salary', 'normal_salary', 'night_salary',
        'sunday_salary', 'holiday_salary', 'overtime_salary', 'total_deductions'
    ]
    inlines = [PayrollItemInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('employee', 'period', 'year', 'month', 'status')
        }),
        ('Heures travaillées', {
            'fields': ('total_hours', 'normal_hours', 'night_hours', 'sunday_hours', 'holiday_hours', 'overtime_hours')
        }),
        ('Salaires bruts', {
            'fields': ('gross_salary', 'normal_salary', 'night_salary', 'sunday_salary', 'holiday_salary', 'overtime_salary')
        }),
        ('Déductions', {
            'fields': ('total_deductions', 'social_security', 'taxes', 'other_deductions')
        }),
        ('Salaire net', {
            'fields': ('net_salary',)
        }),
        ('Validation et paiement', {
            'fields': ('calculated_at', 'validated_at', 'validated_by', 'paid_at')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PayrollItem)
class PayrollItemAdmin(admin.ModelAdmin):
    list_display = ['payroll', 'item_type', 'description', 'amount']
    list_filter = ['item_type', 'payroll__period']
    search_fields = ['payroll__employee__user__first_name', 'payroll__employee__user__last_name', 'description']
    readonly_fields = ['created_at']

