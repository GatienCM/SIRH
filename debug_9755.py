"""
Debug détaillé du calcul pour 9755€ brut
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sirh_core.settings')
django.setup()

from decimal import Decimal
from payroll.models import PayrollContribution

print("=" * 100)
print("🔍 DEBUG CALCUL 9755€ BRUT - DÉTAIL LIGNE PAR LIGNE")
print("=" * 100)
print()

# Liste toutes les cotisations ACTIVES salariales
contributions = PayrollContribution.objects.filter(
    is_patronal=False,
    is_active=True
).order_by('name')

salaire_brut = Decimal('9755.00')
total_cotisations = Decimal('0.00')

print(f"💶 Salaire brut : {salaire_brut}€")
print(f"📅 PMSS 2026 : 3864€/mois")
print()
print("=" * 100)
print("COTISATIONS SALARIALES ACTIVES")
print("=" * 100)
print()

for contrib in contributions:
    # Déterminer l'assiette
    if contrib.assiette_type == 'ABATTUE_9825':
        assiette = salaire_brut * Decimal('0.9825')
        assiette_label = f"{salaire_brut}€ × 0.9825 = {assiette:.2f}€"
    elif contrib.assiette_type == 'PLAFONNEE' and contrib.ceiling:
        if contrib.tranche_min:
            # Tranche T2
            tranche_haute = min(salaire_brut, contrib.ceiling)
            assiette = max(Decimal('0'), tranche_haute - contrib.tranche_min)
            assiette_label = f"min({salaire_brut}, {contrib.ceiling}) - {contrib.tranche_min} = {assiette:.2f}€"
        else:
            # Tranche T1 ou plafonnée simple
            assiette = min(salaire_brut, contrib.ceiling)
            assiette_label = f"min({salaire_brut}, {contrib.ceiling}) = {assiette:.2f}€"
    else:
        # BRUT ou déplafonnée
        assiette = salaire_brut
        assiette_label = f"{salaire_brut}€"
    
    # Calculer le montant
    montant = assiette * (contrib.rate / Decimal('100'))
    taux_effectif = (montant / salaire_brut * Decimal('100'))
    
    total_cotisations += montant
    
    print(f"📋 {contrib.name}")
    print(f"   Taux : {contrib.rate}%")
    print(f"   Assiette ({contrib.assiette_type}) : {assiette_label}")
    print(f"   Montant : {montant:.2f}€")
    print(f"   Taux effectif : {taux_effectif:.4f}%")
    print()

print("=" * 100)
print(f"💳 TOTAL COTISATIONS SALARIALES : {total_cotisations:.2f}€")
print(f"📊 TAUX EFFECTIF GLOBAL : {(total_cotisations / salaire_brut * Decimal('100')):.2f}%")
print(f"💵 SALAIRE NET : {salaire_brut - total_cotisations:.2f}€")
print("=" * 100)
print()

# Calcul théorique attendu
print("=" * 100)
print("📐 CALCUL THÉORIQUE ATTENDU (URSSAF 2026)")
print("=" * 100)
print()

calcul_theorique = {
    'Vieillesse plafonnée (T1)': {'taux': Decimal('6.90'), 'assiette': min(salaire_brut, Decimal('3864.00'))},
    'Vieillesse déplafonnée': {'taux': Decimal('0.40'), 'assiette': salaire_brut},
    'Assurance chômage': {'taux': Decimal('2.40'), 'assiette': min(salaire_brut, Decimal('15456.00'))},
    'Retraite complémentaire T1': {'taux': Decimal('3.15'), 'assiette': min(salaire_brut, Decimal('3864.00'))},
    'CEG T1': {'taux': Decimal('0.86'), 'assiette': min(salaire_brut, Decimal('3864.00'))},
    'CSG déductible (98.25%)': {'taux': Decimal('6.80'), 'assiette': salaire_brut * Decimal('0.9825')},
    'CSG non déductible (98.25%)': {'taux': Decimal('2.40'), 'assiette': salaire_brut * Decimal('0.9825')},
    'CRDS (98.25%)': {'taux': Decimal('0.50'), 'assiette': salaire_brut * Decimal('0.9825')},
}

total_theorique = Decimal('0.00')
for nom, data in calcul_theorique.items():
    montant = data['assiette'] * (data['taux'] / Decimal('100'))
    total_theorique += montant
    print(f"• {nom}: {data['assiette']:.2f}€ × {data['taux']}% = {montant:.2f}€")

print()
print(f"💳 TOTAL THÉORIQUE : {total_theorique:.2f}€")
print(f"📊 TAUX THÉORIQUE : {(total_theorique / salaire_brut * Decimal('100')):.2f}%")
print()
print("=" * 100)
