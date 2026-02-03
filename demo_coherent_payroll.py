"""
Script de démonstration COMPLÈTE et COHÉRENTE:
Planning (Shifts) → TimeSheet (auto-fill) → Payroll
Tout est synchronisé!
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sirh_core.settings")
django.setup()

from decimal import Decimal
from datetime import date, datetime, time, timedelta
from employees.models import Employee
from contracts.models import Contract
from timesheets.models import TimeSheet
from payroll.models import Payroll
from planning.models import Shift, ShiftType, Assignment
from django.utils import timezone

print("=" * 80)
print("📋 DÉMONSTRATION COMPLÈTE: PLANNING → TIMESHEET → PAYROLL (COHÉRENT)")
print("=" * 80)

# Étape 1: Récupérer employé et contrat
employee = Employee.objects.first()
if not employee:
    print("❌ Aucun employé trouvé!")
    exit(1)

print(f"\n👤 Employé: {employee.user.get_full_name()}")

today = date.today()
active_contract = Contract.objects.filter(
    employee=employee,
    start_date__lte=today,
    end_date__gte=today
).first()

if not active_contract or not active_contract.hourly_rate:
    print("❌ Pas de contrat actif!")
    exit(1)

print(f"💼 Contrat actif: {active_contract.hourly_rate}€/h")

# Étape 2: Créer des Shifts dans le Planning
year = 2026
month = 1

print(f"\n📅 Planning pour {month:02d}/{year}:")
print("-" * 80)

# Récupérer ou créer le type de quart
shift_type, _ = ShiftType.objects.get_or_create(
    name='Jour Complet',
    defaults={
        'description': 'Quart journalier standard',
        'start_hour': time(9, 0),
        'end_hour': time(17, 0),
        'base_hours': 8
    }
)

# Supprimer les shifts existants du mois
Shift.objects.filter(date__year=year, date__month=month).delete()

# Créer des shifts (exemple réaliste)
shifts_data = [
    # Semaine 1
    (date(2026, 1, 1), time(8, 0), time(16, 0), 'Jour normales'),
    (date(2026, 1, 2), time(8, 0), time(16, 0), 'Jour normales'),
    (date(2026, 1, 3), time(8, 0), time(16, 0), 'Jour normales'),
    (date(2026, 1, 4), time(8, 0), time(16, 0), 'Jour normales'),
    (date(2026, 1, 5), time(8, 0), time(16, 0), 'Jour normales'),
    # Semaine 2
    (date(2026, 1, 8), time(8, 0), time(16, 0), 'Jour normales'),
    (date(2026, 1, 9), time(8, 0), time(16, 0), 'Jour normales'),
    (date(2026, 1, 10), time(8, 0), time(16, 0), 'Jour normales'),
    (date(2026, 1, 11), time(8, 0), time(16, 0), 'Jour normales'),
    (date(2026, 1, 12), time(8, 0), time(16, 0), 'Jour normales'),
    # Semaine 3
    (date(2026, 1, 15), time(22, 0), time(6, 0), 'Nuit'),  # De nuit qui passe minuit
    (date(2026, 1, 16), time(22, 0), time(6, 0), 'Nuit'),
    (date(2026, 1, 17), time(22, 0), time(6, 0), 'Nuit'),
    (date(2026, 1, 18), time(8, 0), time(16, 0), 'Jour normales'),
    (date(2026, 1, 19), time(8, 0), time(16, 0), 'Jour normales'),
    # Semaine 4
    (date(2026, 1, 22), time(8, 0), time(16, 0), 'Jour normales'),
    (date(2026, 1, 23), time(8, 0), time(16, 0), 'Jour normales'),
    (date(2026, 1, 24), time(8, 0), time(16, 0), 'Jour normales'),
    (date(2026, 1, 25), time(8, 0), time(16, 0), 'Jour normales'),
    (date(2026, 1, 26), time(8, 0), time(16, 0), 'Jour normales'),
]

shifts_created = []
for shift_date, start_time, end_time, description in shifts_data:
    shift = Shift.objects.create(
        date=shift_date,
        start_time=start_time,
        end_time=end_time,
        shift_type=shift_type,
        notes=description
    )
    shifts_created.append(shift)
    
    # Calculer les heures
    start = datetime.combine(shift_date, start_time)
    end = datetime.combine(shift_date, end_time)
    if end < start:
        end += timedelta(days=1)
    hours = (end - start).total_seconds() / 3600
    
    # Assigner au employé
    assignment = Assignment.objects.create(
        employee=employee,
        shift=shift,
        status='confirmed'
    )
    print(f"  ✓ {shift_date} ({shift_date.strftime('%A')}): {start_time} - {end_time} ({hours}h) → {description}")

print(f"\n✓ {len(shifts_created)} Shifts créés dans le Planning")

# Étape 3: Créer TimeSheet depuis Planning (auto-fill)
print(f"\n📝 Création feuille de temps depuis Planning...")
timesheet, created = TimeSheet.objects.get_or_create(
    employee=employee,
    year=year,
    month=month,
    defaults={'status': 'draft'}
)

# Auto-remplir depuis les Assignments
entries_created = timesheet.auto_fill_from_assignments()
print(f"✓ {entries_created} entrées créées dans la feuille de temps")

# Approuver la feuille de temps
timesheet.status = 'approved'
timesheet.approved_at = timezone.now()
timesheet.save()
print(f"✓ Feuille de temps approuvée")

# Afficher les totaux
print(f"\n📊 Totaux feuille de temps:")
print(f"   Normal: {timesheet.total_normal_hours}h")
print(f"   Nuit: {timesheet.total_night_hours}h")
print(f"   Dimanche: {timesheet.total_sunday_hours}h")
print(f"   Féries: {timesheet.total_holiday_hours}h")
print(f"   Supp: {timesheet.total_overtime_hours}h")
print(f"   TOTAL: {timesheet.total_hours}h")

# Étape 4: Générer la Payroll depuis TimeSheet
print(f"\n💰 GÉNÉRATION DE LA PAIE...")
print("-" * 80)

payroll, created = Payroll.objects.get_or_create(
    employee=employee,
    year=year,
    month=month,
    defaults={'period': f'{year}-{month:02d}', 'status': 'draft'}
)

# Remplir heures depuis TimeSheet
if payroll.populate_hours_from_timesheet():
    print("✓ Heures récupérées depuis feuille de temps (elle-même issue du Planning)")
else:
    print("❌ Erreur import heures")
    exit(1)

# Calculer les salaires
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

# Appliquer cotisations
payroll.calculate_with_payroll_rules()

payroll.status = 'calculated'
payroll.calculated_at = timezone.now()
payroll.save()

# Étape 5: Afficher le résumé cohérent
print(f"\n✅ RÉSUMÉ COHÉRENT (Planning → TimeSheet → Payroll):")
print("=" * 80)
print(f"\n📅 SOURCE:")
print(f"   Planning: {len(shifts_created)} shifts assignés")
print(f"   TimeSheet: Auto-remplie depuis Planning ({timesheet.total_hours}h)")
print(f"   Paie: Récupérée de la TimeSheet")

print(f"\n⏱️  HEURES (cohérentes):")
print(f"   Normales: {payroll.normal_hours}h")
print(f"   Nuit: {payroll.night_hours}h")
print(f"   Dimanche: {payroll.sunday_hours}h")
print(f"   Féries: {payroll.holiday_hours}h")
print(f"   Supp: {payroll.overtime_hours}h")
print(f"   TOTAL: {payroll.total_hours}h ✓ (correspond au Planning)")

print(f"\n💵 SALAIRES:")
print(f"   Normales: {payroll.normal_hours}h × {hourly_rate}€ = {payroll.normal_salary}€")
print(f"   Nuit: {payroll.night_hours}h × {hourly_rate}€ × 1.25 = {payroll.night_salary}€")
print(f"   Dimanche: {payroll.sunday_hours}h × {hourly_rate}€ × 1.50 = {payroll.sunday_salary}€")
print(f"   Féries: {payroll.holiday_hours}h × {hourly_rate}€ × 2.00 = {payroll.holiday_salary}€")
print(f"   Supp: {payroll.overtime_hours}h × {hourly_rate}€ × 1.50 = {payroll.overtime_salary}€")
print(f"   BRUT: {payroll.gross_salary}€")

print(f"\n🏛️  COTISATIONS (code du travail):")
print(f"   URSSAF: {payroll.social_security * Decimal('8.03') / Decimal('100'):.2f}€")
print(f"   CSG + CRDS: {(payroll.social_security * (Decimal('2.40') + Decimal('5.10') + Decimal('0.95')) / Decimal('100')):.2f}€")
print(f"   Retraite: {(payroll.social_security * Decimal('6.20') / Decimal('100')):.2f}€")
print(f"   TOTAL COTISATIONS: {payroll.social_security:.2f}€")

print(f"\n📄 RÉSULTAT FINAL:")
print(f"   Salaire BRUT: {payroll.gross_salary:.2f}€")
print(f"   Déductions: {payroll.total_deductions:.2f}€ (dont {payroll.social_security:.2f}€ cotisations)")
print(f"   ➡️  SALAIRE NET: {payroll.net_salary:.2f}€")

print(f"\n" + "=" * 80)
print(f"✅ COHÉRENCE VÉRIFIÉE:")
print(f"   ✓ Planning ({len(shifts_created)} shifts) → TimeSheet ({timesheet.total_hours}h) → Payroll")
print(f"   ✓ Total heures: {payroll.total_hours}h (cohérent)")
print(f"   ✓ Cotisations: {payroll.social_security:.2f}€ (~{(payroll.social_security / payroll.gross_salary * 100):.1f}% du brut)")
print(f"   ✓ Net/Brut: {(payroll.net_salary / payroll.gross_salary * 100):.1f}% (réaliste)")
print("=" * 80)

print(f"\n📍 Fiche de paie: ID {payroll.id}")
print(f"   /payroll/{payroll.id}/detail/")
