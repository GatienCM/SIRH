from django.contrib import admin
from .models import LeaveRequest, TimeOffBalance, Document, Notification


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'days_requested', 'status', 'created_at']
    list_filter = ['status', 'leave_type', 'start_date', 'created_at']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'reason']
    readonly_fields = ['approved_by', 'approved_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('employee', 'leave_type', 'start_date', 'end_date', 'days_requested', 'reason')
        }),
        ('Statut', {
            'fields': ('status', 'approved_by', 'approved_at', 'rejection_reason')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TimeOffBalance)
class TimeOffBalanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'year', 'vacation_days_total', 'vacation_days_taken', 'vacation_days_remaining']
    list_filter = ['year', 'created_at']
    search_fields = ['employee__user__first_name', 'employee__user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('employee', 'year')
        }),
        ('Congés payés', {
            'fields': ('vacation_days_total', 'vacation_days_taken')
        }),
        ('Autres absences', {
            'fields': ('sick_days_taken', 'other_days_taken')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'employee', 'document_type', 'uploaded_by', 'is_confidential', 'created_at']
    list_filter = ['document_type', 'is_confidential', 'created_at']
    search_fields = ['title', 'employee__user__first_name', 'employee__user__last_name', 'description']
    readonly_fields = ['uploaded_by', 'created_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('employee', 'document_type', 'title', 'description', 'file')
        }),
        ('Sécurité', {
            'fields': ('is_confidential', 'uploaded_by')
        }),
        ('Audit', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'employee', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'employee__user__first_name', 'employee__user__last_name']
    readonly_fields = ['read_at', 'created_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('employee', 'notification_type', 'title', 'message')
        }),
        ('Statut', {
            'fields': ('is_read', 'read_at')
        }),
        ('Audit', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
