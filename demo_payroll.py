"""
Script de démonstration pour créer une fiche de paie exemple
avec les variables et cotisations intégrées
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sirh_core.settings")
django.setup()

from decimal import Decimal
from employees.models import Employee, Profession
from payroll.models import Payroll, SalaryScale, PayrollContribution, PayrollVariable
from accounts.models import CustomUser as User
from django.utils import timezone
from datetime import date

# Récupérer le premier employé existant, sinon en créer un
try:
    employee = Employee.objects.first()
    if not employee:
        raise Employee.DoesNotExist
except Employee.DoesNotExist:
    # Créer un utilisateur
    user, _ = User.objects.get_or_create(
        username='demo_employee',
        defaults={
            'email': 'demo@example.com',
            'first_name': 'Jean',
            'last_name': 'Dupont',
            'role': 'employee'
        }
    )
    
    profession, _ = Profession.objects.get_or_create(
        label='Agent de service',
        defaults={'description': 'Poste standard'}
    )
    
    employee = Employee.objects.create(
        user=user,
        employee_id='EMP_DEMO_001',
        profession=profession,
        birth_date=date(1990, 1, 1)
    )

# Créer une grille salariale
salary_scale, created = SalaryScale.objects.get_or_create(
    name='Grille Standard 2026',
    level='smic',
    defaults={
        'base_rate': Decimal('11.88'),  # SMIC 2026 mis à jour
        'night_multiplier': Decimal('1.25'),
        'sunday_multiplier': Decimal('1.50'),
        'holiday_multiplier': Decimal('2.00'),
        'overtime_multiplier': Decimal('1.50'),
    }
)

# Mettre à jour si existe déjà
if not created:
    salary_scale.base_rate = Decimal('11.88')
    salary_scale.save()

print("=" * 60)
print("📊 DÉMONSTRATION INTÉGRATION COTISATIONS SOCIALES")
print("=" * 60)
print(f"\n👤 Employé: {employee.user.get_full_name()}")
print(f"💼 Profession: {employee.profession.label}")
print(f"\n💰 Grille: {salary_scale.name}")
print(f"⏱️  Taux horaire: {salary_scale.base_rate}€/h")

# Créer une paie exemple
period = "2026-01"
payroll, created = Payroll.objects.update_or_create(
    employee=employee,
    period=period,
    defaults={
        'year': 2026,
        'month': 1,
        'status': 'draft',
        'normal_hours': Decimal('160.00'),
        'night_hours': Decimal('20.00'),
        'sunday_hours': Decimal('8.00'),
        'holiday_hours': Decimal('0.00'),
        'overtime_hours': Decimal('10.00'),
        'total_hours': Decimal('198.00'),
    }
)

# Calculer le salaire brut
payroll.calculate_salary(salary_scale)
payroll.save()

print(f"\n📅 Période: {payroll.period}")
print(f"⏰ Heures:")
print(f"   - Normales: {payroll.normal_hours}h")
print(f"   - Nuit: {payroll.night_hours}h")
print(f"   - Dimanche: {payroll.sunday_hours}h")
print(f"   - Féries: {payroll.holiday_hours}h")
print(f"   - Supplémentaires: {payroll.overtime_hours}h")
print(f"   TOTAL: {payroll.total_hours}h")

print(f"\n💵 Salaires bruts:")
print(f"   - Normal: {payroll.normal_salary}€")
print(f"   - Nuit: {payroll.night_salary}€")
print(f"   - Dimanche: {payroll.sunday_salary}€")
print(f"   - Féries: {payroll.holiday_salary}€")
print(f"   - Supplémentaires: {payroll.overtime_salary}€")
print(f"   BRUT TOTAL: {payroll.gross_salary}€")

# Appliquer les cotisations depuis la DB
print(f"\n🏛️ COTISATIONS SOCIALES APPLIQUÉES:")
print("-" * 60)

active_contributions = PayrollContribution.objects.filter(is_active=True).exclude(name__icontains='patronale').order_by('name')
total_contributions = Decimal('0')

for contribution in active_contributions:
    rate = contribution.rate / Decimal('100')
    
    if contribution.ceiling:
        applicable_base = min(payroll.gross_salary, contribution.ceiling)
        amount = applicable_base * rate
        plafond_info = f" (plafond: {contribution.ceiling}€)"
    else:
        applicable_base = payroll.gross_salary
        amount = applicable_base * rate
        plafond_info = ""
    
    total_contributions += amount
    print(f"   {contribution.name}")
    print(f"      Taux: {contribution.rate}%{plafond_info}")
    print(f"      Assiette: {applicable_base}€")
    print(f"      Montant: {amount:.2f}€")
    print()

print("-" * 60)
print(f"   TOTAL COTISATIONS: {total_contributions:.2f}€")

# Calculer le net
payroll.social_security = total_contributions
payroll.total_deductions = payroll.social_security + payroll.taxes + payroll.other_deductions
payroll.net_salary = payroll.gross_salary - payroll.total_deductions
payroll.status = 'calculated'
payroll.calculated_at = timezone.now()
payroll.save()

print(f"\n📄 RÉSUMÉ FICHE DE PAIE:")
print(f"   Salaire BRUT: {payroll.gross_salary}€")
print(f"   Cotisations: {payroll.social_security}€")
print(f"   Impôts: {payroll.taxes}€")
print(f"   Autres déductions: {payroll.other_deductions}€")
print(f"   Déductions TOTAL: {payroll.total_deductions}€")
print(f"   ➡️  SALAIRE NET: {payroll.net_salary}€")

print(f"\n✅ Fiche de paie créée/mise à jour: ID {payroll.id}")
print(f"   Accessible via: /payroll/{payroll.id}/detail/")
print(f"   API JSON: /payroll/{payroll.id}/api/calculation/")
print("\n" + "=" * 60)
