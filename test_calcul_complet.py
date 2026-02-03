"""
Test du calcul complet sur un bulletin de paie réel
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sirh_project.settings')
django.setup()

from decimal import Decimal
from payroll.models import Payroll, Employee
from django.contrib.auth.models import User

print("=" * 100)
print("🧪 TEST CALCUL BULLETIN DE PAIE - Vérification assiette 98.25% + Tranches T2")
print("=" * 100)
print()

# Trouver un employé existant
employee = Employee.objects.first()

if not employee:
    print("❌ Aucun employé trouvé dans la base de données")
    print("Veuillez créer un employé depuis l'interface admin")
    exit(1)

print(f"👤 Employé : {employee.user.get_full_name()} (ID: {employee.employee_id})")
print()

# Test 1 : Salaire standard (≤ PMSS)
print("=" * 100)
print("TEST 1 : Salaire 3000€ (< PMSS)")
print("=" * 100)

# Supprimer d'abord le bulletin existant s'il existe
Payroll.objects.filter(employee=employee, period='2026-01').delete()

payroll1 = Payroll.objects.create(
    employee=employee,
    period='2026-01',
    year=2026,
    month=1,
    status='draft',
    gross_salary=Decimal('3000.00'),
    net_salary=Decimal('0.00')
)

payroll1.calculate_with_payroll_rules()

print(f"💶 Salaire brut : {payroll1.gross_salary}€")
print(f"💳 Cotisations salariales : {payroll1.total_deductions}€")
print(f"📊 Taux de cotisation : {(payroll1.total_deductions / payroll1.gross_salary * 100):.2f}%")
print(f"💵 Salaire net : {payroll1.net_salary}€")
print()

# Détail des items
print("Détail des cotisations :")
for item in payroll1.items.filter(item_type='deduction').order_by('description'):
    if any(term in item.description.lower() for term in ['csg', 'crds']):
        taux_effectif = (item.amount / payroll1.gross_salary * 100) if payroll1.gross_salary else 0
        print(f"  • {item.description} : {item.amount:.2f}€ (taux effectif: {taux_effectif:.4f}%)")

print()

# Test 2 : Salaire élevé (> PMSS pour tester T2)
print("=" * 100)
print("TEST 2 : Salaire 9755€ (> PMSS pour tester tranches)")
print("=" * 100)

# Supprimer d'abord le bulletin existant s'il existe
Payroll.objects.filter(employee=employee, period='2026-02').delete()

payroll2 = Payroll.objects.create(
    employee=employee,
    period='2026-02',
    year=2026,
    month=2,
    status='draft',
    gross_salary=Decimal('9755.00'),
    net_salary=Decimal('0.00')
)

payroll2.calculate_with_payroll_rules()

print(f"💶 Salaire brut : {payroll2.gross_salary}€")
print(f"💳 Cotisations salariales : {payroll2.total_deductions}€")
print(f"📊 Taux de cotisation : {(payroll2.total_deductions / payroll2.gross_salary * 100):.2f}%")
print(f"💵 Salaire net : {payroll2.net_salary}€")
print()

# Détail des items CSG/CRDS
print("Détail CSG/CRDS :")
for item in payroll2.items.filter(item_type='deduction').order_by('description'):
    if any(term in item.description.lower() for term in ['csg', 'crds']):
        taux_effectif = (item.amount / payroll2.gross_salary * 100) if payroll2.gross_salary else 0
        print(f"  • {item.description} : {item.amount:.2f}€ (taux effectif: {taux_effectif:.4f}%)")

print()

# Détail retraite (plafonnée)
print("Détail retraite :")
for item in payroll2.items.filter(item_type='deduction').order_by('description'):
    if 'vieillesse' in item.description.lower():
        print(f"  • {item.description} : {item.amount:.2f}€")

print()
print("=" * 100)
print("✅ Tests terminés")
print("=" * 100)

# Nettoyage
payroll1.delete()
payroll2.delete()
