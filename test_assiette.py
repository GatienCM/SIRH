"""
Test pour vérifier que l'assiette CSG/CRDS est bien à 98.25%
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sirh_project.settings')
django.setup()

from decimal import Decimal
from payroll.models import PayrollContribution

print("=" * 100)
print("🧪 TEST CONFIGURATION CSG/CRDS - Vérification assiette 98.25%")
print("=" * 100)
print()

# Récupérer les contributions CSG/CRDS
csg_ded = PayrollContribution.objects.filter(name='CSG déductible', is_active=True).first()
csg_non_ded = PayrollContribution.objects.filter(name='CSG non déductible', is_active=True).first()
crds = PayrollContribution.objects.filter(name='CRDS', is_active=True).first()

contributions_to_test = [
    ('CSG déductible', csg_ded),
    ('CSG non déductible', csg_non_ded),
    ('CRDS', crds)
]

test_brut = Decimal('5000.00')
print(f"💶 Salaire brut de test : {test_brut}€")
print()

for name, contrib in contributions_to_test:
    if contrib:
        print(f"📋 {name}")
        print(f"   - Taux nominal : {contrib.rate}%")
        print(f"   - Type assiette : {contrib.assiette_type}")
        print(f"   - Organisme : {contrib.organisme}")
        print(f"   - Déductible fiscalement : {contrib.deductible_fiscalement}")
        
        # Calculer l'assiette
        if contrib.assiette_type == 'ABATTUE_9825':
            assiette = test_brut * Decimal('0.9825')
            print(f"   - Assiette calculée : {test_brut} × 0.9825 = {assiette:.2f}€")
            montant = assiette * (contrib.rate / Decimal('100'))
            taux_effectif = (montant / test_brut) * Decimal('100')
            print(f"   - Montant cotisation : {assiette:.2f}€ × {contrib.rate}% = {montant:.2f}€")
            print(f"   ✅ Taux effectif : {taux_effectif:.4f}% (au lieu de {contrib.rate}%)")
        else:
            print(f"   ❌ ERREUR : Type assiette devrait être 'ABATTUE_9825' mais est '{contrib.assiette_type}'")
        print()
    else:
        print(f"❌ {name} : NON TROUVÉE")
        print()

print("=" * 100)

# Vérifier aussi les tranches T2
print()
print("📐 VÉRIFICATION TRANCHES T2")
print("=" * 100)
print()

retraite_t2 = PayrollContribution.objects.filter(name='Retraite complémentaire T2').first()
ceg_t2 = PayrollContribution.objects.filter(name='CEG T2').first()

for contrib in [retraite_t2, ceg_t2]:
    if contrib:
        print(f"📋 {contrib.name}")
        print(f"   - Taux : {contrib.rate}%")
        print(f"   - Plafond : {contrib.ceiling}€")
        print(f"   - Tranche min : {contrib.tranche_min}€" if contrib.tranche_min else "   - Tranche min : Non définie ❌")
        print(f"   - Organisme : {contrib.organisme}")
        print(f"   - Active : {contrib.is_active}")
        print()

print("=" * 100)
print("✅ Test terminé")
print("=" * 100)
