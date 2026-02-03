"""
Management command pour initialiser les données de base
"""
from django.core.management.base import BaseCommand
from employees.models import Profession
from planning.models import ShiftType

class Command(BaseCommand):
    help = 'Initialise les données de base (Professions, Types de quart)'

    def handle(self, *args, **options):
        # Professions
        professions_data = [
            ('ambulancier_dea', 'Ambulancier DEA', 'Ambulancier diplômé d\'état'),
            ('auxiliaire_ambulancier', 'Auxiliaire ambulancier', 'Auxiliaire ambulancier'),
            ('chauffeur_vsl', 'Chauffeur VSL', 'Chauffeur véhicule sanitaire léger'),
            ('chauffeur_taxi', 'Chauffeur taxi', 'Chauffeur taxi'),
            ('assistant_rh', 'Assistant RH', 'Assistant ressources humaines'),
            ('responsable_rh', 'Responsable RH', 'Responsable ressources humaines'),
            ('responsable_exploitation', 'Responsable d\'exploitation', 'Responsable d\'exploitation'),
            ('comptable', 'Comptable', 'Comptable'),
            ('apprenti', 'Apprenti', 'Apprenti'),
            ('stagiaire', 'Stagiaire', 'Stagiaire'),
        ]
        
        for code, label, description in professions_data:
            profession, created = Profession.objects.get_or_create(
                code=code,
                defaults={'label': label, 'description': description}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Profession créée: {label}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️  Profession existe déjà: {label}'))
        
        # Types de quart
        shifttypes_data = [
            ('Matin', '06:00', '14:00'),
            ('Après-midi', '14:00', '22:00'),
            ('Nuit', '22:00', '06:00'),
            ('Complet', '08:00', '18:00'),
        ]
        
        for name, start, end in shifttypes_data:
            shifttype, created = ShiftType.objects.get_or_create(
                name=name,
                defaults={'start_hour': start, 'end_hour': end}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Type de quart créé: {name}'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️  Type de quart existe déjà: {name}'))
        
        self.stdout.write(self.style.SUCCESS('✅ Initialisation terminée!'))
