from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Admin pour les utilisateurs personnalisés"""
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Rôle SIRH', {'fields': ('role',)}),
        ('Dates importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    list_display = ['username', 'get_full_name', 'email', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser', 'created_at']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'phone']
    ordering = ['-created_at']
    readonly_fields = ['last_login', 'date_joined', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
    get_full_name.short_description = 'Nom complet'
