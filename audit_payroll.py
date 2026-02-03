#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sirh_core.settings')
django.setup()

from payroll.models import Payroll, PayrollContribution
from decimal import Decimal

# Récupérer la dernière paie créée
payroll = Payroll.objects.order_by('-id').first()

if not payroll:
    print("❌ Aucune paie trouvée")
    exit(1)

print(f"\n📋 AUDIT DE LA FICHE DE PAIE #{payroll.id}")
print("=" * 80)
print(f"Employé: {payroll.employee.user.get_full_name()}")
print(f"Période: {payroll.period}")
print(f"Salaire BRUT: {payroll.gross_salary}€")
print()

# Voir toutes les cotisations
print("🏛️ COTISATIONS SALARIALES (déductibles du salaire):")
print("-" * 80)
salarial = PayrollContribution.objects.filter(is_active=True, is_patronal=False)
total_salarial = Decimal('0.00')
for contrib in salarial:
    rate = contrib.rate / Decimal('100')
    if contrib.ceiling:
        base = min(payroll.gross_salary, contrib.ceiling)
        amount = base * rate
    else:
        base = payroll.gross_salary
        amount = payroll.gross_salary * rate
    total_salarial += amount
    print(f"  {contrib.name:40} {contrib.rate:6.2f}% × {base:10.2f}€ = {amount:10.2f}€")

print(f"\n  TOTAL COTISATIONS SALARIALES: {total_salarial:10.2f}€")

print("\n" + "=" * 80)
print("🏢 COTISATIONS PATRONALES (payées par l'employeur, PAS sur la fiche):")
print("-" * 80)
patronal = PayrollContribution.objects.filter(is_active=True, is_patronal=True)
total_patronal = Decimal('0.00')
for contrib in patronal:
    rate = contrib.rate / Decimal('100')
    if contrib.ceiling:
        base = min(payroll.gross_salary, contrib.ceiling)
        amount = base * rate
    else:
        base = payroll.gross_salary
        amount = payroll.gross_salary * rate
    total_patronal += amount
    print(f"  {contrib.name:40} {contrib.rate:6.2f}% × {base:10.2f}€ = {amount:10.2f}€")

print(f"\n  TOTAL COTISATIONS PATRONALES: {total_patronal:10.2f}€")

print("\n" + "=" * 80)
print("💰 RÉSUMÉ:")
print("-" * 80)
print(f"Salaire BRUT:                    {payroll.gross_salary:10.2f}€")
print(f"- Cotisations SALARIALES:        {total_salarial:10.2f}€")
print(f"= Salaire NET (fiche employé):   {payroll.gross_salary - total_salarial:10.2f}€")
print()
print(f"COÛT RÉEL POUR EMPLOYEUR:")
print(f"  Salaire BRUT:                  {payroll.gross_salary:10.2f}€")
print(f"+ Cotisations PATRONALES:        {total_patronal:10.2f}€")
print(f"= TOTAL COÛT EMPLOYEUR:          {payroll.gross_salary + total_patronal:10.2f}€")
print()
print(f"Payroll.social_security stored:  {payroll.social_security:10.2f}€")
print(f"Payroll.net_salary stored:       {payroll.net_salary:10.2f}€")
