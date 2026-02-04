#!/usr/bin/env python
"""Script pour ajouter les professions par défaut"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sirh_core.settings')
django.setup()

from employees.models import Profession

# Liste des professions à créer
professions_data = [
    {
        'code': 'ambulancier_dea',
        'label': 'Ambulancier DEA',
        'description': 'Ambulancier diplômé d\'État, habilité à effectuer le transport sanitaire et les gestes d\'urgence'
    },
    {
        'code': 'auxiliaire_ambulancier',
        'label': 'Auxiliaire ambulancier',
        'description': 'Auxiliaire ambulancier, assiste l\'ambulancier DEA dans le transport de patients'
    },
    {
        'code': 'chauffeur_vsl',
        'label': 'Chauffeur VSL',
        'description': 'Chauffeur de Véhicule Sanitaire Léger, transport de patients assis'
    },
    {
        'code': 'chauffeur_taxi',
        'label': 'Chauffeur taxi',
        'description': 'Chauffeur de taxi conventionné pour le transport de patients'
    },
    {
        'code': 'assistant_rh',
        'label': 'Assistant RH',
        'description': 'Assistant des ressources humaines, gestion administrative du personnel'
    },
    {
        'code': 'responsable_rh',
        'label': 'Responsable RH',
        'description': 'Responsable des ressources humaines, pilotage de la fonction RH'
    },
    {
        'code': 'responsable_exploitation',
        'label': 'Responsable d\'exploitation',
        'description': 'Responsable de l\'exploitation, gestion des plannings et des équipes'
    },
    {
        'code': 'comptable',
        'label': 'Comptable',
        'description': 'Comptable, gestion de la comptabilité et de la paie'
    },
    {
        'code': 'apprenti',
        'label': 'Apprenti',
        'description': 'Apprenti en formation dans l\'entreprise'
    },
    {
        'code': 'stagiaire',
        'label': 'Stagiaire',
        'description': 'Stagiaire en période de découverte professionnelle'
    },
]

print('🔄 Ajout des professions...\n')

created_count = 0
existing_count = 0

for prof_data in professions_data:
    profession, created = Profession.objects.get_or_create(
        code=prof_data['code'],
        defaults={
            'label': prof_data['label'],
            'description': prof_data['description'],
            'is_active': True
        }
    )
    
    if created:
        print(f'  ✅ Créée: {profession.label}')
        created_count += 1
    else:
        print(f'  ℹ️  Existe déjà: {profession.label}')
        existing_count += 1

print(f'\n✅ Terminé!')
print(f'   {created_count} profession(s) créée(s)')
print(f'   {existing_count} profession(s) déjà existante(s)')
print(f'   Total: {Profession.objects.count()} profession(s) dans la base')
