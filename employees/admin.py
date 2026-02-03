from django.contrib import admin
from .models import Profession, Employee


@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    """Admin pour les professions"""
    
    list_display = ['label', 'code', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['label', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Identification', {
            'fields': ('code', 'label')
        }),
        ('Détails', {
            'fields': ('description', 'is_active')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin pour les salariés"""
    
    list_display = ['employee_id', 'user_full_name', 'profession', 'status', 'date_entry', 'is_active_employee']
    list_filter = ['status', 'profession', 'date_entry', 'created_at']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name', 'social_security_number', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'age', 'years_of_service']
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user', 'employee_id')
        }),
        ('Identité', {
            'fields': ('birth_date', 'birth_place', 'nationality', 'age')
        }),
        ('Adresse', {
            'fields': ('address', 'postal_code', 'city', 'country')
        }),
        ('Contact', {
            'fields': ('phone', 'emergency_contact', 'emergency_phone')
        }),
        ('Documents', {
            'fields': ('social_security_number', 'rib')
        }),
        ('Professionnel', {
            'fields': ('profession', 'qualification', 'years_of_service')
        }),
        ('Statut', {
            'fields': ('status', 'date_entry', 'date_exit')
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_full_name.short_description = 'Nom complet'
    
    def is_active_employee(self, obj):
        return obj.is_active_employee()
    is_active_employee.boolean = True
    is_active_employee.short_description = 'Actuellement actif'
