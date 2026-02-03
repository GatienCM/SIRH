from django.contrib import admin
from .models import ShiftType, Shift, Assignment


@admin.register(ShiftType)
class ShiftTypeAdmin(admin.ModelAdmin):
    """Admin pour ShiftType"""
    
    list_display = ['name', 'start_hour', 'end_hour', 'base_hours', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    fieldsets = (
        ('Informations', {
            'fields': ('name', 'description')
        }),
        ('Horaires', {
            'fields': ('start_hour', 'end_hour', 'base_hours')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    """Admin pour Shift"""
    
    list_display = ['date', 'shift_type', 'start_time', 'end_time', 'status', 'duration_hours']
    list_filter = ['date', 'status', 'shift_type', 'created_at']
    search_fields = ['notes']
    readonly_fields = ['created_at', 'updated_at', 'duration_hours']
    fieldsets = (
        ('Informations', {
            'fields': ('shift_type', 'date', 'status')
        }),
        ('Horaires', {
            'fields': ('start_time', 'end_time', 'duration_hours')
        }),
        ('Notes', {
            'fields': ('notes', 'created_by')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Enregistrer le créateur"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    """Admin pour Assignment"""
    
    list_display = ['shift', 'employee', 'vehicle', 'status', 'is_confirmed']
    list_filter = ['status', 'shift__date', 'confirmed_at', 'created_at']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'notes']
    readonly_fields = ['created_at', 'updated_at', 'confirmed_at', 'is_confirmed']
    fieldsets = (
        ('Assignment', {
            'fields': ('shift', 'employee', 'vehicle')
        }),
        ('Statut', {
            'fields': ('status', 'is_confirmed', 'confirmed_at')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
