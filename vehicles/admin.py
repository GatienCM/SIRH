from django.contrib import admin
from django.utils.html import format_html
from .models import Vehicle


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    """Admin pour les véhicules"""
    
    list_display = [
        'vehicle_id',
        'registration_number',
        'vehicle_type',
        'brand_model',
        'status_badge',
        'current_mileage',
        'is_available'
    ]
    
    list_filter = [
        'vehicle_type',
        'status',
        'brand',
        'year',
        'entry_date',
        'created_at'
    ]
    
    search_fields = [
        'vehicle_id',
        'registration_number',
        'brand',
        'model',
        'insurance_policy_number'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'age_years',
        'total_mileage',
        'is_maintenance_needed',
        'is_inspection_needed',
        'is_insurance_valid'
    ]
    
    fieldsets = (
        ('Identification', {
            'fields': ('vehicle_id', 'registration_number')
        }),
        ('Type et caractéristiques', {
            'fields': (
                'vehicle_type',
                'brand',
                'model',
                'year',
                'color',
                'age_years'
            )
        }),
        ('Capacités', {
            'fields': ('seats_count', 'stretcher_capacity')
        }),
        ('Kilométrage', {
            'fields': ('initial_mileage', 'current_mileage', 'total_mileage')
        }),
        ('Motorisation', {
            'fields': ('fuel_type', 'consumption_per_100km')
        }),
        ('Dates', {
            'fields': ('purchase_date', 'entry_date', 'exit_date')
        }),
        ('Statut', {
            'fields': ('status',)
        }),
        ('Maintenance', {
            'fields': (
                'last_maintenance_date',
                'next_maintenance_date',
                'is_maintenance_needed'
            ),
            'classes': ('collapse',)
        }),
        ('Contrôle technique', {
            'fields': (
                'last_inspection_date',
                'next_inspection_date',
                'is_inspection_needed'
            ),
            'classes': ('collapse',)
        }),
        ('Assurance', {
            'fields': (
                'insurance_policy_number',
                'insurance_expiry_date',
                'is_insurance_valid'
            ),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def brand_model(self, obj):
        return f'{obj.brand} {obj.model}'
    brand_model.short_description = 'Marque et modèle'
    
    def status_badge(self, obj):
        """Affiche le statut avec une couleur"""
        colors = {
            'available': 'green',
            'maintenance': 'orange',
            'out_of_service': 'red',
            'retired': 'gray',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Statut'
    
    def is_available(self, obj):
        return obj.is_available
    is_available.boolean = True
    is_available.short_description = 'Disponible'
