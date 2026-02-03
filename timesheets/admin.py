from django.contrib import admin
from .models import TimeSheet, TimeSheetEntry, AbsenceRecord


@admin.register(TimeSheet)
class TimeSheetAdmin(admin.ModelAdmin):
    """Admin pour TimeSheet"""
    
    list_display = ['employee', 'year', 'month', 'status', 'total_hours', 'submitted_at']
    list_filter = ['status', 'year', 'month', 'created_at']
    search_fields = ['employee__user__first_name', 'employee__user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'submitted_at', 'approved_at', 'total_hours']
    fieldsets = (
        ('Informations', {
            'fields': ('employee', 'year', 'month', 'status')
        }),
        ('Totaux', {
            'fields': ('total_hours',),
            'classes': ('collapse',)
        }),
        ('Approbation', {
            'fields': ('approved_by', 'approved_at', 'submitted_at'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TimeSheetEntry)
class TimeSheetEntryAdmin(admin.ModelAdmin):
    """Admin pour TimeSheetEntry"""
    
    list_display = ['timesheet', 'date', 'hour_type', 'hours_worked', 'amount']
    list_filter = ['hour_type', 'date', 'created_at']
    search_fields = ['timesheet__employee__user__first_name', 'timesheet__employee__user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'amount']
    fieldsets = (
        ('Feuille de temps', {
            'fields': ('timesheet', 'assignment')
        }),
        ('Détails', {
            'fields': ('date', 'hour_type', 'hours_worked', 'hourly_rate', 'amount')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AbsenceRecord)
class AbsenceRecordAdmin(admin.ModelAdmin):
    """Admin pour AbsenceRecord"""
    
    list_display = ['employee', 'absence_type', 'date_start', 'date_end', 'duration_days']
    list_filter = ['absence_type', 'date_start', 'created_at']
    search_fields = ['employee__user__first_name', 'employee__user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'duration_days']
    fieldsets = (
        ('Informations', {
            'fields': ('employee', 'absence_type')
        }),
        ('Dates', {
            'fields': ('date_start', 'date_end', 'duration_days')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
