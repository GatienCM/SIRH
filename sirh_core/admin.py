from django.contrib import admin
from .models import AuditLog, SystemSetting


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'object_repr', 'timestamp', 'ip_address']
    list_filter = ['action', 'timestamp', 'content_type']
    search_fields = ['user__username', 'user__email', 'object_repr', 'ip_address']
    readonly_fields = [
        'user', 'action', 'content_type', 'object_id', 'object_repr',
        'changes', 'ip_address', 'user_agent', 'timestamp'
    ]
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ['key', 'setting_type', 'is_sensitive', 'updated_at']
    list_filter = ['setting_type', 'is_sensitive']
    search_fields = ['key', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Paramètre', {
            'fields': ('key', 'value', 'setting_type', 'description')
        }),
        ('Sécurité', {
            'fields': ('is_sensitive',)
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
