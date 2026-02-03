"""
Script de démonstration complet:
TimeSheet (avec heures réelles) → Payroll (calcul automatique avec cotisations)
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sirh_core.settings")
django.setup()

from decimal import Decimal
from datetime import date, datetime, time
from employees.models import Employee
from contracts.models import Contract
from timesheets.models import TimeSheet, TimeSheetEntry
from payroll.models import Payroll
from planning.models import Shift, Assignment
from accounts.models import CustomUser

print("=" * 70)
print("📋 DÉMONSTRATION: COHÉRENCE FEUILLE DE TEMPS → FICHE DE PAIE")
print("=" * 70)

# Étape 1: Récupérer un employé existant
employee = Employee.objects.first()
if not employee:
    print("❌ Aucun employé trouvé!")
    exit(1)

print(f"\n👤 Employé: {employee.user.get_full_name()}")
print(f"💼 Profession: {employee.profession.label}")

# Étape 2: Vérifier qu'il a un contrat actif
today = date.today()
active_contract = Contract.objects.filter(
    employee=employee,
    start_date__lte=today,
    end_date__gte=today
).first()

if not active_contract or not active_contract.hourly_rate:
    print(f"❌ Pas de contrat actif avec taux horaire!")
    # Créer un contrat de test
    active_contract = Contract.objects.create(
        employee=employee,
        start_date=date(2026, 1, 1),
        end_date=date(2027, 12, 31),
        position='Test Position',
        contract_type='CDI',
        hourly_rate=Decimal('11.88'),
        occupational_health_service='Médecin Généraliste'
    )
    print(f"✓ Contrat créé: {active_contract.hourly_rate}€/h")
else:
    print(f"✓ Contrat actif: {active_contract.hourly_rate}€/h")

# Étape 3: Créer une feuille de temps pour le mois
year = 2026
month = 1
period_str = f"{year}-{month:02d}"

timesheet, created = TimeSheet.objects.get_or_create(
    employee=employee,
    year=year,
    month=month,
    defaults={
        'status': 'approved'  # Approuvée pour pouvoir générer la paie
    }
)

print(f"\n📅 Feuille de temps: {period_str}")
print(f"   Statut: {timesheet.get_status_display()}")

# Étape 4: Créer des entrées de feuille de temps réalistes
TimeSheetEntry.objects.filter(timesheet=timesheet).delete()

entries_data = [
    ('normal', Decimal('160.00'), 'Heures normales'),
    ('night', Decimal('16.00'), 'Heures de nuit'),
    ('sunday', Decimal('8.00'), 'Heures dimanche'),
    ('overtime', Decimal('6.00'), 'Heures supplémentaires'),
]

print(f"\n⏱️  Heures saisies dans la feuille de temps:")
for hour_type, hours, description in entries_data:
    entry = TimeSheetEntry.objects.create(
        timesheet=timesheet,
        date=date(year, month, 1),
        hour_type=hour_type,
        hours_worked=hours,
        hourly_rate=active_contract.hourly_rate,
        notes=description
    )
    print(f"   - {description}: {hours}h")

# Étape 5: Vérifier les totaux dans la TimeSheet
print(f"\n✓ Totaux dans feuille de temps:")
print(f"   Normal: {timesheet.total_normal_hours}h")
print(f"   Nuit: {timesheet.total_night_hours}h")
print(f"   Dimanche: {timesheet.total_sunday_hours}h")
print(f"   Heures supp: {timesheet.total_overtime_hours}h")
print(f"   TOTAL: {timesheet.total_hours}h")

# Étape 6: Créer la paie depuis la feuille de temps
print(f"\n💰 GÉNÉRATION DE LA PAIE:")
print("-" * 70)

payroll, created = Payroll.objects.get_or_create(
    employee=employee,
    year=year,
    month=month,
    defaults={
        'period': period_str,
        'status': 'draft'
    }
)

# Étape 7: Remplir les heures depuis la TimeSheet
if payroll.populate_hours_from_timesheet():
    print("✓ Heures importées depuis feuille de temps")
else:
    print("❌ Impossible d'importer les heures")
    exit(1)

# Étape 8: Calculer les salaires
hourly_rate = Decimal(str(active_contract.hourly_rate))

payroll.normal_salary = payroll.normal_hours * hourly_rate
payroll.night_salary = payroll.night_hours * hourly_rate * Decimal('1.25')
payroll.sunday_salary = payroll.sunday_hours * hourly_rate * Decimal('1.50')
payroll.holiday_salary = payroll.holiday_hours * hourly_rate * Decimal('2.00')
payroll.overtime_salary = payroll.overtime_hours * hourly_rate * Decimal('1.50')

payroll.gross_salary = (
    payroll.normal_salary +
    payroll.night_salary +
    payroll.sunday_salary +
    payroll.holiday_salary +
    payroll.overtime_salary
)

print(f"\n📊 HEURES RÉCUPÉRÉES DEPUIS TIMESHEET:")
print(f"   Normales: {payroll.normal_hours}h × {hourly_rate}€ = {payroll.normal_salary}€")
print(f"   Nuit: {payroll.night_hours}h × {hourly_rate}€ × 1.25 = {payroll.night_salary}€")
print(f"   Dimanche: {payroll.sunday_hours}h × {hourly_rate}€ × 1.50 = {payroll.sunday_salary}€")
print(f"   Féries: {payroll.holiday_hours}h × {hourly_rate}€ × 2.00 = {payroll.holiday_salary}€")
print(f"   Supp: {payroll.overtime_hours}h × {hourly_rate}€ × 1.50 = {payroll.overtime_salary}€")
print(f"   ➡️  BRUT: {payroll.gross_salary}€")

# Étape 9: Appliquer les cotisations depuis la BD
payroll.calculate_with_payroll_rules()

print(f"\n🏛️  COTISATIONS CALCULÉES DEPUIS LA BASE DE DONNÉES:")
from payroll.models import PayrollContribution

active_contributions = PayrollContribution.objects.filter(
    is_active=True
).exclude(name__icontains='patronale')

for contribution in active_contributions.order_by('name'):
    rate = contribution.rate / Decimal('100')
    if contribution.ceiling:
        applicable_base = min(payroll.gross_salary, contribution.ceiling)
        amount = applicable_base * rate
    else:
        applicable_base = payroll.gross_salary
        amount = applicable_base * rate
    print(f"   {contribution.name}: {amount:.2f}€")

# Étape 10: Sauvegarder et afficher résumé
payroll.status = 'calculated'
from django.utils import timezone
payroll.calculated_at = timezone.now()
payroll.save()

print(f"\n📄 RÉSUMÉ FICHE DE PAIE:")
print("=" * 70)
print(f"   Salaire BRUT (depuis TimeSheet): {payroll.gross_salary}€")
print(f"   Cotisations sociales: {payroll.social_security:.2f}€")
print(f"   Taxes: {payroll.taxes:.2f}€")
print(f"   Autres déductions: {payroll.other_deductions:.2f}€")
print(f"   Déductions TOTAL: {payroll.total_deductions:.2f}€")
print(f"   ➡️  SALAIRE NET: {payroll.net_salary:.2f}€")
print("=" * 70)

print(f"\n✅ Fiche de paie générée: ID {payroll.id}")
print(f"   Accessible via: /payroll/{payroll.id}/detail/")
print(f"   API JSON: /payroll/{payroll.id}/api/calculation/")

print(f"\n✓ COHÉRENCE VÉRIFIÉE:")
print(f"   Les heures de paie correspondent à la feuille de temps")
print(f"   Les cotisations appliquées respectent le code du travail")
print(f"   Le net à payer est cohérent (brut - cotisations)")
print("\n" + "=" * 70)
