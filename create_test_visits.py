"""
Script pour créer des visites médicales de test
Usage: python create_test_visits.py
"""

import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sirh_core.settings')
django.setup()

from employees.models import Employee, MedicalVisit

def create_test_visits():
    """Crée quelques visites médicales de test"""
    
    # Récupérer les employés
    employees = Employee.objects.all()
    
    if not employees:
        print("❌ Aucun employé trouvé. Créez d'abord des employés.")
        return
    
    today = date.today()
    
    # Créer différents types de visites
    visits_data = [
        {
            'employee': employees[0],
            'visit_type': 'embauche',
            'scheduled_date': today + timedelta(days=5),
            'status': 'scheduled',
            'doctor_name': 'Dr. Martin',
            'notes': 'Visite médicale d\'embauche urgente'
        },
        {
            'employee': employees[0] if len(employees) >= 1 else employees[0],
            'visit_type': 'periodique',
            'scheduled_date': today + timedelta(days=25),
            'status': 'scheduled',
            'doctor_name': 'Dr. Dupont',
            'notes': 'Visite périodique annuelle'
        },
        {
            'employee': employees[0] if len(employees) >= 2 else employees[0],
            'visit_type': 'reprise',
            'scheduled_date': None,
            'status': 'to_schedule',
            'notes': 'Visite de reprise après arrêt maladie à planifier'
        },
        {
            'employee': employees[0] if len(employees) >= 3 else employees[0],
            'visit_type': 'periodique',
            'scheduled_date': today - timedelta(days=15),
            'status': 'completed',
            'completed_date': today - timedelta(days=15),
            'doctor_name': 'Dr. Bernard',
            'result': 'apte',
            'next_visit_date': today + timedelta(days=350),
            'notes': 'Visite effectuée - RAS'
        },
    ]
    
    print("🏥 Création des visites médicales de test...\n")
    
    for visit_data in visits_data:
        visit = MedicalVisit.objects.create(**visit_data)
        print(f"✅ Visite créée : {visit.employee.user.get_full_name()} - {visit.get_visit_type_display()}")
        if visit.scheduled_date:
            print(f"   Date : {visit.scheduled_date.strftime('%d/%m/%Y')}")
            if visit.is_urgent:
                print(f"   ⚠️  URGENT : Dans {visit.days_until_visit} jours")
        else:
            print(f"   📅 À planifier")
        print()
    
    print(f"✨ {len(visits_data)} visites médicales créées avec succès !")

if __name__ == '__main__':
    create_test_visits()
