#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sirh_core.settings')
django.setup()

from payroll.models import PayrollVariable, PayrollContribution
from decimal import Decimal

print("\n" + "=" * 80)
print("🔍 VÉRIFICATION DE L'INTÉGRATION DES VARIABLES ET COTISATIONS")
print("=" * 80)

# Test 1: Variables de paie
print("\n📊 VARIABLES DE PAIE ACTIVES:")
print("-" * 80)
variables = PayrollVariable.objects.filter(is_active=True).order_by('name')
if variables.exists():
    for var in variables:
        if var.unit == '%':
            multiplier = var.value / Decimal('100')
            print(f"  ✓ {var.name:45} {var.value:>8.2f}% → multiplicateur x{multiplier}")
        else:
            print(f"  ✓ {var.name:45} {var.value:>8.2f} {var.unit}")
else:
    print("  ❌ Aucune variable active")

# Test 2: Cotisations salariales
print("\n💼 COTISATIONS SALARIALES ACTIVES:")
print("-" * 80)
salarial_contribs = PayrollContribution.objects.filter(is_active=True, is_patronal=False).order_by('name')
if salarial_contribs.exists():
    for contrib in salarial_contribs:
        ceiling_text = f"plafond {contrib.ceiling:.2f}€" if contrib.ceiling else "sans plafond"
        print(f"  ✓ {contrib.name:45} {contrib.rate:>6.2f}% ({ceiling_text})")
    
    total_rate = sum(c.rate for c in salarial_contribs if not c.ceiling)
    print(f"\n  TOTAL taux sans plafond: {total_rate:.2f}%")
else:
    print("  ❌ Aucune cotisation salariale active")

# Test 3: Cotisations patronales
print("\n🏢 COTISATIONS PATRONALES ACTIVES:")
print("-" * 80)
patronal_contribs = PayrollContribution.objects.filter(is_active=True, is_patronal=True).order_by('name')
if patronal_contribs.exists():
    for contrib in patronal_contribs:
        ceiling_text = f"plafond {contrib.ceiling:.2f}€" if contrib.ceiling else "sans plafond"
        print(f"  ✓ {contrib.name:45} {contrib.rate:>6.2f}% ({ceiling_text})")
else:
    print("  ⚠️  Aucune cotisation patronale active")

# Test 4: Simulation d'un calcul
print("\n" + "=" * 80)
print("🧮 SIMULATION D'UN CALCUL DE PAIE (1000€ brut)")
print("=" * 80)

brut = Decimal('1000.00')

# Cotisations salariales
total_salarial = Decimal('0.00')
for contrib in salarial_contribs:
    rate = contrib.rate / Decimal('100')
    if contrib.ceiling:
        base = min(brut, contrib.ceiling)
    else:
        base = brut
    amount = base * rate
    total_salarial += amount
    print(f"  - {contrib.name:45} {amount:>8.2f}€")

net = brut - total_salarial

print(f"\n  Salaire BRUT:                                   {brut:>8.2f}€")
print(f"  Total cotisations salariales:                   {total_salarial:>8.2f}€")
print(f"  Salaire NET:                                    {net:>8.2f}€")
print(f"  Taux de prélèvement: {(total_salarial/brut*100):.2f}%")

print("\n" + "=" * 80)
print("✅ RÉSUMÉ:")
print(f"  - Variables actives: {variables.count()}")
print(f"  - Cotisations salariales actives: {salarial_contribs.count()}")
print(f"  - Cotisations patronales actives: {patronal_contribs.count()}")
print("=" * 80 + "\n")
