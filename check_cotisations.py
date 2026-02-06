import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sirh_core.settings')
django.setup()

from payroll.models import PayrollContribution
from decimal import Decimal

print("=" * 80)
print("COTISATIONS SALARIALES ACTIVES")
print("=" * 80)

actives_salariales = PayrollContribution.objects.filter(is_active=True, is_patronal=False).order_by('name')
total_sans_plafond = Decimal('0')
total_avec_plafond = Decimal('0')

for c in actives_salariales:
    print(f"  ✓ {c.name:50s} {c.rate:6.2f}% {'(plafond ' + str(c.ceiling) + '€)' if c.ceiling else ''}")
    if not c.ceiling:
        total_sans_plafond += c.rate
    else:
        total_avec_plafond += c.rate

print(f"\nTotal taux sans plafond: {total_sans_plafond:.2f}%")
print(f"Total taux avec plafond: {total_avec_plafond:.2f}%")
print(f"Taux effectif estimé (sur salaire standard <4005€): {total_sans_plafond + total_avec_plafond:.2f}%")

print("\n" + "=" * 80)
print("SIMULATION: 9755.85€ brut")
print("=" * 80)

brut = Decimal('9755.85')
total_cotisations = Decimal('0')

for c in actives_salariales:
    rate = c.rate / Decimal('100')
    if c.ceiling:
        applicable_base = min(brut, c.ceiling)
        amount = applicable_base * rate
    else:
        applicable_base = brut
        amount = applicable_base * rate
    
    total_cotisations += amount
    print(f"  {c.name:50s} {amount:8.2f}€")

print(f"\n{'TOTAL COTISATIONS':50s} {total_cotisations:8.2f}€")
print(f"{'Taux effectif':50s} {(total_cotisations/brut*100):7.2f}%")
print(f"{'Salaire NET':50s} {brut - total_cotisations:8.2f}€")
