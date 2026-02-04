#!/usr/bin/env python
"""Script pour ajouter les types de quarts par défaut"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sirh_core.settings')
django.setup()

from planning.models import ShiftType
from datetime import time

# Liste des types de quarts à créer
shift_types_data = [
    {
        'name': 'day',
        'description': 'Quart de jour standard (8h-16h)',
        'start_hour': time(8, 0),
        'end_hour': time(16, 0),
        'base_hours': 8.0
    },
    {
        'name': 'night',
        'description': 'Quart de nuit (20h-6h)',
        'start_hour': time(20, 0),
        'end_hour': time(6, 0),
        'base_hours': 10.0
    },
    {
        'name': 'sunday',
        'description': 'Quart du dimanche (8h-18h)',
        'start_hour': time(8, 0),
        'end_hour': time(18, 0),
        'base_hours': 10.0
    },
    {
        'name': 'holiday',
        'description': 'Quart jour férié (8h-18h)',
        'start_hour': time(8, 0),
        'end_hour': time(18, 0),
        'base_hours': 10.0
    },
    {
        'name': 'early',
        'description': 'Quart tôt (6h-14h)',
        'start_hour': time(6, 0),
        'end_hour': time(14, 0),
        'base_hours': 8.0
    },
    {
        'name': 'late',
        'description': 'Quart tard (14h-22h)',
        'start_hour': time(14, 0),
        'end_hour': time(22, 0),
        'base_hours': 8.0
    },
]

print('🔄 Ajout des types de quarts...\n')

created_count = 0
existing_count = 0

for shift_data in shift_types_data:
    shift_type, created = ShiftType.objects.get_or_create(
        name=shift_data['name'],
        defaults={
            'description': shift_data['description'],
            'start_hour': shift_data['start_hour'],
            'end_hour': shift_data['end_hour'],
            'base_hours': shift_data['base_hours'],
            'is_active': True
        }
    )
    
    if created:
        print(f'  ✅ Créé: {shift_type.get_name_display()} ({shift_type.start_hour.strftime("%H:%M")} - {shift_type.end_hour.strftime("%H:%M")})')
        created_count += 1
    else:
        print(f'  ℹ️  Existe déjà: {shift_type.get_name_display()}')
        existing_count += 1

print(f'\n✅ Terminé!')
print(f'   {created_count} type(s) de quart créé(s)')
print(f'   {existing_count} type(s) de quart déjà existant(s)')
print(f'   Total: {ShiftType.objects.count()} type(s) de quart dans la base')
